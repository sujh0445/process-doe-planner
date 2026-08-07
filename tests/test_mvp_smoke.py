from pathlib import Path

from ai_doe_planner.engine import analyze_from_files
from ai_doe_planner.schemas import load_request
from ai_doe_planner.doe_generator import generate_design


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples" / "wafer_sawing" / "request.yaml"
DATA = ROOT / "examples" / "wafer_sawing" / "results.csv"


def test_request_loads_and_generates_design():
    request = load_request(REQUEST)
    table = generate_design(request)
    assert len(table) == 4
    assert {"spindle_rpm", "feed_speed_mm_s"}.issubset(table.columns)


def test_analyze_wafer_sawing_example(tmp_path):
    output = tmp_path / "report.md"
    result = analyze_from_files(REQUEST, DATA, output)
    assert output.exists()
    assert result["criteria_result"]["best_condition"] is not None
    assert result["next_doe"]["mode"] != "no_recommendation"
    assert len(result["next_doe_options"]) >= 2
    assert result["next_doe_options"][0]["mode"] == result["next_doe"]["mode"]
    text = output.read_text(encoding="utf-8")
    assert "Design generation logic:" in text
    assert "Decision basis:" in text


def test_analyze_writes_visual_evidence(tmp_path):
    output = tmp_path / "report.md"
    plots = tmp_path / "plots"

    result = analyze_from_files(REQUEST, DATA, output, plots)

    assert result["visualizations"]
    assert all(Path(item["path"]).exists() for item in result["visualizations"])
    text = output.read_text(encoding="utf-8")
    assert "Visual evidence:" in text
    assert "plots/" in text
