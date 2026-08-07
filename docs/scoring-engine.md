# DOE Scoring Engine

## Purpose

The scoring engine turns DOE results into consistent internal decisions while
allowing different external display styles.

Core principle:

```text
internal decision = numeric score + hard rules
external display  = selected by output profile
```

The system may calculate 0-100 scores internally, but it does not always need
to show those scores to the user. A presentation may show only grades and key
evidence, while an engineering review may show scores, margins, and formulas.

Process-specific rule sets can refine this generic engine. Current concrete
rule set:

- `docs/wire-bonding-2nd-bond-scoring-rules.md`: 2nd-bond wire bonding
  pull-force / failure-code / ball-shear scoring rules.

Related decision documents:

- `docs/x-candidate-scoring.md`: factor selection before DOE design.
- `docs/recommendation-confidence-grading.md`: user-facing recommendation
  grades after analysis.
- `docs/statistics_ml_interpretation_guidelines.md`: shared statistical
  interpretation guardrails.
- `docs/statistics_experiment_design_principles.md`: DOE-specific decision
  principles for factors, responses, confirmation, and guardrails.

## Governing Principles

The scoring engine must not turn statistical output into an unsupported final
claim. Scores are decision aids, not proof of an optimum.

Required interpretation boundaries:

- hard constraints and guardrails can block a recommendation even when the
  numeric score is high
- production objectives can rank only quality-safe conditions
- p-values, contribution ratios, and score differences must be read with effect
  size, repeatability, and process plausibility
- a recommended condition remains a candidate until confirmation or repeated
  evidence supports it
- small-sample DOE results should be reported with uncertainty and confidence
  grade language
- condition score is not a success probability
- recommendation grade is a decision-confidence label, not a production-yield
  guarantee
- main effects, interactions, aliasing, and execution limits must be carried
  into the final claim boundary
- a robust candidate may be preferred over the highest-mean condition when
  min/max, range, failure code, or guardrail stability is better

Unsafe wording:

```text
condition score 86 means this condition has an 86% success probability.
```

Preferred wording:

```text
condition score 86 means this condition ranks strongly under the current
scoring rules, after hard constraints, guardrails, quality margin, repeatability,
and production objectives are considered.
```

## Overall Pipeline

The correct order is:

```text
1. Y type classification
2. Y decision-role assignment
3. Y-level metric calculation
4. Y-level numeric scoring
5. Hard gate evaluation
6. Group score aggregation
7. Condition state decision
8. Next DOE decision
9. Output profile rendering
```

Do not start from one global quality score. Score each Y according to its
type first, then aggregate.

## Decision Roles Before Scores

The engine must know what each Y is allowed to decide before it calculates a
final condition score.

| Decision role | Internal use | Can it block adoption? | Can it drive optimization? |
| --- | --- | --- | --- |
| Hard constraint | spec pass/fail and margin | yes | only after pass |
| Quality objective | quality improvement direction | sometimes, if tied to spec | yes |
| Guardrail | failure mode, defect case, critical visual risk | yes | no, except stabilization |
| Production objective | time, material, energy, force, tool burden | no | yes, only after quality passes |
| Monitor | explanation or future clue | no | no |

Default aggregation order:

```text
hard constraints
-> guardrails
-> weakest primary quality margin
-> repeatability
-> process plausibility
-> production objective
```

Production score is intentionally late. It can distinguish between two
quality-safe conditions, but it cannot rescue a condition that fails quality or
critical guardrails.

## Focused DOE Decision Score

The same score system should also help choose the next DOE mode. The planner
should not select the next DOE only from the largest contribution ratio.

For each candidate X, calculate or record these decision signals:

| Signal | Meaning |
| --- | --- |
| bottleneck_link | can this X improve the weakest or blocking Y? |
| mechanism_confidence | does the expected X -> Y mechanism make sense? |
| observed_effect | effect size, contribution, rate change, or code shift from DOE data |
| guardrail_risk | does moving this X create bad codes, visual defects, or spec failures? |
| production_value | does moving this X reduce time, material, energy, force, or tool burden? |
| interaction_need | does this X need another X to be interpreted correctly? |
| range_confidence | is the next low/high/local range evidence-backed? |

Next DOE selection uses this priority:

```text
1. If no quality-safe baseline exists, choose baseline search or rescue DOE.
2. If a guardrail blocks adoption, choose guardrail stabilization DOE.
3. If the weakest quality margin is thin, choose conservative confirmation or
   margin-protection DOE.
4. If quality is stable and production burden is high, choose production-
   efficiency or mixed confirmation DOE.
5. If a key interaction is unresolved and affects the bottleneck Y, choose
   focused full factorial on that interaction.
6. If factor ranking is still unclear, choose screening DOE.
```

This makes 2- or 3-factor focused DOE the normal choice when process knowledge
is strong, and 4-factor fractional screening the fallback when the X ranking is
still genuinely uncertain.

## ANOVA and Effect Interpretation

ANOVA output is evidence, not the final recommendation. The scoring engine must
read ANOVA or regression results with engineering context.

Required checks:

- p-value: is the observed effect unlikely under the no-effect assumption?
- effect size: is the effect large enough to matter for spec, quality, or
  production?
- interaction: does the factor effect depend on another factor level?
- repeatability: is the effect stable across repeats or confirmation?
- guardrail: does the condition create a failure mode that overrides the mean?
- process plausibility: does the direction make physical/process sense?

Recommendation logic should not select a condition from p-value alone.

Effect interpretation output should include:

| Field | Required interpretation |
| --- | --- |
| main effect | average factor effect direction and size |
| interaction | whether one factor's effect depends on another factor level |
| aliasing / resolution | whether the current design can separate the effect being discussed |
| execution reliability | whether repeats, center points, randomization, or blocks support the claim |
| claim boundary | what can and cannot be claimed from this DOE |

For fractional factorial or Plackett-Burman designs, factor effects should be
reported as candidate signals unless the alias structure supports stronger
interpretation.

## Robust Candidate Evaluation

The scoring engine should not always select the highest average response.
For quality and risk work, stability can be more valuable than the largest
mean.

Additional robustness signals:

| Signal | Meaning |
| --- | --- |
| min / worst-case margin | whether the weakest observed result still clears spec |
| range or standard deviation | whether the condition is stable across repeats |
| guardrail frequency | whether failure modes appear even when the mean is good |
| noise-factor sensitivity | whether lot, time, operator, chamber, or material changes alter the result |
| S/N-style stability | optional Taguchi-style stability cue, not a hard gate |

Decision rule:

```text
If condition A has the best mean but condition B has acceptable mean, better
worst-case margin, smaller range, and no guardrail failures, condition B may be
the stronger robust candidate.
```

S/N ratio, when used, is a supporting signal only. It must not override hard
constraints, critical guardrails, or physical plausibility.

## Final Report Decision Pack

Every scored DOE result should be renderable into a report pack, not only a
single score.

Required report pack:

| Section | Content |
| --- | --- |
| data quality | missing values, impossible values, run-order issues, repeat availability |
| Y role summary | hard constraints, quality objectives, guardrails, production objectives, monitors |
| condition summary | mean, min/max, range, pass/fail, score, grade |
| effect summary | main effects, interaction candidates, effect size, contribution or ANOVA cue |
| reliability summary | center point, replication, randomization, blocking limitations |
| candidate decision | candidate/provisional baseline/confirmed baseline/production candidate/reject |
| rejected conditions | explicit reason each attractive-looking condition was rejected |
| claim boundary | what was found, what can be claimed, what remains uncertain |
| next action | confirmation, focused interaction DOE, robustness DOE, RSM, or stop |

## Monitoring to DOE Follow-Up

The scoring engine should also accept follow-up questions from Risk AI Engine
monitoring.

Examples:

| Monitoring signal | DOE Planner response |
| --- | --- |
| risk_score distribution shifted upward | identify changed tool/chamber/recipe segments and define follow-up Y |
| feature PSI increased for pressure instability | map the signal to controllable pressure/flow factor candidates |
| FN increased in a specific chamber | propose focused diagnostic DOE or guardrail stabilization DOE |
| watch-zone rate increased after maintenance | recommend data-quality check before DOE, then confirmation if persistent |

Monitoring signals are not root causes. They become DOE candidates only after
mechanism, controllability, safe range, response, and guardrail linkage are
checked.

## Output Profiles

Output profile controls what the user sees.

| Output profile | Intended use | Show |
| --- | --- | --- |
| `presentation` | portfolio / slide / interview | grade, key margin, decision sentence |
| `engineering_review` | process engineer discussion | grade, score, margin, fail reason, risk |
| `full_report` | technical report | score, grade, metric table, formulas, raw summary |
| `debug` | engine development | all intermediate values and rules |

Recommended visibility:

| Item | Presentation | Engineering review | Full report | Debug |
| --- | --- | --- | --- | --- |
| Pass/fail | yes | yes | yes | yes |
| Key margins | yes | yes | yes | yes |
| Numeric score | optional | yes | yes | yes |
| Hard gates | yes | yes | yes | yes |
| Formula details | no | optional | yes | yes |
| Raw repeated data | no | optional | yes | yes |
| Internal rule trace | no | optional | optional | yes |

## Y-Level Internal Record

Every Y should produce the same internal record shape.

| Field | Meaning |
| --- | --- |
| `y_id` | response identifier |
| `y_type` | continuous, ordinal, categorical, count, proportion, image_derived |
| `role` | primary, guardrail, secondary, monitor |
| `metrics` | type-specific calculated values |
| `score` | 0-100 internal score |
| `state` | pass, borderline, fail, reject, monitor |
| `hard_gate` | none, warning, block, reject |
| `evidence` | short explanation |

Example:

| Y | Type | Score | State | Hard gate | Evidence |
| --- | --- | ---: | --- | --- | --- |
| BLT | continuous range | 88 | pass | none | all values inside 35-55 um |
| Die shear | continuous lower-bound | 76 | pass_thin_margin | none | minimum margin +0.85 MPa |
| Void | ordinal guardrail | 100 | pass | none | worst grade 1 |
| Bleed | ordinal guardrail | 55 | borderline | warning | one risky grade |

## Y-Type Metric Calculation

### Continuous Y

Use for BLT, die shear, pull force, ball shear, warpage, thickness, etc.

Required metrics:

| Metric | Meaning |
| --- | --- |
| mean | average response |
| min | worst low value |
| max | worst high value |
| std | repetition spread when useful |
| margin | spec margin based on spec type |
| pass_count | number of repeated passes |
| capability_index | Cp/Cpk or one-sided capability when enough repeated data exists |

Spec-specific margin:

| Spec type | Margin |
| --- | --- |
| lower-bound | `min(Y) - LSL` |
| upper-bound | `USL - max(Y)` |
| range | `min(min(Y)-LSL, USL-max(Y))` |
| target | distance from target plus tolerance rule |

Scoring guide:

| Result | Score |
| --- | ---: |
| hard spec fail | 0-30 |
| pass but very thin margin | 40-60 |
| pass with moderate margin | 60-80 |
| pass with strong margin | 80-100 |

For small samples, use worst-case margin before mean.

### Process Capability Metrics

Use Cp/Cpk after the system has enough repeated measurement data for a
candidate condition. Cp/Cpk is a production-readiness metric, not a substitute
for DOE screening.

Basic formulas:

```text
Cp  = (USL - LSL) / (6 * sigma)
Cpk = min((USL - mean) / (3 * sigma), (mean - LSL) / (3 * sigma))
```

For one-sided specs:

```text
Cpl = (mean - LSL) / (3 * sigma)
Cpu = (USL - mean) / (3 * sigma)
```

Use by spec type:

| Spec type | Metric |
| --- | --- |
| lower-bound, e.g. pull force >= 7 g | Cpl |
| upper-bound, e.g. warpage <= limit | Cpu |
| range, e.g. BLT 35-55 um | Cp and Cpk |
| target +/- tolerance | Cpk plus target distance |

Sample-size rule:

| Repeats for a condition | Capability interpretation |
| ---: | --- |
| 1-3 | do not calculate as decision evidence; report margin/min/max only |
| 4-9 | provisional only; useful for warning, not final claim |
| 10-32 | screening reference only; do not present as a formal process-capability claim |
| 33+ | capability becomes more credible, but still requires stable and representative sampling |

Decision rule:

```text
If Cpk is weak, the condition may pass the current DOE samples but still be
poor as a production baseline because variation can consume the spec margin.
```

For short DOE rounds, especially n=10 per condition, the planner may still
calculate Cpu/Cpl/Cpk numerically for traceability, but the report must label
the value as a reference indicator. The next DOE decision should prioritize
spec pass/fail, worst-case or p95 risk, margin, measurement confidence, and
process mechanism before treating capability as a formal adoption metric.

Cp/Cpk is not used for categorical failure code, ordinal defect grade, or
count/rate Y. Those Y types keep their own bad-code rate, worst-grade, defect
count, or pass-rate logic.

### Ordinal Grade Y

Use for void grade, bleed grade, chipping severity grade, visual defect grade.

Required metrics:

| Metric | Meaning |
| --- | --- |
| worst_grade | maximum observed severity |
| risky_count | number of risky observations |
| pass_count | number of acceptable observations |
| grade_distribution | count by grade |

Scoring guide:

| Result | Score |
| --- | ---: |
| critical grade appears | 0-30 |
| risky grade appears once | 40-60 |
| borderline but acceptable grades | 60-80 |
| all grades acceptable | 80-100 |

Rule:

```text
Ordinal guardrails are controlled by worst grade, not average grade.
```

### Categorical Y

Use for pull failure code, ball shear case, failure reason, defect type.

Required metrics:

| Metric | Meaning |
| --- | --- |
| good_code_count | acceptable cases |
| bad_code_count | unacceptable cases |
| bad_code_rate | bad count / total |
| worst_code | most severe code observed |
| mode_distribution | count by category |

Scoring guide:

| Result | Score |
| --- | ---: |
| critical code appears | 0-30 |
| bad code appears but not critical | 40-60 |
| all acceptable but borderline mode appears | 60-80 |
| all acceptable modes | 80-100 |

### Count Y

Use for chipping count, crack count, void count, defect count.

Required metrics:

| Metric | Meaning |
| --- | --- |
| count | observed defect count |
| opportunity_count | inspected dies, chips, area, or images |
| density | count / opportunity |
| change_vs_baseline | reduction or increase |

Scoring guide:

| Result | Score |
| --- | ---: |
| count exceeds hard limit | 0-30 |
| count/density high vs baseline | 40-60 |
| count/density acceptable | 60-80 |
| count/density clearly improved | 80-100 |

Rule:

```text
Count Y must include denominator or inspection opportunity.
```

### Proportion / Rate Y

Use for void ratio, defect rate, pass rate, yield rate.

Required metrics:

| Metric | Meaning |
| --- | --- |
| numerator | defect/pass count |
| denominator | total inspected |
| rate | numerator / denominator |
| difference_vs_baseline | rate change |

Scoring should account for denominator size. A 1/2 result is much weaker than
a 10/20 result even if the rate is the same.

### Image-Derived Y

Use when a photo or microscope image is converted into a measurement.

First convert the image into one of:

- continuous Y, e.g. void area percent,
- ordinal Y, e.g. chipping grade,
- count Y, e.g. number of chips,
- proportion Y, e.g. defect area / total area.

Then route it through the corresponding scoring logic.

## Hard Gates

Hard gates are not weighted averages. They can override numeric scores.

| Gate | Example | Result |
| --- | --- | --- |
| critical guardrail fail | bad failure code, destructive crack, void grade above allowed limit | reject |
| primary spec fail | die shear below LSL, BLT outside range | fail/rescue target |
| missing decision rule | Y has no spec or acceptable grade rule | cannot finalize |
| baseline repeat failure | baseline fails inside mixed DOE | improvement candidates cannot be finalized |

Rule:

```text
If hard gate = reject, production score cannot rescue the condition.
```

## Group Score Aggregation

After Y-level scoring, aggregate into group scores.

| Group score | Inputs |
| --- | --- |
| Quality score | primary numeric Y values |
| Guardrail score | categorical/ordinal/count/rate hard-risk Y values |
| Repeatability score | pass count, repeated fail pattern, spread |
| Process plausibility score | match between result and process knowledge |
| Production score | time, material, force, energy, tool burden |

Recommended aggregation:

| Group | Aggregation |
| --- | --- |
| Quality | weakest primary Y score, with average as secondary |
| Guardrail | worst guardrail score |
| Repeatability | pass-count score plus repeated failure penalty |
| Process plausibility | lowest mechanism confidence for active conclusion |
| Production | weighted benefit among quality-acceptable candidates |

Use weakest-link aggregation for quality-critical decisions.

```text
quality is only as strong as the weakest primary Y
guardrail is only as strong as the worst hard-risk Y
```

## Repeatability Score

Repeatability is calculated across repeated observations and across DOE rounds
when available.

| Pattern | Score |
| --- | ---: |
| all repeats pass, no guardrail issue | 80-100 |
| one noncritical borderline event | 60-80 |
| one hard fail in three repeats | 30-60 |
| repeated same fail mode | 0-40 |

For `n >= 5`, the engine may add:

```text
lower_bound = mean - 2 * std
upper_bound = mean + 2 * std
```

For small project DOE, pass count and worst-case evidence are more important
than p-value.

## Process Plausibility Score

Process plausibility compares the observed result with the process knowledge
database.

| Evidence | Score |
| --- | ---: |
| trend matches known mechanism | 80-100 |
| trend is plausible but risky | 60-80 |
| trend is weak but not contradictory | 40-60 |
| trend conflicts with mechanism | 20-40 |
| mechanism unknown | 40 with engineer-review flag |

Examples:

| Trend | Process interpretation | Decision impact |
| --- | --- | --- |
| lower epoxy lowers BLT | matches volume mechanism | supports direction |
| lower wetting time increases void | matches wetting/settling mechanism | reject reduction if guardrail fails |
| higher force does not compensate low epoxy | plausible limitation | do not keep increasing force blindly |
| high force with bad failure code | mechanism risk overrides numeric strength | reject or stabilize |

## Production Score

Production score is evaluated only after quality and hard guardrails pass.

| Production item | Good direction |
| --- | --- |
| process time | lower |
| material usage | lower |
| force / energy | lower if quality preserved |
| temperature / thermal load | lower if quality preserved |
| tool stress | lower |

Production score interpretation:

| Result | Score |
| --- | ---: |
| quality fails | not evaluated for adoption |
| quality passes, production burden high | 40-60 |
| quality passes, burden acceptable | 60-80 |
| quality passes, burden clearly improved | 80-100 |

## Quality Margin Budget

After a condition passes primary quality specs, the remaining quality margin is
treated as a limited budget. Production improvement is allowed only if it does
not spend that budget too aggressively.

Core rule:

```text
First satisfy quality.
Then treat remaining quality margin as the budget for production improvement.
If production improvement consumes the weakest quality margin too much, keep
the baseline or run confirmation instead of adopting the improved condition.
```

For each primary Y, calculate a worst-case margin from repeated observations.

| Y spec type | Margin budget |
| --- | --- |
| Upper-bound, lower-is-better | `USL - max(Y)` |
| Lower-bound, higher-is-better | `min(Y) - LSL` |
| Range spec | `min(min(Y)-LSL, USL-max(Y))` |
| Ordinal guardrail | `allowed_worst_grade - observed_worst_grade` |
| Categorical guardrail | acceptable-rate or zero-critical-event rule |

Then classify the weakest margin.

| Weakest margin state | Meaning | Production action |
| --- | --- | --- |
| No budget | pass/fail boundary or guardrail touched | no adoption; repeat or stabilize |
| Thin budget | pass but a small drift can fail | only small-step efficiency DOE |
| Moderate budget | some quality margin remains | mixed DOE with baseline repeats |
| Strong budget | quality has clear margin and repeatability | production-efficiency DOE allowed |

The budget is not a new objective score that can hide failures. It is a gate
that limits how much production benefit can be pursued after quality passes.

Example from molding:

| Condition | Quality state | Production state | Decision |
| --- | --- | --- | --- |
| A=0.60 | robust pass | slower injection | confirmed quality baseline |
| A=0.65 | pass but void margin thin | slight time gain | follow-up candidate, not final without confirmation |
| A=0.70 | faster injection | void failures appear | reject production-improvement direction |

## Condition State Decision

Condition state is decided from hard gates and group scores.

User-facing A/B/C/D/F recommendation grades are defined separately in
`docs/recommendation-confidence-grading.md`. The state labels below are the
workflow states used by the engine.

| State | Rule |
| --- | --- |
| Rejected boundary | hard guardrail fail or primary spec fail, but useful for boundary learning |
| Not usable | unstable, unsafe, or off-spec without clear boundary value |
| Candidate | one DOE result looks promising |
| Provisional baseline | passes enough to use as reference under limited budget |
| Confirmed baseline | repeated baseline pass across independent or mixed DOE |
| Production candidate | confirmed baseline plus production burden acceptable |

Suggested score thresholds:

| State | Quality | Guardrail | Repeatability | Process | Production |
| --- | ---: | ---: | ---: | ---: | ---: |
| Candidate | `>= 70` | `>= 70` | `>= 50` | `>= 50` | any |
| Provisional baseline | `>= 75` | `>= 80` | `>= 70` | `>= 60` | any |
| Confirmed baseline | `>= 75` | `>= 85` | `>= 80` | `>= 60` | any |
| Production candidate | `>= 75` | `>= 85` | `>= 80` | `>= 60` | `>= 60` |

Thresholds are defaults. A process-specific knowledge file can override them.

## Next DOE Decision From Scores

| Score / gate pattern | Next DOE |
| --- | --- |
| no usable quality pass | baseline search or rescue DOE |
| primary quality low | bottleneck-Y rescue DOE |
| guardrail low | guardrail stabilization DOE |
| repeatability low | confirmation or local robustness DOE |
| process plausibility low | mechanism confirmation or engineer review |
| confirmed baseline, production score low | production-efficiency DOE |
| production-efficiency DOE fails by guardrail | terminate improvement direction or redesign mechanism |
| confirmed baseline and no acceptable improvement | final recommendation |

## External Rendering Examples

Internal record:

| Y | Score | State | Evidence |
| --- | ---: | --- | --- |
| BLT | 88 | pass | inside 35-55 um |
| Die shear | 76 | pass_thin_margin | min margin +0.85 MPa |
| Void | 100 | pass | worst grade 1 |
| Bleed | 55 | borderline | one grade 2 event |

Presentation output:

```text
Quality mostly passed, but bleed guardrail was borderline. The condition is
not final; it needs confirmation or a safer recipe.
```

Engineering review output:

| Y | Score | Margin / worst case | State |
| --- | ---: | --- | --- |
| BLT | 88 | closest margin +4.5 um | Pass |
| Die shear | 76 | min margin +0.85 MPa | Pass, thin margin |
| Bleed | 55 | worst grade 2 | Borderline |

Full report output includes the formulas, raw repeated data, and score trace.

## Example: Die Attach Time-Reduction DOE

Final baseline condition:

`A=0.85, B=425 gf, C=800 ms, D=12 sec`

Internal interpretation:

| Score group | Class |
| --- | --- |
| Quality | high: BLT and die shear passed repeatedly |
| Guardrail | high: void/bleed stayed within allowed grade for baseline |
| Repeatability | high: repeated pass across later DOE rounds |
| Process plausibility | high: result matches epoxy/force/time mechanism |
| Production | medium: epoxy and force acceptable, but C/D time is long |

Time-reduction candidates:

| Direction | Score issue | Decision |
| --- | --- | --- |
| Reduce C | bleed/shear risk | reject or defer |
| Reduce D | void/shear risk | reject or defer |
| Reduce C and D together | shear and bleed risk | reject |

Final report sentence:

```text
Recommend A=0.85, B=425 gf, C=800 ms, D=12 sec as a confirmed baseline.
Do not claim production optimum. Cycle-time reduction is deferred because the
time-reduction conditions created shear, void, or bleed risk.
```
