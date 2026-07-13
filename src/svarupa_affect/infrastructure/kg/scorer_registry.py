"""Read-only layer scorer registry from ``svarupa_layer_scorer`` (+ output concepts).

Defines which dimensions have wired scorers and ``emits_signals`` for a layer.
Output concept slugs are loaded from ``svarupa_layer_scorer_concept`` (FK -> concepts).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from ... import LAYER_CODE
from ..config import Settings
from .mysql_client import open_mysql

logger = logging.getLogger("svarupa_affect.scorer_registry")

_DATA_DIR = Settings.load().data_dir
_LAYER_SCORER_SNAPSHOTS: dict[str, Path] = {
    "NAR": _DATA_DIR / "kg" / "nar_layer_scorers.v1.json",
    "MET": _DATA_DIR / "kg" / "met_layer_scorers.v1.json",
    "PSY": _DATA_DIR / "kg" / "psy_layer_scorers.v1.json",
}

_STATIC_SPECS: tuple[dict[str, object], ...] = (
    {
        "scorer_id": 1,
        "dimension_id": 2,
        "scorer_slug": "guna_field",
        "scorer_kind": "field_native",
        "data_ref": "field/guna_synthesis.v1.json",
        "pole_map_ref": "pole_maps/d2_poles.v1.json",
        "modulator_ref": None,
        "emits_signals": True,
        "sort_order": 1,
    },
    {
        "scorer_id": 2,
        "dimension_id": 8,
        "scorer_slug": "hyp2sthayi",
        "scorer_kind": "hypothesis_bridge",
        "data_ref": "bridge/hyp2sthayi.v2.json",
        "pole_map_ref": "pole_maps/d8_poles.v1.json",
        "modulator_ref": "bridge/guna_families.v1.json",
        "emits_signals": True,
        "sort_order": 2,
    },
    {
        "scorer_id": 3,
        "dimension_id": 9,
        "scorer_slug": "hyp2vyabhi",
        "scorer_kind": "hypothesis_bridge",
        "data_ref": "bridge/hyp2vyabhi.v2.json",
        "pole_map_ref": None,
        "modulator_ref": "bridge/guna_families.v1.json",
        "emits_signals": True,
        "sort_order": 3,
    },
    {
        "scorer_id": 4,
        "dimension_id": 22,
        "scorer_slug": "brahmavihara_tone",
        "scorer_kind": "field_native",
        "data_ref": "field/guna_synthesis.v1.json",
        "pole_map_ref": None,
        "modulator_ref": None,
        "emits_signals": False,
        "sort_order": 4,
    },
    {
        "scorer_id": 5,
        "dimension_id": 24,
        "scorer_slug": "daivi_asuri_tone",
        "scorer_kind": "field_native",
        "data_ref": "field/guna_synthesis.v1.json",
        "pole_map_ref": None,
        "modulator_ref": None,
        "emits_signals": False,
        "sort_order": 5,
    },
    {
        "scorer_id": 6,
        "dimension_id": 19,
        "scorer_slug": "klesha_raga_dvesha",
        "scorer_kind": "field_native",
        "data_ref": "field/klesha_raga_dvesha.v1.json",
        "pole_map_ref": None,
        "modulator_ref": None,
        "emits_signals": False,
        "sort_order": 6,
    },
)


@dataclass(frozen=True)
class LayerScorerSpec:
    scorer_id: int
    dimension_id: int
    scorer_slug: str
    scorer_kind: str
    data_path: Path
    pole_map_path: Path | None
    modulator_path: Path | None
    emits_signals: bool
    sort_order: int


class StaticScorerRegistry:
    """In-memory scorer registry (offline fallback)."""

    def __init__(
        self,
        *,
        layer_code: str = LAYER_CODE,
        data_dir: Path | None = None,
        specs: tuple[LayerScorerSpec, ...] | None = None,
    ) -> None:
        self.layer_code = layer_code
        root = data_dir or Settings.load().data_dir
        if specs is None:
            layer_rows = _specs_for_layer(layer_code, root)
            specs = tuple(_spec_from_dict(root, row) for row in layer_rows) if layer_rows else (
                tuple(_spec_from_dict(root, row) for row in _STATIC_SPECS)
                if layer_code == LAYER_CODE
                else ()
            )
        self._specs: tuple[LayerScorerSpec, ...] = specs
        self._by_dimension = {s.dimension_id: s for s in self._specs}
        self._output_slugs: dict[int, frozenset[str]] = {}

    def scorers(self, layer_code: str | None = None) -> tuple[LayerScorerSpec, ...]:
        if layer_code and layer_code != self.layer_code:
            return ()
        return self._specs

    def emit_dimensions(self, layer_code: str | None = None) -> frozenset[int]:
        if layer_code and layer_code != self.layer_code:
            return frozenset()
        return frozenset(s.dimension_id for s in self._specs if s.emits_signals)

    def scorer_for(self, dimension_id: int, layer_code: str | None = None) -> LayerScorerSpec | None:
        if layer_code and layer_code != self.layer_code:
            return None
        return self._by_dimension.get(dimension_id)

    def output_slugs(self, dimension_id: int, layer_code: str | None = None) -> frozenset[str]:
        if layer_code and layer_code != self.layer_code:
            return frozenset()
        return self._output_slugs.get(dimension_id, frozenset())

    def set_output_slugs(self, dimension_id: int, slugs: frozenset[str]) -> None:
        self._output_slugs[dimension_id] = slugs


def _load_layer_static_specs(layer_code: str, data_dir: Path) -> tuple[dict[str, object], ...]:
    path = _LAYER_SCORER_SNAPSHOTS.get(layer_code)
    if path is None or not path.is_file():
        return ()
    raw = json.loads(path.read_text(encoding="utf-8"))
    return tuple(raw.get("scorers", ()))


def _specs_for_layer(layer_code: str, data_dir: Path) -> tuple[dict[str, object], ...]:
    if layer_code == LAYER_CODE:
        return _STATIC_SPECS
    layer_specs = _load_layer_static_specs(layer_code, data_dir)
    if layer_specs:
        return layer_specs
    return ()


def _spec_from_dict(data_dir: Path, row: dict[str, object]) -> LayerScorerSpec:
    pole = row.get("pole_map_ref")
    mod = row.get("modulator_ref")
    return LayerScorerSpec(
        scorer_id=int(row["scorer_id"]),
        dimension_id=int(row["dimension_id"]),
        scorer_slug=str(row["scorer_slug"]),
        scorer_kind=str(row["scorer_kind"]),
        data_path=data_dir / str(row["data_ref"]),
        pole_map_path=(data_dir / str(pole)) if pole else None,
        modulator_path=(data_dir / str(mod)) if mod else None,
        emits_signals=bool(row["emits_signals"]),
        sort_order=int(row["sort_order"]),
    )


def _load_from_mysql(settings: Settings, layer_code: str) -> StaticScorerRegistry:
    scorer_sql = """
        SELECT scorer_id, dimension_id, scorer_slug, scorer_kind, data_ref,
               pole_map_ref, modulator_ref, emits_signals, sort_order
          FROM svarupa_layer_scorer
         WHERE layer_code = %s
         ORDER BY sort_order, dimension_id
    """
    concept_sql = """
        SELECT s.dimension_id, c.slug
          FROM svarupa_layer_scorer_concept sc
          JOIN svarupa_layer_scorer s ON s.scorer_id = sc.scorer_id
          JOIN svarupa_concepts c ON c.concept_id = sc.concept_id
         WHERE s.layer_code = %s
    """
    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(scorer_sql, (layer_code,))
            scorer_rows = cur.fetchall()
            if not scorer_rows:
                raise RuntimeError(
                    f"svarupa_layer_scorer returned no rows for layer_code={layer_code!r}"
                )
            cur.execute(concept_sql, (layer_code,))
            concept_rows = cur.fetchall()
    finally:
        conn.close()

    data_dir = settings.data_dir
    specs = tuple(
        LayerScorerSpec(
            scorer_id=int(row["scorer_id"]),
            dimension_id=int(row["dimension_id"]),
            scorer_slug=str(row["scorer_slug"]),
            scorer_kind=str(row["scorer_kind"]),
            data_path=data_dir / str(row["data_ref"]),
            pole_map_path=(
                data_dir / str(row["pole_map_ref"]) if row["pole_map_ref"] else None
            ),
            modulator_path=(
                data_dir / str(row["modulator_ref"]) if row["modulator_ref"] else None
            ),
            emits_signals=bool(row["emits_signals"]),
            sort_order=int(row["sort_order"]),
        )
        for row in scorer_rows
    )
    output: dict[int, set[str]] = {}
    for row in concept_rows:
        output.setdefault(int(row["dimension_id"]), set()).add(str(row["slug"]))

    reg = StaticScorerRegistry(layer_code=layer_code, data_dir=data_dir, specs=specs)
    for dim_id, slugs in output.items():
        reg.set_output_slugs(dim_id, frozenset(slugs))
    logger.info(
        "Loaded scorer registry from MySQL (%s): %d scorers, %d emit dimensions",
        settings.mysql_database,
        len(specs),
        len(reg.emit_dimensions()),
    )
    return reg


def build_scorer_registry(*, layer_code: str = LAYER_CODE) -> StaticScorerRegistry:
    """Composition root: MySQL when configured, else static seed."""
    settings = Settings.load()
    if settings.mysql_host and settings.mysql_database:
        try:
            return _load_from_mysql(settings, layer_code)
        except Exception as exc:
            logger.warning(
                "Could not load svarupa_layer_scorer from MySQL (%s); using static seed",
                exc,
            )
    return StaticScorerRegistry(layer_code=layer_code, data_dir=settings.data_dir)
