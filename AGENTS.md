# Agent instructions — Svarupa Multi-Axis Affect Analysis (AFF)

This component implements **Layer 1 (AFF)** of the Svarupa Assistant: the emotion-reading
specialist that maps a user's expression onto the affective dimensions of the 31-Dimension
framework. It is one of seven independent analytical layers and is independently useful.

## What AFF does (and only does)

Applicability is defined in **`svarupa_assistant_v1.svarupa_concept_layer`** where
`layer_code = 'AFF'`. Each row tags a concept with `role` (`primary` | `contributing`).
Regenerate the offline snapshot after KG changes:

```bash
PYTHONPATH=src python scripts/export_aff_concept_layer.py
```

### Dimension applicability vs signal emission

Two different KG tables govern different things:

| Table | Meaning |
|-------|---------|
| `svarupa_concept_layer` | Closed vocabulary + steward glosses AFF may reference (`role` per concept). |
| `svarupa_layer_scorer` | Which dimensions AFF actually scores into `signals[]` / `attribute_scores` (`emits_signals`). |

**Applicability (concept_layer)** — dimension ids tagged for AFF: `{2, 8, 9, 15, 19, 21, 22, 24}`.

| Role in `concept_layer` | Dimensions | Notes |
|-------------------------|------------|-------|
| **Primary** | D2 Triguṇa, D8 Sthāyībhāvas, D9 Vyabhicārībhāvas | AFF-owned affective core |
| **Contributing** | D2 meta constructs, D15 Tridoṣa, D19 Kleśa, D21 Antarāyas, D22 Brahmavihāras, D24 Daivī/Āsurī Sampat | Cross-layer vocabulary; not all become AFF emits |

D2 appears in both roles: **sattva / rajas / tamas** are primary; four philosophical
meta-constructs are contributing only.

**AFF emit set (design + `svarupa_layer_scorer`)** — `{2, 8, 9, 19, 22, 24}` only.
Runtime rule: **`concept_layer` ∩ `emit_dimensions`**. Currently wired emitters: D2, D8, D9.

**D15 Tridoṣa (pitta / vāta / kapha) — do not emit from AFF.** Per the layer matrix
(Excel → `concept_layer`), D15 is **primary for PHE and MET**; AFF is **contributing** only.
Constitutional dosha readings (e.g. a lived-experience item tagged `pitta`) belong to those
primary layers, not to AFF `attribute_scores`. Pitta rows in `concept_layer` give AFF steward
vocabulary when informing upstream fusion; they are **not** a target for an AFF layer scorer.
Affectively similar patterns may still surface via AFF-owned dimensions (e.g. D2 rajas, D8 krodha,
D24 tone scorers when enabled).

**Does not emit D7** (PHE owns phenomenological valence/arousal; AFF may consume shared readings).

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
`build_concept_registry()` loads affinity from MySQL when configured; else
`data/kg/aff_concept_layer.v1.json`.

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

1. **KG applicability:** `svarupa_assistant_v1.svarupa_concept_layer` (seeded from
   `documentation/dimensions_and_concepts/Dimension & Attribute Mapping to Analytical Layers.xlsx`
   via `scripts/seed_concept_layer_from_excel.py`).
2. **Scorer wiring:** `svarupa_layer_scorer` + `svarupa_layer_scorer_concept`
   (`sql/005_layer_scorer_emit.sql`, `scripts/seed_aff_layer_scorers.py`).
3. **Layer design:** specs in sibling repo `svarupa-assist-server/documentations/dimensions/`
   (31-Dimension Spec v7.1, Analytical Layers Spec v1.0). File-scoped conventions live in
   `.cursor/rules/`.
