#!/usr/bin/env python3
"""Run dimension-dwelling lived-experience generation via **Bedrock Batch Inference** (50% off).

Batch inference is asynchronous and ~50% cheaper than on-demand ``converse`` calls.
Because each lived prompt embeds the concept's Step 2 ✗/✓ calibration (itself an LLM
call), this tool consumes the **already-assembled prompt files** produced by
``generate_dimension_dwelling_prompts.py`` — so the cheap Step 2 calls run once,
synchronously, and only the expensive lived generation is batched.

Pipeline
--------
STEP 1 — prepare the prompts and make them batch-ready (no batch/AWS yet):

  1a. Assemble prompts (writes ``<dim>__<concept>__<status>.txt``; one sync Step-2
      calibration LLM call per concept)::

        export AWS_PROFILE=195705949994_svarupa.org-dev-developer
        .venv/bin/python scripts/generate_dimension_dwelling_prompts.py \
          --output-dir ./prompts/26-05-2026 --max-workers 8          # all dimensions
        # or --dimension trigunas for one dimension

      (omit ``--generate-lived-experience`` — batch does that generation in Step 2.)

  1b. Build the batch-ready JSONL + manifest (offline, no AWS, no LLM)::

        .venv/bin/python scripts/batch_lived_experience.py prepare \
          --prompts-dir ./prompts/26-05-2026        # [--dimension trigunas]

      Writes ``batch_input_<tag>.jsonl`` and ``batch_manifest_<tag>.json``.

STEP 2 — run the batch inference over the prepared input:

  2a. Submit (defaults: bucket/prefix/role/region from .env)::

        .venv/bin/python scripts/batch_lived_experience.py submit \
          --prompts-dir ./prompts/26-05-2026 \
          --input-file ./prompts/26-05-2026/batch_input_all.jsonl \
          --manifest-file ./prompts/26-05-2026/batch_manifest_all.json

      Prints a JOB ARN and writes a job record (``batch_job_*.json``). Batch requires
      **>= 100 records**; a single small dimension won't qualify — combine dimensions.

  2b. Poll, then fetch to Excel::

        .venv/bin/python scripts/batch_lived_experience.py status --job-file ./prompts/26-05-2026/batch_job_all-run.json
        .venv/bin/python scripts/batch_lived_experience.py fetch  --job-file ./prompts/26-05-2026/batch_job_all-run.json \
          --output ./prompts/26-05-2026/dimension_dwelling_lived_experience.xlsx

  (``run`` does submit -> poll -> fetch end-to-end; ``submit`` also builds the JSONL
  itself from --prompts-dir if you skip the explicit ``prepare`` step.)

Environment (loaded from ./.env if present)
-------------------------------------------
  SVARUPA_BATCH_ROLE_ARN   IAM role Bedrock assumes for batch (required)
  SVARUPA_BATCH_S3_BUCKET  default S3 bucket for input/output (or pass --s3-bucket)
  BEDROCK_MODEL_ID         default model / inference profile (must be batch-supported)
  AWS_REGION / SVARUPA_AWS_REGION
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import boto3

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_DIR = REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from svarupa_affect.infrastructure.config import load_dotenv as _load_repo_dotenv

from dimension_dwelling_prompt_template import (
    parse_lived_experience_json,
    split_cache_segments,
)

_load_repo_dotenv()

logger = logging.getLogger("batch_lived_experience")

ANTHROPIC_VERSION = "bedrock-2023-05-31"
DEFAULT_MAX_TOKENS = 4096
MIN_BATCH_RECORDS = 100
_PROMPT_HEADER_DIVIDER = f"{'=' * 72}\n\n"

# Excel columns (mirror generate_dimension_dwelling_prompts.LIVED_EXPERIENCE_COLUMNS).
LIVED_EXPERIENCE_COLUMNS = [
    "dimension",
    "concept",
    "display_name",
    "regional_perspective",
    "status",
    "statement_number",
    "statement",
]


def _setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        stream=sys.stdout,
    )


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def _resolve_region(explicit: str | None) -> str:
    # Batch jobs / role / bucket live in us-west-2 for this account, so prefer the
    # Svarupa region over the general AWS_REGION (which is us-east-1 for runtime calls).
    for candidate in (explicit, _env("SVARUPA_AWS_REGION"), _env("AWS_REGION"), "us-west-2"):
        if candidate and candidate.strip():
            return candidate.strip()
    return "us-west-2"


def _resolve_model_id(explicit: str | None) -> str:
    for candidate in (
        explicit,
        _env("SVARUPA_DIMENSION_DWELLING_BEDROCK_MODEL_ID"),
        _env("BEDROCK_MODEL_ID"),
    ):
        if candidate and candidate.strip():
            return candidate.strip().strip('"')
    raise SystemExit("No model id: pass --model-id or set BEDROCK_MODEL_ID in .env")


# --------------------------------------------------------------------------- #
# Prompt files -> batch records
# --------------------------------------------------------------------------- #
def _read_prompt_header_and_body(path: Path) -> tuple[dict[str, str], str]:
    """Return (header_fields, prompt_body) for an assembled prompt file."""
    content = path.read_text(encoding="utf-8")
    idx = content.find(_PROMPT_HEADER_DIVIDER)
    header_text = content[:idx] if idx != -1 else ""
    body = content[idx + len(_PROMPT_HEADER_DIVIDER) :] if idx != -1 else content
    header: dict[str, str] = {}
    for line in header_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            header[key.strip().lower()] = val.strip()
    return header, body


def _flatten_prompt(body: str) -> str:
    """Join cache-aligned segments back into a single plain prompt (batch has no cachePoint)."""
    return "\n\n".join(split_cache_segments(body))


def _collect_prompt_files(prompts_dir: Path, dimension: str | None) -> list[Path]:
    files = sorted(p for p in prompts_dir.glob("*.txt") if p.name != "all_prompts.txt")
    if not files:
        raise SystemExit(f"No prompt .txt files in {prompts_dir}. Run generate_dimension_dwelling_prompts.py first.")
    if not dimension:
        return files
    kept: list[Path] = []
    for path in files:
        header, _ = _read_prompt_header_and_body(path)
        if header.get("dimension") == dimension:
            kept.append(path)
    if not kept:
        raise SystemExit(f"No prompt files for dimension={dimension!r} in {prompts_dir}.")
    return kept


def _build_records(
    prompt_files: list[Path], *, max_tokens: int
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    """Build (jsonl_records, manifest). manifest maps recordId -> {dimension, concept, status, path}."""
    records: list[dict[str, Any]] = []
    manifest: dict[str, dict[str, str]] = {}
    for i, path in enumerate(prompt_files):
        header, body = _read_prompt_header_and_body(path)
        prompt = _flatten_prompt(body)
        record_id = f"rec{i:05d}"
        records.append(
            {
                "recordId": record_id,
                "modelInput": {
                    "anthropic_version": ANTHROPIC_VERSION,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
                },
            }
        )
        manifest[record_id] = {
            "dimension": header.get("dimension", ""),
            "concept": header.get("concept", ""),
            "status": header.get("status", ""),
            "path": str(path),
        }
    return records, manifest


# --------------------------------------------------------------------------- #
# AWS helpers
# --------------------------------------------------------------------------- #
def _s3(region: str):
    return boto3.client("s3", region_name=region)


def _bedrock(region: str):
    return boto3.client("bedrock", region_name=region)


def _upload_jsonl(s3, bucket: str, key: str, records: list[dict[str, Any]]) -> str:
    payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
    s3.put_object(Bucket=bucket, Key=key, Body=payload.encode("utf-8"))
    return f"s3://{bucket}/{key}"


def _job_id_from_arn(job_arn: str) -> str:
    return job_arn.rsplit("/", 1)[-1]


# Cross-region inference-profile id prefixes (Bedrock geo routing).
_PROFILE_PREFIXES = ("us.", "eu.", "apac.", "us-gov.")


def _expand_model_arn(model_id: str, *, region: str, role_arn: str) -> str:
    """Expand a bare cross-region inference-profile id into its full ARN.

    Batch authorizes ``InvokeModel`` against the inference-profile ARN resource, so a
    bare id like ``us.anthropic.claude-sonnet-4-5-...`` gets denied even when the role
    is permitted; the full ``arn:aws:bedrock:<region>:<account>:inference-profile/<id>``
    matches the policy. Already-ARN ids and plain foundation ids pass through unchanged.
    """
    if model_id.startswith("arn:"):
        return model_id
    if not model_id.startswith(_PROFILE_PREFIXES):
        return model_id  # plain foundation model id — invoke directly
    try:
        account = role_arn.split(":")[4]
    except IndexError:
        return model_id
    if not account:
        return model_id
    return f"arn:aws:bedrock:{region}:{account}:inference-profile/{model_id}"


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_prepare(args: argparse.Namespace) -> int:
    """Step 1 (offline): turn assembled prompt files into a batch-ready JSONL + manifest.

    Pure file transform — no AWS, no LLM. Produces exactly the input Bedrock batch
    consumes, so Step 2 (`submit`/`run --input-file ...`) just uploads and runs.
    """
    prompts_dir = Path(args.prompts_dir)
    prompt_files = _collect_prompt_files(prompts_dir, args.dimension)
    records, manifest = _build_records(prompt_files, max_tokens=args.max_tokens)

    tag = args.job_name or (args.dimension or "all")
    out_jsonl = Path(args.out_jsonl) if args.out_jsonl else prompts_dir / f"batch_input_{tag}.jsonl"
    out_manifest = (
        Path(args.out_manifest) if args.out_manifest else prompts_dir / f"batch_manifest_{tag}.json"
    )
    out_jsonl.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records), encoding="utf-8"
    )
    out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(
        "Prepared %s record(s) -> %s (manifest: %s)", len(records), out_jsonl, out_manifest
    )
    if len(records) < MIN_BATCH_RECORDS:
        logger.warning(
            "Only %s record(s); Bedrock batch needs >= %s. Combine dimensions or use the "
            "sync path for this set.",
            len(records),
            MIN_BATCH_RECORDS,
        )
    print(out_jsonl)
    return 0


def _load_prepared(input_file: str, manifest_file: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    records = [
        json.loads(line)
        for line in Path(input_file).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest = (
        json.loads(Path(manifest_file).read_text(encoding="utf-8")) if manifest_file else {}
    )
    return records, manifest


def cmd_submit(args: argparse.Namespace) -> int:
    region = _resolve_region(args.region)
    model_id = _resolve_model_id(args.model_id)
    role_arn = args.role_arn or _env("SVARUPA_BATCH_ROLE_ARN")
    bucket = args.s3_bucket or _env("SVARUPA_BATCH_S3_BUCKET")
    if not role_arn:
        raise SystemExit("No role ARN: pass --role-arn or set SVARUPA_BATCH_ROLE_ARN in .env")
    if not bucket:
        raise SystemExit("No S3 bucket: pass --s3-bucket or set SVARUPA_BATCH_S3_BUCKET in .env")

    resolved_model = _expand_model_arn(model_id, region=region, role_arn=role_arn)
    if resolved_model != model_id:
        logger.info("Expanded model id to inference-profile ARN: %s", resolved_model)
    model_id = resolved_model

    prompts_dir = Path(args.prompts_dir)
    if args.input_file:
        records, manifest = _load_prepared(args.input_file, args.manifest_file)
        logger.info("Loaded %s prepared record(s) from %s", len(records), args.input_file)
    else:
        prompt_files = _collect_prompt_files(prompts_dir, args.dimension)
        records, manifest = _build_records(prompt_files, max_tokens=args.max_tokens)
        logger.info("Prepared %s record(s) from %s", len(records), prompts_dir)

    if len(records) < MIN_BATCH_RECORDS and not args.allow_small:
        raise SystemExit(
            f"Batch inference requires >= {MIN_BATCH_RECORDS} records (have {len(records)}). "
            "Batch several dimensions together, or use the on-demand path "
            "(generate_dimension_dwelling_prompts.py --generate-lived-experience). "
            "Pass --allow-small to attempt anyway (AWS may reject)."
        )

    tag = args.job_name or (args.dimension or "all")
    stamp = args.stamp  # caller-provided timestamp keeps the script deterministic/testable
    prefix = args.s3_prefix.strip("/")
    input_key = f"{prefix}/input/{tag}-{stamp}.jsonl"
    output_uri = f"s3://{bucket}/{prefix}/output/{tag}-{stamp}/"

    s3 = _s3(region)
    input_uri = _upload_jsonl(s3, bucket, input_key, records)
    logger.info("Uploaded input: %s", input_uri)

    bedrock = _bedrock(region)
    # Job names must be unique across jobs (even Failed ones linger), so always append a
    # timestamp. S3 keys and the local job-record filename stay stamped by `stamp` so
    # status/fetch commands remain predictable; the unique jobArn is what they use.
    job_name = f"svarupa-dwelling-{tag}-{time.strftime('%Y%m%d-%H%M%S')}"[:63]
    resp = bedrock.create_model_invocation_job(
        jobName=job_name,
        roleArn=role_arn,
        modelId=model_id,
        inputDataConfig={"s3InputDataConfig": {"s3Uri": input_uri}},
        outputDataConfig={"s3OutputDataConfig": {"s3Uri": output_uri}},
    )
    job_arn = resp["jobArn"]
    logger.info("Submitted batch job: %s", job_arn)

    job_record = {
        "job_arn": job_arn,
        "job_name": job_name,
        "region": region,
        "model_id": model_id,
        "bucket": bucket,
        "input_uri": input_uri,
        "output_uri": output_uri,
        "record_count": len(records),
        "manifest": manifest,
    }
    job_file = Path(args.job_file) if args.job_file else prompts_dir / f"batch_job_{tag}-{stamp}.json"
    job_file.write_text(json.dumps(job_record, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Wrote job record: %s", job_file)
    print(job_arn)
    return 0


def _load_job_record(args: argparse.Namespace) -> dict[str, Any]:
    if args.job_file:
        return json.loads(Path(args.job_file).read_text(encoding="utf-8"))
    raise SystemExit("Pass --job-file (written by `submit`).")


def cmd_status(args: argparse.Namespace) -> int:
    job = _load_job_record(args)
    bedrock = _bedrock(job["region"])
    info = bedrock.get_model_invocation_job(jobIdentifier=job["job_arn"])
    logger.info(
        "Job %s | status=%s | submitted=%s",
        job["job_name"],
        info.get("status"),
        info.get("submitTime"),
    )
    if info.get("message"):
        logger.info("message: %s", info["message"])
    print(info.get("status"))
    return 0


def _download_output_records(s3, bucket: str, output_prefix: str) -> list[dict[str, Any]]:
    """List and parse all *.jsonl.out records under the job's output prefix."""
    records: list[dict[str, Any]] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=output_prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".out") and not key.endswith(".jsonl.out") and not key.endswith(".jsonl"):
                continue
            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
            for line in body.splitlines():
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def _extract_text(model_output: dict[str, Any]) -> str:
    """Pull the assistant text out of a Claude batch modelOutput block."""
    parts = model_output.get("content") or []
    return "".join(p.get("text", "") for p in parts if isinstance(p, dict))


def cmd_fetch(args: argparse.Namespace) -> int:
    job = _load_job_record(args)
    region = job["region"]
    bucket = job["bucket"]
    bedrock = _bedrock(region)
    info = bedrock.get_model_invocation_job(jobIdentifier=job["job_arn"])
    status = info.get("status")
    if status != "Completed":
        raise SystemExit(f"Job status is {status!r}; can only fetch a Completed job.")

    # Bedrock writes output under <output_uri>/<jobId>/
    job_id = _job_id_from_arn(job["job_arn"])
    output_uri = job["output_uri"].rstrip("/")
    output_prefix = output_uri.replace(f"s3://{bucket}/", "") + f"/{job_id}/"

    s3 = _s3(region)
    out_records = _download_output_records(s3, bucket, output_prefix)
    logger.info("Downloaded %s output record(s) from s3://%s/%s", len(out_records), bucket, output_prefix)

    manifest: dict[str, dict[str, str]] = job["manifest"]
    rows: list[dict[str, Any]] = []
    parsed = failed = 0
    for rec in out_records:
        rid = rec.get("recordId")
        meta = manifest.get(rid, {})
        model_output = rec.get("modelOutput") or {}
        text = _extract_text(model_output)
        try:
            statements = parse_lived_experience_json(text)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            logger.warning("Parse failed for %s (%s/%s): %s", rid, meta.get("concept"), meta.get("status"), exc)
            continue
        parsed += 1
        status_label = meta.get("status", "")
        display = (meta.get("concept") or "").replace("_", " ").strip()
        for n, stmt in enumerate(statements, start=1):
            rows.append(
                {
                    "dimension": meta.get("dimension", ""),
                    "concept": meta.get("concept", ""),
                    "display_name": display,
                    "regional_perspective": stmt["regional_perspective"],
                    "status": status_label or stmt["status"],
                    "statement_number": n,
                    "statement": stmt["statement"],
                }
            )

    _write_excel(rows, Path(args.output))
    logger.info(
        "Wrote %s (%s row(s)); %s record(s) parsed, %s failed", args.output, len(rows), parsed, failed
    )
    return 0 if failed == 0 else 1


def cmd_run(args: argparse.Namespace) -> int:
    rc = cmd_submit(args)
    if rc != 0:
        return rc
    job = _load_job_record(args) if args.job_file else None
    # cmd_submit wrote a job file; discover it if not explicitly given.
    if job is None:
        tag = args.job_name or (args.dimension or "all")
        candidates = sorted(Path(args.prompts_dir).glob(f"batch_job_{tag}-*.json"))
        if not candidates:
            raise SystemExit("Could not locate the job record written by submit.")
        args.job_file = str(candidates[-1])
        job = _load_job_record(args)

    bedrock = _bedrock(job["region"])
    logger.info("Polling job every %ss (Ctrl-C to stop; resume later with `fetch`)...", args.poll_interval)
    while True:
        info = bedrock.get_model_invocation_job(jobIdentifier=job["job_arn"])
        status = info.get("status")
        logger.info("  status=%s", status)
        if status in ("Completed", "Failed", "Stopped", "Expired"):
            break
        time.sleep(args.poll_interval)
    if status != "Completed":
        raise SystemExit(f"Job ended with status {status!r}: {info.get('message')}")
    return cmd_fetch(args)


def _write_excel(rows: list[dict[str, Any]], output_path: Path) -> None:
    try:
        import openpyxl
    except ImportError as exc:
        raise SystemExit("openpyxl is required: pip install openpyxl") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "lived_experience"
    ws.append(LIVED_EXPERIENCE_COLUMNS)
    for row in rows:
        ws.append([row[col] for col in LIVED_EXPERIENCE_COLUMNS])
    wb.save(output_path)


def _add_common_submit_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--prompts-dir", required=True, help="Directory of assembled prompt .txt files.")
    p.add_argument("--dimension", default="", help="Optional: only prompts for this dimension slug.")
    p.add_argument("--s3-bucket", default="", help="S3 bucket (or SVARUPA_BATCH_S3_BUCKET).")
    p.add_argument(
        "--s3-prefix",
        default=((_env("SVARUPA_BATCH_S3_PREFIX").rstrip("/") or "rag-data/svarupa_2_attribute_descriptions") + "/dwelling"),
        help=(
            "S3 key prefix. Default is a 'dwelling' subfolder UNDER SVARUPA_BATCH_S3_PREFIX so it "
            "stays within the batch role's IAM-allowed prefix "
            "(e.g. rag-data/svarupa_2_attribute_descriptions/dwelling). Overriding this to a prefix "
            "the role cannot read causes 'Could not validate GetObject permissions'."
        ),
    )
    p.add_argument("--role-arn", default="", help="Batch IAM role (or SVARUPA_BATCH_ROLE_ARN).")
    p.add_argument("--model-id", default="", help="Model / inference profile (or BEDROCK_MODEL_ID).")
    p.add_argument("--region", default="", help="AWS region (or AWS_REGION).")
    p.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    p.add_argument("--job-name", default="", help="Override job tag (default: dimension or 'all').")
    p.add_argument("--stamp", default="run", help="Timestamp tag for S3 keys / job file (default: 'run').")
    p.add_argument("--job-file", default="", help="Path for the job record JSON (default: under prompts-dir).")
    p.add_argument("--allow-small", action="store_true", help=f"Allow < {MIN_BATCH_RECORDS} records.")
    p.add_argument(
        "--input-file",
        default="",
        help="Use a prepared JSONL (from `prepare`) instead of building from prompt files.",
    )
    p.add_argument("--manifest-file", default="", help="Manifest JSON matching --input-file.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    p_prepare = sub.add_parser(
        "prepare", help="Step 1: build a batch-ready JSONL + manifest from prompt files (offline)."
    )
    p_prepare.add_argument("--prompts-dir", required=True, help="Directory of assembled prompt .txt files.")
    p_prepare.add_argument("--dimension", default="", help="Optional: only prompts for this dimension slug.")
    p_prepare.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    p_prepare.add_argument("--job-name", default="", help="Tag for output filenames (default: dimension or 'all').")
    p_prepare.add_argument("--out-jsonl", default="", help="Output JSONL path (default: under prompts-dir).")
    p_prepare.add_argument("--out-manifest", default="", help="Output manifest path (default: under prompts-dir).")
    p_prepare.set_defaults(func=cmd_prepare)

    p_submit = sub.add_parser("submit", help="Step 2: upload input and create the batch job.")
    _add_common_submit_args(p_submit)
    p_submit.set_defaults(func=cmd_submit)

    p_run = sub.add_parser("run", help="submit -> poll -> fetch, end to end.")
    _add_common_submit_args(p_run)
    p_run.add_argument("--output", required=True, help="Excel output path.")
    p_run.add_argument("--poll-interval", type=int, default=60, help="Seconds between status polls.")
    p_run.set_defaults(func=cmd_run)

    p_status = sub.add_parser("status", help="Print the job status.")
    p_status.add_argument("--job-file", required=True)
    p_status.set_defaults(func=cmd_status)

    p_fetch = sub.add_parser("fetch", help="Download a completed job's output and write Excel.")
    p_fetch.add_argument("--job-file", required=True)
    p_fetch.add_argument("--output", required=True, help="Excel output path.")
    p_fetch.set_defaults(func=cmd_fetch)

    args = parser.parse_args()
    _setup_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
