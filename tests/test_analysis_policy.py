import pandas as pd

from ai_doe_planner.schemas import DoeRequest
from ai_doe_planner.statistics import analyze_responses


def _request(*, stage: str, design: str, factor_count: int = 2, spec: dict | None = None) -> DoeRequest:
    factors = [
        {"name": chr(65 + index), "column": chr(97 + index), "levels": [0, 1]}
        for index in range(factor_count)
    ]
    return DoeRequest.from_dict(
        {
            "project": {"name": "Policy test"},
            "objective": {"primary_goal": "Verify stage-aware analysis"},
            "factors": factors,
            "responses": [
                {
                    "name": "Y",
                    "column": "y",
                    "type": "continuous",
                    "direction": "lower_is_better",
                    "spec": spec or {"upper_spec": 12},
                    "measurement_method": "Replicated measurement.",
                }
            ],
            "constraints": {"analysis_stage": stage, "design_type": design},
            "mechanism_hypotheses": ["Factor changes Y."],
        }
    )


def _full_two_factor_data() -> pd.DataFrame:
    rows = []
    for a in [0, 1]:
        for b in [0, 1]:
            for repeat in [0, 1, 2]:
                rows.append({"a": a, "b": b, "y": 5 + 2 * a + b + a * b + 0.1 * repeat})
    return pd.DataFrame(rows)


def test_upper_only_full_factorial_uses_tail_metrics_and_interactions():
    result = analyze_responses(
        _full_two_factor_data(),
        _request(stage="screening", design="full_factorial"),
    )["Y"]

    assert result["analysis_policy"]["spec_profile"] == "upper_only"
    assert "over_spec_count_rate" in result["analysis_policy"]["decision_metrics"]
    assert "p95" in result["analysis_policy"]["decision_metrics"]
    assert "Cpu_if_eligible" in result["analysis_policy"]["decision_metrics"]
    assert any(row["kind"] == "interaction" for row in result["effects"])
    assert any(row["term_kind"] == "error" for row in result["anova"])


def test_fractional_screening_suppresses_unidentifiable_pairwise_interactions():
    request = _request(stage="screening", design="fractional_factorial", factor_count=4)
    data = pd.DataFrame(
        [
            {"a": -1, "b": -1, "c": -1, "d": -1, "y": 7.0},
            {"a": 1, "b": -1, "c": -1, "d": 1, "y": 8.0},
            {"a": -1, "b": 1, "c": -1, "d": 1, "y": 7.5},
            {"a": 1, "b": 1, "c": -1, "d": -1, "y": 9.0},
            {"a": -1, "b": -1, "c": 1, "d": 1, "y": 7.2},
            {"a": 1, "b": -1, "c": 1, "d": -1, "y": 8.2},
            {"a": -1, "b": 1, "c": 1, "d": -1, "y": 7.8},
            {"a": 1, "b": 1, "c": 1, "d": 1, "y": 9.4},
        ]
    )
    result = analyze_responses(data, request)["Y"]

    assert result["analysis_policy"]["interaction_policy"] == "main_effects_only_alias_aware"
    assert all(row["kind"] == "main" for row in result["effects"])
    assert all(row["term_kind"] != "interaction" for row in result["anova"])


def test_trend_refinement_uses_trend_suite_instead_of_screening_effects():
    request = _request(stage="trend_refinement", design="custom_or_multilevel")
    data = pd.DataFrame(
        [
            {"a": a, "b": b, "y": 4 + 0.03 * a + 0.2 * b + repeat * 0.01}
            for a in [10, 50, 100, 150]
            for b in [0, 1]
            for repeat in [0, 1]
        ]
    )
    result = analyze_responses(data, request)["Y"]

    assert result["effects"] == []
    assert result["anova"] == []
    assert result["trend"]
    assert {row["factor"] for row in result["trend"]} == {"a", "b"}


def test_confirmation_focuses_on_repeatability_and_capability_eligibility():
    request = _request(stage="confirmation", design="confirmation")
    data = _full_two_factor_data()
    result = analyze_responses(data, request)["Y"]

    assert result["effects"] == []
    assert result["anova"] == []
    assert result["confirmation"]["condition_count"] == 4
    assert result["confirmation"]["minimum_condition_n"] == 3
    assert result["confirmation"]["capability_claim_allowed"] is False


def test_lower_only_response_selects_lower_tail_and_cpl_metrics():
    request = _request(
        stage="confirmation",
        design="confirmation",
        spec={"lower_spec": 7},
    )
    result = analyze_responses(_full_two_factor_data(), request)["Y"]
    metrics = result["analysis_policy"]["decision_metrics"]

    assert "p05" in metrics
    assert "lower_margin" in metrics
    assert "Cpl_if_eligible" in metrics
    assert "p95" not in metrics
