# Agent instructions — Svarupa Multi-Axis Affect Analysis (AFF)

This component implements **Layer 1 (AFF)** of the Svarupa Assistant: the emotion-reading
specialist that maps a user's expression onto the affective dimensions of the 31-Dimension
framework. It is one of seven independent analytical layers and is independently useful.

## Runtime modes (v1 vs v2)

AFF supports two pipelines selected by **`SVARUPA_AFFECT_MODE`** (or request `options.affect_mode`):

| Mode | Pipeline | When to use |
|------|----------|-------------|
| `legacy_deterministic` (default) | Lexicons → field synthesis JSON → hypotheses → `hyp2*` bridges | Regression, offline eval, no Bedrock |
| `llm_primary` | Single Bedrock call (`lived_experience_v1`) → safety shell → signals | Free-text lived experience (target production path) |

**v2 design:** `documentation/design/aff_layer_design_v2_llm_native.md`  
**v1 design:** `documentation/design/aff_layer_design.md`

Enable v2:

```bash
export SVARUPA_AFFECT_MODE=llm_primary
export AWS_REGION=us-east-1   # Bedrock
PYTHONPATH=src python -m svarupa_affect.cli "your lived experience text"
```

Key v2 modules:

- `application/lived_experience_orchestrator.py` — primary scorer
- `application/safety_shell.py` — whitelist, poles, abstention
- `infrastructure/llm/prompts/lived_experience_v1.py` — pinned prompt + schema
- `api/routes_v2.py`, `api/app_v2.py` — FastAPI v2 surface (`POST /v2/analyze`)

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

### v2 (`llm_primary`)

- **LLM-primary:** one structured Bedrock call scores field organization + D2/D8/D9 from text and KG glosses.
- Deterministic **safety shell** only: slug whitelist, pole math, abstention, provenance.
- No `hyp2*` JSON bridges on the primary path.

### v1 (`legacy_deterministic`)

- **Model-first, LLM-assisted:** deterministic affect models (VAD, NRCLex, TF-IDF anchors) do the work;
  Claude (Bedrock) is invoked only for flagged field ambiguity (`field_assist`).
- Hypothesis bridges: `hyp2sthayi.v2.json`, `hyp2vyabhi.v2.json`, `guna_families.v1.json`.

Both modes: reads emotion onto Rasa theory (enduring vs transient bhāvas, guṇa coloration).
Shares valence/arousal with PHE and temporal cues with NAR via `SharedFeatures`.

## Non-negotiable design philosophy

1. **Recognition, not diagnosis** — observations/invitations, never labels/predictions/prescriptions.
2. **Relevance vs confidence** are two separate numbers, never collapsed. Confidence is about the
   *process*, never certainty about the person.
3. **Abstention is a valid, meaningful output**; never fabricate signals on thin input.

## Architecture

Clean/hexagonal: `api/` → `application/` → `domain/` (ports) ← `infrastructure/` (adapters).
LLM and KG sit behind ports (`ILLMProvider`, `IConceptRegistry`). AFF is read-only against the KG.
Dimensions are data, not code — no `if dimension == X` branching in scoring logic.
`build_concept_registry()` loads affinity from MySQL when configured; else
`data/kg/aff_concept_layer.v1.json`.

## Tooling

- Python `>=3.11,<3.14`, FastAPI, pydantic v2.
- Format/lint/type/test: `ruff check . && black --check . && mypy src && pytest`
  (black line-length 100, mypy strict).

## Testing methodology

Per-layer tests first (deterministic math + mocked LLM failures), then fusion (mocked JSON),
then gold-standard eval cases in `data/ground_truth/`. For v2: `tests/test_lived_experience_primary.py`
with mocked `ILLMProvider`. This is a subjective domain: assert invariants, property tests, and
philosophy-regression (no verdict language) rather than bitwise-perfect LLM output.

## Source of truth

1. **KG applicability:** `svarupa_assistant_v1.svarupa_concept_layer` (seeded from
   `documentation/dimensions_and_concepts/Dimension & Attribute Mapping to Analytical Layers.xlsx`
   via `scripts/seed_concept_layer_from_excel.py`).
2. **Scorer wiring:** `svarupa_layer_scorer` + `svarupa_layer_scorer_concept`
   (`sql/005_layer_scorer_emit.sql`, `scripts/seed_aff_layer_scorers.py`).
3. **Layer design:** v2 `documentation/design/aff_layer_design_v2_llm_native.md`; v1
   `documentation/design/aff_layer_design.md`; specs in sibling repo
   `svarupa-assist-server/documentations/dimensions/` (31-Dimension Spec v7.1, Analytical Layers Spec v1.0).
