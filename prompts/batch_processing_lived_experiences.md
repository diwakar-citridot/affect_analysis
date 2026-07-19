# Batch Processing — Dimension-Dwelling Lived Experiences

End-to-end runbook for generating the lived-experience statements for all concepts
via **AWS Bedrock Batch Inference** (~50% cheaper than on-demand, asynchronous).

## Overview

The pipeline is two stages:

- **Step 1 — Prepare** (synchronous, cheap): assemble one prompt per
  `(dimension, concept, status)` and turn them into a batch-ready JSONL.
- **Step 2 — Batch inference** (asynchronous, the bulk of the cost): submit the
  JSONL to Bedrock, poll for completion, then extract results into Excel.

Each concept produces **3 prompts** (one per state: `balanced` / `excessive` /
`deficient`), and each prompt asks for **20 statements** (10 Western + 10 Asian) —
so 60 statements per concept. Full corpus ≈ **608 concepts → 1,804 batch records**.

Scripts:
- `scripts/generate_dimension_dwelling_prompts.py` — assembles prompts (Step 1a).
- `scripts/batch_lived_experience.py` — `prepare` / `submit` / `status` / `fetch` / `run` (Steps 1b, 2).

---

## 0. Session setup

```bash
cd /Users/sampath/svarupa/affect_analysis
export AWS_PROFILE=195705949994_svarupa.org-dev-developer   # or valid env-var creds
```

Defaults resolve automatically (override any with the matching flag):

| Setting | Default | Source |
|---|---|---|
| S3 bucket | `dev-veda-cms-data` | `SVARUPA_BATCH_S3_BUCKET` |
| S3 prefix | `rag-data/svarupa_2_attribute_descriptions/dwelling` | under the role's IAM-allowed prefix |
| Region | `us-west-2` | `SVARUPA_AWS_REGION` (where batch/role/bucket live) |
| Role | `arn:aws:iam::195705949994:role/BedrockBatchSvarupaDescriptions` | `SVARUPA_BATCH_ROLE_ARN` |
| Model | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` → auto-expanded to its inference-profile ARN | `BEDROCK_MODEL_ID` |

> The bare `us.` model id is auto-expanded to
> `arn:aws:bedrock:us-west-2:195705949994:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0`
> at submit time, because batch authorizes `InvokeModel` against the profile ARN.

---

## Step 1 — Prepare prompts (batch-ready)

### 1a. Assemble the prompt files

Runs one small synchronous "Step-2 calibration" LLM call per concept (~$4 total for
the full corpus). **Do not** pass `--generate-lived-experience` — batch does the
generation in Step 2.

```bash
# All dimensions:
.venv/bin/python scripts/generate_dimension_dwelling_prompts.py \
  --output-dir ./prompts/26-05-2026 --max-workers 8

# One dimension (only useful when combined with others to reach >= 100 records):
.venv/bin/python scripts/generate_dimension_dwelling_prompts.py \
  --dimension trigunas --output-dir ./prompts/26-05-2026 --max-workers 6
```

Writes `./prompts/26-05-2026/<dimension>__<concept>__<status>.txt` and `all_prompts.txt`.

### 1b. Build the batch input JSONL + manifest (offline — no AWS, no LLM)

```bash
.venv/bin/python scripts/batch_lived_experience.py prepare \
  --prompts-dir ./prompts/26-05-2026            # [--dimension trigunas]
```

Writes:
- `./prompts/26-05-2026/batch_input_all.jsonl` — one Bedrock `InvokeModel` record per prompt.
- `./prompts/26-05-2026/batch_manifest_all.json` — maps `recordId` → `(dimension, concept, status)`.

> ⚠️ **Batch requires ≥ 100 records.** The full corpus (1,804) qualifies; a single
> small dimension does not. For one small dimension, use the sync path instead (see
> Appendix A).

---

## Step 2 — Batch inference

### 2a. Submit

```bash
.venv/bin/python scripts/batch_lived_experience.py submit \
  --prompts-dir ./prompts/26-05-2026 \
  --input-file    ./prompts/26-05-2026/batch_input_all.jsonl \
  --manifest-file ./prompts/26-05-2026/batch_manifest_all.json
```

- Uploads the JSONL to S3, creates the job, prints the **JOB ARN**.
- Writes a job record: `./prompts/26-05-2026/batch_job_all-run.json` (used by `status`/`fetch`).
- Job name is auto-timestamped, so re-submits never collide.

(If you skipped `prepare`, drop `--input-file/--manifest-file` and `submit` builds the JSONL from the prompt files itself.)

### 2b. Check status

```bash
.venv/bin/python scripts/batch_lived_experience.py status \
  --job-file ./prompts/26-05-2026/batch_job_all-run.json
```

Re-run periodically. Expect `Submitted` → `InProgress` → `Completed`
(typically tens of minutes to a few hours).

### 2c. Extract results to Excel (once `Completed`)

```bash
.venv/bin/python scripts/batch_lived_experience.py fetch \
  --job-file ./prompts/26-05-2026/batch_job_all-run.json \
  --output ./prompts/26-05-2026/dimension_dwelling_lived_experience.xlsx
```

Downloads the S3 output, parses each concept×status result, and writes the workbook
with columns: `dimension, concept, display_name, regional_perspective, status,
statement_number, statement`.

---

## One-command variant (submit → poll → extract)

```bash
.venv/bin/python scripts/batch_lived_experience.py run \
  --prompts-dir ./prompts/26-05-2026 \
  --input-file    ./prompts/26-05-2026/batch_input_all.jsonl \
  --manifest-file ./prompts/26-05-2026/batch_manifest_all.json \
  --output ./prompts/26-05-2026/dimension_dwelling_lived_experience.xlsx \
  --poll-interval 120
```

Ctrl-C is safe — resume later with `status` / `fetch` using the written job file.

---

## Troubleshooting

| Symptom | Cause | Resolution |
|---|---|---|
| `Could not validate GetObject permissions to access S3 bucket` | input uploaded to a prefix the batch role can't read | keep `--s3-prefix` under `rag-data/svarupa_2_attribute_descriptions/…` (default already does) |
| `The provided job name is currently in use` | duplicate job name | job name is auto-timestamped; just re-submit |
| `Customer doesn't have permissions to invokeModel` | bare profile id resolved to the foundation-model ARN | model id auto-expands to the inference-profile ARN; or pass `--model-id arn:aws:bedrock:us-west-2:195705949994:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `ExpiredToken` / `security token ... expired` | SSO/session creds expired | refresh creds (`aws sso login --profile …` or re-export env vars) |
| Job `Failed` for another reason | see the `message` field | `status` prints it; also `aws bedrock get-model-invocation-job --region us-west-2 --job-identifier <arn>` |

To re-run a failed job, just repeat **Step 2a** — the prepared JSONL from Step 1 is unchanged.

Inspect what models the role is permitted for (a Completed job proves permission):

```bash
aws bedrock list-model-invocation-jobs --region us-west-2 --max-results 20 \
  --query "invocationJobSummaries[?status=='Completed'].{name:jobName,model:modelId}" --output table
```

---

## Appendix A — Sync path (no batch; for small sets or convenience)

Does prompt assembly **and** lived-experience generation in one command, using
prompt caching + concurrency. No S3/batch required. ~$70–80 for the full corpus,
resumable via checkpoint.

```bash
.venv/bin/python scripts/generate_dimension_dwelling_prompts.py \
  --output-dir ./prompts/26-05-2026 \
  --generate-lived-experience --max-workers 8
# single small dimension:
#   add --dimension <slug>
```

Output: `./prompts/26-05-2026/dimension_dwelling_lived_experience.xlsx`
(+ `lived_experience_checkpoint.json` for resume).

---

## Appendix B — Output locations

| Artifact | Location |
|---|---|
| Prompt files | `./prompts/26-05-2026/<dim>__<concept>__<status>.txt`, `all_prompts.txt` |
| Batch input JSONL / manifest | `./prompts/26-05-2026/batch_input_all.jsonl`, `batch_manifest_all.json` |
| Job record | `./prompts/26-05-2026/batch_job_all-run.json` |
| Batch S3 input | `s3://dev-veda-cms-data/rag-data/svarupa_2_attribute_descriptions/dwelling/input/…` |
| Batch S3 output | `s3://dev-veda-cms-data/rag-data/svarupa_2_attribute_descriptions/dwelling/output/<job-id>/…` |
| Final Excel | `./prompts/26-05-2026/dimension_dwelling_lived_experience.xlsx` |

> The generated statements are **not** written to MySQL — the Excel/checkpoint is the
> final store. Ask if a DB write-back (`svarupa_lived_experience`) is needed.
