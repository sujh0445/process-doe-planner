from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .criteria import canonical_criterion_role
from .doe_generator import describe_design_plan
from .schemas import DoeRequest


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(_fmt(row.get(column)) for column in columns) + " |")
    return "\n".join([header, sep, *body])


def _capability_ref(row: dict[str, Any]) -> float | None:
    for key in ("cpk", "cpu", "cpl"):
        value = row.get(key)
        if value is not None:
            return value
    return None


def _condition_columns_for_y_type(y_type: str) -> list[str]:
    if y_type in {"continuous", "image-derived"}:
        return [
            "condition",
            "n",
            "mean",
            "mean_ci95",
            "min",
            "max",
            "p05",
            "p95",
            "fail",
            "fail_rate",
            "warning",
            "capability_ref",
            "capability_status",
        ]
    if y_type == "count":
        return ["condition", "n", "sum", "mean", "max", "p95", "fail", "fail_rate", "warning", "warning_rate"]
    if y_type == "binary":
        return ["condition", "n", "positive_rate", "fail", "fail_rate", "warning", "warning_rate"]
    return ["condition", "n", "top_value", "fail", "fail_rate", "warning", "warning_rate", "value_counts"]


def _overall_columns_for_y_type(y_type: str) -> list[str]:
    if y_type in {"continuous", "image-derived"}:
        return [
            "n",
            "mean",
            "std",
            "min",
            "max",
            "p05",
            "p95",
            "mean_ci95_lower",
            "mean_ci95_upper",
            "fail_count",
            "fail_rate",
            "warning_count",
            "warning_rate",
            "capability_ref",
            "capability_status",
            "cpu",
            "cpl",
            "cpk",
        ]
    if y_type == "count":
        return [
            "n",
            "sum",
            "mean",
            "min",
            "max",
            "p95",
            "fail_count",
            "fail_rate",
            "warning_count",
            "warning_rate",
        ]
    if y_type == "binary":
        return ["n", "positive_rate", "fail_count", "fail_rate", "warning_count", "warning_rate"]
    return ["n", "top_value", "fail_count", "fail_rate", "warning_count", "warning_rate", "value_counts"]


def _condition_values_text(values: dict[str, Any]) -> str:
    return ", ".join(f"{key}={_fmt(value)}" for key, value in values.items())


def _factor_context_rows(request: DoeRequest) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    initial_levels = request.constraints.get("initial_screening_levels", {})
    followup_levels = request.constraints.get("followup_exploration_levels", {})
    if isinstance(initial_levels, dict):
        for factor, levels in initial_levels.items():
            rows.append(
                {
                    "scope": "initial screening",
                    "factor": factor,
                    "levels/range": levels,
                    "purpose": "first DOE contrast, not the full equipment limit",
                }
            )
    for factor in request.factors:
        if factor.practical_range is not None:
            rows.append(
                {
                    "scope": "practical follow-up",
                    "factor": factor.column,
                    "levels/range": factor.practical_range,
                    "purpose": "allowed search window after the first evidence review",
                }
            )
    if isinstance(followup_levels, dict):
        for factor, levels in followup_levels.items():
            rows.append(
                {
                    "scope": "observed follow-up",
                    "factor": factor,
                    "levels/range": levels,
                    "purpose": "boundary or trend check used after screening",
                }
            )
    return rows


def _criterion_priority(role: str) -> int:
    canonical_role = canonical_criterion_role(role)
    order = {
        "quality_gate": 1,
        "risk_guardrail": 2,
        "mechanism_consistency": 3,
        "production_objective": 4,
        "measurement_confidence": 5,
    }
    return order.get(canonical_role, 9)


def _criterion_layer(role: str) -> str:
    canonical_role = canonical_criterion_role(role)
    layers = {
        "quality_gate": "hard quality decision",
        "risk_guardrail": "tail-risk guardrail",
        "mechanism_consistency": "process mechanism check",
        "production_objective": "production trade-off",
        "measurement_confidence": "measurement confidence",
    }
    return layers.get(canonical_role, "project-specific criterion")


def _include_pooled_diagnostics(request: DoeRequest) -> bool:
    value = request.constraints.get("include_pooled_diagnostics", False)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _criterion_rows(request: DoeRequest) -> list[dict[str, Any]]:
    rows = [
        {
            "priority": _criterion_priority(criterion.decision_role),
            "decision_layer": _criterion_layer(criterion.decision_role),
            "criterion": criterion.name,
            "role": canonical_criterion_role(criterion.decision_role),
            "source_role": criterion.decision_role,
            "metric": criterion.metric,
            "rule": criterion.pass_rule,
            "next_doe_impact": criterion.next_doe_impact,
        }
        for criterion in request.criteria
    ]
    rows.sort(key=lambda row: row["priority"])
    return rows


def _factor_level_text(factor: Any) -> str:
    unit = f" {factor.unit}" if factor.unit else ""
    if len(factor.levels) >= 2:
        return f"{_fmt(factor.levels[0])} -> {_fmt(factor.levels[-1])}{unit}"
    if factor.practical_range is not None:
        return f"{_fmt(factor.practical_range[0])} -> {_fmt(factor.practical_range[1])}{unit}"
    if factor.low is not None and factor.high is not None:
        return f"{_fmt(factor.low)} -> {_fmt(factor.high)}{unit}"
    return "-"


def _quality_direction_text(response: Any, effect: float | None) -> str:
    if effect is None:
        return "-"
    if response.direction == "lower_is_better":
        if effect < 0:
            return "high level moves Y in the quality-improving direction"
        if effect > 0:
            return "high level moves Y in the quality-risk direction"
    if response.direction == "higher_is_better":
        if effect > 0:
            return "high level moves Y in the quality-improving direction"
        if effect < 0:
            return "high level moves Y in the quality-risk direction"
    return "little directional change"


def _process_mechanism_rows(request: DoeRequest, response_analysis: dict[str, Any]) -> list[dict[str, Any]]:
    factors = {factor.column: factor for factor in request.factors}
    rows: list[dict[str, Any]] = []
    for response_name, analysis in response_analysis.items():
        response = analysis["response"]
        for effect in analysis["effects"]:
            if effect["kind"] != "main":
                continue
            factor = factors.get(effect["term"])
            if factor is None:
                continue
            rows.append(
                {
                    "response": response_name,
                    "factor": factor.column,
                    "levels": _factor_level_text(factor),
                    "effect": effect["effect"],
                    "quality_direction": _quality_direction_text(response, effect.get("effect")),
                    "mechanism_note": factor.mechanism_note or "-",
                }
            )
    return rows


def _interaction_mechanism_rows(response_analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for response_name, analysis in response_analysis.items():
        interactions = [item for item in analysis["effects"] if item["kind"] == "interaction"]
        interactions.sort(key=lambda item: abs(float(item.get("effect", 0.0))), reverse=True)
        for effect in interactions[:3]:
            rows.append(
                {
                    "response": response_name,
                    "interaction": effect["term"],
                    "effect": effect["effect"],
                    "relative_effect_weight": effect["relative_effect_weight"],
                    "interpretation": "review before separating main-effect-only conclusions",
                }
            )
    return rows


def _production_interpretation_rows(request: DoeRequest, criteria_result: dict[str, Any]) -> list[dict[str, Any]]:
    production_factor = request.production_factor
    best_condition = criteria_result.get("best_condition")
    if production_factor is None or best_condition is None:
        return []
    current_value = best_condition.condition_values.get(production_factor.column)
    return [
        {
            "item": "production factor",
            "interpretation": production_factor.column,
            "evidence": f"desired direction={production_factor.production_direction}, selected value={_fmt(current_value)}",
        },
        {
            "item": "selected condition",
            "interpretation": best_condition.condition,
            "evidence": (
                f"state={best_condition.state}, quality={_fmt(best_condition.quality_score)}, "
                f"tail={_fmt(best_condition.tail_risk_score)}, measurement={_fmt(best_condition.measurement_score)}, "
                f"mechanism={_fmt(best_condition.mechanism_score)}, production={_fmt(best_condition.production_score)}, "
                f"total={_fmt(best_condition.total_score)}"
            ),
        },
        {
            "item": "DOE steering rule",
            "interpretation": "production is optimized only inside the quality/risk guardrail",
            "evidence": "candidate feed or throughput gains are rejected or held if tail risk, worst case, or spec margin is weak",
        },
    ]


def render_report(result: dict[str, Any]) -> str:
    request: DoeRequest = result["request"]
    response_analysis: dict[str, Any] = result["response_analysis"]
    criteria_result: dict[str, Any] = result["criteria_result"]
    next_doe: dict[str, Any] = result["next_doe"]
    next_doe_options: list[dict[str, Any]] = result.get("next_doe_options") or [next_doe]
    risk_gate: dict[str, Any] = result.get("risk_gate", {"state": "PASS", "findings": []})
    visualizations: list[dict[str, str]] = result.get("visualizations", [])

    lines: list[str] = []
    project_name = request.project.get("name", "DOE Project")
    lines.append(f"# {project_name} DOE Analysis Report")
    lines.append("")
    lines.append("## 1. DOE Round Summary")
    lines.append("")
    lines.append(f"- Process area: {request.project.get('process_area', '-')}")
    lines.append(f"- Equipment: {request.project.get('equipment', '-')}")
    lines.append(f"- Primary goal: {request.objective.get('primary_goal', '-')}")
    lines.append(f"- Business goal: {request.objective.get('business_goal', '-')}")
    lines.append(f"- Decision mode: {request.objective.get('decision_mode', '-')}")
    lines.append("")

    lines.append("## 2. Validation and Risk Gate")
    lines.append("")
    lines.append(f"- Gate state: {risk_gate['state']}")
    if risk_gate["findings"]:
        lines.append(
            _md_table(
                risk_gate["findings"],
                ["severity", "code", "message"],
            )
        )
    else:
        lines.append("- No validation or risk-gate findings.")
    lines.append("")

    lines.append("## 3. X/Y Definition")
    lines.append("")
    factor_rows = [
        {
            "factor": factor.column,
            "name": factor.name,
            "unit": factor.unit,
            "role": factor.role,
            "range/levels": factor.levels or factor.practical_range or [factor.low, factor.high],
        }
        for factor in request.factors
    ]
    lines.append(_md_table(factor_rows, ["factor", "name", "unit", "role", "range/levels"]))
    lines.append("")
    factor_context_rows = _factor_context_rows(request)
    if factor_context_rows:
        lines.append("Factor level context:")
        lines.append("")
        lines.append(_md_table(factor_context_rows, ["scope", "factor", "levels/range", "purpose"]))
        lines.append("")
    response_rows = [
        {
            "response": response.column,
            "type": response.y_type,
            "role": response.role,
            "direction": response.direction,
            "spec": f"LSL={response.spec.lower}, USL={response.spec.upper}",
        }
        for response in request.responses
    ]
    lines.append(_md_table(response_rows, ["response", "type", "role", "direction", "spec"]))
    lines.append("")

    design_plan = describe_design_plan(request)
    lines.append("Design generation logic:")
    lines.append("")
    design_rows = [
        {
            "requested": design_plan["requested_design_type"],
            "selected": design_plan["selected_design_type"],
            "factor_count": design_plan["factor_count"],
            "full_runs": design_plan["full_factorial_runs"],
            "selected_runs": design_plan["selected_runs"],
            "max_runs": design_plan["max_runs"],
            "rationale": design_plan["rationale"],
        }
    ]
    lines.append(
        _md_table(
            design_rows,
            ["requested", "selected", "factor_count", "full_runs", "selected_runs", "max_runs", "rationale"],
        )
    )
    if design_plan.get("alias_structure"):
        lines.append(f"- Alias structure: {design_plan['alias_structure']}")
    for warning in design_plan.get("warnings", []):
        lines.append(f"- Design warning: {warning}")
    for rejected in design_plan.get("rejected_alternatives", []):
        lines.append(f"- Rejected alternative: {rejected['design_type']} because {rejected['reason']}.")
    lines.append("")

    lines.append("## 4. Y-Type and Analysis Method")
    lines.append("")
    lines.append(
        "Analysis is selected by response type and DOE purpose. The project criteria decide what matters first; "
        "statistics are used as reproducible evidence for those criteria. Condition-level evidence drives the decision, "
        "while round-level pooled statistics are optional diagnostic context because they mix different process settings."
    )
    lines.append("")
    for response in request.responses:
        analysis = response_analysis[response.name]
        policy = analysis["analysis_policy"]
        lines.append(f"### {response.name}")
        lines.append("")
        lines.append(
            f"- Selection basis: Y type `{response.y_type}`, spec `{policy['spec_profile']}`, "
            f"DOE stage `{policy['analysis_stage']}`, design `{policy['design_type']}`."
        )
        lines.append(f"- Decision metrics: {', '.join(policy['decision_metrics'])}")
        lines.append(f"- Interaction policy: `{policy['interaction_policy']}`")
        lines.append(f"- Capability policy: `{policy['capability_policy']}`")
        selected_rows = policy.get("selected_methods", [])
        skipped_rows = policy.get("skipped_methods", [])
        lines.append("- Selected methods:")
        lines.append(_md_table(selected_rows, ["method", "reason"]))
        if skipped_rows:
            lines.append("- Intentionally skipped methods:")
            lines.append(_md_table(skipped_rows, ["method", "reason"]))
        lines.append("")
    lines.append("")

    criterion_rows = _criterion_rows(request)
    if criterion_rows:
        lines.append("Project decision profile:")
        lines.append("")
        lines.append(
            "- These criteria come from the request file, process objective, Y type, specs, measurement method, and mechanism notes."
        )
        lines.append(
            "- Do not reuse these exact criteria for another DOE unless that project's objective and failure mode are the same."
        )
        lines.append("- Statistics below are evidence for these criteria, not the criteria themselves.")
        lines.append("")
        lines.append(
            _md_table(
                criterion_rows,
                ["priority", "decision_layer", "criterion", "role", "metric", "rule", "next_doe_impact"],
            )
        )
        lines.append("")

    lines.append("## 5. Condition-Level Response Analysis")
    lines.append("")
    for response_name, analysis in response_analysis.items():
        response = analysis["response"]
        lines.append(f"### {response_name}")
        lines.append("")
        condition_rows = []
        for row in analysis["by_condition"]:
            ci_lower = row.get("mean_ci95_lower")
            ci_upper = row.get("mean_ci95_upper")
            condition_rows.append(
                {
                    "condition": row["condition"],
                    "n": row.get("n"),
                    "sum": row.get("sum"),
                    "mean": row.get("mean"),
                    "mean_ci95": (
                        f"[{_fmt(ci_lower)}, {_fmt(ci_upper)}]"
                        if ci_lower is not None and ci_upper is not None
                        else None
                    ),
                    "min": row.get("min"),
                    "max": row.get("max"),
                    "p05": row.get("p05"),
                    "p95": row.get("p95"),
                    "fail": row.get("fail_count"),
                    "fail_rate": row.get("fail_rate"),
                    "warning": row.get("warning_count"),
                    "warning_rate": row.get("warning_rate"),
                    "capability_ref": _capability_ref(row),
                    "capability_status": row.get("capability_status"),
                    "positive_rate": row.get("positive_rate"),
                    "top_value": row.get("top_value"),
                    "value_counts": row.get("value_counts"),
                }
            )
        lines.append("Primary decision evidence by condition:")
        if response.y_type in {"continuous", "image-derived"}:
            lines.append(
                "- Capability is shown as a reference only; it is a sample-size-gated capability reference unless "
                "the same condition has enough repeated, representative measurements and the process is stable."
            )
        lines.append(_md_table(condition_rows, _condition_columns_for_y_type(response.y_type)))
        lines.append("")
        overall = analysis["overall"]
        overall_columns = _overall_columns_for_y_type(response.y_type)
        overall_row = {key: overall.get(key) for key in overall_columns if key in overall}
        if response.y_type in {"continuous", "image-derived"}:
            overall_row["capability_ref"] = _capability_ref(overall)
            if overall.get("capability_status") is not None:
                overall_row["capability_status"] = "pooled_diagnostic_not_formal"
        lines.append("Round-level diagnostic summary:")
        lines.append("")
        if _include_pooled_diagnostics(request):
            lines.append(
                "- This pooled summary is not the main DOE decision basis because it combines multiple factor settings."
            )
            if response.y_type in {"continuous", "image-derived"}:
                lines.append(
                    "- Pooled capability is not a formal capability claim even when pooled n is large, because it mixes different process conditions."
                )
            if response.y_type in {"continuous", "image-derived"} and overall.get("capability_note"):
                lines.append(f"- Capability note: {overall['capability_note']}")
            lines.append(_md_table([overall_row], list(overall_row.keys())))
        else:
            lines.append(
                "- Omitted by project criteria. This DOE uses condition-level criteria as the decision basis."
            )
            lines.append(
                "- Set `constraints.include_pooled_diagnostics: true` only when a pooled round-level diagnostic is useful for the current project."
            )
        lines.append("")
        policy = analysis["analysis_policy"]
        effect_rows = [
            {
                "term": item["term"],
                "kind": item["kind"],
                "effect": item["effect"],
                "relative_effect_weight": item["relative_effect_weight"],
                "basis": item["contribution_basis"],
            }
            for item in analysis["effects"][:8]
        ]
        if effect_rows:
            lines.append("Factor/effect evidence (modeled effects only, error not included):")
            lines.append(_md_table(effect_rows, ["term", "kind", "effect", "relative_effect_weight", "basis"]))
            lines.append(
                "- These weights rank modeled main/interaction effects only; use the ANOVA table below for residual/error-inclusive contribution."
            )
            if policy["interaction_policy"] == "main_effects_only_alias_aware":
                lines.append(
                    "- Pairwise interactions are not listed because this fractional design aliases them with other effects."
                )
        else:
            lines.append(
                f"Factor/effect evidence: intentionally not used as primary evidence in the "
                f"`{policy['analysis_stage']}` stage."
            )
        lines.append("")

        anova_rows = [
            {
                "term": item["term"],
                "kind": item["term_kind"],
                "scope": item["model_scope"],
                "df": item["df"],
                "sum_sq": item["sum_sq"],
                "mean_sq": item["mean_sq"],
                "F": item["F"],
                "p_value": item["p_value"],
                "contribution": item["contribution_ratio"],
            }
            for item in analysis["anova"]
        ]
        if anova_rows:
            lines.append("ANOVA evidence (residual/error included):")
            lines.append(
                _md_table(
                    anova_rows,
                    ["term", "kind", "scope", "df", "sum_sq", "mean_sq", "F", "p_value", "contribution"],
                )
            )
            lines.append(
                "- Residual/Error captures within-condition, sampling, measurement, and unmodeled variation; small DOE p-values remain exploratory."
            )
        elif policy["run_anova"]:
            lines.append(
                "ANOVA evidence: the requested model was not estimable with the available replication/degrees of freedom."
            )
        else:
            lines.append(
                f"ANOVA evidence: intentionally not primary for the `{policy['analysis_stage']}` stage."
            )
        lines.append("")

        trend_rows = analysis.get("trend", [])
        if trend_rows:
            lines.append("Trend/refinement evidence:")
            lines.append(
                _md_table(
                    trend_rows,
                    [
                        "factor",
                        "levels",
                        "n",
                        "pearson_r",
                        "pearson_p",
                        "spearman_r",
                        "spearman_p",
                        "regression_slope",
                        "regression_r_squared",
                        "one_way_anova_p",
                        "kruskal_p",
                        "boundary_levels",
                        "boundary_welch_p",
                    ],
                )
            )
            lines.append("")

        confirmation = analysis.get("confirmation", {})
        if confirmation:
            lines.append("Confirmation evidence:")
            lines.append(_md_table([confirmation], list(confirmation.keys())))
            lines.append("")

        response_visuals = [item for item in visualizations if item.get("response") == response_name]
        if response_visuals:
            lines.append("Visual evidence:")
            for visual in response_visuals:
                label = visual["kind"].replace("_", " ").title()
                path = visual.get("report_path", visual["path"])
                lines.append(f"![{response_name} {label}]({path})")
            lines.append("")

    lines.append("## 6. Decision Criteria Evaluation")
    lines.append("")
    lines.append(
        "Condition state is decided by explicit project criteria first: quality gate, tail risk, measurement confidence, "
        "mechanism consistency, then production trade-off inside the accepted quality window."
    )
    lines.append("")
    decision_rows = []
    evidence_rows = []
    for decision in criteria_result["condition_decisions"]:
        decision_rows.append(
            {
                "condition": decision.condition,
                "state": decision.state,
                "quality": decision.quality_score,
                "tail_risk": decision.tail_risk_score,
                "measurement": decision.measurement_score,
                "mechanism": decision.mechanism_score,
                "production": decision.production_score,
                "total": decision.total_score,
                "reason": "; ".join(decision.reasons[:2]),
            }
        )
        for item in decision.criteria_evidence:
            evidence_rows.append(
                {
                    "condition": decision.condition,
                    "criterion": item.get("criterion"),
                    "role": item.get("role"),
                    "score": item.get("score"),
                    "state": item.get("state"),
                    "evidence": item.get("evidence"),
                }
            )
    lines.append(
        _md_table(
            decision_rows,
            ["condition", "state", "quality", "tail_risk", "measurement", "mechanism", "production", "total", "reason"],
        )
    )
    lines.append("")
    if evidence_rows:
        lines.append("Criterion-by-criterion evidence:")
        lines.append("")
        lines.append(_md_table(evidence_rows, ["condition", "criterion", "role", "score", "state", "evidence"]))
    lines.append("")

    lines.append("## 7. Bottleneck Y Decision")
    lines.append("")
    bottleneck = criteria_result.get("bottleneck_y")
    if bottleneck:
        lines.append(f"- Bottleneck response: {bottleneck['response']}")
        lines.append(f"- Fail count: {bottleneck['fail_count']}")
        lines.append(f"- Weakest margin: {_fmt(bottleneck['weakest_margin'])}")
    else:
        lines.append("- No bottleneck response was identified.")
    lines.append("")

    lines.append("## 8. Process and Production Interpretation")
    lines.append("")
    lines.append("### Process mechanism evidence")
    lines.append("")
    if request.mechanism_hypotheses:
        for hypothesis in request.mechanism_hypotheses:
            lines.append(f"- Mechanism hypothesis: {hypothesis}")
    else:
        lines.append("- No mechanism hypotheses were provided in the request.")
    lines.append("")
    mechanism_rows = _process_mechanism_rows(request, response_analysis)
    if mechanism_rows:
        lines.append(_md_table(mechanism_rows, ["response", "factor", "levels", "effect", "quality_direction", "mechanism_note"]))
        lines.append("")
    interaction_rows = _interaction_mechanism_rows(response_analysis)
    if interaction_rows:
        lines.append("Interaction check:")
        lines.append("")
        lines.append(_md_table(interaction_rows, ["response", "interaction", "effect", "relative_effect_weight", "interpretation"]))
        lines.append(
            "- Interaction evidence is used as a guardrail. Strong or mechanism-critical interactions should trigger confirmation or focused follow-up before broad optimization."
        )
        lines.append("")

    lines.append("### Production interpretation")
    lines.append("")
    if request.production_factor is not None:
        production_rows = _production_interpretation_rows(request, criteria_result)
        lines.append(_md_table(production_rows, ["item", "interpretation", "evidence"]))
    else:
        lines.append("- No production trade-off factor was provided.")
    lines.append("")
    if factor_context_rows:
        lines.append("Level strategy note:")
        lines.append("")
        lines.append(
            "- Initial low/high levels are screening contrasts. Follow-up levels can move outside the first low/high pair when the decision criteria require boundary, productivity, or confirmation evidence."
        )
    lines.append("")

    lines.append("## 9. Next DOE Recommendation")
    lines.append("")
    lines.append(f"- Primary mode: {next_doe['mode']}")
    lines.append(f"- Primary rationale: {next_doe['rationale']}")
    lines.append("")
    lines.append("Recommendation options:")
    lines.append("")
    for index, option in enumerate(next_doe_options, start=1):
        title = option.get("title", option["mode"])
        lines.append(f"### Option {index}. {title}")
        lines.append("")
        lines.append(f"- Mode: {option['mode']}")
        lines.append(f"- Priority: {option.get('priority', index)}")
        lines.append(f"- Rationale: {option['rationale']}")
        if option.get("decision_basis"):
            lines.append("- Decision basis:")
            for basis in option["decision_basis"]:
                lines.append(f"  - {basis}")
        table = option["table"]
        if isinstance(table, pd.DataFrame) and not table.empty:
            lines.append("")
            lines.append(_md_table(table.to_dict("records"), list(table.columns)))
        lines.append("")
    lines.append("")

    lines.append("## 10. Remaining Risk")
    lines.append("")
    lines.append("- This MVP report treats small-sample statistics as exploratory evidence.")
    lines.append("- Capability indices are screening references when condition n is below 33 or sampling is not representative.")
    lines.append("- Project criteria must be regenerated for each DOE objective; reuse the framework, not another project's thresholds.")
    lines.append("- Measurement confidence, sampling method, and process transfer risk must be reviewed by an engineer.")
    lines.append("- The recommendation is a candidate next DOE direction, not a production-release decision.")
    lines.append("")
    return "\n".join(lines)


def write_report(markdown: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path
