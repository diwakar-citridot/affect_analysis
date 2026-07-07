#!/usr/bin/env python3
"""Bulk-run passages through the AFF v2 LLM-primary API (``POST /v2/analyze``).

Reads an input file, sends one request per passage (concurrently), and writes a
JSONL where each line is ``{id, analysis_text, ok, http_status, latency_s,
abstained_dimensions, attribute_scores, error}``. Input order is preserved.

Input formats (auto-detected by extension):
  .jsonl : one JSON object per line; text taken from analysis_text|text|question
  .csv   : rows; text column via --text-col (default "text"); id via --id-col
  .txt   : one passage per line (blank lines skipped)

Examples:
  # start the API first:  bash scripts/run_api.sh   (needs AWS creds for Bedrock)
  .venv/bin/python scripts/bulk_analyze.py --input questions.txt --output results.jsonl
  .venv/bin/python scripts/bulk_analyze.py --input data.jsonl --concurrency 6 --latency deep --force
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


def load_inputs(path: Path, text_col: str, id_col: str) -> list[dict]:
    """Return [{id, analysis_text}] from .jsonl / .csv / .txt."""
    rows: list[dict] = []
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            text = obj.get("analysis_text") or obj.get("text") or obj.get("question")
            if not text:
                continue
            # preserve extra fields (e.g. expected_* labels) so results are self-scoring
            rec = {k: v for k, v in obj.items() if k not in ("analysis_text", "text", "question")}
            rec["id"] = obj.get("id", obj.get(id_col, i))
            rec["analysis_text"] = text
            rows.append(rec)
    elif suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as fh:
            for i, r in enumerate(csv.DictReader(fh)):
                text = r.get(text_col)
                if not text or not text.strip():
                    continue
                rows.append({"id": r.get(id_col, i), "analysis_text": text.strip()})
    else:  # .txt — one passage per line
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if line.strip():
                rows.append({"id": i, "analysis_text": line.strip()})
    return rows


def analyze_one(
    session: requests.Session, url: str, row: dict, *, latency: str, force: bool, timeout: float
) -> dict:
    body = {
        "analysis_text": row["analysis_text"],
        # LatencyMode enum values are lowercase ("standard"/"deep").
        "options": {"latency_mode": latency.lower(), "force": force},
    }
    out: dict = dict(row)  # carry id, analysis_text, and any expected_* labels through
    t0 = time.monotonic()
    try:
        resp = session.post(url, json=body, timeout=timeout)
        out["http_status"] = resp.status_code
        out["latency_s"] = round(time.monotonic() - t0, 2)
        if resp.status_code == 200:
            data = resp.json()
            out["ok"] = True
            out["abstained_dimensions"] = data.get("abstained_dimensions", [])
            out["attribute_scores"] = data.get("attribute_scores", [])
            usage = data.get("usage") or {}
            out["input_tokens"] = usage.get("input_tokens")
            out["output_tokens"] = usage.get("output_tokens")
            out["cache_read_input_tokens"] = usage.get("cache_read_input_tokens")
            out["cache_creation_input_tokens"] = usage.get("cache_creation_input_tokens")
            out["response"] = data  # full payload for downstream analysis
        else:
            out["ok"] = False
            out["error"] = resp.text[:500]
    except Exception as exc:  # network / timeout / JSON errors
        out["ok"] = False
        out["latency_s"] = round(time.monotonic() - t0, 2)
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", type=Path, default=Path("bulk_results.jsonl"))
    ap.add_argument("--base-url", default="http://localhost:8000")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--latency", choices=["standard", "deep"], default="standard")
    ap.add_argument("--force", action="store_true", help="bypass the salience gate")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--text-col", default="text", help="CSV text column")
    ap.add_argument("--id-col", default="id", help="CSV/JSONL id column")
    args = ap.parse_args()

    rows = load_inputs(args.input, args.text_col, args.id_col)
    if not rows:
        print(f"No passages found in {args.input}", file=sys.stderr)
        return 1
    url = args.base_url.rstrip("/") + "/v2/analyze"
    print(f"Analyzing {len(rows)} passage(s) -> {url}  (concurrency={args.concurrency}, "
          f"latency={args.latency}, force={args.force})", file=sys.stderr)

    session = requests.Session()
    results: list[dict | None] = [None] * len(rows)
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(
                analyze_one, session, url, row,
                latency=args.latency, force=args.force, timeout=args.timeout,
            ): idx
            for idx, row in enumerate(rows)
        }
        done = 0
        for fut in as_completed(futures):
            idx = futures[fut]
            results[idx] = fut.result()
            done += 1
            if done % 10 == 0 or done == len(rows):
                print(f"  {done}/{len(rows)} done", file=sys.stderr)

    with args.output.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    ok = sum(1 for r in results if r and r.get("ok"))
    abstained = sum(1 for r in results if r and r.get("abstained_dimensions"))
    errors = sum(1 for r in results if r and not r.get("ok"))
    print(f"\nDone. ok={ok}  with-abstention={abstained}  errors={errors}  -> {args.output}",
          file=sys.stderr)
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
