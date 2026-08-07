# X Candidate Scoring

## Purpose

This document defines how the planner compresses many possible process
parameters into the active factors for the next DOE.

The goal is not to make factor selection look mathematical for its own sake.
The goal is to prevent arbitrary factor choice when experiment count is
limited.

## When To Use

Use this scoring before:

- first DOE design,
- changing from broad screening to focused DOE,
- deciding which factor to fix, defer, or reopen,
- explaining why a 2- or 3-factor DOE was selected instead of a 4-factor
  screening DOE.

## Scoring Axes

Score each candidate X from 1 to 5 unless noted.

| Axis | Question | Score guide |
| --- | --- | --- |
| Mechanism relevance | Can this X physically move the current hard constraint, quality objective, or guardrail? | 1 = weak/unknown, 5 = direct known mechanism |
| Engineer priority | Did an engineer identify it as important? | 1 = dismissed, 3 = unknown, 5 = strongly recommended |
| Controllability | Can it be changed safely and repeatably in the project? | 1 = difficult/unsafe, 5 = easy |
| Measurement linkage | Will the current Y reveal this X's effect? | 1 = hard to observe, 5 = clearly measurable |
| Interaction importance | Is this X part of a suspected important interaction? | 1 = isolated/weak, 5 = key interaction |
| Production relevance | Does this X affect time, material, energy, force, thermal load, or tool burden? | 1 = little, 5 = strong |
| Range confidence | Are DOE-safe levels known and realistic? | 1 = guessed, 5 = engineer-backed/local evidence |
| Risk penalty | Could moving this X create failure, damage, or confounding? | 0 = low risk, -5 = high risk |

Base score:

```text
base_x_score =
  mechanism_relevance
+ engineer_priority
+ controllability
+ measurement_linkage
+ interaction_importance
+ production_relevance
+ range_confidence
+ risk_penalty
```

## Bottleneck Adjustment

The base score is not enough. The planner must adjust it for the current
decision bottleneck.

| Condition | Adjustment |
| --- | ---: |
| X directly improves current bottleneck Y | +4 |
| X plausibly stabilizes a hard guardrail | +4 |
| X mainly improves an already-safe Y | -3 |
| X worsens weakest-margin Y | -4 |
| X is only useful for production before quality passes | -4 |
| X participates in a key unresolved interaction with active X | +2 |

Final score:

```text
final_x_score = base_x_score + bottleneck_adjustment
```

## Selection Status

| Final score | Default status | Meaning |
| ---: | --- | --- |
| 28+ | active | strong factor for the next DOE |
| 22-27 | active or fixed | use if it answers the current DOE purpose |
| 16-21 | deferred or fixed | record for later; avoid spending first-round runs unless needed |
| 10-15 | fixed or monitor | not a main DOE factor |
| < 10 | excluded | not suitable for this DOE |

Override rules:

- If an X controls a critical guardrail, it can be active even with a moderate
  score.
- If an X cannot be safely changed, it cannot be active even with a high score.
- If an X has no measurable Y linkage, it should be deferred until measurement
  is available.
- If a known interaction is central, keep the pair together or explicitly
  state why one side is fixed.

## DOE Mode From X Scores

| Active X after scoring | Recommended first DOE |
| --- | --- |
| 2 active X | 2-factor full factorial with repeats or center/baseline runs |
| 3 active X | 3-factor full factorial if 8 runs are feasible |
| 4 active X with unclear ranking | 4-factor fractional screening |
| 4 active X with one weak/nuisance factor | focused 3-factor DOE, weak factor fixed/deferred |
| key interaction pair dominates | focused interaction DOE on that pair plus one context factor |

Rule:

```text
Do not force 4-factor screening when the scoring table clearly supports a
2- or 3-factor focused DOE.
```

## Required Report Table

Every first DOE recommendation should include this table.

| X | Mechanism | Engineer | Control | Measure | Interaction | Production | Range | Risk | Bottleneck adj. | Final | Status | Reason |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |

The final DOE table should follow only after this factor-selection evidence is
shown.
