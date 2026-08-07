# Next DOE Recommendation Logic

## Purpose

This document defines how the planner uses project-specific decision criteria,
then combines statistical evidence, process mechanism evidence, and production
evidence to choose the next DOE direction and factor ranges.

The planner should not choose the next DOE by intuition. It should make a
traceable decision:

```text
DOE project definition
-> project-specific decision criteria
-> criteria state evaluation
-> statistical evidence for each criterion
-> process plausibility check
-> production trade-off check
-> next DOE purpose
-> factor/range selection
```

Supporting documents:

- `docs/x-candidate-scoring.md` defines how candidate X values are compressed
  into active/fixed/deferred factors.
- `docs/recommendation-confidence-grading.md` defines final A/B/C/D/F
  confidence labels.
- `docs/spc-control-chart-risk-doe-integration.md` defines how control-chart
  stability evidence gates DOE purpose selection.

## 0. Decision Criteria Layer

The planner does not start from "which statistical method should I use?" It
starts from "what does this DOE project need to decide?"

Decision criteria are generated from:

- process goal,
- Y type and Y role,
- quality spec or guardrail,
- worst-case / tail-risk definition,
- production objective,
- measurement confidence,
- mechanism hypotheses.

The criteria become the routing surface for the next DOE.

| Criteria state | Meaning | Next DOE implication |
| --- | --- | --- |
| hard gate fail | a critical spec or defect rule failed | stabilize, isolate, or avoid the direction |
| hard gate pass but thin margin | condition works but may be fragile | confirmation or margin-improvement DOE |
| hard gate pass with sufficient margin | baseline is usable | productivity or local refinement DOE may be allowed |
| tail risk unresolved | mean looks acceptable but worst-case is risky | repeat, sampling, or guardrail DOE |
| trade-off unresolved | one Y improves while another worsens | mixed confirmation DOE |
| measurement confidence weak | data collection cannot support adoption | measurement-focused repeat or simplified DOE |
| mechanism conflict | statistical trend disagrees with process expectation | mechanism-check DOE before optimization |

Statistical, process, and production analyses are evidence layers used to score
or explain each criterion. They are not the criteria themselves.

## 1. Evidence Layers

After decision criteria are selected, each candidate factor direction is
evaluated through three evidence layers.

| Layer | Question | Output |
| --- | --- | --- |
| Statistical evidence | Did the data show an effect, contribution, trend, or risk? | strength and direction |
| Process evidence | Does the trend make physical/process sense? | plausibility and failure mechanism |
| Production evidence | Does the direction help time, material, throughput, tool burden, or cost? | benefit/risk |

The planner should only make a strong next-DOE recommendation when these
layers are aligned or when the conflict is explicitly handled by the DOE
design.

## 1.0 Mandatory Recommendation Report

Every next-DOE recommendation must start with a compact decision report. The
DOE table is the final output of the decision, not the starting point.

Minimum report:

| Item | Required answer |
| --- | --- |
| DOE purpose | what this next DOE is trying to prove |
| Current baseline state | candidate, provisional baseline, confirmed baseline, production candidate, or not usable |
| Decision criteria used | project-specific criteria used for this recommendation |
| Criteria source / assumptions | spec, engineer comment, project goal, measurement constraint, or planner assumption |
| Criteria result summary | pass/watch/fail state for each criterion |
| Primary Y state | pass/fail, weakest margin, and worst repeated value |
| Secondary Y state | production/time/material burden and whether it is eligible to influence the decision |
| Bottleneck Y | the Y currently blocking adoption or improvement |
| Statistical evidence | effect, contribution, regression direction, interaction, or defect-rate signal |
| Process evidence | mechanism that supports or challenges the statistical trend |
| Production evidence | benefit and risk of the proposed direction |
| Active factors | factors to move and the reason for each |
| Fixed factors | factors to hold and the reason for each |
| Candidate comparison | baseline versus proposed candidates using quality margin and production benefit |
| Success criteria | numeric or categorical criteria for accepting the next DOE result |
| Reject criteria | numeric or categorical criteria for stopping that direction |

The planner must explicitly say when evidence is weak. In that case the DOE
purpose should be labeled as exploratory, confirmation, or boundary learning,
not final optimization.

Add this SPC state block when current or recent process data is available:

| Item | Required answer |
| --- | --- |
| Stability state | stable, OOC-like, OOS-like, variance-limited, or unknown |
| Weakest margin | the limiting spec/guardrail margin, using worst repeat when possible |
| Variation state | stable, widened, trend, cycle, run, or segment-specific |
| Subgroup quality | rational, mixed, unknown, or insufficient |
| DOE gate result | optimize, confirm, stabilize, isolate, or contain |

## 1.1 Bottleneck-Y Routing Before Factor Ranking

Before ranking factors, the planner must identify the response that currently
blocks the decision.

The largest contribution factor is not automatically the next DOE factor.
It may be improving a Y that is already acceptable.

Required routing:

```text
all Y results
-> evaluate project-specific decision criteria
-> convert each criterion to pass / watch / fail / unknown
-> identify bottleneck Y
-> find X factors that plausibly move that bottleneck Y
-> select active factors and ranges
```

Factor ranking is therefore response-specific:

| Question | Use |
| --- | --- |
| Which X has the largest effect on any Y? | overall statistical description only |
| Which X has the largest effect on the bottleneck Y? | next DOE factor candidate |
| Which X is process-plausible for the bottleneck mechanism? | active factor priority |
| Which X only improves an already-safe Y? | fix, monitor, or use later for efficiency |

Example rule:

```text
If pull force passes with high margin but pull failure code is unstable,
do not keep optimizing the force-driving factor only.
Re-route the next DOE to failure-code stabilization factors such as US time,
force time, contact force balance, and suspected interaction terms.
```

## 2. Statistical Evidence Score

For each X and each Y, classify the statistical evidence.

### Continuous Y

Inputs:

- main effect size,
- contribution ratio / SS share,
- ANOVA or pooled-effect decision when valid,
- regression coefficient direction,
- interaction signal,
- repeat stability: mean, min, max, standard deviation,
- spec margin impact.

Statistical evidence classes:

| Class | Rule of thumb | Meaning |
| --- | --- | --- |
| Strong | large effect, high contribution, repeated direction, spec margin changes materially | reliable enough to drive next DOE |
| Moderate | visible effect but contribution or repeatability is limited | include as candidate or local check |
| Weak | small effect near noise or inconsistent direction | fix, drop, or monitor only |
| Risk signal | average looks good but min/failure/margin is weak | guardrail or confirmation needed |

### Categorical / count / proportion Y

Inputs:

- pass/fail count,
- bad-code count,
- defect count,
- defect rate,
- worst code / worst grade,
- denominator such as inspected chip count or area,
- repeated occurrence of the same failure mode.

Evidence classes:

| Class | Rule of thumb | Meaning |
| --- | --- | --- |
| Strong bad signal | critical failure appears or defect rate clearly worsens | avoid direction or run guardrail DOE |
| Moderate bad signal | noncritical failures increase | include boundary/confirmation run |
| Strong good signal | pass rate improves and bad-code/defect count decreases | direction can be explored |
| Inconclusive | too few opportunities or inconsistent codes | repeat or classify better |

## 3. Process Plausibility Score

Statistical effects are checked against process knowledge.

| Class | Meaning | Action |
| --- | --- | --- |
| Plausible | direction matches known mechanism | can support next DOE |
| Plausible but risky | mechanism explains improvement and possible damage | include guardrail/boundary runs |
| Questionable | data trend does not match mechanism | confirm before optimizing |
| Unknown | mechanism not known yet | ask engineer / collect more process info |

Example:

| Finding | Process check | Decision |
| --- | --- | --- |
| Lower epoxy lowers BLT | plausible because less adhesive volume forms a thinner bond line | explore reduction |
| Higher force lowers BLT | plausible due to compression/spreading | watch lower BLT and bleed risk |
| Higher force compensates low epoxy shear | questionable if data does not show shear recovery | do not assume compensation |

## 4. Production Evidence Score

Production evidence is only allowed to decide among quality-acceptable
candidates.

| Production factor | Typical interpretation |
| --- | --- |
| Lower process time | throughput benefit |
| Lower material usage | cost and contamination benefit |
| Lower force/energy/temperature | tool/material stress benefit |
| Higher force/energy/temperature | possible damage, wear, or reliability risk |
| Longer wait/cure/time | throughput burden |

Production decision rule:

```text
If quality guardrail fails -> production benefit cannot rescue it.
If quality passes but margins are weak -> production benefit must be conservative.
If quality passes with sufficient margin -> production benefit can drive next DOE.
```

### Quality Margin Budget Rule

Production improvement is not free. It spends quality margin.

After quality specs pass, the planner must compare the production gain against
the loss of the weakest quality margin.

Decision flow:

```text
quality pass condition
-> calculate weakest primary-Y margin from worst repeated value
-> compare improvement candidate against baseline
-> estimate margin consumed by production gain
-> choose keep baseline, conservative DOE, mixed DOE, or production DOE
```

Required comparison table:

| Item | Baseline | Candidate | Decision use |
| --- | --- | --- | --- |
| weakest quality margin | margin before improvement | margin after improvement | budget consumed |
| guardrail state | worst code/grade | worst code/grade | hard stop if worsened critically |
| repeatability | pass count | pass count | candidate cannot outrank unstable baseline |
| production metric | time/material/energy | improved value | benefit size |

Production candidates must be labeled by what they consume:

| Candidate type | Definition | Next action |
| --- | --- | --- |
| Free improvement | production improves with no meaningful margin loss | confirm or adopt |
| Cheap improvement | production improves with small margin loss | local confirmation |
| Expensive improvement | production improves but weakest margin becomes thin | keep as follow-up candidate |
| Over-budget improvement | production improves but spec/guardrail fails | reject direction |

Rule:

```text
Do not recommend a production-improved condition as final if it only passes
because the observed repeats happened to stay barely inside spec.
Mark it as a production candidate requiring confirmation.
```

### Candidate Comparison Table

When at least one baseline and one improvement candidate exist, output this
comparison before selecting the next DOE:

| Candidate | Primary Y pass | Weakest margin | Repeat stability | Guardrail state | Production gain | Label |
| --- | --- | ---: | --- | --- | --- | --- |
| Baseline | pass/fail count | margin from worst repeat | stable / noisy | pass / watch / fail | reference | confirmed or provisional baseline |
| Candidate 1 | pass/fail count | margin from worst repeat | stable / noisy | pass / watch / fail | time/material/energy change | free, cheap, expensive, or over-budget |
| Candidate 2 | pass/fail count | margin from worst repeat | stable / noisy | pass / watch / fail | time/material/energy change | free, cheap, expensive, or over-budget |

Decision rule:

```text
If the candidate improves production but turns the weakest margin from
moderate/strong into thin/no-budget, the next DOE is margin-budget
confirmation, not final recommendation.
```

## 5. Combined Direction Decision

For each possible X movement, combine the layers.

| Statistical result | Process result | Production result | Direction decision |
| --- | --- | --- | --- |
| good | plausible | beneficial | explore or optimize |
| good | plausible but risky | beneficial | mixed DOE with guardrail/boundary |
| good | questionable | beneficial | confirmation DOE before adoption |
| weak | plausible | beneficial | include as secondary candidate only |
| bad risk signal | plausible | beneficial | boundary only or reject |
| good | plausible | production-bad | use only if quality needs it |
| quality neutral | plausible | beneficial | production-efficiency DOE |

The planner should output this table before proposing the next DOE.

## 6. Next DOE Purpose Selection Rules

Choose the next DOE purpose from the combined decision.

| Evidence state | Next DOE purpose |
| --- | --- |
| No usable baseline | baseline search / rescue DOE |
| Quality pass but margin weak | conservative margin DOE |
| Quality pass, production burden high, clear efficiency lever | production-efficiency DOE |
| Strong improvement direction but guardrail risk exists | mixed confirmation DOE |
| One factor dominates and others are weak | focused local DOE on dominant factor |
| Interaction suspected and important | interaction confirmation DOE |
| Candidate looks best but repetition is limited | confirmation/repeatability DOE |
| Smooth optimum region expected and enough budget exists | RSM/local optimization DOE |
| Quality baseline passes and production gain consumes margin | margin-budget confirmation DOE |

### Baseline-State Gate

Before selecting the next DOE purpose, classify the best current condition.

| Baseline state | Allowed next DOE | Not allowed |
| --- | --- | --- |
| Candidate | repeatability, local robustness, guardrail check | final recommendation |
| Provisional baseline | mixed improvement with baseline repeats | pure aggressive optimization without repeats |
| Confirmed baseline | production-efficiency, robustness, local optimization | reopening wide screening without a new failure reason |
| Production candidate | final recommendation or pilot confirmation | further DOE without defined gain |
| Not usable | rescue/search/stabilization DOE | efficiency optimization |

Rule:

```text
The next DOE purpose is gated by baseline state first, then by margin and
production opportunity.
```

## 7. Factor Selection Rules

Do not keep all factors active by default.

| Factor status | Rule |
| --- | --- |
| high statistical effect + plausible mechanism | keep active |
| moderate effect + plausible mechanism | keep active if related to weak Y or trade-off |
| weak effect + production risk | fix or drop |
| weak effect but cheap/important guardrail | monitor only |
| important interaction suspected | keep the pair or design a focused interaction DOE |
| factor improves one Y but hurts another | include conservative and boundary levels |

Additional bottleneck-Y rule:

| Factor observation | Factor decision |
| --- | --- |
| large effect on an already-safe Y but weak link to bottleneck Y | do not make it the main active factor |
| modest effect on numeric Y but plausible link to bad code/defect mode | keep active for guardrail stabilization |
| production-efficiency factor may also stabilize failure mode | treat as quality factor first, efficiency factor second |
| fixed factor assumption was never tested and guardrail keeps failing | reopen the factor even if its numeric effect looked small |

In short:

```text
active factor = effect on bottleneck Y + process plausibility + guardrail need
not simply max contribution across all Y
```

### Quality-Production Factor Tags

Each X should be tagged before DOE design.

| X tag | Meaning | Example | Handling |
| --- | --- | --- | --- |
| Quality primary | Directly controls primary quality Y | epoxy amount, bond force | active during baseline search |
| Quality-production mixed | Affects both quality and cycle/cost | bond time, wetting time | do not reduce until quality baseline exists, then boundary-check |
| Production secondary | Mainly affects time/cost after quality passes | cycle delay, noncritical wait | optimize only after guardrails pass |
| Guardrail stabilizer | May not improve average Y but prevents bad modes | force time, wetting time | keep active if failure/defect code is bottleneck |

This prevents time-related factors from being fixed forever while also
preventing premature cycle-time reduction before quality is stable.

## 8. Range Selection Rules

Ranges should be chosen from evidence, not feeling.

### When moving from baseline to improvement DOE

Use:

- current baseline value,
- best observed value,
- nearest failed or risky value,
- engineer-provided feasible range,
- process-mechanism limit,
- primary-Y margin.

Range selection templates:

| Situation | Range choice |
| --- | --- |
| current baseline passes with large margin | include aggressive step toward production benefit |
| current baseline passes with moderate margin | include conservative and moderate steps |
| current baseline barely passes | small local step or repeatability check |
| nearest lower value failed | set boundary between last pass and first fail |
| compensation factor failed to help | do not expand compensation range |
| interaction suspected | vary both factors around baseline, not one at a time |

### Boundary logic

If `A=1.00` passes and `A=0.95` fails:

```text
usable lower boundary is between 0.95 and 1.00
do not recommend below 1.00 without more confirmation
next range should compare 1.00 vs 1.05, or confirm 1.00 with more repeats
```

If `B=675` does not improve the weak Y and worsens BLT margin:

```text
B=675 is not a compensation direction
fix B at 650 or test lower B only for production burden, not quality rescue
```

### Step Size Selection

Use the nearest pass and fail/risky conditions to select new levels.

| Case | Recommended step |
| --- | --- |
| Pass and fail are far apart | choose midpoint and conservative midpoint |
| Fail is caused by hard guardrail | move only halfway toward the failed condition, or stop the direction |
| Fail is only weak numeric margin | test midpoint with baseline repeat |
| Previous aggressive step failed | do not continue more aggressive; return to baseline or smaller step |
| Improvement is production-only | require quality baseline repeat in the same DOE |

Example:

```text
C=800/D=12 passes.
C=650/D=12 fails by bleed or shear.
Next C levels should be 750 or 700 only if the baseline repeats remain stable.
If C=750 still produces guardrail failure, stop C reduction.
```

## 9. Improvement DOE Acceptance Rules

An improvement condition is not accepted just because its average is better.

Acceptance order:

```text
1. Hard guardrail pass
2. Primary numeric Y spec pass
3. Weakest margin is acceptable
4. Repeat stability is acceptable
5. Production benefit is meaningful
6. Process mechanism is plausible
```

Reject or defer an improvement condition when:

| Signal | Decision |
| --- | --- |
| Any hard guardrail failure appears | reject for current round |
| Minimum primary Y falls below spec | reject |
| Margin becomes too thin | defer and confirm only if benefit is large |
| Baseline repeat fails in same DOE | do not trust improvement result yet |
| Production benefit is small but quality risk appears | keep baseline |

For limited lab projects, a practical acceptance rule is:

```text
An improved condition requires 3/3 pass in its own condition or a follow-up
confirmation. A single pass is only a candidate, not a final recipe.
```

## 10. Final Recommendation Rule

The final recommendation must state both what is proven and what is not proven.

Required final labels:

| Label | Meaning |
| --- | --- |
| Confirmed baseline | Repeated quality-pass condition suitable as project conclusion |
| Conservative fallback | Slightly higher burden but stronger stability margin |
| Rejected boundary | Condition tested to find the limit, not for adoption |
| Follow-up opportunity | Production-efficiency direction that needs more margin or data |

Final decision template:

```text
Recommend [condition] as confirmed baseline because [quality evidence].
Reject [improvement direction] because [guardrail/margin evidence].
Production note: [condition] is/ is not cycle-time optimal; further reduction
requires [specific follow-up DOE or process change].
```

## 9. Candidate Ranking Logic

Rank candidates in this order:

```text
1. hard guardrail pass
2. primary Y spec pass
3. weakest primary-Y margin
4. repeat stability / worst-case result
5. process plausibility
6. production benefit
7. simplicity and transferability
```

This prevents a production-efficient but quality-risky condition from being
selected too early.

## 10. Example: Die Attach Epoxy Reduction

Observed:

- `A=1.15, B=650, C=300, D=3` was a usable baseline.
- Reducing A improved epoxy usage and could keep BLT in spec.
- Very low A (`0.95`) produced low-shear failures.
- Increasing B to `675` did not reliably recover shear and reduced BLT lower
  margin.

Decision logic:

| Evidence | Interpretation |
| --- | --- |
| A reduction gives material benefit | production-positive |
| A reduction can consume shear margin | quality-risk |
| A=1.00 repeats passed | aggressive candidate plausible |
| A=0.95 failed | lower boundary found |
| B=675 did not rescue | compensation rejected |

Therefore:

```text
Next DOE purpose: aggressive candidate confirmation / boundary check.
Active factor: A primarily.
Fixed factor: B at 650 unless testing production relief.
Rejected direction: B=675 force compensation.
Final candidates: A=1.05 conservative, A=1.00 aggressive.
```

The recommendation is not based on intuition. It follows from:

```text
statistical pass/fail and margin evidence
-> process plausibility of epoxy-volume / force-compression effects
-> production benefit of lower epoxy
-> guardrail failure at A=0.95
-> compensation failure at B=675
```
