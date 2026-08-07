# Public Documentation Map

This directory exposes the reviewed design contracts and reusable process
knowledge for AI DOE Planner. Raw lecture files, transcripts, lab photographs,
local file-organization logs, and one-off analysis notes are intentionally not
part of the public repository.

## Start Here

- `doe-decision-algorithm.md`: criteria-first decision sequence.
- `project-specific-decision-criteria.md`: how objective, Y type, spec
  direction, and DOE stage change the primary decision criteria.
- `structured-request-schema.md`: required project input contract.
- `validation-risk-gate-contract.md`: PASS, HOLD, and BLOCK behavior.
- `allowed-factor-space-to-doe-generator.md`: safe factor-space handoff to DOE
  generation.
- `doe-evidence-report-format.md`: evidence and report contract.
- `next-doe-recommendation-logic.md`: multi-mode next-experiment routing.

## System Design

- `ai_doe_planning_agent_design.md`
- `evidence-and-unknown-context-risk.md`
- `artifact-logging-and-feedback-loop.md`
- `recommendation-confidence-grading.md`
- `scoring-engine.md`
- `report-automation-plan.md`

## Statistical Interpretation

- `statistics_ml_interpretation_guidelines.md`
- `spc-control-chart-risk-doe-integration.md`

The statistical layer supplies reproducible evidence. Project-specific quality
criteria, process-mechanism consistency, measurement confidence, and production
trade-offs determine the engineering recommendation.

## Process Knowledge Cards

- `knowledge/wafer-sawing-disco-d3241-card.md`
- `knowledge/die-attach-spa300-epoxy-card.md`
- `knowledge/wire-bonding-2nd-bond-card.md`
- `knowledge/molding-substrate-frame-card.md`

These cards are engineering context inputs, not universal process truth or a
replacement for equipment manuals and engineer approval.
