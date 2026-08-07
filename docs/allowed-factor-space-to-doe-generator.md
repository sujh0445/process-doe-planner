# Allowed Factor Space To DOE Generator

## Purpose

The DOE generator should not directly use every factor and range mentioned by the user.

It should only use the allowed factor space produced by validation and risk gating.

```text
Structured request
-> validation/risk gate
-> allowed factor space
-> DOE mode selection
-> DOE matrix
-> metrology plan
```

## Core Concepts

| Concept | Meaning |
| --- | --- |
| candidate factor | A variable that may affect Y |
| active factor | A variable selected for the next DOE |
| fixed factor | A variable held constant because of risk, low priority, or strategy |
| deferred factor | A variable not used now but tracked for later |
| allowed factor space | The range the DOE generator is allowed to use |
| practical DOE range | The narrower low/high or multi-level range selected for this DOE |

## Factor Selection Logic

Factors should be selected using:

1. controllability
2. expected process mechanism
3. expected interaction risk
4. impact on bottleneck Y
5. measurement feasibility
6. run budget
7. production relevance

This is different from simply selecting every factor that is available.

## DOE Mode Selection

| Situation | Recommended DOE mode |
| --- | --- |
| Many uncertain factors, low process confidence | Screening or fractional factorial |
| 2 to 3 key factors already known | Focused full factorial |
| Need to separate interaction from main effect | Full factorial or targeted interaction DOE |
| Good baseline exists and production improvement is the goal | Mixed confirmation DOE |
| One factor is productivity lever and quality margin is known | One-factor sweep with guardrails |
| Strong nonlinear suspicion | Add center point or RSM-style refinement |
| Measurement confidence is weak | Repeat/confirmation before aggressive range expansion |

## Level Selection Rules

Low/high values should be chosen from the allowed factor space, not from equipment limits by default.

| Level type | When to use |
| --- | --- |
| 2-level low/high | Screening or main-effect direction check |
| 3-level low/mid/high | Curvature or safe refinement check |
| center point | Repeatability, curvature, and baseline stability check |
| mixed levels | When one factor needs sweep and others need confirmation |
| fixed value | When factor is not current bottleneck or is used as a safe anchor |

## Interaction And Aliasing Rule

If run count is limited, not every interaction can be separated.

Before creating a fractional or reduced DOE, the planner should list:

- expected important interactions
- interactions intentionally protected
- interactions that may be aliased
- interactions to resolve in a later DOE

Example:

```text
Wire bonding:
- US power x US time may represent total ultrasonic energy
- US power x bond force may affect stitch bond deformation

Therefore, avoid a design where these interactions are blindly hidden under residual error.
```

## DOE Matrix Output Fields

Each generated DOE matrix should include:

| Field | Meaning |
| --- | --- |
| run_id | Experiment run number |
| factor settings | Actual values and coded values |
| fixed factors | Values intentionally held constant |
| randomization_group | If run order should be randomized or blocked |
| repeat_count | Planned repeats per run |
| measurement_plan_id | Link to metrology plan |
| design_reason | Why this run exists |
| alias_note | Relevant aliasing or interaction limitations |

## Metrology Plan

The DOE table must be paired with a measurement plan.

| Field | Meaning |
| --- | --- |
| Y name | Response variable |
| measurement tool | Pull tester, high scope, X-ray, profilometer, etc. |
| sample count | Number of samples per condition |
| sampling rule | How samples are chosen |
| aggregation rule | mean, max, p95, pass rate, worst code, etc. |
| known measurement risk | Manual selection, low repeat count, image ambiguity |

## Generator Contract

The DOE generator should return both a matrix and a rationale.

```text
DOE matrix alone is not enough.
The planner must explain why this DOE mode, these factors, and these levels were selected.
```

## Implementation Note

For MVP implementation:

- use deterministic Python generation for full factorial and simple mixed DOE
- use a structured schema for DOE matrix output
- store the design rationale with the matrix
- add pyDOE3 or similar only when fractional/RSM generation becomes necessary
