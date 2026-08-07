# SPC Control Chart Integration For AI DOE Planner

## Purpose

This document translates the statistical quality control lecture concepts into
AI DOE Planner decision logic. The planner should use SPC/control-chart thinking
before recommending an optimization DOE.

Core idea:

```text
process stability first
-> then margin/capability judgment
-> then DOE purpose selection
```

The planner should not treat every problem as an optimization problem. If the
current process is unstable, the next experiment should usually isolate or
stabilize the special cause before searching for a better recipe.

## Control Chart Concepts To Reuse

| Concept | Meaning | Planner interpretation |
| --- | --- | --- |
| Common cause | natural variation under controlled conditions | usable baseline variation |
| Special cause | abnormal variation from equipment, material, method, person, or environment | root-cause or stabilization candidate |
| CL | center line of current stable process | baseline center |
| UCL/LCL | statistically expected control limits | stability boundary |
| USL/LSL | product or customer specification limits | acceptance boundary |
| OOC | out of control | do not jump to final optimization |
| OOS | out of specification | containment/MRB/SOP before DOE adoption |
| Run/trend/cycle | non-random pattern inside limits | drift or segment mechanism candidate |
| Rational subgroup | samples grouped under comparable conditions | required for meaningful baseline evidence |

Important boundary:

```text
Control limits judge whether the process is stable.
Specification limits judge whether the product is acceptable.
```

A condition can be inside spec but still out of control. It can also be stable
but centered too close to a spec boundary. DOE routing must distinguish these
cases.

## DOE Stability Gate

Before selecting DOE type, classify the current process state.

| Current state | Decision label | Next DOE posture |
| --- | --- | --- |
| Stable and clear spec margin | optimization-ready | local optimization or production-improvement DOE |
| Stable but thin weakest margin | margin-limited | margin-improvement or confirmation DOE |
| OOC signal without OOS | unstable-process | special-cause isolation or stabilization DOE |
| OOS signal | containment-needed | stop adoption; route to SOP/MRB/recovery before DOE |
| Mean acceptable but variation large | variance-limited | variance-reduction DOE |
| Repeated pattern by lot/tool/chamber | segmented-instability | blocked or segmented DOE |

Recommended rule:

```text
If OOC/OOS evidence exists, the next DOE purpose is not final optimization.
It is stabilization, special-cause isolation, boundary learning, or recovery.
```

## Mapping SPC Signals To DOE Purposes

| SPC/risk signal | Likely mechanism question | DOE purpose |
| --- | --- | --- |
| Mean shift | What moved the process center? | center-shift root-cause DOE |
| Increased R/S/MR | What increased variation? | variance-reduction DOE |
| Trend | Is drift tied to time, wear, temperature, material age, or maintenance? | drift-factor DOE |
| Cycle | Is there a shift, recipe cycle, chamber cycle, or PM cycle? | blocked/cycle DOE |
| Same-side run | Did the baseline center move? | baseline revalidation DOE |
| Segment-specific OOC | Does one tool/chamber/lot behave differently? | segmented or blocked DOE |
| Good mean but weak worst repeat | Is the condition robust? | confirmation/margin DOE |
| Production gain consumes margin | Is the efficiency gain worth the margin loss? | margin-budget DOE |

## Rational Subgroup Rule For Lab And Production Data

The planner should treat subgroup construction as a decision input. Averages,
standard deviations, and ranges are only meaningful when the grouped samples are
comparable.

Preferred subgroup examples:

- same tool/chamber/recipe/time window,
- same lot or controlled lot slice,
- repeated measurements under the same DOE condition,
- comparable measurement method and operator state.

Risky subgroup examples:

- mixing tools/chambers without block labels,
- mixing pre-maintenance and post-maintenance wafers,
- combining different recipes into one baseline,
- averaging across a known drift window.

Planner behavior:

```text
If rational subgroup evidence is weak, lower recommendation confidence and
route to measurement/baseline clarification before a high-confidence DOE.
```

## AI Risk Engine Handoff

When a risk engine exists, the planner should consume its alerts as DOE
hypotheses, not as confirmed root causes.

Recommended handoff fields:

| Field | Meaning |
| --- | --- |
| signal_type | mean shift, variance increase, trend, cycle, run, OOC-like, score drift |
| affected_segment | lot, wafer group, tool, chamber, recipe, time window |
| suspected_feature_group | sensor group or process variable family |
| evidence_window | number of wafers/lots and time period |
| severity | watch, warning, OOS-like, repeated |
| proposed_DOE_purpose | stabilize, isolate, confirm, optimize, rescue |
| leakage_boundary | whether the signal was generated without future labels |

Safe language:

```text
The risk signal is a DOE hypothesis candidate, not a confirmed process cause.
```

## Recommendation Report Additions

Every DOE recommendation should add a compact SPC state block when data exists.

| Field | Required content |
| --- | --- |
| Stability state | stable, OOC-like, OOS-like, variance-limited, unknown |
| Weakest margin | margin against the most limiting spec/guardrail |
| Variation state | stable, widened, trend, cycle, segment-specific |
| Subgroup quality | rational, mixed, unknown, insufficient |
| DOE gate result | optimize, confirm, stabilize, isolate, contain |
| Rejected route | why a richer optimization DOE was not chosen if blocked |

Example:

```text
SPC state: variance-limited, no OOS evidence, subgroup quality acceptable.
DOE gate: run variance-reduction DOE before production optimization.
Rejected: final recipe optimization because worst-repeat margin is thin and
moving-range evidence suggests the process is not robust enough yet.
```

## Portfolio Positioning

This integration makes the planner more practical than a textbook DOE selector:

```text
The system does not recommend experiments from factor count alone. It first
checks whether the process is stable enough for optimization, then routes the
next DOE to stabilization, confirmation, margin improvement, or production
optimization according to SPC evidence.
```
