# Agent instructions — Svarupa Multi-Axis Affect Analysis (AFF)

This component implements **Layer 1 (AFF)** of the Svarupa Assistant: the emotion-reading
specialist that maps a user's expression onto the affective dimensions of the 31-Dimension
framework. It is one of seven independent analytical layers and is independently useful.

## What AFF does (and only does)

- **Primary:** D8 Sthāyībhāvas (9 enduring emotions), D9 Vyabhicārībhāvas (33 transient states).
- **Contributing:** D2 Triguṇa, D22 Brahmavihāras, D24 Daivī/Āsurī Sampat.
- **Affinity set — the only ids AFF may emit:** `{2, 8, 9, 22, 24}`.
- **Model-first, LLM-assisted:** deterministic affect models (VAD axes, NRCLex, VADER, TextBlob,
  embeddings) do the work; Claude (Bedrock) is invoked only for flagged ambiguity.
- Reads emotion onto Rasa theory: separates *enduring* dispositions from *transient* weather,
  and reads guṇa coloration. Shares valence/arousal with PHE and temporal cues with NAR via a
  per-request feature cache.

## Non-negotiable design philosophy

1. **Recognition, not diagnosis** — observations/invitations, never labels/predictions/prescriptions.
2. **Relevance vs confidence** are two separate numbers, never collapsed. Confidence is about the
   *process*, never certainty about the person.
3. **Abstention is a valid, meaningful output**; never fabricate signals on thin input.

## Architecture

Clean/hexagonal: `api/` → `application/` → `domain/` (ports) ← `infrastructure/` (adapters).
LLM and KG sit behind ports (`ILLMProvider`, Knowledge Steward). AFF is read-only against the KG.
Dimensions are data, not code — no `if dimension == X` branching.

## Tooling

- Python `>=3.11,<3.14`, FastAPI, pydantic v2.
- Format/lint/type/test: `ruff check . && black --check . && mypy src && pytest`
  (black line-length 100, mypy strict).

## Testing methodology

Per-layer tests first (deterministic math + mocked LLM failures), then fusion (mocked JSON),
then gold-standard eval cases in `data/ground_truth/`. This is a subjective domain: assert
invariants, property tests, and philosophy-regression (no verdict language) rather than
bitwise-perfect LLM output.

## Source of truth

The specs in the sibling repo `svarupa-assist-server/documentations/dimensions/`
(31-Dimension Spec v7.1, Analytical Layers Spec v1.0, Architecture Review). The detailed,
file-scoped conventions live in `.cursor/rules/`.
