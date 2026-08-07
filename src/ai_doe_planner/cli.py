from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from .data_loader import load_experiment_data
from .doe_generator import describe_design_plan, generate_design
from .engine import analyze_from_files
from .risk_gate import run_risk_gate
from .schemas import load_request


def _format_gate_report(gate: dict) -> str:
    lines = [
        "Validation / risk gate:",
        f"- state: {gate['state']}",
        f"- human_review_required: {gate.get('human_review_required', False)}",
    ]
    if gate.get("blocking_reasons"):
        lines.append("- blocking reasons:")
        lines.extend(f"  - {reason}" for reason in gate["blocking_reasons"])
    if gate.get("review_reasons"):
        lines.append("- review reasons:")
        lines.extend(f"  - {reason}" for reason in gate["review_reasons"])
    if gate.get("missing_fields"):
        lines.append("- missing fields:")
        lines.extend(f"  - {field}" for field in gate["missing_fields"])
    if gate.get("recommended_questions"):
        lines.append("- recommended questions:")
        lines.extend(f"  - {question}" for question in gate["recommended_questions"])
    return "\n".join(lines)


def _validate(args: argparse.Namespace) -> None:
    request = load_request(args.request)
    df = load_experiment_data(args.data) if args.data else None
    gate = run_risk_gate(request, df)
    if args.json:
        print(json.dumps(gate, ensure_ascii=False, indent=2))
    else:
        print(_format_gate_report(gate))

    if gate["state"] == "BLOCK":
        raise SystemExit(2)
    if args.strict and gate["state"] == "HOLD":
        raise SystemExit(1)


def _analyze(args: argparse.Namespace) -> None:
    result = analyze_from_files(args.request, args.data, args.out, args.plots_out)
    report_path = result.get("report_path")
    if report_path:
        print(f"Wrote report: {report_path}")
    else:
        print(result["report_markdown"])
    if args.plots_out:
        print(f"Wrote plots: {args.plots_out}")

    next_out = args.next_doe_out
    if next_out:
        table = result["next_doe"]["table"]
        Path(next_out).parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(next_out, index=False)
        print(f"Wrote next DOE table: {next_out}")


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "option"


def _option_to_jsonable(option: dict) -> dict:
    table = option.get("table")
    payload = {key: value for key, value in option.items() if key != "table"}
    if hasattr(table, "to_dict"):
        payload["table"] = table.to_dict("records")
    else:
        payload["table"] = []
    return payload


def _print_recommendation_summary(options: list[dict]) -> None:
    print("Next DOE recommendation options:")
    for index, option in enumerate(options, start=1):
        print(f"\nOption {index}. {option.get('title', option['mode'])}")
        print(f"- mode: {option['mode']}")
        print(f"- priority: {option.get('priority', index)}")
        print(f"- rationale: {option['rationale']}")
        if option.get("decision_basis"):
            print("- decision basis:")
            for basis in option["decision_basis"]:
                print(f"  - {basis}")
        table = option.get("table")
        if hasattr(table, "to_csv") and not table.empty:
            print("")
            print(table.to_csv(index=False).strip())


def _write_recommendation_tables(
    options: list[dict],
    out_dir: str | None,
    primary_out: str | None,
    stream=sys.stdout,
) -> None:
    if primary_out:
        Path(primary_out).parent.mkdir(parents=True, exist_ok=True)
        options[0]["table"].to_csv(primary_out, index=False)
        print(f"Wrote primary next DOE table: {primary_out}", file=stream)

    if out_dir:
        directory = Path(out_dir)
        directory.mkdir(parents=True, exist_ok=True)
        for index, option in enumerate(options, start=1):
            table = option.get("table")
            if not hasattr(table, "to_csv"):
                continue
            mode = _safe_filename(str(option.get("mode", f"option_{index}")))
            path = directory / f"{index:02d}_{mode}.csv"
            table.to_csv(path, index=False)
            print(f"Wrote recommendation option {index}: {path}", file=stream)


def _recommend(args: argparse.Namespace) -> None:
    result = analyze_from_files(args.request, args.data)
    options = result["next_doe_options"]

    if args.json:
        print(json.dumps([_option_to_jsonable(option) for option in options], ensure_ascii=False, indent=2))
    else:
        _print_recommendation_summary(options)

    _write_recommendation_tables(
        options,
        args.out_dir,
        args.primary_out,
        stream=sys.stderr if args.json else sys.stdout,
    )


def _report(args: argparse.Namespace) -> None:
    result = analyze_from_files(args.request, args.data, args.out, args.plots_out)
    print(f"Wrote report: {result['report_path']}")
    if args.next_doe_out:
        table = result["next_doe"]["table"]
        Path(args.next_doe_out).parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(args.next_doe_out, index=False)
        print(f"Wrote primary next DOE table: {args.next_doe_out}")
    if args.recommendations_out_dir:
        _write_recommendation_tables(result["next_doe_options"], args.recommendations_out_dir, None)
    if args.plots_out:
        print(f"Wrote plots: {args.plots_out}")


def _design(args: argparse.Namespace) -> None:
    request = load_request(args.request)
    gate = run_risk_gate(request)
    if gate["state"] == "BLOCK":
        print(_format_gate_report(gate), file=sys.stderr)
        raise SystemExit(2)
    if gate["state"] == "HOLD":
        print(_format_gate_report(gate), file=sys.stderr)
        if not args.allow_hold:
            print(
                "DOE generation stopped because the request is HOLD. "
                "Use --allow-hold only when you intentionally want a review-marked draft.",
                file=sys.stderr,
            )
            raise SystemExit(1)

    plan = describe_design_plan(request)
    table = generate_design(request)
    if args.explain:
        summary_lines = [
            "Validation / risk gate:",
            f"- state: {gate['state']}",
            "",
            "Design selection:",
            f"- requested: {plan['requested_design_type']}",
            f"- selected: {plan['selected_design_type']}",
            f"- full factorial runs: {plan['full_factorial_runs']}",
            f"- selected runs: {plan['selected_runs']}",
            f"- max_runs: {plan['max_runs']}",
            f"- rationale: {plan['rationale']}",
        ]
        if plan.get("alias_structure"):
            summary_lines.append(f"- alias structure: {plan['alias_structure']}")
        for warning in plan.get("warnings", []):
            summary_lines.append(f"- warning: {warning}")
        stream = sys.stdout if args.out else sys.stderr
        print("\n".join(summary_lines), file=stream)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(args.out, index=False)
        print(f"Wrote DOE table: {args.out}")
    else:
        print(table.to_csv(index=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-doe", description="AI DOE Planner MVP CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a DOE request and optional data before analysis/design.")
    validate.add_argument("--request", required=True, help="Path to request YAML/JSON.")
    validate.add_argument("--data", required=False, help="Optional result CSV/XLSX to validate against the request.")
    validate.add_argument("--json", action="store_true", help="Print the full gate result as JSON.")
    validate.add_argument("--strict", action="store_true", help="Exit nonzero for HOLD as well as BLOCK.")
    validate.set_defaults(func=_validate)

    analyze = subparsers.add_parser("analyze", help="Analyze experiment results and recommend a next DOE.")
    analyze.add_argument("--request", required=True, help="Path to request YAML/JSON.")
    analyze.add_argument("--data", required=True, help="Path to result CSV/XLSX.")
    analyze.add_argument("--out", required=False, help="Path to write Markdown report.")
    analyze.add_argument("--next-doe-out", required=False, help="Optional path to write next DOE CSV.")
    analyze.add_argument("--plots-out", required=False, help="Optional directory to write evidence plots.")
    analyze.set_defaults(func=_analyze)

    recommend = subparsers.add_parser("recommend", help="Analyze results and print/write multiple next DOE options.")
    recommend.add_argument("--request", required=True, help="Path to request YAML/JSON.")
    recommend.add_argument("--data", required=True, help="Path to result CSV/XLSX.")
    recommend.add_argument("--primary-out", required=False, help="Optional path to write the primary next DOE CSV.")
    recommend.add_argument("--out-dir", required=False, help="Optional directory to write every recommendation option as CSV.")
    recommend.add_argument("--json", action="store_true", help="Print recommendation options as JSON.")
    recommend.set_defaults(func=_recommend)

    report = subparsers.add_parser("report", help="Generate the full Markdown analysis report.")
    report.add_argument("--request", required=True, help="Path to request YAML/JSON.")
    report.add_argument("--data", required=True, help="Path to result CSV/XLSX.")
    report.add_argument("--out", required=True, help="Path to write Markdown report.")
    report.add_argument("--next-doe-out", required=False, help="Optional path to write the primary next DOE CSV.")
    report.add_argument(
        "--recommendations-out-dir",
        required=False,
        help="Optional directory to write every recommendation option as CSV.",
    )
    report.add_argument("--plots-out", required=False, help="Optional directory to write evidence plots.")
    report.set_defaults(func=_report)

    design = subparsers.add_parser("design", help="Generate a DOE design table from request factors.")
    design.add_argument("--request", required=True, help="Path to request YAML/JSON.")
    design.add_argument("--out", required=False, help="Path to write DOE CSV.")
    design.add_argument("--explain", action="store_true", help="Print why the selected DOE design was chosen.")
    design.add_argument(
        "--allow-hold",
        action="store_true",
        help="Generate a review-marked DOE draft even when the validation gate is HOLD.",
    )
    design.set_defaults(func=_design)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
