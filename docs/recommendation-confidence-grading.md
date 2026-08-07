# Recommendation Confidence Grading

## Purpose

The planner must separate a promising DOE result from a final recommendation.
This grading system gives user-facing confidence labels while preserving the
internal numeric scoring rules.

## Grade Definitions

| Grade | Name | Meaning | Typical use |
| --- | --- | --- | --- |
| A | Confirmed recommendation | Quality specs pass, hard guardrails pass, repeat evidence is acceptable, process mechanism is plausible | final project recommendation |
| B | Project-level recommendation | Quality passes and no critical risk appears, but data is limited or confirmation is partial | practical portfolio/lab conclusion |
| C | Needs next DOE | Average may look good, but margin, repeatability, or guardrail confidence is not enough | run confirmation, margin, or stabilization DOE |
| D | Boundary evidence | Useful for locating fail/pass boundary, but not adoptable | keep as learning evidence |
| F | Reject | Primary spec fails or critical guardrail fails | do not optimize for adoption |

## Hard-Gate Rules

Grades are not weighted averages. Hard gates are checked first.

```text
critical guardrail fail -> F or D
primary spec fail       -> F or D
missing spec/rule       -> cannot finalize
quality pass            -> C/B/A depending on margin and repeatability
```

## Default Grade Logic

| Evidence pattern | Grade |
| --- | --- |
| Any repeated critical failure mode | F |
| Spec fail but useful boundary condition | D |
| Spec pass by mean but worst repeat fails | C |
| Spec pass, guardrail pass, but weakest margin is thin | C |
| Spec pass, guardrail pass, 3/3 repeat pass, mechanism plausible | B |
| B-grade condition repeated in an independent or mixed confirmation DOE | A |
| Production improved but quality margin becomes thin | C or provisional production candidate |
| Production improved and quality remains stable after confirmation | A production candidate |

## Margin Class

Margin class is response-specific. For each primary Y, calculate the worst-case
margin first.

| Margin state | Meaning | Grade effect |
| --- | --- | --- |
| No margin | at or beyond spec boundary | cannot exceed C |
| Thin | small drift can fail spec | usually C |
| Moderate | usable project margin | can reach B |
| Strong | clear margin after repeats | can reach A if confirmed |

For small project data, margin state should use min/max or worst repeated
value, not only average.

## Production Candidate Labels

Production labels are separate from quality grades.

| Label | Meaning |
| --- | --- |
| Quality baseline | quality-safe, but not production-optimized |
| Production candidate | production burden improves while quality remains acceptable |
| Provisional production candidate | production improves, but quality margin or repeatability is limited |
| Over-budget production candidate | production improves but spends too much quality margin |

Example:

```text
Grade B + production candidate = usable project recommendation with production
benefit, but not production-qualified.
Grade C + production gain = follow-up candidate, not final recipe.
```

## Required Report Output

Every final or interim recommendation should include:

| Field | Required content |
| --- | --- |
| Grade | A/B/C/D/F |
| Condition label | baseline, production candidate, boundary, reject |
| Hard-gate status | pass/fail/warning |
| Weakest Y margin | numeric or categorical margin |
| Repeat evidence | pass count, min/max, code distribution |
| Process plausibility | supported, questionable, or unknown |
| Production interpretation | benefit, burden, or not eligible |
| Required next action | conclude, confirm, stabilize, rescue, or reject |

Final sentence template:

```text
This condition is Grade [B] / [project-level recommendation], not Grade [A],
because it passes the current quality and guardrail rules but has only limited
repeat/confirmation evidence.
```
