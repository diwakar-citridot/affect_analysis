#!/usr/bin/env python3
"""Seed ``svarupa_concept_layer`` from the dimension/layer Excel mapping.

Steps:
  1. Add ``role ENUM('primary','contributing')`` to ``svarupa_concept_layer`` when missing.
  2. Read ``documentation/dimensions_and_concepts/Dimension & Attribute Mapping to
     Analytical Layers.xlsx``.
  3. Resolve ``Dimension`` -> ``dimension_id`` (``D{n}`` prefix or name lookup).
  4. Resolve concepts for each dimension from **all** rows in ``svarupa_concepts``
     (seeded from the latest dimension-attribute documentation JSON). Excel
     ``Core Attributes / Constructs`` names the *primary* subset when it lists
     specific tokens; remaining documentation concepts are still attached as
     ``contributing``. Bulk / descriptive cells (e.g. ``etc.``, ``16 archetypes``)
     treat every concept in the dimension as primary.
  5. Parse ``Primary Layer(s)`` / ``Contributing Layer(s)`` for layer codes
     (SEM, AFF, …). Parentheticals ending in ``only`` restrict that layer to
     named concepts (e.g. ``AFF (rāga/dveṣa only)``).
  6. Insert ``(dimension_id, concept_id, layer_code, role)`` rows.

Usage:
    PYTHONPATH=src python scripts/seed_concept_layer_from_excel.py
    PYTHONPATH=src python scripts/seed_concept_layer_from_excel.py --dry-run
    PYTHONPATH=src python scripts/seed_concept_layer_from_excel.py --truncate
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

logger = logging.getLogger("seed_concept_layer_from_excel")

DEFAULT_DATABASE = "svarupa_assistant_v1"
DEFAULT_XLSX = (
    Path(__file__).resolve().parents[1]
    / "documentation"
    / "dimensions_and_concepts"
    / "Dimension & Attribute Mapping to Analytical Layers.xlsx"
)

DIMENSION_RE = re.compile(r"^D(\d+)\b", re.IGNORECASE)
LAYER_CODE_RE = re.compile(r"\b([A-Z]{3})\b")
# ``AFF (rāga/dveṣa only)`` / ``PSY (vikalpa, smṛti only)`` — concept filters.
LAYER_ONLY_FILTER_RE = re.compile(
    r"\b([A-Z]{3})\s*\(([^)]*?\bonly\b[^)]*)\)",
    re.IGNORECASE,
)
VALID_LAYER_CODES = frozenset({"SEM", "COT", "AFF", "PHE", "PSY", "MET", "NAR"})

# English / common tokens -> concept slug (within a dimension when ambiguous).
# Keys use ``_ascii_key`` form (lookup always ascii-folds the Excel token).
CONCEPT_SLUG_ALIASES: dict[tuple[int, str], str] = {
    (1, "earth"): "prthivi",
    (1, "prithvi"): "prthivi",
    (1, "water"): "apas",
    (1, "fire"): "agni",
    (1, "air"): "vayu",
    (1, "ether"): "akasa",
    (1, "akasha"): "akasa",
    (10, "yoga"): "chapter_4_raja_yoga",
    (10, "rajayoga"): "chapter_4_raja_yoga",
    (10, "jnana"): "chapter_3_jnana_yoga",
    (10, "karma"): "chapter_2_karma_yoga",
    (10, "bhakti"): "chapter_5_bhakti_yoga",
    (12, "karma"): "karma_phala",
    (15, "vata"): "part_i_vata",
    (15, "pitta"): "part_ii_pitta",
    (15, "kapha"): "part_iii_kapha",
}

BULK_DESCRIPTOR_PATTERNS = (
    re.compile(r"\betc\.?\b", re.I),
    re.compile(r"\d+\s+(personality|practice|obstacles)\b", re.I),
    re.compile(r"\bthrough\b", re.I),
    re.compile(r"^virtue/vice\b", re.I),
    re.compile(r"\bprofiles\b", re.I),
    re.compile(r"^contemplative\b", re.I),
    re.compile(r"^waking\b", re.I),
    re.compile(r"^annamaya\b", re.I),
    re.compile(r"^cleansing\b", re.I),
    re.compile(r"^inquiry\b", re.I),
    re.compile(r"^higher/lower\b", re.I),
    re.compile(r"^superimposition\b", re.I),
    re.compile(r"^graha\b", re.I),
    re.compile(r"^descent\b", re.I),
    re.compile(r"^soul-age\b", re.I),
)

_XLSX_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


@dataclass(frozen=True)
class ExcelRow:
    dimension_label: str
    concepts_text: str
    primary_layers_text: str
    contributing_layers_text: str


@dataclass(frozen=True)
class LayerSpec:
    """A layer code with an optional concept-token filter from ``(… only)``."""

    layer_code: str
    concept_tokens: tuple[str, ...] | None = None


@dataclass(frozen=True)
class ConceptLayerInsert:
    dimension_id: int
    concept_id: int
    layer_code: str
    role: str


def _ascii_key(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value)
    stripped = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", stripped.lower())


def _col_index(cell_ref: str) -> int:
    """Convert Excel column letters in ``A1`` / ``AE12`` to a 0-based index."""
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    n = 0
    for ch in letters.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _cell_text(cell: ET.Element, shared: list[str]) -> str | None:
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        parts = [t.text or "" for t in cell.findall(".//m:t", _XLSX_NS)]
        text = "".join(parts)
        return text if text else None
    value_el = cell.find("m:v", _XLSX_NS)
    if value_el is None or value_el.text is None:
        return None
    if cell_type == "s":
        return shared[int(value_el.text)]
    return value_el.text


def _read_xlsx_stdlib(path: Path) -> list[list[str | None]]:
    """Read the first worksheet via stdlib (no openpyxl dependency)."""
    with zipfile.ZipFile(path) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall(".//m:si", _XLSX_NS):
                parts = [t.text or "" for t in si.findall(".//m:t", _XLSX_NS)]
                shared.append("".join(parts))

        sheet_name = next(
            (n for n in zf.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
            "xl/worksheets/sheet1.xml",
        )
        root = ET.fromstring(zf.read(sheet_name))
        rows: list[list[str | None]] = []
        for row_el in root.findall(".//m:sheetData/m:row", _XLSX_NS):
            by_col: dict[int, str | None] = {}
            max_col = -1
            for cell in row_el.findall("m:c", _XLSX_NS):
                ref = cell.get("r") or ""
                col = _col_index(ref) if ref else (max_col + 1)
                by_col[col] = _cell_text(cell, shared)
                max_col = max(max_col, col)
            row = [by_col.get(i) for i in range(max_col + 1)] if max_col >= 0 else []
            rows.append(row)
        return rows


def load_excel_rows(path: Path) -> list[ExcelRow]:
    if not path.is_file():
        raise FileNotFoundError(f"Excel mapping not found: {path}")

    raw_rows = _read_xlsx_stdlib(path)
    if not raw_rows:
        raise ValueError(f"Excel file is empty: {path}")

    header = [str(c or "").strip() for c in raw_rows[0]]
    expected = {
        "Dimension",
        "Core Attributes / Constructs",
        "Primary Layer(s)",
        "Contributing Layer(s)",
    }
    if not expected.issubset(set(header)):
        raise ValueError(f"Unexpected header row in {path}: {header}")

    col = {name: header.index(name) for name in expected}
    out: list[ExcelRow] = []
    for raw in raw_rows[1:]:
        if not raw or col["Dimension"] >= len(raw) or not raw[col["Dimension"]]:
            continue
        def _cell(name: str) -> str:
            idx = col[name]
            if idx >= len(raw) or raw[idx] is None:
                return ""
            return str(raw[idx]).strip()

        out.append(
            ExcelRow(
                dimension_label=_cell("Dimension"),
                concepts_text=_cell("Core Attributes / Constructs"),
                primary_layers_text=_cell("Primary Layer(s)"),
                contributing_layers_text=_cell("Contributing Layer(s)"),
            )
        )
    return out


def parse_dimension_id(
    label: str, dimension_by_id: dict[int, str], dimension_by_name: dict[str, int]
) -> int | None:
    match = DIMENSION_RE.match(label.strip())
    if match:
        dim_id = int(match.group(1))
        if dim_id in dimension_by_id:
            return dim_id

    key = _ascii_key(re.sub(r"^D\d+\s*", "", label, flags=re.I))
    if key in dimension_by_name:
        return dimension_by_name[key]

    for name_key, dim_id in dimension_by_name.items():
        if key and (key in name_key or name_key in key):
            return dim_id
    return None


def _split_filter_tokens(filter_body: str) -> tuple[str, ...]:
    """Extract concept tokens from ``rāga/dveṣa only`` / ``vikalpa, smṛti only``."""
    body = re.sub(r"\bonly\b", "", filter_body, flags=re.I)
    body = body.strip(" ,/;")
    tokens: list[str] = []
    for part in re.split(r"[,/]| and ", body):
        token = part.strip()
        if not token:
            continue
        token = re.sub(r"\s*\([^)]*\)\s*$", "", token).strip()
        if token:
            tokens.append(token)
    return tuple(tokens)


def parse_layer_specs(text: str) -> list[LayerSpec]:
    """Parse layer codes; keep ``(… only)`` concept filters when present."""
    if not text:
        return []

    # Scan original text so Sanskrit diacritics inside ``(… only)`` survive.
    filtered: dict[str, tuple[str, ...] | None] = {}
    for match in LAYER_ONLY_FILTER_RE.finditer(text):
        code = match.group(1).upper()
        if code not in VALID_LAYER_CODES:
            continue
        filtered[code] = _split_filter_tokens(match.group(2))

    seen: set[str] = set()
    ordered: list[LayerSpec] = []
    for match in LAYER_CODE_RE.finditer(text.upper()):
        code = match.group(1)
        if code not in VALID_LAYER_CODES or code in seen:
            continue
        seen.add(code)
        ordered.append(LayerSpec(layer_code=code, concept_tokens=filtered.get(code)))
    return ordered


def parse_layer_codes(text: str) -> list[str]:
    """Backward-compatible helper: layer codes only, ignoring filters."""
    return [spec.layer_code for spec in parse_layer_specs(text)]


def _is_bulk_descriptor(text: str) -> bool:
    return any(p.search(text) for p in BULK_DESCRIPTOR_PATTERNS)


def _split_concept_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for part in re.split(r",| and ", text):
        token = part.strip()
        if not token:
            continue
        token = re.sub(r"\s*\([^)]*\)\s*$", "", token).strip()
        token = re.sub(r"\s+etc\.?$", "", token, flags=re.I).strip()
        if token:
            tokens.append(token)
    return tokens


class ConceptLookup:
    """Resolve concept tokens within a dimension (latest ``svarupa_concepts``)."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._by_dimension: dict[int, list[dict[str, object]]] = defaultdict(list)
        self._index: dict[tuple[int, str], int] = {}
        for row in rows:
            dim_id = int(row["dimension_id"])
            concept_id = int(row["concept_id"])
            slug = str(row["slug"])
            name = str(row.get("name") or "")
            sanskrit = str(row.get("sanskrit_term") or "")
            self._by_dimension[dim_id].append(row)
            for raw in (slug, name, sanskrit):
                if raw:
                    self._index[(dim_id, _ascii_key(raw))] = concept_id
            for word in re.split(r"[/\s_-]+", name):
                word_key = _ascii_key(word)
                if len(word_key) >= 3:
                    self._index.setdefault((dim_id, word_key), concept_id)

    def all_concept_ids(self, dimension_id: int) -> list[int]:
        return [int(r["concept_id"]) for r in self._by_dimension.get(dimension_id, [])]

    def resolve_token(self, dimension_id: int, token: str) -> int | None:
        alias_slug = CONCEPT_SLUG_ALIASES.get((dimension_id, _ascii_key(token)))
        if alias_slug:
            aliased = self._index.get((dimension_id, _ascii_key(alias_slug)))
            if aliased is not None:
                return aliased

        direct = self._index.get((dimension_id, _ascii_key(token)))
        if direct is not None:
            return direct

        token_key = _ascii_key(token)
        if not token_key:
            return None
        # Prefer longest slug that equals / ends with / is ended by the token key
        # (handles documentation slugs like part_i_vata or chapter_2_karma_yoga).
        best: tuple[int, int] | None = None
        for row in self._by_dimension.get(dimension_id, []):
            slug_key = _ascii_key(str(row["slug"]))
            if not slug_key:
                continue
            if slug_key == token_key or slug_key.endswith(token_key) or token_key.endswith(slug_key):
                candidate = (len(slug_key), int(row["concept_id"]))
                if best is None or candidate[0] > best[0]:
                    best = candidate
        return best[1] if best else None

    def resolve_tokens(self, dimension_id: int, tokens: list[str] | tuple[str, ...]) -> list[int]:
        matched: list[int] = []
        seen: set[int] = set()
        for token in tokens:
            concept_id = self.resolve_token(dimension_id, token)
            if concept_id is not None and concept_id not in seen:
                seen.add(concept_id)
                matched.append(concept_id)
        return matched

    def resolve_primary_and_remainder(
        self, dimension_id: int, text: str
    ) -> tuple[list[int], list[int], bool]:
        """Return ``(primary_ids, remainder_ids, used_bulk)``.

        * Bulk / empty Excel cells → every documentation concept is primary.
        * Specific Excel tokens → those are primary; every other concept in the
          dimension (from the latest documentation seed) is remainder/contributing.
        * If specific tokens resolve to nothing → fall back to all as primary.
        """
        all_ids = self.all_concept_ids(dimension_id)
        if not text or _is_bulk_descriptor(text):
            return all_ids, [], True

        primary = self.resolve_tokens(dimension_id, _split_concept_tokens(text))
        if not primary:
            return all_ids, [], True

        primary_set = set(primary)
        remainder = [cid for cid in all_ids if cid not in primary_set]
        return primary, remainder, False


def _append_insert(
    inserts: list[ConceptLayerInsert],
    dedupe: set[tuple[int, str, str]],
    *,
    dimension_id: int,
    concept_id: int,
    layer_code: str,
    role: str,
) -> None:
    key = (concept_id, layer_code, role)
    if key in dedupe:
        return
    if role == "contributing" and (concept_id, layer_code, "primary") in dedupe:
        return
    dedupe.add(key)
    inserts.append(
        ConceptLayerInsert(
            dimension_id=dimension_id,
            concept_id=concept_id,
            layer_code=layer_code,
            role=role,
        )
    )


def build_inserts(
    excel_rows: list[ExcelRow],
    *,
    dimension_by_id: dict[int, str],
    dimension_by_name: dict[str, int],
    concept_lookup: ConceptLookup,
) -> tuple[list[ConceptLayerInsert], list[str]]:
    inserts: list[ConceptLayerInsert] = []
    warnings: list[str] = []
    dedupe: set[tuple[int, str, str]] = set()

    for row in excel_rows:
        dimension_id = parse_dimension_id(row.dimension_label, dimension_by_id, dimension_by_name)
        if dimension_id is None:
            warnings.append(f"Unmapped dimension: {row.dimension_label!r}")
            continue

        primary_ids, remainder_ids, used_bulk = concept_lookup.resolve_primary_and_remainder(
            dimension_id, row.concepts_text
        )
        if not primary_ids and not remainder_ids:
            warnings.append(
                f"D{dimension_id} ({row.dimension_label!r}): no concepts in database — skipped"
            )
            continue

        if not used_bulk and remainder_ids:
            logger.info(
                "D%s: Excel lists %d primary concept(s); attaching %d remaining "
                "documentation concept(s) as contributing",
                dimension_id,
                len(primary_ids),
                len(remainder_ids),
            )

        primary_layers = parse_layer_specs(row.primary_layers_text)
        contributing_layers = parse_layer_specs(row.contributing_layers_text)
        if not primary_layers and not contributing_layers:
            warnings.append(f"D{dimension_id}: no layer codes parsed — skipped")
            continue

        for spec in primary_layers:
            if spec.concept_tokens is not None:
                concept_ids = concept_lookup.resolve_tokens(dimension_id, spec.concept_tokens)
                if not concept_ids:
                    warnings.append(
                        f"D{dimension_id} primary {spec.layer_code}: "
                        f"only-filter {spec.concept_tokens!r} matched nothing"
                    )
                    continue
                for concept_id in concept_ids:
                    _append_insert(
                        inserts,
                        dedupe,
                        dimension_id=dimension_id,
                        concept_id=concept_id,
                        layer_code=spec.layer_code,
                        role="primary",
                    )
                continue

            for concept_id in primary_ids:
                _append_insert(
                    inserts,
                    dedupe,
                    dimension_id=dimension_id,
                    concept_id=concept_id,
                    layer_code=spec.layer_code,
                    role="primary",
                )
            for concept_id in remainder_ids:
                _append_insert(
                    inserts,
                    dedupe,
                    dimension_id=dimension_id,
                    concept_id=concept_id,
                    layer_code=spec.layer_code,
                    role="contributing",
                )

        for spec in contributing_layers:
            if spec.concept_tokens is not None:
                concept_ids = concept_lookup.resolve_tokens(dimension_id, spec.concept_tokens)
                if not concept_ids:
                    warnings.append(
                        f"D{dimension_id} contributing {spec.layer_code}: "
                        f"only-filter {spec.concept_tokens!r} matched nothing"
                    )
                    continue
            else:
                # Include every documentation concept for unrestricted contributing layers.
                concept_ids = primary_ids + remainder_ids

            for concept_id in concept_ids:
                _append_insert(
                    inserts,
                    dedupe,
                    dimension_id=dimension_id,
                    concept_id=concept_id,
                    layer_code=spec.layer_code,
                    role="contributing",
                )

    return inserts, warnings


def ensure_role_column(conn, *, dry_run: bool) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS n
              FROM information_schema.COLUMNS
             WHERE TABLE_SCHEMA = DATABASE()
               AND TABLE_NAME = 'svarupa_concept_layer'
               AND COLUMN_NAME = 'role'
            """
        )
        exists = int(cur.fetchone()["n"]) > 0
    if exists:
        logger.info("Column svarupa_concept_layer.role already exists")
        return

    ddl = """
        ALTER TABLE svarupa_concept_layer
            ADD COLUMN role ENUM('primary','contributing') NOT NULL DEFAULT 'contributing'
            AFTER layer_code
    """
    logger.info("Adding svarupa_concept_layer.role column")
    if not dry_run:
        with conn.cursor() as cur:
            cur.execute(ddl)


def load_dimension_maps(conn) -> tuple[dict[int, str], dict[str, int]]:
    with conn.cursor() as cur:
        cur.execute("SELECT dimension_id, slug, name FROM svarupa_dimensions")
        rows = cur.fetchall()

    by_id = {int(r["dimension_id"]): str(r["slug"]) for r in rows}
    by_name: dict[str, int] = {}
    for row in rows:
        dim_id = int(row["dimension_id"])
        by_name[_ascii_key(str(row["slug"]))] = dim_id
        by_name[_ascii_key(str(row["name"]))] = dim_id
    return by_id, by_name


def load_concept_lookup(conn) -> ConceptLookup:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT concept_id, dimension_id, slug, name, sanskrit_term
              FROM svarupa_concepts
             ORDER BY dimension_id, sort_order, slug
            """
        )
        return ConceptLookup(list(cur.fetchall()))


def seed_concept_layer_from_excel(
    *,
    xlsx_path: Path,
    database: str,
    dry_run: bool = False,
    truncate: bool = False,
) -> tuple[int, list[str]]:
    excel_rows = load_excel_rows(xlsx_path)
    settings = Settings.load()
    if not settings.mysql_host:
        raise RuntimeError("MySQL is not configured (SVARUPA_MYSQL_HOST)")

    conn = open_mysql(settings, database=database)
    warnings: list[str] = []
    try:
        ensure_role_column(conn, dry_run=dry_run)
        dimension_by_id, dimension_by_name = load_dimension_maps(conn)
        concept_lookup = load_concept_lookup(conn)
        inserts, warnings = build_inserts(
            excel_rows,
            dimension_by_id=dimension_by_id,
            dimension_by_name=dimension_by_name,
            concept_lookup=concept_lookup,
        )

        if dry_run:
            logger.info("DRY-RUN: would insert %d concept_layer row(s)", len(inserts))
            return len(inserts), warnings

        with conn.cursor() as cur:
            if truncate:
                cur.execute("DELETE FROM svarupa_concept_layer")
                logger.info("Truncated svarupa_concept_layer")

            insert_sql = """
                INSERT INTO svarupa_concept_layer
                    (dimension_id, concept_id, layer_code, role)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    dimension_id = VALUES(dimension_id),
                    role = VALUES(role),
                    updated_at = CURRENT_TIMESTAMP
            """
            for row in inserts:
                cur.execute(
                    insert_sql,
                    (row.dimension_id, row.concept_id, row.layer_code, row.role),
                )
        conn.commit()
        logger.info("Inserted/updated %d concept_layer row(s)", len(inserts))
        return len(inserts), warnings
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=DEFAULT_XLSX,
        help=f"path to mapping workbook (default: {DEFAULT_XLSX.name})",
    )
    parser.add_argument(
        "--database",
        default=DEFAULT_DATABASE,
        help=f"MySQL database name (default: {DEFAULT_DATABASE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="parse workbook and resolve rows; do not modify the database",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="delete all existing svarupa_concept_layer rows before insert",
    )
    args = parser.parse_args(argv)

    count, warnings = seed_concept_layer_from_excel(
        xlsx_path=args.xlsx,
        database=args.database,
        dry_run=args.dry_run,
        truncate=args.truncate,
    )
    mode = "Would insert/update" if args.dry_run else "Inserted/updated"
    print(f"{mode} {count} row(s) in {args.database}.svarupa_concept_layer")
    for warning in warnings:
        logger.warning("%s", warning)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
