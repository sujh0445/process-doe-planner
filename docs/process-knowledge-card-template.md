# Process Knowledge Card Template

## Purpose

This template turns lecture notes, equipment screens, engineer comments,
photos, and transcripts into reusable process knowledge.

The planner should not rely on the user repeating the same process mechanism
in chat. Each process should have a card that the scoring and DOE engines can
read.

## Card Header

| Field | Value |
| --- | --- |
| process_id |  |
| process_name |  |
| process_scope |  |
| context_profile | general_screening / semiconductor_training_lab_7h / semiconductor_process_optimization / manufacturing_quality_improvement / research_development_rsm / material_mixture_experiment / custom |
| equipment_name |  |
| material / product |  |
| fixed assumptions |  |
| available measurements |  |
| unavailable measurements |  |
| total lab time window | 7 hours / other |
| execution maturity | beginner / intermediate / experienced |
| setup/changeover risk | low / medium / high |
| measurement time per run |  |
| documentation/review buffer |  |
| expected run budget |  |
| repeat budget |  |

Context profile rule:

```text
The core DOE logic is general. The context_profile supplies practical
constraints such as time budget, operator maturity, measurement availability,
equipment risk, and domain guardrails.
```

## Y Definition

Define Y before selecting X.

| Y | Type | Decision role | Spec / target | Preference | Measurement method | Notes |
| --- | --- | --- | --- | --- | --- | --- |
|  | continuous / categorical / ordinal / count / rate / image_derived | hard_constraint / quality_objective / guardrail / production_objective / monitor |  | higher / lower / range / target |  |  |

Decision-role rule:

```text
Hard constraints and guardrails are evaluated first. Production objectives
rank only quality-safe candidates.
```

## X Candidate Table

| X | Unit | Candidate levels / safe range | Role tag | Expected Y impact | Production impact | Risk | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | quality_primary / quality_production_mixed / production_secondary / guardrail_stabilizer |  |  |  | lecture / engineer / assumption / data |

Important:

```text
DOE low/high levels are not equipment hard limits unless explicitly stated.
```

## X Selection Scoring

Use `docs/x-candidate-scoring.md`.

| X | Mechanism | Engineer | Control | Measure | Interaction | Production | Range | Risk | Bottleneck adj. | Final | Status | Reason |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |

Status values:

- active,
- fixed,
- blocked,
- deferred,
- excluded.

## Mechanism Map

| X | Y | Expected direction | Mechanism | Confidence | Risk |
| --- | --- | --- | --- | --- | --- |
|  |  | increase / decrease / U-shaped / threshold / unknown |  | low / medium / high |  |

## Interaction Hypotheses

| Interaction | Affected Y | Expected pattern | Priority | DOE implication |
| --- | --- | --- | --- | --- |
|  |  |  | high / medium / low | avoid aliasing / confirm later / monitor |

## Design Interpretability

| Item | Decision |
| --- | --- |
| main effects intended for interpretation |  |
| interactions intended for interpretation |  |
| interactions that must be protected from aliasing |  |
| expected design resolution if fractional/PB | III / IV / V / unknown / NA |
| effects that may be aliased or unresolved |  |
| follow-up needed to separate effects | focused factorial / confirmation / RSM / robustness / none |

## Defect / Failure Map

| Defect or failure mode | Related Y | Criticality | Possible causes | Immediate action |
| --- | --- | --- | --- | --- |
|  |  | critical / major / minor / monitor |  | reject / stabilize / inspect / ask engineer |

## Production Burden Map

| X or condition | Production burden | Good direction | Quality risk if moved |
| --- | --- | --- | --- |
|  | time / material / energy / force / thermal / tool stress | lower / higher / target |  |

## First DOE Recommendation Brief

| Item | Decision |
| --- | --- |
| active X |  |
| fixed X |  |
| deferred X |  |
| first DOE mode | 2-factor full / 3-factor full / 4-factor fractional / mixed / other |
| reason rejected alternatives |  |
| primary success criteria |  |
| guardrail reject criteria |  |
| expected next decision | baseline search / confirmation / guardrail stabilization / production improvement |

Execution reliability plan:

| Item | Decision |
| --- | --- |
| center point | included / not included / reason |
| replication plan | full / baseline only / center only / candidate only / none |
| randomization plan | full / partial / fixed order / reason |
| blocking candidates | lot / operator / tool / chamber / time / material / none |
| run-order notes required | yes / no |

Context feasibility check:

| Check | Decision |
| --- | --- |
| Which context_profile was applied? |  |
| Can setup, runs, measurement, recording, and review fit inside the lab window? | yes / no / uncertain |
| What is the maximum realistic run count after buffer? |  |
| What design was rejected because it is too large for the lab window? |  |
| What was simplified to protect execution quality? |  |

Rule:

```text
For the `semiconductor_training_lab_7h` profile, prefer a completed 2-factor
DOE with baseline or repeat evidence over an unfinished 4-factor screening
DOE. Other profiles may justify broader screening, RSM, mixture design, or
production-optimization DOE.
```

## Source Log

| Source | Evidence captured | Confidence |
| --- | --- | --- |
| lecture slide |  | low / medium / high |
| transcript |  | low / medium / high |
| engineer comment |  | low / medium / high |
| experiment data |  | low / medium / high |

## Report Claim Boundary

| Field | Content |
| --- | --- |
| what we found |  |
| what we can claim |  |
| what remains uncertain |  |
| evidence level | 1 / 2 / 3 / 4 / 5 |
| recommendation label | candidate / provisional baseline / confirmed baseline / production candidate / reject |
| confirmation plan |  |
