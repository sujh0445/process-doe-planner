# DOE Evidence Report Format

## Purpose

The planner must not only recommend the next DOE. It must show why the
recommendation follows from the data, statistics, process mechanism, and
production constraints.

The detailed recommendation rules are defined in
`docs/next-doe-recommendation-logic.md`. This report format is the presentation
surface for those rules.

Use these companion documents:

- `docs/x-candidate-scoring.md` before first DOE or factor changes.
- `docs/process-knowledge-card-template.md` when converting lecture/engineer
  knowledge into reusable process records.
- `docs/recommendation-confidence-grading.md` when labeling final or interim
  recommendations.

The report should answer this presentation question:

> Why did the system recommend this next DOE direction from these results?

## Report Flow

Every analysis report should follow the same evidence chain:

```text
1. Experiment summary
2. Y-type classification
3. Response-level statistical evidence
4. Multi-Y trade-off summary
5. Process-mechanism validation
6. Production/manufacturing validation
7. Baseline decision
8. Next DOE direction decision
9. Proposed next DOE table
10. Remaining risk / required confirmation
```

## 1. Experiment Summary

Show what was actually tested before interpreting anything.

Required output:

| Item | Content |
| --- | --- |
| DOE round | 1st DOE, confirmation DOE, mixed DOE, etc. |
| DOE purpose | baseline search, improvement, robustness, boundary check |
| Factors | X names, units, tested levels |
| Responses | Y names, units, Y type, spec |
| Runs / repetitions | number of conditions and repetitions |
| Known constraints | limited time, unavailable measurement, visual inspection only |

## 2. Y-Type Classification

Before selecting statistics, classify each Y.

| Y | Type | Spec / target | Analysis family | Role |
| --- | --- | --- | --- | --- |
| BLT | continuous | 35-60 um, lower within spec preferred | effect / ANOVA / regression | primary |
| Die shear | continuous | >= 22 MPa | effect / ANOVA / regression | primary |
| Failure code | categorical | critical codes forbidden | code frequency / guardrail | hard guardrail |
| Chipping count | count | lower is better | count effect / Poisson or NB when enough data | primary |
| Defect rate | proportion | lower is better | proportion / binomial | primary |

The report should explicitly say:

```text
Y is continuous, so effect/ANOVA/regression is appropriate.
Y is categorical/count/rate, so ANOVA alone is not appropriate.
```

## 3. Response-Level Statistical Evidence

For each Y, show evidence in a structured block.

### Continuous Y

Required tables:

1. Condition summary

| Run | X condition | mean | min | max | standard deviation | spec margin | pass count |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |

2. Main effect table

| Factor | low mean | high mean | effect | direction | contribution | interpretation |
| --- | ---: | ---: | ---: | --- | ---: | --- |

3. ANOVA / pooled-effect table where applicable

| Term | Effect | SS | df | MS | F / score | Contribution | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |

4. Regression / prediction table when useful

| Model term | Coefficient | Meaning | Keep / drop |
| --- | ---: | --- | --- |

### Categorical Y

Required tables:

| Condition | Good code count | Bad code count | Bad-code rate | Worst code | Guardrail decision |
| --- | ---: | ---: | ---: | --- | --- |

### Count Y

Required tables:

| Condition | Inspected count / area | Defect count | Defect rate or density | Count reduction | Decision |
| --- | ---: | ---: | ---: | ---: | --- |

### Proportion Y

Required tables:

| Condition | Numerator | Denominator | Rate | Difference vs baseline | Decision |
| --- | ---: | ---: | ---: | ---: | --- |

## 4. Multi-Y Trade-Off Summary

The planner should not optimize one Y while hiding damage to another Y.

Required output:

| Candidate | Y1 result | Y2 result | Guardrail | Production metric | Trade-off decision |
| --- | --- | --- | --- | --- | --- |

Also include a plain-language trade-off statement:

```text
Increasing A improves shear but increases BLT and material usage.
Reducing A improves BLT/material usage but consumes shear margin.
Increasing B does not compensate enough and may reduce BLT lower margin.
```

## 5. Process-Mechanism Validation

For each major statistical conclusion, verify whether it makes process sense.

| Statistical finding | Process explanation | Plausibility | Risk |
| --- | --- | --- | --- |
| Epoxy reduction lowers BLT | Less adhesive volume leaves thinner bond line | high | shear margin may decrease |
| Higher force lowers BLT | More compression spreads/squeezes epoxy | high | bleed/too-thin BLT risk |
| Longer time raises strength | More wetting/settling/cure opportunity | medium | process time penalty |

The system should label each finding as:

- statistically supported and process-plausible,
- statistically supported but process-questionable,
- process-plausible but statistically weak,
- unsupported / needs confirmation.

## 6. Production / Manufacturing Validation

After quality pass, evaluate production practicality.

| Candidate | Quality status | Time impact | Material impact | Tool/process burden | Production decision |
| --- | --- | ---: | ---: | --- | --- |

Production metrics are secondary unless quality is already acceptable.

Decision order:

```text
quality guardrail
-> primary Y margin
-> repeatability
-> production efficiency
-> final candidate ranking
```

## 7. Baseline Decision

The report must explicitly decide whether a condition can be used as the next
reference point.

| Candidate | Spec pass | Failure mode | Weakest margin | Process plausible | Production burden | Baseline decision |
| --- | --- | --- | ---: | --- | --- | --- |

Baseline decision language:

- candidate,
- provisional baseline,
- confirmed baseline,
- production candidate,
- conservative fallback,
- not usable yet.

Also show the user-facing confidence grade:

| Grade | Meaning |
| --- | --- |
| A | confirmed recommendation |
| B | project-level recommendation |
| C | needs next DOE |
| D | boundary evidence |
| F | reject |

The report should not use "confirmed baseline" unless repeated evidence exists.
If the planner skips a pure confirmation DOE because experiment time is
limited, the report must say:

```text
This is a provisional baseline. The next mixed DOE includes baseline repeats
to check whether the reference condition remains stable.
```

## 8. Next DOE Direction Decision

Show why the recommended next DOE mode was chosen.

| Possible next DOE | Reason to choose | Reason rejected / accepted |
| --- | --- | --- |
| Rescue DOE | if spec fails | rejected if baseline passes |
| Robustness DOE | if baseline is good but repeatability unknown | accepted if margin is enough but reliability uncertain |
| Production-efficiency DOE | if quality margin is enough and time/material burden can improve | accepted after quality pass |
| Mixed DOE | if budget is limited and several directions must be tested at once | accepted when conservative/aggressive/boundary candidates are all useful |
| Interaction confirmation DOE | if a suspected interaction controls the result | accepted when aliasing or mechanism suggests interaction |
| RSM / local optimization | if smooth optimum search is justified | rejected when sample budget or baseline confidence is too low |

The report should include a final decision sentence:

```text
The next DOE is a mixed confirmation DOE because the baseline is usable,
quality margins exist, experiment budget is limited, and the main uncertainty
is how far material usage can be reduced before shear or BLT guardrails fail.
```

Also include the rejected options:

| Rejected option | Why rejected |
| --- | --- |
| Pure confirmation DOE | experiment budget too limited, but baseline repeats are included in mixed DOE |
| Pure production-efficiency DOE | baseline not yet confirmed or guardrail recently failed |
| Aggressive optimization | weakest Y margin is too small |
| More broad screening | usable baseline already exists; current question is local stability or efficiency |

## 9. Proposed Next DOE Table

The DOE table must include purpose per run, not only X settings.

| Run | A | B | C | D | Purpose |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | baseline | baseline | baseline | baseline | baseline repeat |
| 2 | conservative | baseline | baseline | baseline | safe improvement |
| 3 | aggressive | baseline | baseline | baseline | efficiency limit |
| 4 | aggressive | compensation | baseline | baseline | compensation check |
| 5 | boundary | baseline | baseline | baseline | failure boundary |

This lets the presenter explain why every run exists.

For mixed DOE, use this run-purpose vocabulary:

| Purpose label | Meaning |
| --- | --- |
| baseline repeat | confirms reference condition in the same round |
| conservative improvement | small step toward production or quality benefit |
| moderate improvement | larger but still mechanism-plausible step |
| aggressive boundary | tests the likely failure boundary |
| guardrail check | specifically probes void, bleed, failure code, or defect risk |
| fallback candidate | more conservative recipe if the efficient condition fails |

The table should be followed by expected decision rules:

| Result pattern | Next action |
| --- | --- |
| baseline repeat fails | stop improvement interpretation and investigate baseline instability |
| improvement condition passes but margin is thin | classify as candidate, not final |
| improvement condition fails by guardrail | reject direction or use smaller step |
| conservative and aggressive both pass | choose by production benefit after confirming margin |
| conservative passes, aggressive fails | set boundary between them |

## 10. Remaining Risk / Required Confirmation

Every final recommendation should state what is not proven yet.

| Risk | Why it matters | Required confirmation |
| --- | --- | --- |
| Small repetition count | 3 repeats cannot prove production stability | repeat final candidate |
| Visual judgement | subjective pass/fail can vary by inspector | define image/grade rule |
| Hidden interaction | fractional DOE aliases interactions | focused follow-up DOE |
| Production transfer | lab tool does not equal mass-production line | engineer review / pilot run |

## 11. Final Conclusion Block

Every completed DOE sequence should end with a concise conclusion block.

Required output:

| Item | Content |
| --- | --- |
| Final recommended condition | X values and units |
| Decision label | confirmed baseline, production candidate, etc. |
| Quality evidence | pass count, margins, guardrails |
| Production evidence | time/material/force/cost interpretation |
| Rejected improvements | tested directions and why they failed |
| Residual risk | what remains unproven |
| Follow-up if more time exists | exact next DOE type or measurement need |

Example:

```text
Recommend A=0.85, B=425 gf, C=800 ms, D=12 sec as a confirmed baseline.
It repeatedly passed BLT, die shear, void, and bleed guardrails. Attempts to
reduce bond time and wetting time produced low-shear, void, or bleed risk, so
cycle-time optimization is deferred. The condition is quality-defensible but
not proven to be production-optimal.
```

## Example Final Evidence Chain

```text
The initial DOE found a usable baseline.
The baseline passed BLT and shear, but epoxy usage was high.
The follow-up DOE showed epoxy amount was the most actionable efficiency lever.
Reducing epoxy improved BLT/material usage but consumed shear margin.
The mixed DOE showed A=1.00, B=650 passed repeatedly, while A=0.95 produced
low-shear failures.
Force increase did not reliably compensate and reduced BLT lower margin.
Therefore the recommended final aggressive condition is A=1.00, B=650, C=300,
D=3, with A=1.05, B=650, C=300, D=3 as the conservative backup.
```
