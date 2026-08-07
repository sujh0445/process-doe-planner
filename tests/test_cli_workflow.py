from pathlib import Path

from ai_doe_planner.cli import main


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples" / "wafer_sawing" / "request.yaml"
DATA = ROOT / "examples" / "wafer_sawing" / "results.csv"


def test_recommend_command_writes_primary_and_option_tables(tmp_path, capsys):
    primary = tmp_path / "primary.csv"
    options_dir = tmp_path / "options"

    main(
        [
            "recommend",
            "--request",
            str(REQUEST),
            "--data",
            str(DATA),
            "--primary-out",
            str(primary),
            "--out-dir",
            str(options_dir),
        ]
    )

    captured = capsys.readouterr()
    option_files = sorted(options_dir.glob("*.csv"))
    assert primary.exists()
    assert len(option_files) >= 2
    assert "Next DOE recommendation options:" in captured.out
    assert "Option 1." in captured.out
    assert "decision basis" in captured.out


def test_report_command_writes_full_analysis_artifacts(tmp_path):
    report = tmp_path / "report.md"
    primary = tmp_path / "next.csv"
    options_dir = tmp_path / "recommendations"
    plots_dir = tmp_path / "plots"

    main(
        [
            "report",
            "--request",
            str(REQUEST),
            "--data",
            str(DATA),
            "--out",
            str(report),
            "--next-doe-out",
            str(primary),
            "--recommendations-out-dir",
            str(options_dir),
            "--plots-out",
            str(plots_dir),
        ]
    )

    text = report.read_text(encoding="utf-8")
    assert report.exists()
    assert primary.exists()
    assert len(list(options_dir.glob("*.csv"))) >= 2
    assert len(list(plots_dir.glob("*.png"))) >= 1
    assert "Recommendation options:" in text
    assert "ANOVA evidence (residual/error included):" in text
    assert "Primary decision evidence by condition:" in text
    assert "Project decision profile:" in text
    assert "These criteria come from the request file" in text
    assert "Statistics below are evidence for these criteria" in text
    assert "Round-level diagnostic summary:" in text
    assert "Omitted by project criteria" in text
    assert "Criterion-by-criterion evidence:" in text
    assert "sample-size-gated capability reference" in text
    assert "Capability is shown as a reference only" in text
    assert "capability_status" in text
    assert "exploratory_n_lt_33" in text
    assert "tail_risk" in text
    assert "measurement" in text
    assert "mechanism" in text
    assert "Process mechanism evidence" in text
    assert "Production interpretation" in text
    assert "initial screening" in text
