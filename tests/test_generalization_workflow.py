from pathlib import Path

from ai_doe_planner.engine import analyze_from_files


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples" / "wire_bonding" / "request.yaml"
DATA = ROOT / "examples" / "wire_bonding" / "results.csv"


def test_wire_bonding_uses_lower_spec_and_categorical_failure_logic(tmp_path: Path):
    result = analyze_from_files(
        REQUEST,
        DATA,
        output_path=tmp_path / "wire_bonding_report.md",
        plots_path=tmp_path / "plots",
    )

    assert result["risk_gate"]["state"] == "PASS"

    pull = result["response_analysis"]["Pull force"]
    pull_policy = pull["analysis_policy"]
    assert pull_policy["spec_profile"] == "lower_only"
    assert "min" in pull_policy["decision_metrics"]
    assert "p05" in pull_policy["decision_metrics"]
    assert "lower_margin" in pull_policy["decision_metrics"]
    assert "Cpl_if_eligible" in pull_policy["decision_metrics"]
    assert "p95" not in pull_policy["decision_metrics"]

    failure_code = result["response_analysis"]["Failure code"]
    assert failure_code["overall"]["fail_count"] == 1
    assert failure_code["overall"]["warning_count"] == 2
    assert "code1:4" in failure_code["overall"]["value_counts"]

    best = result["criteria_result"]["best_condition"]
    assert best.condition_values == {"us_power": 450, "bond_force_gf": 100}
    assert best.state == "borderline"
    assert result["criteria_result"]["bottleneck_y"]["response"] == "Pull force"

    report = result["report_markdown"]
    assert "lower_only" in report
    assert "categorical" in report
    assert "Process mechanism evidence" in report
    assert "Production interpretation" in report
