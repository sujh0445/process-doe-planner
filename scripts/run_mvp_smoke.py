from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_doe_planner.engine import analyze_from_files
from ai_doe_planner.doe_generator import generate_design
from ai_doe_planner.schemas import load_request


def main() -> None:
    request_path = ROOT / "examples" / "wafer_sawing" / "request.yaml"
    data_path = ROOT / "examples" / "wafer_sawing" / "results.csv"
    output_path = ROOT / "outputs" / "mvp" / "smoke_report.md"

    request = load_request(request_path)
    design = generate_design(request)
    assert len(design) == 4, f"Expected 4 design rows, got {len(design)}"

    result = analyze_from_files(request_path, data_path, output_path)
    assert result["criteria_result"]["best_condition"] is not None
    assert result["next_doe"]["mode"] != "no_recommendation"

    print("MVP smoke test passed")
    print(f"- design rows: {len(design)}")
    print(f"- next DOE mode: {result['next_doe']['mode']}")
    print(f"- report: {output_path}")


if __name__ == "__main__":
    main()
