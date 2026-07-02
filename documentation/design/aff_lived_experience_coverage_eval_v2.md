# AFF Lived-Experience Coverage Eval v2 — Design Document

**Status:** Implemented  
**Script:** `scripts/eval_aff_lived_experience_coverage_v2.py`  
**Scope:** Offline regression harness only — **not** the affect analysis pipeline.

> **Pipeline design** (how `/v2/analyze` scores lived experience): see
> [`aff_layer_design_v2_llm_native.md`](aff_layer_design_v2_llm_native.md).

---

## 1. Purpose

The v2 coverage eval answers one question:

> When we feed state-specific, first-person lived-experience prompts into the **LLM-primary AFF pipeline**, does the layer surface the **intended concept slug** in its emitted `attribute_scores`?

Unlike v1 (`scripts/eval_aff_lived_experience_coverage.py`), which:

- generates **2** questions per **concept** (no state axis),
- calls **`POST /analyze`** (legacy or mode-dependent),

v2 eval:

- generates **10** questions per **Dimension → Concept → State** triplet,
- uses a **psychometric gold-standard prompt** (no direct naming of concept/state),
- calls **`POST /v2/analyze`** with `options.force=true` by default,
- records v2-specific response fields (`llm_primary_used`, `abstained_dimensions`).

Match is at **concept slug** level only — not state-pole accuracy.

---

## 2. Eval-only artifacts

| Artifact | Path |
|----------|------|
| Eval script | `scripts/eval_aff_lived_experience_coverage_v2.py` |
| Output workbook | `data/eval/aff_lived_experience_coverage_v2.xlsx` |

---

## 3. Eval pipeline — step by step

The script supports three steps via `--step {all|generate|evaluate}`.

### Phase A — Load triplets

**Goal:** Build the closed set of `(dimension, concept, state)` targets AFF primary layer owns.

#### A.1 MySQL path (preferred)

When `SVARUPA_MYSQL_*` is configured and PyMySQL is available:

```sql
SELECT c.concept_id, cl.dimension_id, c.slug, c.name, cl.role,
       gloss, s.code AS state_code, s.label AS state_label,
       cd.description AS state_description
  FROM svarupa_concept_layer cl
  JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
  JOIN (
        SELECT concept_id, status_id, MIN(description_id) AS description_id
          FROM svarupa_concept_descriptions
         GROUP BY concept_id, status_id
       ) cd_pick ON cd_pick.concept_id = c.concept_id
  JOIN svarupa_concept_descriptions cd ON cd.description_id = cd_pick.description_id
  JOIN svarupa_status s ON s.status_id = cd.status_id
 WHERE cl.layer_code = 'AFF' AND cl.role = 'primary'
 ORDER BY cl.dimension_id, c.slug, s.sort_order
```

**Filters:**

| Filter | Rationale |
|--------|-----------|
| `layer_code = 'AFF'` | Only concepts AFF may reference |
| `role = 'primary'` | D2/D8/D9 owned core (not contributing-only vocabulary) |
| `GROUP BY concept_id, status_id` | Dedupe duplicate description rows in KG |

**Canonical states** (`svarupa_status`):

| `status_id` | `code` | `label` | `polarity` |
|-------------|--------|---------|------------|
| 1 | `deficiency` | Deficiency | −1 |
| 2 | `balance` | Balance | 0 |
| 3 | `excess` | Excess | +1 |

#### A.2 Static fallback

If MySQL is unavailable, load `data/kg/aff_concept_layer.v1.json`, filter `role == primary`, and synthesize three triplets per concept using default poles (`deficiency`, `balance`, `excess`) with gloss excerpt as `state_description`.

#### A.3 Limiting

`--limit N` keeps the first **N distinct `concept_id` values** (in sort order) and **all states** for each — e.g. `--limit 1` → 3 triplets → 30 Excel rows.

**Cardinality:** `triplets × 10 prompts = rows`. Full primary set ≈ 50 triplets → 500 rows (after dedupe).

---

### Phase B — Generate lived-experience questions

**Goal:** For each triplet, produce 10 first-person "I" statements that fingerprint **one state of one concept** without naming it.

#### B.1 Psychometric system prompt

Pinned in `QUESTION_GEN_SYSTEM` inside the eval script. Core constraints:

1. **No direct naming** — concept name, state name, synonyms forbidden in prompt text.
2. **Lived-experience focus** — sensory, somatic, behavioral, cognitive detail.
3. **State-level specificity** — distinguish sibling states and neighboring concepts.
4. **Temporal variety** — past, present, anticipated future narrations.

The model must return JSON (Bedrock `complete_json`):

```json
{
  "fingerprint_summary": "...",
  "prompts": ["I ...", "..."],
  "validation_notes": ["...", "..."],
  "sibling_contrast": "...",
  "edge_case_warning": "..."
}
```

`prompts` and `validation_notes` are arrays of **exactly 10** strings.

#### B.2 Per-triplet user message

```
The target triplet I want you to build this for is:
Dimension: {dimension_name}
Concept: {concept_name}
State: {state_label}

Steward context (for your analysis only; do not echo in prompts): '{state_description excerpt}'
```

One Bedrock call **per triplet** (not batched — each prompt is highly state-specific).

#### B.3 LLM invocation parameters

| Parameter | Source | Typical value |
|-----------|--------|---------------|
| `model_id` | `Settings.bedrock_model_id` | Claude on Bedrock |
| `region` | `Settings.aws_region` | e.g. `us-east-1` |
| `temperature` | hardcoded | `0.7` (creative question diversity) |
| `max_tokens` | `max(8192, llm_assist_max_tokens)` | room for 10 prompts + notes |
| `timeout_s` | `Settings.llm_assist_timeout_s` | per call |

#### B.4 Template fallback

`--use-templates` or LLM failure → `_template_questions()`:

- Rotates tense across prompts (present / recent past / anticipated future).
- **Does** mention concept name and state label (not suitable for blind eval; use for plumbing tests only).

#### B.5 Workbook rows

Each triplet expands to 10 rows. Columns:

| Column | Content |
|--------|---------|
| `dimension_id`, `dimension_name` | From dimension registry |
| `concept_id`, `concept_slug`, `concept_name`, `role` | From concept layer |
| `state_code`, `state_label` | From `svarupa_status` |
| `question_number` | 1–10 |
| `lived_experience_question` | Generated "I" statement |
| `validation_note` | Why this prompt targets the triplet |
| `match_result`, `matched_attributes`, `api_attributes`, `llm_primary_used`, `abstained_dimensions`, `api_error` | Filled in evaluate phase |

---

### Phase C — Evaluate via `/v2/analyze`

**Goal:** POST each question; record whether the API returns the expected `concept_slug`.

#### C.1 HTTP request

```http
POST /v2/analyze
Content-Type: application/json

{
  "analysis_text": "<lived_experience_question>",
  "options": { "force": true }
}
```

| Flag | Default | Purpose |
|------|---------|---------|
| `options.force` | `true` | Maps to `LayerContext.force_llm_primary` — bypasses pre-LLM salience gate so short affective prompts are not rejected as "too short" or "factual" |
| `--no-api-force` | — | CLI flag to disable force (tests abstention behavior) |

#### C.2 Match algorithm

```python
expected = canonical_slug(row.concept_slug)
found = attributes_from_response(response, dimension_id=row.dimension_id)
matched = {a for a in found if canonical_slug(a) == expected}
```

**`attributes_from_response` logic:**

1. If `dimension_id` is set → scan `signals[]` for matching `dimension_name`, return that signal's `attribute_scores[].attribute` only.
2. Else → flatten top-level `attribute_scores`, then all signals.

**Outcome:**

| `match_result` | Condition |
|----------------|-----------|
| `match` | `matched` non-empty |
| `no match` | HTTP 200 but slug not in attributes |
| (empty) + `api_error` | HTTP/transport failure |

**Note:** Match is at **concept** level, not **state** level. A prompt targeting "Excess Krodha" passes if `krodha` appears regardless of returned `state` pole.

#### C.3 Checkpointing

Every 10 evaluated rows, workbook is saved incrementally. `--force` re-evaluates rows that already have `match_result`.

#### C.4 Summary metrics

Logged at end: rows processed, `match` count, `no match` count.

---

## 4. v1 eval vs v2 eval

| Aspect | v1 | v2 eval |
|--------|----|---------|
| Granularity | Concept | Dimension → Concept → State |
| Questions per target | 2 | 10 |
| API endpoint | `/analyze` | `/v2/analyze` |
| Match criterion | `concept_slug` | Same (concept-level) |
| Output file | `aff_lived_experience_coverage.xlsx` | `aff_lived_experience_coverage_v2.xlsx` |

---

## 5. Operational usage

```bash
pip install openpyxl
uvicorn svarupa_affect.api.app:app --reload

PYTHONPATH=src python scripts/eval_aff_lived_experience_coverage_v2.py
PYTHONPATH=src python scripts/eval_aff_lived_experience_coverage_v2.py --step generate
PYTHONPATH=src python scripts/eval_aff_lived_experience_coverage_v2.py --limit 3 --use-templates
```

---

## 6. Known limitations

1. **Concept-level match only** — does not assert returned `state` pole matches row `state_code`.
2. **Template fallback leaks names** — Bedrock path required for real coverage measurement.
3. **Cost** — full run ≈ 500 scoring API calls + 50 question-generation Bedrock calls.
