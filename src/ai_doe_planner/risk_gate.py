from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .schemas import DoeRequest, Factor, Response


SUPPORTED_Y_TYPES = {"continuous", "image-derived", "count", "binary", "categorical", "category", "class"}
QUALITY_ROLES = {"primary_quality_y", "secondary_quality_y", "quality_y", "guardrail_y"}
CONTINUOUS_LIKE_Y_TYPES = {"continuous", "image-derived", "count"}
SUPPORTED_DIRECTIONS = {"lower_is_better", "higher_is_better", "target_is_best", "nominal_is_best"}


@dataclass(frozen=True)
class GateFinding:
    severity: str
    code: str
    message: str
    field: str = ""
    fix: str = ""
    question: str = ""


def _has_hard_decision_definition(response: Response) -> bool:
    if response.spec.lower is not None or response.spec.upper is not None:
        return True
    return bool(response.fail_values or response.pass_values)


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _as_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _add_finding(
    findings: list[GateFinding],
    severity: str,
    code: str,
    message: str,
    *,
    field: str = "",
    fix: str = "",
    question: str = "",
) -> None:
    findings.append(GateFinding(severity, code, message, field, fix, question))


def _has_usable_factor_space(factor: Factor) -> bool:
    if factor.levels:
        return True
    if factor.low is not None and factor.high is not None:
        return True
    if factor.practical_range is not None:
        return True
    return factor.current is not None


def _validate_numeric_range(
    findings: list[GateFinding],
    *,
    low: Any,
    high: Any,
    field: str,
    label: str,
) -> None:
    low_float = _as_float(low)
    high_float = _as_float(high)
    if low_float is not None and high_float is not None and low_float >= high_float:
        _add_finding(
            findings,
            "BLOCK",
            "invalid_range_order",
            f"{label} has low >= high ({low} >= {high}).",
            field=field,
            fix="Set the lower bound below the upper bound before DOE generation.",
            question=f"What is the approved low/high range for {label}?",
        )


def _factor_space_entry(factor: Factor) -> dict[str, Any]:
    if factor.levels:
        candidate_levels = list(factor.levels)
    elif factor.low is not None and factor.high is not None:
        candidate_levels = [factor.low, factor.high]
    elif factor.practical_range is not None:
        candidate_levels = [factor.practical_range[0], factor.practical_range[1]]
    elif factor.current is not None:
        candidate_levels = [factor.current]
    else:
        candidate_levels = []

    return {
        "name": factor.name,
        "column": factor.column,
        "unit": factor.unit,
        "role": factor.role,
        "controllable": factor.controllable,
        "current": factor.current,
        "levels": candidate_levels,
        "practical_range": list(factor.practical_range) if factor.practical_range is not None else None,
    }


def _summarize_findings(findings: list[GateFinding]) -> dict[str, Any]:
    return {
        "blocking_reasons": [finding.message for finding in findings if finding.severity == "BLOCK"],
        "review_reasons": [finding.message for finding in findings if finding.severity == "HOLD"],
        "missing_fields": sorted(
            {finding.field for finding in findings if finding.field and finding.code.startswith("missing_")}
        ),
        "unit_warnings": [
            finding.message
            for finding in findings
            if finding.code in {"missing_y_unit", "missing_factor_unit"}
        ],
        "y_type_warnings": [
            finding.message
            for finding in findings
            if finding.code in {"unsupported_y_type", "unsupported_direction", "missing_quality_decision_rule"}
        ],
        "factor_range_warnings": [
            finding.message
            for finding in findings
            if "range" in finding.code or "level" in finding.code or "factor" in finding.code
        ],
        "recommended_questions": [
            finding.question for finding in findings if finding.question
        ],
    }


def run_risk_gate(request: DoeRequest, df: pd.DataFrame | None = None) -> dict[str, Any]:
    findings: list[GateFinding] = []

    if not isinstance(request.project, dict) or _is_blank(request.project.get("name")):
        _add_finding(
            findings,
            "HOLD",
            "missing_project_name",
            "Project name is missing.",
            field="project.name",
            fix="Add a short project name for traceability.",
            question="What should this DOE project be called?",
        )
    if not isinstance(request.project, dict) or _is_blank(request.project.get("process_area")):
        _add_finding(
            findings,
            "HOLD",
            "missing_process_area",
            "Process area is missing.",
            field="project.process_area",
            fix="Add the target process area such as wafer_sawing, die_attach, wire_bonding, or molding.",
            question="Which process area does this DOE target?",
        )
    if not isinstance(request.project, dict) or _is_blank(request.project.get("equipment")):
        _add_finding(
            findings,
            "HOLD",
            "missing_equipment",
            "Equipment name/model is missing.",
            field="project.equipment",
            fix="Add the equipment name/model so factor windows can be checked against the right tool.",
            question="Which equipment and fixture/tooling will be used?",
        )
    if not isinstance(request.objective, dict) or _is_blank(request.objective.get("primary_goal")):
        _add_finding(
            findings,
            "HOLD",
            "missing_primary_goal",
            "Primary DOE goal is missing.",
            field="objective.primary_goal",
            fix="State whether the next DOE should screen factors, confirm a baseline, refine quality, or improve productivity.",
            question="What is the primary decision this DOE should support?",
        )
    if "max_runs" not in request.constraints:
        _add_finding(
            findings,
            "HOLD",
            "missing_max_runs",
            "Run budget is missing.",
            field="constraints.max_runs",
            fix="Add max_runs so the generator can choose between full, fractional, and confirmation DOE modes explicitly.",
            question="What is the maximum number of experimental conditions allowed?",
        )

    factor_columns = [factor.column for factor in request.factors]
    response_columns = [response.column for response in request.responses]
    all_columns = factor_columns + response_columns
    duplicated = sorted({column for column in all_columns if all_columns.count(column) > 1})
    if duplicated:
        _add_finding(
            findings,
            "BLOCK",
            "duplicate_columns",
            f"Factor/response columns must be unique: {', '.join(duplicated)}.",
            fix="Rename duplicate factor/response columns so each X and Y maps to one data column.",
        )

    for response_index, response in enumerate(request.responses):
        response_field = f"responses[{response_index}]"
        if response.y_type not in SUPPORTED_Y_TYPES:
            _add_finding(
                findings,
                "BLOCK",
                "unsupported_y_type",
                f"{response.name} uses unsupported y_type '{response.y_type}'.",
                field=f"{response_field}.type",
                fix=f"Use one of: {', '.join(sorted(SUPPORTED_Y_TYPES))}.",
                question=f"Should {response.name} be treated as continuous, count, binary, or categorical data?",
            )
        if response.direction and response.direction not in SUPPORTED_DIRECTIONS:
            _add_finding(
                findings,
                "HOLD",
                "unsupported_direction",
                f"{response.name} uses unsupported direction '{response.direction}'.",
                field=f"{response_field}.direction",
                fix=f"Use one of: {', '.join(sorted(SUPPORTED_DIRECTIONS))}.",
                question=f"What direction should be optimized for {response.name}?",
            )
        if response.role in QUALITY_ROLES and not _has_hard_decision_definition(response):
            _add_finding(
                findings,
                "HOLD",
                "missing_quality_decision_rule",
                f"{response.name} is a quality Y but has no spec or pass/fail values.",
                field=f"{response_field}.spec_or_pass_fail",
                fix="Add upper/lower spec limits or explicit pass/fail values.",
                question=f"What makes {response.name} acceptable, warning, or rejected?",
            )
        if response.role in QUALITY_ROLES and not response.measurement_method:
            _add_finding(
                findings,
                "HOLD",
                "missing_measurement_method",
                f"{response.name} has no measurement method description.",
                field=f"{response_field}.measurement_method",
                fix="Describe the measurement tool, sampling unit, and how the recorded value is produced.",
                question=f"How exactly will {response.name} be measured?",
            )
        if response.y_type in CONTINUOUS_LIKE_Y_TYPES and not response.unit:
            _add_finding(
                findings,
                "HOLD",
                "missing_y_unit",
                f"{response.name} has no unit.",
                field=f"{response_field}.unit",
                fix="Add a unit so margin and capability metrics are interpretable.",
                question=f"What is the unit for {response.name}?",
            )

    for factor_index, factor in enumerate(request.factors):
        factor_field = f"factors[{factor_index}]"
        if not factor.controllable:
            _add_finding(
                findings,
                "HOLD",
                "non_controllable_factor",
                f"{factor.name} is marked non-controllable; review before DOE generation.",
                field=f"{factor_field}.controllable",
                fix="Either remove this from controllable DOE factors or document it as a noise/blocking factor.",
                question=f"Can {factor.name} actually be set independently during the experiment?",
            )
        if not _has_usable_factor_space(factor):
            _add_finding(
                findings,
                "BLOCK",
                "missing_factor_levels",
                f"{factor.name} has no DOE levels, low/high pair, current value, or practical range.",
                field=f"{factor_field}.levels",
                fix="Add levels or a practical range before generating a DOE table.",
                question=f"What low/high or allowed levels should be used for {factor.name}?",
            )
        if (factor.low is None) ^ (factor.high is None):
            _add_finding(
                findings,
                "BLOCK",
                "incomplete_factor_low_high",
                f"{factor.name} has only one of low/high specified.",
                field=f"{factor_field}.low_high",
                fix="Provide both low and high, or use explicit levels.",
                question=f"What is the missing low/high value for {factor.name}?",
            )
        if not factor.unit:
            _add_finding(
                findings,
                "HOLD",
                "missing_factor_unit",
                f"{factor.name} has no unit.",
                field=f"{factor_field}.unit",
                fix="Add the engineering unit or mark categorical levels explicitly.",
                question=f"What unit does {factor.name} use?",
            )
        if factor.low is not None and factor.high is not None:
            _validate_numeric_range(
                findings,
                low=factor.low,
                high=factor.high,
                field=f"{factor_field}.low_high",
                label=factor.name,
            )
        if factor.practical_range is not None:
            _validate_numeric_range(
                findings,
                low=factor.practical_range[0],
                high=factor.practical_range[1],
                field=f"{factor_field}.practical_range",
                label=f"{factor.name} practical range",
            )
            practical_low = _as_float(factor.practical_range[0])
            practical_high = _as_float(factor.practical_range[1])
            if practical_low is not None and practical_high is not None:
                numeric_levels = [(level, _as_float(level)) for level in factor.levels]
                outside_levels = [
                    level
                    for level, numeric_level in numeric_levels
                    if numeric_level is not None and (numeric_level < practical_low or numeric_level > practical_high)
                ]
                if outside_levels:
                    _add_finding(
                        findings,
                        "BLOCK",
                        "factor_level_outside_practical_range",
                        f"{factor.name} levels are outside the approved practical range: {outside_levels}.",
                        field=f"{factor_field}.levels",
                        fix="Keep DOE levels inside the approved practical range or explicitly widen the allowed range.",
                        question=f"Are the proposed levels for {factor.name} approved by the engineer/equipment owner?",
                    )
                current = _as_float(factor.current)
                if current is not None and (current < practical_low or current > practical_high):
                    _add_finding(
                        findings,
                        "HOLD",
                        "current_value_outside_practical_range",
                        f"{factor.name} current value is outside the practical range.",
                        field=f"{factor_field}.current",
                        fix="Check whether the current/baseline value or the practical range is wrong.",
                        question=f"Should {factor.name} current value be inside the DOE practical range?",
                    )

    if not request.mechanism_hypotheses:
        _add_finding(
            findings,
            "HOLD",
            "missing_mechanism_hypotheses",
            "No process mechanism hypotheses were provided.",
            field="mechanism_hypotheses",
            fix="Add expected factor-to-response mechanisms and likely interactions.",
            question="What process mechanism explains why these Xs should affect these Ys?",
        )

    if not request.criteria:
        _add_finding(
            findings,
            "HOLD",
            "missing_decision_criteria",
            "No decision criteria were provided.",
            field="criteria",
            fix="Add criteria such as spec pass/fail, over-spec count, tail risk, margin, productivity trade-off, and measurement confidence.",
            question="Which criteria should decide whether a condition is rejected, candidate, or best?",
        )

    if df is not None:
        if df.empty:
            _add_finding(findings, "BLOCK", "empty_data", "Experiment data has no rows.", field="data")
        missing = sorted(set(all_columns).difference(df.columns))
        if missing:
            _add_finding(
                findings,
                "BLOCK",
                "missing_data_columns",
                f"Experiment data is missing required columns: {', '.join(missing)}.",
                field="data.columns",
                fix="Rename the data columns or update the request schema so factor/response columns match.",
                question="Which data columns correspond to each factor and response?",
            )
        present_required = [column for column in all_columns if column in df.columns]
        missing_value_columns = sorted(
            column for column in present_required if df[column].isna().any()
        )
        if missing_value_columns:
            _add_finding(
                findings,
                "HOLD",
                "missing_data_values",
                f"Experiment data has missing values in required columns: {', '.join(missing_value_columns)}.",
                field="data.values",
                fix="Fill missing measurements or exclude incomplete rows with a documented reason.",
                question="Are these missing values measurement failures, skipped samples, or unavailable responses?",
            )

    severities = {finding.severity for finding in findings}
    if "BLOCK" in severities:
        state = "BLOCK"
    elif "HOLD" in severities:
        state = "HOLD"
    else:
        state = "PASS"

    summary = _summarize_findings(findings)

    return {
        "state": state,
        "human_review_required": state in {"HOLD", "BLOCK"},
        "allowed_factor_space": [_factor_space_entry(factor) for factor in request.factors],
        "findings": [
            {
                "severity": finding.severity,
                "code": finding.code,
                "message": finding.message,
                "field": finding.field,
                "fix": finding.fix,
                "question": finding.question,
            }
            for finding in findings
        ],
        **summary,
    }
