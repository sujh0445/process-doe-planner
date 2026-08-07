import pytest

from ai_doe_planner.cli import main


def _write_hold_request(path):
    path.write_text(
        """
project:
  name: HOLD CLI DOE
  process_area: wafer_sawing
  equipment: DAD3241
objective:
  primary_goal: Check CLI gate behavior
factors:
  - name: A
    column: a
    unit: rpm
    levels: [30000, 50000]
responses:
  - name: Y
    column: y
    type: continuous
    role: primary_quality_y
    direction: lower_is_better
    unit: um
    measurement_method: Manual high-scope measurement.
criteria:
  - name: Review Y
    applies_to_y: y
    decision_role: quality_gate
constraints:
  max_runs: 2
mechanism_hypotheses:
  - A may change Y.
""",
        encoding="utf-8",
    )


def test_design_stops_on_hold_without_explicit_override(tmp_path, capsys):
    request_path = tmp_path / "hold_request.yaml"
    _write_hold_request(request_path)

    with pytest.raises(SystemExit) as error:
        main(["design", "--request", str(request_path)])

    captured = capsys.readouterr()
    assert error.value.code == 1
    assert "state: HOLD" in captured.err
    assert "Use --allow-hold" in captured.err


def test_design_allows_review_draft_when_hold_is_explicitly_allowed(tmp_path, capsys):
    request_path = tmp_path / "hold_request.yaml"
    _write_hold_request(request_path)

    main(["design", "--request", str(request_path), "--allow-hold"])

    captured = capsys.readouterr()
    assert "state: HOLD" in captured.err
    assert "run,a" in captured.out
