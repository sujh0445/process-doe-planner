from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .criteria import evaluate_conditions
from .data_loader import load_experiment_data, validate_data_columns
from .doe_generator import recommend_next_doe_options
from .reporter import render_report, write_report
from .risk_gate import run_risk_gate
from .schemas import DoeRequest, load_request
from .statistics import analyze_responses
from .visualization import write_visualizations


def analyze_experiment(request: DoeRequest, data_path: str | Path) -> dict[str, Any]:
    df = load_experiment_data(data_path)
    risk_gate = run_risk_gate(request, df)
    if risk_gate["state"] == "BLOCK":
        messages = "; ".join(item["message"] for item in risk_gate["findings"] if item["severity"] == "BLOCK")
        raise ValueError(f"Risk gate blocked analysis: {messages}")
    validate_data_columns(df, request)
    response_analysis = analyze_responses(df, request)
    criteria_result = evaluate_conditions(df, request, response_analysis)
    next_doe_options = recommend_next_doe_options(request, criteria_result, response_analysis)
    next_doe = next_doe_options[0]
    return {
        "request": request,
        "data_path": str(data_path),
        "row_count": len(df),
        "risk_gate": risk_gate,
        "response_analysis": response_analysis,
        "criteria_result": criteria_result,
        "next_doe": next_doe,
        "next_doe_options": next_doe_options,
    }


def analyze_from_files(
    request_path: str | Path,
    data_path: str | Path,
    output_path: str | Path | None = None,
    plots_path: str | Path | None = None,
) -> dict[str, Any]:
    request = load_request(request_path)
    result = analyze_experiment(request, data_path)
    if plots_path is not None:
        visualizations = write_visualizations(result, plots_path)
        if output_path is not None:
            report_dir = Path(output_path).parent
            for item in visualizations:
                item["report_path"] = os.path.relpath(item["path"], report_dir)
        else:
            for item in visualizations:
                item["report_path"] = item["path"]
        result["visualizations"] = visualizations
    report = render_report(result)
    result["report_markdown"] = report
    if output_path is not None:
        result["report_path"] = str(write_report(report, output_path))
    return result
