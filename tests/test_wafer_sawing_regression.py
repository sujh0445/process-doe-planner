from pathlib import Path

import pytest

from ai_doe_planner.engine import analyze_from_files


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples" / "wafer_sawing" / "request.yaml"
DATA = ROOT / "examples" / "wafer_sawing" / "results.csv"


def test_wafer_sawing_end_to_end_decision_contract(tmp_path: Path):
    result = analyze_from_files(
        REQUEST,
        DATA,
        output_path=tmp_path / "wafer_sawing_report.md",
        plots_path=tmp_path / "plots",
    )

    assert result["risk_gate"]["state"] == "PASS"
    assert result["row_count"] == 40

    analysis = result["response_analysis"]["Max chipping size"]
    policy = analysis["analysis_policy"]
    assert policy["spec_profile"] == "upper_only"
    assert policy["analysis_stage"] == "screening"
    assert policy["design_type"] == "full_factorial"
    assert policy["include_interactions"] is True
    assert "max" in policy["decision_metrics"]
    assert "p95" in policy["decision_metrics"]
    assert "upper_margin" in policy["decision_metrics"]

    overall = analysis["overall"]
    assert overall["mean"] == pytest.approx(6.855)
    assert overall["max"] == pytest.approx(12.3)
    assert overall["p95"] == pytest.approx(10.745)
    assert overall["fail_count"] == 1

    anova = {row["term"]: row for row in analysis["anova"]}
    assert anova["feed_speed_mm_s"]["contribution_ratio"] > anova["spindle_rpm"]["contribution_ratio"]
    assert anova["Residual/Error"]["contribution_ratio"] == pytest.approx(0.1969212767)
    assert sum(row["contribution_ratio"] for row in analysis["anova"]) == pytest.approx(1.0)

    effects = {row["term"]: row for row in analysis["effects"]}
    assert effects["feed_speed_mm_s"]["effect"] > 0
    assert effects["spindle_rpm"]["effect"] < 0

    decisions = {item.condition: item for item in result["criteria_result"]["condition_decisions"]}
    best = result["criteria_result"]["best_condition"]
    assert best.condition_values == {"spindle_rpm": 50000, "feed_speed_mm_s": 50}
    assert best.state == "candidate"
    assert decisions["spindle_rpm=30000 / feed_speed_mm_s=150"].state == "rejected"
    assert decisions["spindle_rpm=50000 / feed_speed_mm_s=150"].state == "borderline"

    option_modes = [option["mode"] for option in result["next_doe_options"]]
    assert option_modes == [
        "productivity_refinement_or_confirmation",
        "confirmation_doe",
        "candidate_contrast_confirmation",
    ]

    report = result["report_markdown"]
    assert "## 4. Y-Type and Analysis Method" in report
    assert "## 6. Decision Criteria Evaluation" in report
    assert "## 8. Process and Production Interpretation" in report
    assert "## 9. Next DOE Recommendation" in report
    assert len(result["visualizations"]) == 3
