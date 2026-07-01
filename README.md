# Svarupa — Multi-Axis Affect Analysis (AFF), Layer 1

A field-first implementation of **Layer 1 (AFF)** of the Svarupa Assistant: it reconstructs the
**affective organization of lived experience** rather than classifying emotions. It builds a
hierarchical `AffectiveField`, separates background climate from foreground episodes, reconstructs
the appraisal and drivers behind the affect, recognises experiential patterns, and only then derives
emotion *hypotheses* mapped onto the Rasa-theoretic dimensions (D8/D9, contributing D2/D19/D22/D24).

This code follows the design in
[`documentation/design/aff_layer_design.md`](documentation/design/aff_layer_design.md) (v2.2).

## Quick start

No installation is required beyond `pydantic` (already standard). From the repo root:

```bash
PYTHONPATH=src python3 -m svarupa_affect.cli \
  "I keep hoping things will get better, but I am bracing myself for it to all fall apart again."
```

You can also pipe input or run interactively:

```bash
echo "I was furious, then empty, but slowly I'm at peace with it." | PYTHONPATH=src python3 -m svarupa_affect.cli
PYTHONPATH=src python3 -m svarupa_affect.cli          # prompts: "Describe a lived experience:"
```

Or install it as a console script:

```bash
pip install -e .
svarupa-affect "..."
```

### HTTP API (FastAPI)

```bash
pip install -e ".[api]"
# IMPORTANT: use the venv's Python, not Homebrew's `uvicorn` (different interpreter → no boto3)
PYTHONPATH=src .venv/bin/python -m uvicorn svarupa_affect.api.app:app --reload --port 8000
# POST /analyze  {"analysis_text": "..."}   ->   signals[] + phenomenology_input
# GET  /health
# interactive docs at /docs
```

The repo `.env` is loaded automatically on startup (values already set in the shell are not overridden).

### Output

The CLI prints **tabular console views** (summary, hierarchical affective field, emotion hypotheses,
experiential patterns, appraisal profile, drivers, interactions/tensions, trajectory/dynamics,
dimensional signals, and the typed uncertainty profile), followed by the full **JSON** response.

Flags:

| flag | effect |
| --- | --- |
| `--json-only` | print only the JSON (no tables) |
| `--no-tables` | skip the tables, still print JSON |
| `--json-out PATH` | also write the JSON to a file |

## Architecture (clean / hexagonal)

```
src/svarupa_affect/
  api/             # FastAPI edge: dtos.py, routes.py, dependencies.py (DI), app.py
  application/     # use case + collaborators: AffectiveFieldBuilder, AppraisalReconstructor,
                   #   AffectDriverReconstructor, ExperientialPatternRecognizer,
                   #   EmotionHypothesisGenerator, AffectDynamicsAnalyzer,
                   #   FieldAssist (LLM gate+reconcile), PhenomenologyInputAssembler,
                   #   AffectLayer (orchestrator), mappers.py (domain <-> DTO)
  domain/          # pure core: enums, invariants, models (hierarchical AffectiveField,
                   #   AppraisalProfile, AffectDriver, ExperientialPattern, ForegroundEpisode,
                   #   AffectTrajectory, AffectInteraction, PhenomenologyInput, DimensionalSignal),
                   #   ports (Protocols incl. IFeatureCache), scoring math
  infrastructure/  # adapters: VAD (VADER/TextBlob), lexical affect (NRCLex), linguistic cues,
                   #   emotion evidence, lexical_fallback, JSON bridge tables, config,
                   #   feature_cache, llm/ (Bedrock + Null providers + prompts), kg/ (steward)
  cli.py           # console entry point: input -> JSON + tables
data/
  bridge/          # hypothesis -> Rasa bridge tables (the single editable artifact)
  field/           # field-synthesis weights, experiential-pattern signatures, appraisal rules,
                   #   interaction templates
  pole_maps/       # per-attribute {deficiency, balance, excess} rules
  ground_truth/    # gold-standard eval cases (+ schema)
tests/             # per-layer math, invariants, LLM-failure, property + philosophy regression
```

Run the tests with `pytest` (the suite drives async code via `asyncio.run`, so the
`pytest-asyncio` plugin is optional).

Dependencies point inward; `domain/` performs no I/O. Adapters implement the ports
(`IVADModel`, `ILexicalAffect`, `ILinguisticCues`, `IEmotionEvidence`, `IBridgeTable`, …).

## Lean deterministic stack (v1)

The signal-source adapters use **VADER / TextBlob / NRCLex when installed**, and otherwise fall back
to a self-contained lexicon + heuristic implementation so the layer **runs out of the box** with only
`pydantic`. Swapping in the real libraries (or, later, transformer models) is an
`infrastructure/`-only change thanks to the port seam — exactly as the design promises. To use the
named libraries:

```bash
pip install -e ".[nlp]"
```

The LLM field-assist (Bedrock/Claude) is **disabled by default** (`SVARUPA_ENABLE_LLM_ASSIST=0`); the
deterministic field-reconstruction path covers the common case and the layer degrades gracefully when
the assist is unavailable.

When the assist is **enabled** (`SVARUPA_ENABLE_LLM_ASSIST=1`) but the Bedrock provider cannot be
initialized (missing `boto3`, AWS credentials, or region), the layer does **not** fall back silently:
it logs a loud `ERROR` with the real cause and then degrades to deterministic-only. Set
`SVARUPA_LLM_STRICT=1` to fail fast (raise) instead of degrading. Every response also reports
`provenance.llm_assist_used` so you can confirm whether Bedrock was actually invoked.

## Design philosophy (binding)

- **Field-first** — reconstruct the affective field before deriving any emotion.
- **Recognition, not diagnosis** — describe the experience carried by the language, never the person.
- **Evidence everywhere** — every reconstructed feature carries `value`, `confidence`, and `evidence`.
- **Hierarchy over flat vectors**, **stable contracts** (downstream consumes `PhenomenologyInput`),
  and **deterministic-first, LLM-assisted**.
