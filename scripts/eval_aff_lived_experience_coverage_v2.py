#!/usr/bin/env python3
"""Evaluate AFF v2 concept coverage via state-specific lived-experience questions.

Pipeline:
  1. Load **primary** AFF dimension/concept pairs and their canonical states
     (``svarupa_concept_descriptions`` × ``svarupa_status``), or the static
     concept-layer snapshot with default deficiency/balance/excess poles when
     MySQL is not configured.
  2. For each Dimension → Concept → State triplet, generate 2 first-person
     lived-experience prompts (Bedrock or template fallback) and write rows to Excel.
  3. POST each question to ``POST /v2/affect/analyze`` with ``options.force=true``.
  4. Mark the row ``match`` when any ``attribute_scores[].attribute`` equals the row's
     ``concept_slug``; otherwise ``no match``.

Dependencies (beyond requirements.txt):
  pip install openpyxl

Usage:
  # Full pipeline (generate questions + call API + update Excel)
  PYTHONPATH=src python scripts/eval_aff_lived_experience_coverage_v2.py

  # Generate Excel only
  PYTHONPATH=src python scripts/eval_aff_lived_experience_coverage_v2.py --step generate

  # Evaluate an existing workbook (API must be running on :8000)
  PYTHONPATH=src python scripts/eval_aff_lived_experience_coverage_v2.py --step evaluate

  # Smoke test on first 3 concepts (all states per concept)
  PYTHONPATH=src python scripts/eval_aff_lived_experience_coverage_v2.py --limit 3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect import LAYER_CODE
from svarupa_affect.domain.enums import StatePole
from svarupa_affect.infrastructure.config import Settings

logger = logging.getLogger("eval_aff_lived_experience_coverage_v2")

DEFAULT_OUT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "eval"
    / "aff_lived_experience_coverage_v2.xlsx"
)
STATIC_CONCEPT_LAYER = (
    Path(__file__).resolve().parents[1] / "data" / "kg" / "aff_concept_layer.v1.json"
)

PROMPTS_PER_TRIPLET = 2

HEADERS = [
    "dimension_id",
    "dimension_name",
    "concept_id",
    "concept_slug",
    "concept_name",
    "state_code",
    "state_label",
    "role",
    "question_number",
    "lived_experience_question",
    "validation_note",
    "match_result",
    "matched_attributes",
    "api_attributes",
    "llm_primary_used",
    "abstained_dimensions",
    "api_error",
]

QUESTION_GEN_SYSTEM = """\
Act as an expert psychometrician and qualitative researcher specializing in dimensional models of human experience.
Your goal is to generate a "gold standard" set of 2 human lived-experience prompts designed to isolate and reveal ONE specific state of a concept, within a given dimension. You will be given a Dimension → Concept → State triplet (e.g., Emotions → Krodha → Excessive).
Every single question must be framed as a first-person narration ("I" statement) describing a specific scenario, physical sensation, or thought process. The respondent should read these "I" statements and rate how accurately it reflects their current or recent state.
I will give you the target triplet at the end. For that triplet, generate prompts based on these strict criteria:

No Direct Naming: Do not use the concept's name, the state's name, synonyms, or obvious derivatives in the text.
Lived-Experience Focus: Frame the first-person narrations around sensory details, physical body sensations, behavioral actions, and changes in thought patterns.
State-Level Specificity: The narration must capture the unique "fingerprint" of this exact state of the concept — not the concept in general. Explicitly ensure it cannot be confused with:

Other states of the same concept (e.g., separating "Excessive Krodha" from "Balanced Krodha" or "Deficient Krodha")
Adjacent concepts within the same dimension that share surface features (e.g., Krodha vs. Irshya/envy, or Krodha vs. Bhaya/fear-driven aggression)


Temporal Variety: Include narrations looking back at recent memories, current real-time reactions, and anticipated future choices.

Please format your output into 5 clear sections:

Triplet Fingerprint Summary: A 2-3 sentence breakdown of what distinguishes this specific state of this concept — cognitively, physically, and behaviorally — from (a) the same concept's other states, and (b) neighboring concepts in the dimension.
The 2 Gold-Standard First-Person Prompts: A numbered list of the "I" statements.
Validation Note: A 1-sentence explanation for EACH prompt detailing exactly why it activates this specific state (and not a sibling state or neighboring concept).
Sibling-State Contrast Table: A brief table or list showing how this state would sound different if the same triggering scenario were instead expressed as another state of the same concept.
Edge-Case Warning: One trap to avoid when analyzing answers, so the researcher doesn't collapse this state into a neighboring state or concept.

Return your complete analysis as a single JSON object with these keys:
- fingerprint_summary (string; section 1)
- prompts (array of exactly 2 first-person "I" statement strings; section 2)
- validation_notes (array of exactly 2 one-sentence strings, one per prompt; section 3)
- sibling_contrast (string; section 4)
- edge_case_warning (string; section 5)

Output JSON only — no markdown fences or prose outside the JSON object."""

_QUESTION_GEN_SCHEMA = {
    "type": "object",
    "properties": {
        "fingerprint_summary": {"type": "string"},
        "prompts": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": PROMPTS_PER_TRIPLET,
            "maxItems": PROMPTS_PER_TRIPLET,
        },
        "validation_notes": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": PROMPTS_PER_TRIPLET,
            "maxItems": PROMPTS_PER_TRIPLET,
        },
        "sibling_contrast": {"type": "string"},
        "edge_case_warning": {"type": "string"},
    },
    "required": [
        "fingerprint_summary",
        "prompts",
        "validation_notes",
        "sibling_contrast",
        "edge_case_warning",
    ],
}

_DEFAULT_STATE_POLES: tuple[tuple[str, str], ...] = (
    (StatePole.DEFICIENCY.value, "Deficiency"),
    (StatePole.BALANCE.value, "Balance"),
    (StatePole.EXCESS.value, "Excess"),
)

_OVERVIEW_RE = re.compile(r"Overview:\s*(.+?)(?:\n\n|\Z)", re.DOTALL)


@dataclass(frozen=True)
class TripletRow:
    concept_id: int
    dimension_id: int
    slug: str
    name: str
    role: str
    gloss: str
    state_code: str
    state_label: str
    state_description: str


@dataclass(frozen=True)
class GeneratedTripletQuestions:
    prompts: tuple[str, ...]
    validation_notes: tuple[str, ...]
    fingerprint_summary: str = ""
    sibling_contrast: str = ""
    edge_case_warning: str = ""


def _gloss_excerpt(gloss: str, *, max_len: int = 320) -> str:
    match = _OVERVIEW_RE.search(gloss)
    text = match.group(1).strip() if match else gloss.strip().replace("\n", " ")
    if len(text) > max_len:
        return text[: max_len - 3].rstrip() + "..."
    return text


def _dimension_registry():
    from svarupa_affect.infrastructure.kg.dimension_registry import build_dimension_registry

    return build_dimension_registry()


def _dimension_name(dimension_id: int) -> str:
    try:
        return _dimension_registry().name_for(dimension_id)
    except Exception:
        return f"D{dimension_id}"


def _triplet_key(concept_id: int, state_code: str) -> tuple[int, str]:
    return concept_id, state_code


def load_aff_triplets(*, limit: int | None = None) -> list[TripletRow]:
    """AFF primary concepts expanded to Dimension → Concept → State triplets."""
    settings = Settings.load()
    rows: list[TripletRow] = []

    if settings.mysql_host and settings.mysql_database:
        try:
            from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

            sql = """
            SELECT c.concept_id, cl.dimension_id, c.slug, c.name, cl.role,
                   COALESCE(NULLIF(TRIM(c.description), ''), c.name) AS gloss,
                   s.code AS state_code, s.label AS state_label,
                   cd.description AS state_description
              FROM svarupa_concept_layer cl
              JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
              JOIN (
                    SELECT concept_id, status_id, MIN(description_id) AS description_id
                      FROM svarupa_concept_descriptions
                     GROUP BY concept_id, status_id
                   ) cd_pick
                ON cd_pick.concept_id = c.concept_id
              JOIN svarupa_concept_descriptions cd
                ON cd.description_id = cd_pick.description_id
              JOIN svarupa_status s ON s.status_id = cd.status_id
             WHERE cl.layer_code = %s
               AND cl.role = 'primary'
             ORDER BY cl.dimension_id, c.slug, s.sort_order
            """
            conn = open_mysql(settings)
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (LAYER_CODE,))
                    for row in cur.fetchall():
                        rows.append(
                            TripletRow(
                                concept_id=int(row["concept_id"]),
                                dimension_id=int(row["dimension_id"]),
                                slug=str(row["slug"]),
                                name=str(row["name"]),
                                role=str(row["role"]),
                                gloss=str(row["gloss"] or row["name"]),
                                state_code=str(row["state_code"]),
                                state_label=str(row["state_label"]),
                                state_description=str(row["state_description"] or ""),
                            )
                        )
            finally:
                conn.close()
            source = (
                f"{settings.mysql_database}.svarupa_concept_layer + concept_descriptions "
                "(AFF, primary)"
            )
            if limit is not None:
                rows = _limit_triplets_by_concept(rows, limit)
            logger.info("Loaded %d triplet(s) from %s", len(rows), source)
            return rows
        except (ImportError, RuntimeError) as exc:
            logger.warning("MySQL unavailable (%s); falling back to static concept layer JSON", exc)

    if STATIC_CONCEPT_LAYER.is_file():
        payload = json.loads(STATIC_CONCEPT_LAYER.read_text(encoding="utf-8"))
        for item in payload.get("concepts", []):
            if str(item.get("role", "")).lower() != "primary":
                continue
            gloss = str(item.get("gloss") or item["name"])
            for state_code, state_label in _DEFAULT_STATE_POLES:
                rows.append(
                    TripletRow(
                        concept_id=int(item["concept_id"]),
                        dimension_id=int(item["dimension_id"]),
                        slug=str(item["slug"]),
                        name=str(item["name"]),
                        role=str(item["role"]),
                        gloss=gloss,
                        state_code=state_code,
                        state_label=state_label,
                        state_description=_gloss_excerpt(gloss),
                    )
                )
        source = f"{STATIC_CONCEPT_LAYER} (AFF, primary; default state poles)"
    else:
        raise RuntimeError(
            "MySQL is not configured and static snapshot "
            f"{STATIC_CONCEPT_LAYER} is missing. Configure SVARUPA_MYSQL_* or export the snapshot."
        )

    if limit is not None:
        rows = _limit_triplets_by_concept(rows, limit)
    logger.info("Loaded %d triplet(s) from %s", len(rows), source)
    return rows


def _limit_triplets_by_concept(rows: list[TripletRow], limit: int) -> list[TripletRow]:
    allowed: set[int] = set()
    out: list[TripletRow] = []
    for row in rows:
        if row.concept_id not in allowed and len(allowed) >= limit:
            continue
        allowed.add(row.concept_id)
        out.append(row)
    return out


def _build_triplet_prompt(triplet: TripletRow, dim_name: str) -> str:
    context = _gloss_excerpt(triplet.state_description or triplet.gloss, max_len=480)
    return (
        "The target triplet I want you to build this for is:\n"
        f"Dimension: {dim_name}\n"
        f"Concept: {triplet.name}\n"
        f"State: {triplet.state_label}\n\n"
        f"Steward context (for your analysis only; do not echo in prompts): {context!r}"
    )


def _template_questions(triplet: TripletRow, dim_name: str) -> GeneratedTripletQuestions:
    excerpt = _gloss_excerpt(triplet.state_description or triplet.gloss)
    state_phrase = triplet.state_label.lower()
    prompts: list[str] = []
    for idx in range(PROMPTS_PER_TRIPLET):
        if idx % 3 == 0:
            tense = "right now"
        elif idx % 3 == 1:
            tense = "over the past few days"
        else:
            tense = "when I imagine the next time this comes up"
        prompts.append(
            f"I notice {tense} a quality in my experience that feels like a {state_phrase} "
            f"expression within {dim_name.lower()}: {excerpt} This is what it has been like for me."
        )
    notes = tuple(
        f"Template prompt {i + 1} targets {triplet.state_label.lower()} {triplet.name}."
        for i in range(PROMPTS_PER_TRIPLET)
    )
    return GeneratedTripletQuestions(
        prompts=tuple(prompts),
        validation_notes=notes,
        fingerprint_summary=f"Template fallback for {triplet.name} / {triplet.state_label}.",
    )


async def _generate_questions_llm(
    triplet: TripletRow,
    dim_name: str,
    *,
    model_id: str,
    region: str | None,
    timeout_s: float,
    max_tokens: int,
) -> GeneratedTripletQuestions:
    from svarupa_affect.infrastructure.llm.bedrock_provider import BedrockLLMProvider

    if not region:
        raise RuntimeError("AWS region is not configured (set AWS_REGION or SVARUPA_AWS_REGION)")

    provider = BedrockLLMProvider(region_name=region, read_timeout_s=timeout_s + 5.0)
    payload = await provider.complete_json(
        system=QUESTION_GEN_SYSTEM,
        prompt=_build_triplet_prompt(triplet, dim_name),
        schema=_QUESTION_GEN_SCHEMA,
        model_id=model_id,
        temperature=0.7,
        timeout_s=timeout_s,
        max_tokens=max_tokens,
    )

    prompts = [str(q).strip() for q in payload.get("prompts", []) if str(q).strip()]
    notes = [str(n).strip() for n in payload.get("validation_notes", []) if str(n).strip()]
    if len(prompts) < PROMPTS_PER_TRIPLET:
        raise ValueError(f"expected {PROMPTS_PER_TRIPLET} prompts, got {len(prompts)}")
    while len(notes) < PROMPTS_PER_TRIPLET:
        notes.append("")
    return GeneratedTripletQuestions(
        prompts=tuple(prompts[:PROMPTS_PER_TRIPLET]),
        validation_notes=tuple(notes[:PROMPTS_PER_TRIPLET]),
        fingerprint_summary=str(payload.get("fingerprint_summary", "")),
        sibling_contrast=str(payload.get("sibling_contrast", "")),
        edge_case_warning=str(payload.get("edge_case_warning", "")),
    )


async def generate_all_questions(
    triplets: list[TripletRow],
    *,
    use_templates: bool,
) -> dict[tuple[int, str], GeneratedTripletQuestions]:
    dim_names = {t.dimension_id: _dimension_name(t.dimension_id) for t in triplets}

    if use_templates:
        return {
            _triplet_key(t.concept_id, t.state_code): _template_questions(t, dim_names[t.dimension_id])
            for t in triplets
        }

    settings = Settings.load()
    model_id = settings.bedrock_model_id
    region = settings.aws_region
    timeout_s = settings.llm_assist_timeout_s
    max_tokens = max(8192, settings.llm_assist_max_tokens)

    generated: dict[tuple[int, str], GeneratedTripletQuestions] = {}
    for idx, triplet in enumerate(triplets, start=1):
        dim_name = dim_names[triplet.dimension_id]
        key = _triplet_key(triplet.concept_id, triplet.state_code)
        try:
            generated[key] = await _generate_questions_llm(
                triplet,
                dim_name,
                model_id=model_id,
                region=region,
                timeout_s=timeout_s,
                max_tokens=max_tokens,
            )
        except Exception:
            logger.exception(
                "LLM generation failed for %s / %s; using templates",
                triplet.slug,
                triplet.state_code,
            )
            generated[key] = _template_questions(triplet, dim_name)
        if idx % 5 == 0 or idx == len(triplets):
            logger.info("Generated questions for %d / %d triplet(s)", idx, len(triplets))

    return generated


def _require_openpyxl():
    try:
        import openpyxl  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "openpyxl is required for Excel I/O. Install with: pip install openpyxl"
        ) from exc
    return openpyxl


def build_workbook_rows(
    triplets: list[TripletRow],
    questions: dict[tuple[int, str], GeneratedTripletQuestions],
) -> list[list[object]]:
    rows: list[list[object]] = []
    for triplet in triplets:
        key = _triplet_key(triplet.concept_id, triplet.state_code)
        generated = questions[key]
        dim_name = _dimension_name(triplet.dimension_id)
        for num in range(1, PROMPTS_PER_TRIPLET + 1):
            rows.append(
                [
                    triplet.dimension_id,
                    dim_name,
                    triplet.concept_id,
                    triplet.slug,
                    triplet.name,
                    triplet.state_code,
                    triplet.state_label,
                    triplet.role,
                    num,
                    generated.prompts[num - 1],
                    generated.validation_notes[num - 1],
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )
    return rows


def write_workbook(path: Path, data_rows: list[list[object]]) -> None:
    openpyxl = _require_openpyxl()
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AFF v2 coverage"
    ws.append(HEADERS)
    for row in data_rows:
        ws.append(row)
    wb.save(path)
    logger.info("Wrote %d row(s) to %s", len(data_rows), path)


def read_workbook(path: Path) -> tuple[list[str], list[list[object]]]:
    openpyxl = _require_openpyxl()
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    headers = [str(cell.value or "") for cell in ws[1]]
    rows: list[list[object]] = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row and any(cell is not None and str(cell).strip() for cell in row):
            rows.append(list(row))
    return headers, rows


def save_workbook(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    openpyxl = _require_openpyxl()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AFF v2 coverage"
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(path)


def _col_index(headers: list[str], name: str) -> int:
    try:
        return headers.index(name)
    except ValueError as exc:
        raise RuntimeError(f"Workbook missing required column {name!r}") from exc


def attributes_from_response(payload: dict, *, dimension_id: int | None = None) -> list[str]:
    """Collect attribute slugs; when ``dimension_id`` is set, use that signal only."""
    from svarupa_affect.infrastructure.kg.dimension_registry import StaticDimensionRegistry

    if dimension_id is not None:
        dim_name = StaticDimensionRegistry().name_for(dimension_id)
        for signal in payload.get("signals", []):
            if signal.get("dimension_name") == dim_name:
                return [
                    str(score.get("attribute"))
                    for score in signal.get("attribute_scores", [])
                    if score.get("attribute")
                ]
        return []

    attrs: list[str] = []
    for score in payload.get("attribute_scores", []):
        attr = score.get("attribute")
        if attr:
            attrs.append(str(attr))
    if attrs:
        return attrs
    for signal in payload.get("signals", []):
        for score in signal.get("attribute_scores", []):
            attr = score.get("attribute")
            if attr:
                attrs.append(str(attr))
    return attrs


def evaluate_match(
    expected_slug: str, response: dict, *, dimension_id: int | None = None
) -> tuple[str, str]:
    from svarupa_affect.infrastructure.kg.concept_registry import canonical_slug

    expected = canonical_slug(expected_slug)
    found = attributes_from_response(response, dimension_id=dimension_id)
    matched = sorted({a for a in found if canonical_slug(a) == expected})
    if matched:
        return "match", ", ".join(matched)
    return "no match", ""


def call_v2_analyze_api(
    *,
    api_url: str,
    analysis_text: str,
    timeout_s: float,
    force: bool,
) -> tuple[dict | None, str]:
    import httpx

    body = {
        "analysis_text": analysis_text,
        "options": {"force": force},
    }
    try:
        with httpx.Client(timeout=timeout_s) as client:
            resp = client.post(api_url, json=body, headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, dict):
            return None, "API returned non-object JSON"
        return payload, ""
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def evaluate_workbook(
    path: Path,
    *,
    api_url: str,
    timeout_s: float,
    force: bool,
    api_force: bool,
) -> None:
    headers, rows = read_workbook(path)
    idx = {name: _col_index(headers, name) for name in HEADERS if name in headers}
    for required in ("concept_slug", "lived_experience_question", "match_result"):
        if required not in idx:
            raise RuntimeError(f"Workbook missing required column {required!r}")

    updated = 0
    for row in rows:
        while len(row) < len(HEADERS):
            row.append("")
        question = str(row[idx["lived_experience_question"]] or "").strip()
        if not question:
            continue
        if not force and str(row[idx["match_result"]] or "").strip():
            continue

        concept_slug = str(row[idx["concept_slug"]] or "").strip()
        dimension_id = int(row[idx["dimension_id"]]) if row[idx["dimension_id"]] else None
        response, err = call_v2_analyze_api(
            api_url=api_url,
            analysis_text=question,
            timeout_s=timeout_s,
            force=api_force,
        )
        if err:
            row[idx["match_result"]] = ""
            row[_col_index(headers, "matched_attributes")] = ""
            row[_col_index(headers, "api_attributes")] = ""
            row[_col_index(headers, "llm_primary_used")] = ""
            row[_col_index(headers, "abstained_dimensions")] = ""
            row[_col_index(headers, "api_error")] = err
        else:
            result, matched = evaluate_match(
                concept_slug, response or {}, dimension_id=dimension_id
            )
            row[idx["match_result"]] = result
            row[_col_index(headers, "matched_attributes")] = matched
            row[_col_index(headers, "api_attributes")] = ", ".join(
                attributes_from_response(response or {}, dimension_id=dimension_id)
            )
            row[_col_index(headers, "llm_primary_used")] = str(
                bool((response or {}).get("llm_primary_used"))
            )
            abstained = (response or {}).get("abstained_dimensions") or []
            row[_col_index(headers, "abstained_dimensions")] = ", ".join(
                str(item) for item in abstained
            )
            row[_col_index(headers, "api_error")] = ""
        updated += 1
        if updated % 10 == 0:
            save_workbook(path, headers, rows)
            logger.info("Checkpoint: evaluated %d row(s)", updated)

    save_workbook(path, headers, rows)
    matches = sum(1 for row in rows if str(row[idx["match_result"]]) == "match")
    logger.info(
        "Evaluation complete: %d row(s) processed, %d match, %d no match",
        updated,
        matches,
        sum(1 for row in rows if str(row[idx["match_result"]]) == "no match"),
    )


async def run_generate(path: Path, *, limit: int | None, use_templates: bool) -> None:
    triplets = load_aff_triplets(limit=limit)
    questions = await generate_all_questions(triplets, use_templates=use_templates)
    rows = build_workbook_rows(triplets, questions)
    write_workbook(path, rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step",
        choices=("all", "generate", "evaluate"),
        default="all",
        help="run question generation, API evaluation, or both (default: all)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Excel workbook path (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/v2/affect/analyze",
        help="AFF v2 analyze endpoint (default: http://localhost:8000/v2/affect/analyze)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="process only the first N concepts (all states per concept)",
    )
    parser.add_argument(
        "--use-templates",
        action="store_true",
        help="skip Bedrock; build template questions from concept/state gloss",
    )
    parser.add_argument(
        "--api-timeout",
        type=float,
        default=120.0,
        help="HTTP timeout per /v2/affect/analyze call in seconds (default: 120)",
    )
    parser.add_argument(
        "--no-api-force",
        action="store_true",
        help="do not set options.force=true on /v2/affect/analyze (salience gate may abstain)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-evaluate rows even when match_result is already set",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.step in ("all", "generate"):
        asyncio.run(
            run_generate(
                args.output,
                limit=args.limit,
                use_templates=args.use_templates,
            )
        )

    if args.step in ("all", "evaluate"):
        if not args.output.is_file():
            raise SystemExit(f"Workbook not found: {args.output}. Run with --step generate first.")
        evaluate_workbook(
            args.output,
            api_url=args.api_url,
            timeout_s=args.api_timeout,
            force=args.force,
            api_force=not args.no_api_force,
        )

    print(f"Done. Workbook: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
