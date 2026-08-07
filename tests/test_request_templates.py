from pathlib import Path

from ai_doe_planner.doe_generator import describe_design_plan, generate_design, generate_full_factorial
from ai_doe_planner.risk_gate import run_risk_gate
from ai_doe_planner.schemas import load_request


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_FILES = sorted((ROOT / "templates").rglob("*.yaml"))


def test_all_request_templates_load_and_pass_blocking_validation():
    assert TEMPLATE_FILES

    for path in TEMPLATE_FILES:
        request = load_request(path)
        gate = run_risk_gate(request)

        assert gate["state"] != "BLOCK", (path, gate)
        assert request.factor_columns
        assert request.response_columns
        assert request.mechanism_hypotheses


def test_process_starter_templates_generate_design_tables():
    starter_files = sorted((ROOT / "templates" / "process_requests").glob("*.yaml"))
    assert starter_files

    for path in starter_files:
        request = load_request(path)
        table = generate_design(request)

        assert not table.empty, path
        assert set(request.factor_columns).issubset(table.columns)
        assert table["run"].is_unique
        assert len(table) <= int(request.constraints["max_runs"])


def test_four_factor_templates_use_eight_run_half_fraction():
    starter_files = sorted((ROOT / "templates" / "process_requests").glob("*.yaml"))
    four_factor_files = [path for path in starter_files if len(load_request(path).factors) == 4]
    assert four_factor_files

    for path in four_factor_files:
        request = load_request(path)
        full_table = generate_full_factorial(request)
        design_table = generate_design(request)

        assert len(full_table) == 16
        assert len(design_table) == 8
        assert set(design_table["design_type"]) == {"fractional_factorial_half_fraction"}
        assert "alias_structure" in design_table.columns


def test_design_plan_explains_fractional_selection():
    request = load_request(ROOT / "templates" / "process_requests" / "wire_bonding_2nd_request.yaml")
    plan = describe_design_plan(request)

    assert plan["selected_design_type"] == "fractional_factorial_half_fraction"
    assert plan["full_factorial_runs"] == 16
    assert plan["selected_runs"] == 8
    assert plan["max_runs"] == 8
    assert "exceeding max_runs=8" in plan["rationale"]
    assert plan["alias_structure"]
    assert plan["rejected_alternatives"][0]["design_type"] == "full_factorial"
