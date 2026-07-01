#!/usr/bin/env python3
"""Seed ``svarupa_concept_layer`` from the dimension/layer Excel mapping.

Steps:
  1. Add ``role ENUM('primary','contributing')`` to ``svarupa_concept_layer`` when missing.
  2. Read ``documentation/dimensions_and_concepts/Dimension & Attribute Mapping to
     Analytical Layers.xlsx``.
  3. Resolve ``Dimension`` -> ``dimension_id`` (``D{n}`` prefix or name lookup).
  4. Resolve ``Core Attributes / Constructs`` -> ``concept_id`` (comma-separated tokens;
     falls back to all concepts in the dimension when the cell is descriptive).
  5. Parse ``Primary Layer(s)`` / ``Contributing Layer(s)`` for layer codes (SEM, AFF, …).
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
VALID_LAYER_CODES = frozenset({"SEM", "COT", "AFF", "PHE", "PSY", "MET", "NAR"})

# English / common tokens -> concept slug (within a dimension when ambiguous).
CONCEPT_SLUG_ALIASES: dict[tuple[int, str], str] = {
    (1, "earth"): "prithvi",
    (1, "water"): "apas",
    (1, "fire"): "agni",
    (1, "air"): "vayu",
    (1, "ether"): "akasha",
    (10, "yoga"): "raja_yoga",
    (12, "karma"): "karma_phala",
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


@dataclass(frozen=True)
class ExcelRow:
    dimension_label: str
    concepts_text: str
    primary_layers_text: str
    contributing_layers_text: str


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


def _read_xlsx_stdlib(path: Path) -> list[list[str | None]]:
    """Read the first worksheet via stdlib (no openpyxl dependency)."""
    with zipfile.ZipFile(path) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            for si in root.findall(".//m:si", ns):
                parts = [t.text or "" for t in si.findall(".//m:t", ns)]
                shared.append("".join(parts))

        sheet_xml = zf.read("xl/worksheets/sheet1.xml")
        root = ET.fromstring(sheet_xml)
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        rows: list[list[str | None]] = []
        for row_el in root.findall(".//m:sheetData/m:row", ns):
            row: list[str | None] = []
            for cell in row_el.findall("m:c", ns):
                cell_type = cell.get("t")
                value_el = cell.find("m:v", ns)
                if value_el is None or value_el.text is None:
                    row.append(None)
                elif cell_type == "s":
                    row.append(shared[int(value_el.text)])
                else:
                    row.append(value_el.text)
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
        if not raw or not raw[col["Dimension"]]:
            continue
        out.append(
            ExcelRow(
                dimension_label=str(raw[col["Dimension"]]).strip(),
                concepts_text=str(raw[col["Core Attributes / Constructs"]] or "").strip(),
                primary_layers_text=str(raw[col["Primary Layer(s)"]] or "").strip(),
                contributing_layers_text=str(raw[col["Contributing Layer(s)"]] or "").strip(),
            )
        )
    return out


def parse_dimension_id(label: str, dimension_by_id: dict[int, str], dimension_by_name: dict[str, int]) -> int | None:
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


def parse_layer_codes(text: str) -> list[str]:
    if not text:
        return []
    seen: set[str] = set()
    ordered: list[str] = []
    for match in LAYER_CODE_RE.finditer(text.upper()):
        code = match.group(1)
        if code in VALID_LAYER_CODES and code not in seen:
            seen.add(code)
            ordered.append(code)
    return ordered


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
    """Resolve concept tokens within a dimension."""

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
            for word in re.split(r"[/\s]+", name):
                word_key = _ascii_key(word)
                if len(word_key) >= 3:
                    self._index.setdefault((dim_id, word_key), concept_id)

    def all_concept_ids(self, dimension_id: int) -> list[int]:
        return [int(r["concept_id"]) for r in self._by_dimension.get(dimension_id, [])]

    def resolve_token(self, dimension_id: int, token: str) -> int | None:
        alias_slug = CONCEPT_SLUG_ALIASES.get((dimension_id, _ascii_key(token)))
        if alias_slug:
            return self._index.get((dimension_id, _ascii_key(alias_slug)))

        direct = self._index.get((dimension_id, _ascii_key(token)))
        if direct is not None:
            return direct

        token_key = _ascii_key(token)
        for row in self._by_dimension.get(dimension_id, []):
            slug_key = _ascii_key(str(row["slug"]))
            if slug_key.startswith(token_key) or token_key.startswith(slug_key):
                return int(row["concept_id"])
        return None

    def resolve_concepts(self, dimension_id: int, text: str) -> list[int]:
        if not text or _is_bulk_descriptor(text):
            return self.all_concept_ids(dimension_id)

        matched: list[int] = []
        seen: set[int] = set()
        for token in _split_concept_tokens(text):
            concept_id = self.resolve_token(dimension_id, token)
            if concept_id is not None and concept_id not in seen:
                seen.add(concept_id)
                matched.append(concept_id)

        if not matched:
            return self.all_concept_ids(dimension_id)
        return matched


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

        concept_ids = concept_lookup.resolve_concepts(dimension_id, row.concepts_text)
        if not concept_ids:
            warnings.append(
                f"D{dimension_id} ({row.dimension_label!r}): no concepts in database — skipped"
            )
            continue

        primary_layers = parse_layer_codes(row.primary_layers_text)
        contributing_layers = parse_layer_codes(row.contributing_layers_text)
        if not primary_layers and not contributing_layers:
            warnings.append(f"D{dimension_id}: no layer codes parsed — skipped")
            continue

        for concept_id in concept_ids:
            for layer_code in primary_layers:
                key = (concept_id, layer_code, "primary")
                if key not in dedupe:
                    dedupe.add(key)
                    inserts.append(
                        ConceptLayerInsert(
                            dimension_id=dimension_id,
                            concept_id=concept_id,
                            layer_code=layer_code,
                            role="primary",
                        )
                    )
            for layer_code in contributing_layers:
                key = (concept_id, layer_code, "contributing")
                if key in dedupe:
                    continue
                primary_key = (concept_id, layer_code, "primary")
                if primary_key in dedupe:
                    continue
                dedupe.add(key)
                inserts.append(
                    ConceptLayerInsert(
                        dimension_id=dimension_id,
                        concept_id=concept_id,
                        layer_code=layer_code,
                        role="contributing",
                    )
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
