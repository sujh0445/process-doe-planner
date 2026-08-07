from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]

FALLBACK_PUBLIC_PATHS = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    ROOT / "pyproject.toml",
    ROOT / ".gitignore",
    ROOT / ".github",
    ROOT / "src",
    ROOT / "examples",
    ROOT / "templates",
    ROOT / "tests",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "knowledge",
)

PUBLIC_DOC_NAMES = (
    "ai_doe_planning_agent_design.md",
    "allowed-factor-space-to-doe-generator.md",
    "artifact-logging-and-feedback-loop.md",
    "doe-decision-algorithm.md",
    "doe-evidence-report-format.md",
    "evidence-and-unknown-context-risk.md",
    "four-process-doe-summary.md",
    "next-doe-recommendation-logic.md",
    "process-knowledge-card-template.md",
    "process-knowledge-schema.md",
    "project-specific-decision-criteria.md",
    "recommendation-confidence-grading.md",
    "report-automation-plan.md",
    "scoring-engine.md",
    "spc-control-chart-risk-doe-integration.md",
    "statistics_ml_interpretation_guidelines.md",
    "structured-request-schema.md",
    "validation-risk-gate-contract.md",
    "x-candidate-scoring.md",
)

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

FORBIDDEN_PATTERNS = {
    "personal absolute path": re.compile(
        r"/Users/junhwa|Library/Mobile Documents|CloudDocs|\.codex/attachments"
    ),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "hard-coded credential": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\b\s*[:=]\s*['\"][^'\"]+['\"]"
    ),
}


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return [ROOT / line for line in result.stdout.splitlines() if line.strip()]

    files: list[Path] = []
    for path in FALLBACK_PUBLIC_PATHS:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(candidate for candidate in path.rglob("*") if candidate.is_file())
    files.extend(ROOT / "docs" / name for name in PUBLIC_DOC_NAMES)
    return sorted(set(files))


def main() -> None:
    findings: list[str] = []
    checked = 0

    for path in _tracked_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            ".gitignore",
            "LICENSE",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checked += 1
        for label, pattern in FORBIDDEN_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: {label}")

    if findings:
        print("Public release check failed:")
        for finding in findings:
            print(f"- {finding}")
        raise SystemExit(1)

    print(f"Public release check passed ({checked} text files checked)")


if __name__ == "__main__":
    main()
