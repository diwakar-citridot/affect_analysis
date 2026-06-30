"""Console entry point for the AFF layer.

Takes a lived-experience question/expression, runs the field-first pipeline, prints the
full ``AnalyzeResponse`` as JSON, and renders a set of tabular views to the console.

Usage:
    python -m svarupa_affect.cli "I keep hoping things get better, but I'm bracing for it to fall apart."
    python -m svarupa_affect.cli --json-only "..."        # JSON only
    python -m svarupa_affect.cli --json-out out.json "..." # also write JSON to a file
    echo "..." | python -m svarupa_affect.cli              # read from stdin
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from typing import Any

from .application.analyze_affect import AnalyzeResult, build_default_layer
from .application.mappers import to_response
from .domain.enums import LatencyMode
from .domain.models import LayerContext
from .infrastructure.config import Settings
from .infrastructure.kg.dimension_registry import build_dimension_registry
from .infrastructure.logging_config import setup_console_logging

# --------------------------------------------------------------------------------------
# Minimal dependency-free table renderer
# --------------------------------------------------------------------------------------


def _truncate(text: str, width: int) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= width else text[: width - 1] + "…"


def render_table(title: str, headers: list[str], rows: list[list[Any]], max_col: int = 56) -> str:
    str_rows = [[_truncate(str(c), max_col) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def line(left: str, mid: str, right: str, fill: str = "─") -> str:
        return left + mid.join(fill * (w + 2) for w in widths) + right

    def fmt(cells: list[str]) -> str:
        return "│ " + " │ ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " │"

    out = [f"\n\033[1m{title}\033[0m" if sys.stdout.isatty() else f"\n{title}"]
    out.append(line("┌", "┬", "┐"))
    out.append(fmt(headers))
    out.append(line("├", "┼", "┤"))
    out.extend(fmt(r) for r in str_rows)
    out.append(line("└", "┴", "┘"))
    if not str_rows:
        out.insert(-1, fmt(["—"] * len(headers)))
    return "\n".join(out)


# --------------------------------------------------------------------------------------
# Tabular views
# --------------------------------------------------------------------------------------


def _fmt(x: float) -> str:
    return f"{x:+.2f}" if x < 0 else f"{x:.2f}"


def print_tables(result: AnalyzeResult, response=None) -> None:
    pi = result.phenomenology_input
    bg = pi.background_field
    signals = response.signals if response is not None else []

    # 1) Summary
    dom = pi.emotion_hypotheses[0] if pi.emotion_hypotheses else None
    sig_rows = []
    for s in signals:
        top = s.attribute_scores[0].attribute if s.attribute_scores else "—"
        pole = s.state_hint.state if s.state_hint else "—"
        sig_rows.append(
            [
                s.dimension_name,
                top,
                pole,
                _fmt(s.relevance),
                _fmt(s.confidence),
                "yes" if s.abstained else "no",
            ]
        )
    if not signals:
        for s in result.signals:
            top = s.attribute_scores[0].attribute if s.attribute_scores else "—"
            pole = s.state_hint.state if s.state_hint else "—"
            sig_rows.append(
                [
                    f"D{s.dimension_id}",
                    top,
                    pole,
                    _fmt(s.relevance),
                    _fmt(s.confidence),
                    "yes" if s.abstained else "no",
                ]
            )
    summary = [
        ["request_id", pi.request_id],
        ["dominant emotion (hypothesis)", f"{dom.label} ({dom.probability:.2f})" if dom else "—"],
        ["overall confidence", _fmt(pi.uncertainty.overall)],
        ["evidence coverage", _fmt(pi.evidence_summary.coverage)],
        ["experiential patterns", ", ".join(p.type for p in pi.experiential_patterns) or "—"],
        ["dynamics", ", ".join(d for d in {t.pattern for t in pi.trajectory.transitions}) or "—"],
    ]
    print(
        render_table(
            "SUMMARY — affective reconstruction of lived experience",
            ["field", "value"],
            summary,
            max_col=70,
        )
    )

    # 2) Affective field (background / climate)
    field_rows: list[list[Any]] = []
    groups = {
        "core": bg.core,
        "motivation": bg.motivation,
        "regulation": bg.regulation,
        "relational": bg.relational,
        "temporal": bg.temporal,
        "uncertainty": bg.uncertainty,
    }
    for gname, group in groups.items():
        for attr in type(group).model_fields:
            feat = getattr(group, attr)
            field_rows.append([gname, attr, _fmt(feat.value), _fmt(feat.confidence)])
    print(
        render_table(
            "AFFECTIVE FIELD — background climate (hierarchical)",
            ["group", "axis", "value", "confidence"],
            field_rows,
        )
    )

    # 3) Emotion hypotheses
    hyp_rows = [
        [
            h.label,
            _fmt(h.probability),
            h.durability,
            ", ".join(a.value.split(".")[-1] for a in h.supporting_axes),
        ]
        for h in pi.emotion_hypotheses
    ]
    print(
        render_table(
            "EMOTION HYPOTHESES (derived from the field — never primary)",
            ["label", "probability", "durability", "supporting axes"],
            hyp_rows,
        )
    )

    # 4) Experiential patterns
    pat_rows = [
        [
            p.type,
            _fmt(p.strength.value),
            _fmt(p.strength.confidence),
            ", ".join(a.value.split(".")[-1] for a in p.supporting_axes),
        ]
        for p in pi.experiential_patterns
    ]
    print(
        render_table(
            "EXPERIENTIAL PATTERNS (the lived stance)",
            ["pattern", "strength", "confidence", "supporting axes"],
            pat_rows,
        )
    )

    # 5) Appraisal
    ap = pi.appraisal
    ap_rows = [
        [name, _fmt(getattr(ap, name).value), _fmt(getattr(ap, name).confidence)]
        for name in type(ap).model_fields
        if hasattr(getattr(ap, name), "value")
    ]
    print(
        render_table(
            "APPRAISAL PROFILE (why the affect is present)",
            ["dimension", "value", "confidence"],
            ap_rows,
        )
    )

    # 6) Drivers
    drv_rows = [
        [
            d.trigger,
            d.causal_factor or "—",
            d.maintaining_factor or "—",
            d.contextual_factor or "—",
            _fmt(d.confidence),
        ]
        for d in pi.drivers
    ]
    print(
        render_table(
            "AFFECT DRIVERS (recognition-framed)",
            ["trigger", "causal", "maintaining", "contextual", "conf"],
            drv_rows,
        )
    )

    # 7) Interactions
    int_rows = [
        [
            "+".join(i.components),
            "tension" if i.is_tension else "reinforcing",
            _fmt(i.strength),
            i.description,
        ]
        for i in pi.interactions
    ]
    print(
        render_table(
            "AFFECT INTERACTIONS (coexisting affects / tensions)",
            ["components", "kind", "strength", "description"],
            int_rows,
        )
    )

    # 8) Trajectory / dynamics
    traj = pi.trajectory
    tr_rows = [
        [str(i), t.from_label, t.to_label, t.pattern] for i, t in enumerate(traj.transitions)
    ]
    meta = render_table(
        "AFFECT TRAJECTORY — movement across episodes "
        f"(persistence {traj.persistence:.2f}, reversals {traj.reversals}, "
        f"volatility {traj.volatility:.2f})",
        ["#", "from", "to", "pattern"],
        tr_rows,
    )
    print(meta)

    # 9) Dimensional signals (fusion envelope)
    print(
        render_table(
            "DIMENSIONAL SIGNALS (fusion envelope, affinity {2,8,9,22,24})",
            ["dimension", "top attribute", "pole", "relevance", "confidence", "abstained"],
            sig_rows,
        )
    )

    # 10) Uncertainty profile
    unc_rows = [[k, _fmt(v)] for k, v in pi.uncertainty.components.items()]
    unc_rows.append(["OVERALL (derived)", _fmt(pi.uncertainty.overall)])
    print(
        render_table(
            "UNCERTAINTY PROFILE (typed, independent sources)", ["source", "value"], unc_rows
        )
    )


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------


def _read_text(arg_text: str | None) -> str:
    if arg_text:
        return arg_text.strip()
    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            return piped
    try:
        return input("Describe a lived experience: ").strip()
    except EOFError:
        return ""


def main(argv: list[str] | None = None) -> int:
    setup_console_logging()
    parser = argparse.ArgumentParser(
        prog="svarupa-affect",
        description="Multi-Axis Affect (AFF) — field-first affective reconstruction of "
        "lived experience.",
    )
    parser.add_argument("text", nargs="?", help="the lived-experience question/expression")
    parser.add_argument("--json-only", action="store_true", help="print only the JSON output")
    parser.add_argument("--no-tables", action="store_true", help="skip the tabular views")
    parser.add_argument("--json-out", metavar="PATH", help="also write the JSON to a file")
    parser.add_argument("--latency", choices=["fast", "standard", "deep"], default="standard")
    args = parser.parse_args(argv)

    text = _read_text(args.text)
    if not text:
        print("No input provided.", file=sys.stderr)
        return 2

    layer = build_default_layer()
    settings = Settings.load()
    latency = {
        "fast": LatencyMode.FAST,
        "standard": LatencyMode.STANDARD,
        "deep": LatencyMode.DEEP,
    }[args.latency]
    ctx = LayerContext(
        request_id=str(uuid.uuid4()),
        analysis_text=text,
        latency_mode=latency,
        enable_llm_assist=settings.enable_llm_assist,
        force_llm_assist=settings.force_llm_assist,
    )
    result = asyncio.run(layer.analyze_full(ctx))
    registry = build_dimension_registry()
    response = to_response(result, registry)
    response_dict = response.model_dump(mode="json")

    if not args.json_only and not args.no_tables:
        print_tables(result, response)
        print("\n" + ("═" * 80))
        print("JSON OUTPUT")
        print("═" * 80)

    json_str = json.dumps(response_dict, indent=2, ensure_ascii=False)
    print(json_str)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            fh.write(json_str)
        print(f"\n[written to {args.json_out}]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
