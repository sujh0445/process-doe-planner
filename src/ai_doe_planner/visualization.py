from __future__ import annotations

from pathlib import Path
from typing import Any
import os
import re


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return text or "response"


def _short_label(value: str, max_length: int = 36) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 1] + "..."


def _save_condition_summary(response_name: str, analysis: dict[str, Any], output_dir: Path) -> Path | None:
    rows = analysis["by_condition"]
    if not rows:
        return None

    response = analysis["response"]
    labels = [_short_label(row["condition"]) for row in rows]
    if response.y_type in {"continuous", "image-derived", "count"}:
        metrics = [metric for metric in ["mean", "p95", "max"] if any(row.get(metric) is not None for row in rows)]
    elif response.y_type == "binary":
        metrics = [metric for metric in ["fail_rate", "positive_rate"] if any(row.get(metric) is not None for row in rows)]
    else:
        metrics = [metric for metric in ["fail_rate", "warning_rate"] if any(row.get(metric) is not None for row in rows)]
    if not metrics:
        return None

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x = list(range(len(rows)))
    width = 0.8 / max(len(metrics), 1)
    fig, ax = plt.subplots(figsize=(max(8, len(rows) * 1.4), 4.8))
    for index, metric in enumerate(metrics):
        offset = (index - (len(metrics) - 1) / 2) * width
        values = [row.get(metric) if row.get(metric) is not None else 0 for row in rows]
        ax.bar([item + offset for item in x], values, width=width, label=metric)
    ax.set_title(f"{response_name} by DOE condition")
    ax.set_ylabel(response.unit or response.y_type)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    path = output_dir / f"{_slug(response_name)}-condition-summary.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _save_effect_ranking(response_name: str, analysis: dict[str, Any], output_dir: Path) -> Path | None:
    rows = analysis["effects"][:8]
    if not rows:
        return None

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [row["term"] for row in rows]
    values = [row.get("relative_effect_weight", row.get("contribution_ratio", 0.0)) for row in rows]
    fig, ax = plt.subplots(figsize=(8, max(3.2, len(rows) * 0.48)))
    ax.barh(labels[::-1], values[::-1], color="#2463eb")
    ax.set_title(f"{response_name} modeled-effect ranking")
    ax.set_xlabel("relative effect weight")
    ax.set_xlim(0, max(values) * 1.15 if values and max(values) > 0 else 1)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()

    path = output_dir / f"{_slug(response_name)}-effect-ranking.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _save_anova_contribution(response_name: str, analysis: dict[str, Any], output_dir: Path) -> Path | None:
    rows = analysis["anova"]
    if not rows:
        return None

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [row["term"] for row in rows]
    values = [row.get("contribution_ratio") or 0.0 for row in rows]
    colors = ["#94a3b8" if row.get("term_kind") == "error" else "#16a34a" for row in rows]
    fig, ax = plt.subplots(figsize=(8, max(3.2, len(rows) * 0.5)))
    ax.barh(labels[::-1], values[::-1], color=colors[::-1])
    ax.set_title(f"{response_name} ANOVA contribution including residual/error")
    ax.set_xlabel("sum-of-squares contribution")
    ax.set_xlim(0, max(values) * 1.15 if values and max(values) > 0 else 1)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()

    path = output_dir / f"{_slug(response_name)}-anova-contribution.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_visualizations(result: dict[str, Any], output_dir: str | Path) -> list[dict[str, str]]:
    """Write reusable evidence plots for the Markdown report.

    The plots are derived from already-calculated statistical evidence. They do
    not make new decisions; they only make the evidence easier to audit.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(output_path / ".matplotlib-cache"))
    visuals: list[dict[str, str]] = []
    for response_name, analysis in result["response_analysis"].items():
        plotters = [
            ("condition_summary", _save_condition_summary),
            ("effect_ranking", _save_effect_ranking),
            ("anova_contribution", _save_anova_contribution),
        ]
        for kind, plotter in plotters:
            path = plotter(response_name, analysis, output_path)
            if path is None:
                continue
            visuals.append({"response": response_name, "kind": kind, "path": str(path)})
    return visuals
