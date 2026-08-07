import pandas as pd
import pytest

from ai_doe_planner.criteria import evaluate_conditions
from ai_doe_planner.risk_gate import run_risk_gate
from ai_doe_planner.schemas import DoeRequest
from ai_doe_planner.statistics import analyze_responses


def _mixed_response_request() -> DoeRequest:
    return DoeRequest.from_dict(
        {
            "project": {
                "name": "Mixed response DOE",
                "process_area": "wire_bonding",
                "equipment": "training bonder",
            },
            "objective": {
                "primary_goal": "Find a low-risk condition across multiple Y types",
                "business_goal": "Keep quality first, then compare productivity",
                "decision_mode": "criteria_first",
            },
            "factors": [
                {"name": "US power", "column": "power", "levels": [100, 200], "unit": "machine_unit"},
                {"name": "Bond force", "column": "force", "levels": [10, 20], "unit": "gf"},
            ],
            "responses": [
                {
                    "name": "Pull fail",
                    "column": "pull_fail",
                    "type": "binary",
                    "role": "primary_quality_y",
                    "direction": "lower_is_better",
                    "fail_values": [1],
                    "measurement_method": "Pull-test result converted to 0/1 fail event.",
                },
                {
                    "name": "Failure code",
                    "column": "failure_code",
                    "type": "categorical",
                    "role": "secondary_quality_y",
                    "direction": "lower_is_better",
                    "fail_values": ["code4", "code5"],
                    "warning_values": ["code3"],
                    "measurement_method": "Pull-test fracture mode code.",
                },
                {
                    "name": "Void count",
                    "column": "void_count",
                    "type": "count",
                    "role": "secondary_quality_y",
                    "direction": "lower_is_better",
                    "unit": "count",
                    "spec": {"upper_spec": 2, "warning_upper": 1},
                    "measurement_method": "Counted void defects in the inspection ROI.",
                },
            ],
            "mechanism_hypotheses": [
                "Power and force change bond energy, so failure rate and defect count may respond differently."
            ],
            "criteria": [
                {
                    "name": "Reject pull fail conditions",
                    "response": "pull_fail",
                    "rule": "reject_if_fail_count_gt",
                    "threshold": 0,
                }
            ],
            "constraints": {"max_runs": 4, "samples_per_condition": 2},
        }
    )


def _mixed_response_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"power": 100, "force": 10, "pull_fail": 0, "failure_code": "code1", "void_count": 0},
            {"power": 100, "force": 10, "pull_fail": 0, "failure_code": "code1", "void_count": 1},
            {"power": 200, "force": 10, "pull_fail": 1, "failure_code": "code4", "void_count": 3},
            {"power": 200, "force": 10, "pull_fail": 0, "failure_code": "code3", "void_count": 2},
            {"power": 100, "force": 20, "pull_fail": 0, "failure_code": "code2", "void_count": 1},
            {"power": 100, "force": 20, "pull_fail": 0, "failure_code": "code2", "void_count": 0},
            {"power": 200, "force": 20, "pull_fail": 0, "failure_code": "code1", "void_count": 0},
            {"power": 200, "force": 20, "pull_fail": 0, "failure_code": "code1", "void_count": 1},
        ]
    )


def test_mixed_response_types_are_analyzed_with_python_evidence():
    request = _mixed_response_request()
    df = _mixed_response_data()

    gate = run_risk_gate(request, df)
    analysis = analyze_responses(df, request)
    decisions = evaluate_conditions(df, request, analysis)

    assert gate["state"] == "PASS"
    assert analysis["Pull fail"]["overall"]["fail_count"] == 1
    assert analysis["Pull fail"]["overall"]["fail_rate"] == 0.125
    assert analysis["Pull fail"]["effects"]

    assert analysis["Failure code"]["overall"]["fail_count"] == 1
    assert analysis["Failure code"]["overall"]["warning_count"] == 1
    assert "code1" in analysis["Failure code"]["overall"]["value_counts"]

    assert analysis["Void count"]["overall"]["fail_count"] == 1
    assert analysis["Void count"]["overall"]["warning_count"] == 1
    assert analysis["Void count"]["effects"]

    assert decisions["best_condition"].state == "borderline"
    assert any(item.state == "rejected" for item in decisions["condition_decisions"])


def test_risk_gate_holds_when_quality_y_lacks_decision_rule():
    request = DoeRequest.from_dict(
        {
            "project": {"name": "Incomplete DOE"},
            "objective": {"primary_goal": "Check validation gate"},
            "factors": [{"name": "A", "column": "a", "levels": [1, 2]}],
            "responses": [
                {
                    "name": "Thickness",
                    "column": "thickness",
                    "type": "continuous",
                    "role": "primary_quality_y",
                    "measurement_method": "Manual microscope reading.",
                }
            ],
            "mechanism_hypotheses": ["A may change thickness."],
        }
    )
    df = pd.DataFrame({"a": [1, 2], "thickness": [10.0, 11.0]})

    gate = run_risk_gate(request, df)

    assert gate["state"] == "HOLD"
    assert any(finding["code"] == "missing_quality_decision_rule" for finding in gate["findings"])
    assert "responses[0].spec_or_pass_fail" in gate["missing_fields"]
    assert gate["recommended_questions"]


def test_risk_gate_blocks_unknown_y_type():
    request = DoeRequest.from_dict(
        {
            "project": {"name": "Unsupported DOE"},
            "objective": {"primary_goal": "Check validation gate"},
            "factors": [{"name": "A", "column": "a", "levels": [1, 2]}],
            "responses": [
                {
                    "name": "Mystery",
                    "column": "mystery",
                    "type": "ordinal_score",
                    "role": "primary_quality_y",
                    "fail_values": [3],
                    "measurement_method": "Operator score.",
                }
            ],
            "mechanism_hypotheses": ["A may change mystery score."],
        }
    )
    df = pd.DataFrame({"a": [1, 2], "mystery": [1, 3]})

    gate = run_risk_gate(request, df)

    assert gate["state"] == "BLOCK"
    assert any(finding["code"] == "unsupported_y_type" for finding in gate["findings"])


def test_risk_gate_blocks_factor_levels_outside_practical_range():
    request = DoeRequest.from_dict(
        {
            "project": {
                "name": "Unsafe factor DOE",
                "process_area": "wafer_sawing",
                "equipment": "DAD3241",
            },
            "objective": {"primary_goal": "Check factor range validation"},
            "factors": [
                {
                    "name": "Feed speed",
                    "column": "feed",
                    "unit": "mm/s",
                    "levels": [50, 250],
                    "practical_range": [10, 200],
                }
            ],
            "responses": [
                {
                    "name": "Max chipping",
                    "column": "chipping",
                    "type": "continuous",
                    "role": "primary_quality_y",
                    "direction": "lower_is_better",
                    "unit": "um",
                    "spec": {"upper_spec": 12},
                    "measurement_method": "High-scope max chipping measurement.",
                }
            ],
            "criteria": [{"name": "Spec pass", "response": "chipping", "rule": "reject_if_over_upper_spec"}],
            "constraints": {"max_runs": 2},
            "mechanism_hypotheses": ["Higher feed can increase chipping."],
        }
    )

    gate = run_risk_gate(request)

    assert gate["state"] == "BLOCK"
    assert any(finding["code"] == "factor_level_outside_practical_range" for finding in gate["findings"])
    assert gate["allowed_factor_space"][0]["column"] == "feed"


def test_anova_includes_residual_error_and_full_contribution_ratio():
    request = DoeRequest.from_dict(
        {
            "project": {"name": "Replicated two-factor DOE"},
            "objective": {"primary_goal": "Check residual-inclusive ANOVA evidence"},
            "factors": [
                {"name": "A", "column": "a", "levels": [0, 1]},
                {"name": "B", "column": "b", "levels": [0, 1]},
            ],
            "responses": [
                {
                    "name": "Pull strength",
                    "column": "pull_strength",
                    "type": "continuous",
                    "role": "primary_quality_y",
                    "direction": "higher_is_better",
                    "spec": {"lower_spec": 7},
                    "measurement_method": "Replicated pull force measurement.",
                }
            ],
            "mechanism_hypotheses": ["A and B can interact because both contribute process energy."],
        }
    )
    df = pd.DataFrame(
        [
            {"a": 0, "b": 0, "pull_strength": 10.0},
            {"a": 0, "b": 0, "pull_strength": 11.0},
            {"a": 1, "b": 0, "pull_strength": 13.0},
            {"a": 1, "b": 0, "pull_strength": 14.0},
            {"a": 0, "b": 1, "pull_strength": 12.0},
            {"a": 0, "b": 1, "pull_strength": 13.0},
            {"a": 1, "b": 1, "pull_strength": 18.0},
            {"a": 1, "b": 1, "pull_strength": 19.0},
        ]
    )

    rows = analyze_responses(df, request)["Pull strength"]["anova"]

    assert any(row["term"] == "Residual/Error" for row in rows)
    assert any(row["term"] == "a:b" for row in rows)
    assert {row["model_scope"] for row in rows} == {"main_plus_pairwise_interactions"}
    contribution_total = sum(row["contribution_ratio"] for row in rows if row["contribution_ratio"] is not None)
    assert contribution_total == pytest.approx(1.0)
    residual = next(row for row in rows if row["term"] == "Residual/Error")
    assert residual["contribution_ratio"] > 0
