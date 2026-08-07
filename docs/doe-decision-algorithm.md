# DOE Decision Algorithm

## Core Principle

The planner should not follow a fixed textbook sequence such as
`fractional factorial -> full factorial -> RSM` without first diagnosing the
current process state.

The practical workflow is:

```text
DOE project definition
-> project-specific decision criteria generation
-> process/equipment knowledge
-> Y role definition
-> X candidate compression
-> first DOE mode selection
-> first DOE
-> baseline candidate search
-> baseline usability decision
-> baseline diagnostic
-> next DOE purpose selection
-> DOE design method selection
```

In other words, the system first decides **what the next experiment is trying
to prove**, then chooses a DOE format that fits that purpose.

The next DOE must therefore be routed by **project-specific decision
criteria**, not by statistical output alone. Statistical analysis is used to
quantify, challenge, and explain those criteria; it does not replace them.

This algorithm follows the project-level interpretation guidelines:

- `docs/statistics_ml_interpretation_guidelines.md`
- `docs/statistics_experiment_design_principles.md`

Those guidelines make the following boundaries explicit:

- DOE recommendation is a candidate decision until confirmation evidence exists.
- Statistical significance alone is not enough without engineering effect size
  and process plausibility.
- The planner must explain why rejected DOE alternatives were not chosen.
- Numeric DOE scores are internal decision scores, not success probabilities.
- Monitoring signals from a prediction model are DOE follow-up candidates, not
  confirmed root causes.

## Modular Implementation Roadmap

The general AI DOE Planner should be implemented as linked modules, not as one
long chat prompt.

```text
Natural language request
-> structured request schema
-> validation and risk gate
-> project-specific decision criteria
-> evidence and unknown-context risk review
-> allowed factor space
-> DOE generator
-> statistical/tool analysis
-> criteria-based next DOE recommendation
-> artifact logging and feedback loop
```

| Module | Document | Role |
| --- | --- | --- |
| Structured request builder | [structured-request-schema.md](structured-request-schema.md) | Converts user intent into typed DOE input |
| Validation/risk gate | [validation-risk-gate-contract.md](validation-risk-gate-contract.md) | Produces PASS/HOLD/BLOCK before DOE generation |
| Project-specific criteria | [project-specific-decision-criteria.md](project-specific-decision-criteria.md) | Defines what "better" means for this project |
| Evidence and unknown risk | [evidence-and-unknown-context-risk.md](evidence-and-unknown-context-risk.md) | Separates supported risk from missing-context risk |
| DOE generator contract | [allowed-factor-space-to-doe-generator.md](allowed-factor-space-to-doe-generator.md) | Generates DOE only from allowed factor space |
| Artifact and feedback loop | [artifact-logging-and-feedback-loop.md](artifact-logging-and-feedback-loop.md) | Stores traceable inputs, outputs, decisions, and feedback |

This roadmap incorporates the `DOE_RISK_COPILOT_LESSONS` direction:

```text
LLM + structured output + deterministic validation/risk/stat tools + human review
```

The LLM may explain and recommend, but the critical calculations, gates, and
artifact records should be tool- or schema-backed.

## Tool-Use Calculation Layer

The planner should not rely on the LLM's free-form arithmetic when structured
experiment data is available. Numerical calculation, statistical testing,
capability metrics, spec gates, and plot generation should be handled by
deterministic tools. The LLM then interprets those tool outputs through the
project-specific decision criteria.

Required role split:

| Layer | Responsibility | Output |
| --- | --- | --- |
| Data parser | read CSV, Excel, or pasted experiment tables | normalized data table, column schema, missing-value warnings |
| Statistics tool | calculate descriptive statistics, effects, ANOVA, regression, normality, capability, and count/proportion results when applicable | JSON/tables/plots with reproducible values |
| Rule/gate engine | apply hard specs, guardrails, over-spec rules, and exclusion rules | pass/fail state, risk flags, margin state |
| LLM interpreter | connect tool evidence to DOE purpose, process mechanism, production trade-off, and next DOE options | explanation, rejected alternatives, recommendation boundary |
| Human review | check process feasibility and approve final experiment conditions | approved or revised DOE action |

Prototype tool functions:

| Function | Purpose |
| --- | --- |
| `parse_experiment_table()` | load Excel/CSV/pasted table and standardize run, repeat, X, and Y columns |
| `analyze_continuous_y()` | calculate mean, median, standard deviation, min/max, p95, sample-size-gated Cpu/Cpl/Cpk reference margins, effects, and ANOVA where supported |
| `analyze_count_y()` | calculate defect counts, over-spec counts, pass/fail rates, proportion tests, and count summaries |
| `analyze_categorical_y()` | summarize failure codes, risky-code rates, ordinal grades, and worst-case categories |
| `generate_doe_table()` | generate full factorial, fractional factorial, confirmation, refinement, or mixed DOE tables with alias notes |
| `evaluate_decision_criteria()` | map statistics and rule gates into project-specific criteria states |
| `recommend_next_doe()` | recommend next DOE purpose, X focus, level range, and rejected alternatives from criteria state |
| `generate_evidence_report()` | create tables, plots, and explanation text for review or presentation |

The local `stats-python` skill is the prototype calculation layer for this
contract. It can provide reproducible statistics and plots, but it should not
make the final DOE decision by itself.

Rules:

```text
If tool output and LLM interpretation conflict, trust the tool calculation and
revise the interpretation.

If the data is too small or the design does not support a statistical claim,
the report must mark that claim as unsupported rather than filling the gap with
LLM confidence.

Tool output is evidence, not the decision. The next DOE is still routed by the
project-specific decision criteria and engineer review.
```

## Project-Specific Decision Criteria Are Primary

The planner should not use one fixed checklist for every DOE project. The
decision criteria must be generated from the project definition:

```text
process purpose
-> measurable Y types and specs
-> quality risk definition
-> production objective
-> measurement confidence
-> known process mechanisms
-> project-specific decision criteria
```

The criteria answer: **"What makes a condition acceptable, risky, or worth
testing next in this specific project?"**

Statistics answer a different question: **"What evidence supports or weakens
that decision?"**

Generic criteria template:

| Criterion type | Meaning | Typical evidence |
| --- | --- | --- |
| Hard gate | condition must pass before adoption | spec pass/fail, critical defect absence |
| Quality margin | how much room remains before failure | worst repeat margin, p95 margin, sample-size-gated Cpu/Cpl/Cpk reference margin |
| Tail / worst-case risk | whether rare bad outcomes appear | max value, min value, over-spec count, bad-code count |
| Trade-off | whether improving one Y damages another Y | Y-Y relation, candidate comparison |
| Production objective | throughput, material, energy, tool burden, cost | feed speed, cycle time, material use |
| Measurement confidence | whether the data can support the decision | repeat count, sampling method, measurement error |
| Mechanism consistency | whether the trend makes process sense | X-Y mechanism map, engineer comments |
| Next DOE readiness | whether to confirm, refine, widen, or stop | criteria state plus evidence strength |

The exact criteria are process-specific. For example:

| Process | Example project-specific criteria |
| --- | --- |
| Wafer sawing | chipping pass/fail, over-spec count, max chipping/tail risk, Cpu reference margin only when sample size is clear, feed-speed productivity trade-off, measurement confidence |
| Wire bonding | pull-force spec, risky failure-code count, worst pull force, ball-shear guardrail, US power/force/time mechanism consistency |
| Die attach | BLT spec window, die-shear margin, void/bleed guardrail when measurable, epoxy/material and cycle-time trade-off |
| Molding | wire sweep/sagging limit, void or misfill grade, warpage guardrail, transfer-time/cycle-time trade-off |

Rule:

```text
Do not copy wafer-sawing criteria into another process.
Generate criteria from the current DOE project definition, then choose the
statistical analyses needed to evaluate those criteria.
```

## Gate First, Score Second

The planner must apply hard gates before ranking or scoring conditions. A
condition that fails a project-critical rule is not rescued by a good average,
high contribution ratio, or production benefit.

This rule is generic, but the gates themselves are project-specific:

```text
project-specific decision criteria
-> hard gate definition
-> gate evaluation for each condition
-> ranking only among gate-passing or review-eligible conditions
-> next DOE purpose selection
```

Default gate order:

| Gate order | Question | Examples |
| --- | --- | --- |
| 1. Safety / feasibility gate | Can this condition be executed safely and realistically? | equipment limit, material limit, process recipe boundary |
| 2. Primary spec gate | Does every primary Y satisfy the required spec rule? | pull force >= LSL, BLT in range, chipping below limit |
| 3. Critical guardrail gate | Does any critical failure mode appear? | bad failure code, visual reject grade, severe void/sagging/sweep |
| 4. Tail-risk gate | Is the worst observed value acceptable, not only the mean? | max chipping, min shear, worst repeat, p95-like risk |
| 5. Measurement-confidence gate | Is the evidence trustworthy enough for the claimed decision? | repeat count, sampling method, measurement error, denominator |
| 6. Production eligibility gate | Is quality protected before production is optimized? | feed speed, cycle time, material use, energy, tool burden |

Only after these gates are evaluated should the planner calculate or display
ranking scores.

Ranking among eligible conditions can use:

| Ranking signal | Use |
| --- | --- |
| Quality margin | prefer larger margin for the weakest primary Y |
| Worst-case / tail behavior | prefer stable min/max over only good average |
| Repeatability | prefer conditions with fewer repeat failures and smaller spread |
| Mechanism consistency | prefer trends that match known process/equipment behavior |
| Production value | prefer faster, cheaper, lower-burden conditions only after quality passes |
| Learning value | keep failed boundary conditions as evidence, but do not rank them as adoption candidates |

Important distinction:

```text
gate fail condition  -> reject or boundary evidence
gate warning         -> next DOE / confirmation candidate
gate pass            -> ranking / optimization candidate
```

For example, in wafer sawing, a condition with a low average chipping value can
still be rejected if a worst-case chipping rule fails. In wire bonding, a high
average pull force can still be downgraded if risky failure codes appear. In
die attach, strong die shear cannot rescue a BLT or bleed/void guardrail fail.

The final report must show the gate trace before showing scores:

```text
1. which gates were generated for this project
2. which conditions passed, warned, or failed each gate
3. which conditions remained eligible for ranking
4. which ranking signals decided the next DOE direction
```

## Core Engine And Context Profiles

AI DOE Planner should be a general DOE decision engine. It should not be
hardcoded to one semiconductor class, one equipment set, or one time budget.

The core engine owns the general reasoning steps:

```text
define project purpose
-> generate decision criteria
define Y roles
-> compress X candidates
-> select DOE purpose
-> choose DOE design method
-> generate run table
-> interpret effects and limitations
-> recommend confirmation or next DOE
```

Specific project realities are injected through a `context_profile`. The
profile changes the recommendation posture without changing the core DOE
logic.

Example context profiles:

| Context profile | Typical posture |
| --- | --- |
| `general_screening` | broad factor discovery when knowledge is weak |
| `semiconductor_training_lab_7h` | small executable DOE with setup/measurement/review buffer |
| `semiconductor_process_optimization` | protect baseline, guardrails, and production constraints |
| `manufacturing_quality_improvement` | focus on defect reduction, repeatability, and control limits |
| `research_development_rsm` | allow RSM/CCD/Box-Behnken when time and run budget support optimization |
| `material_mixture_experiment` | use mixture design logic when proportions must sum to a fixed total |

The planner should always report which profile was applied and which design
choices came from that profile.

## SPC Stability Gate Before DOE

The planner should apply an SPC/control-chart stability gate before selecting a
DOE format. This gate is defined in:

- `docs/spc-control-chart-risk-doe-integration.md`

The gate prevents the system from treating every process problem as an
optimization problem.

Required routing:

```text
current process evidence
-> stability state: stable / OOC-like / OOS-like / variance-limited / unknown
-> weakest spec or guardrail margin
-> subgroup quality
-> DOE purpose: optimize / confirm / stabilize / isolate / contain
```

Decision rules:

| SPC state | Planner action |
| --- | --- |
| stable with clear margin | optimization or production-improvement DOE may be allowed |
| stable with thin margin | margin-confirmation or margin-improvement DOE |
| OOC-like signal | special-cause isolation or stabilization DOE before optimization |
| OOS-like signal | containment/SOP/MRB route before adoption-focused DOE |
| variation widened | variance-reduction DOE before final recipe recommendation |
| subgroup quality weak | lower confidence and clarify baseline/measurement first |

The planner should report the rejected route when this gate blocks a richer
optimization DOE.

## Context Profile: Semiconductor Training Lab 7h

The first semiconductor training-lab DOE may run under a tight lab window:

```text
available lab time: about 7 hours
operator maturity: beginner to intermediate
execution risk: high
```

When this profile is selected, the planner must optimize for executable
learning, not textbook coverage. A theoretically richer DOE is not better if
the team cannot finish the runs, measure Y consistently, or document what
changed.

Default posture under this constraint:

| Constraint | Planning consequence |
| --- | --- |
| 7-hour total window | prefer small, interpretable DOE tables |
| users are not yet fluent with equipment/DOE | reduce factor count before adding design sophistication |
| setup, measurement, mistakes, and discussion consume time | reserve buffer instead of filling all 7 hours with runs |
| repeated runs may be difficult | protect at least baseline/center or confirmation-like repeats when possible |
| data quality may be uneven | make measurement method and guardrail logging part of the DOE, not an afterthought |

The planner should treat the first DOE as a **baseline search and learning
DOE**, not as a final optimization DOE. Recommended wording:

```text
This design is optimized for a 7-hour training-lab constraint. It prioritizes
finding a defensible baseline candidate, checking the main quality guardrails,
and creating a clear next-DOE decision over estimating every interaction.
```

Under this context profile, the planner should avoid recommending:

- broad 5+ factor screening,
- RSM/CCD/Box-Behnken as the first real lab design,
- many sequential micro-DOEs that depend on perfect execution,
- designs that require complex analysis but leave no time for measurement QA.

## Knowledge-Focused DOE Is The Default

The planner should not default to a 4-factor fractional factorial DOE just
because screening is a familiar first step.

If engineer knowledge, lecture notes, equipment constraints, or process
mechanism already identify the likely dominant factors, the default first DOE
should be a focused 2- or 3-factor DOE. A broader 4-factor fractional screening
DOE is a fallback for high uncertainty, not the normal path.

| Input knowledge state | First DOE posture | Reason |
| --- | --- | --- |
| 2 dominant X are known | 2-factor full factorial with repeats or center/baseline runs | estimates main effects and interaction cleanly with low run count |
| 3 dominant X are known | 3-factor full factorial when run budget allows | avoids unnecessary aliasing and gives interpretable interactions |
| 2-3 dominant X plus one uncertain nuisance X | focused DOE with nuisance X fixed or blocked | prevents a weak factor from consuming runs |
| 4+ X are plausible and ranking is unclear | fractional screening | useful when the planner truly does not know what matters |
| known key interaction must be protected | design around that interaction, even if it reduces factor count | interaction interpretability is more valuable than wide but aliased screening |

Practical rule:

```text
Use 4-factor fractional screening only when the uncertainty justifies the
aliasing cost.
```

This matches a real engineering workflow: experienced engineers often do not
screen many factors from scratch. They start from the parameters most likely to
matter and spend limited runs on a DOE that can actually answer the decision
question.

## Define Y Roles Before Choosing X

The planner must define the response hierarchy before choosing factors. If the
Y roles are vague, X selection becomes arbitrary.

| Y decision role | Meaning | Example | Decision effect |
| --- | --- | --- | --- |
| Hard constraint | must satisfy spec or the condition cannot be adopted | pull force >= 7 g, BLT inside range | fail blocks recommendation |
| Quality objective | primary quality value to improve after the hard spec is protected | higher die shear, lower wire sweep | drives optimization direction |
| Guardrail | failure mode, defect case, or visual risk that can override averages | bad pull failure code, void grade | can reject a high-scoring numeric result |
| Production objective | time, material, energy, force, thermal load, tool burden | shorter cure/wait time, lower epoxy amount | ranks only quality-safe candidates |
| Monitor | measured for context but not used for the current decision | auxiliary dimension, logged tool value | informs future DOE or mechanism checks |

This creates a constrained optimization structure:

```text
1. hard constraints and guardrails must pass
2. quality objectives decide whether the condition is useful
3. production objectives improve the condition only inside the quality-safe region
4. monitor variables explain or warn, but do not drive the current DOE alone
```

## X Candidate Compression Before First DOE

Before designing the first DOE, the planner should compress the candidate X
list. The output is not just "selected factors"; it is a reasoned factor table
with active, fixed, blocked, and deferred variables.

The detailed scoring rubric is defined in
`docs/x-candidate-scoring.md`. This algorithm document defines how the
resulting selection is used.

Recommended X ranking evidence:

| Evidence axis | Question |
| --- | --- |
| Mechanism relevance | Can this X physically move the current hard constraint or quality objective? |
| Engineer priority | Did an engineer identify it as a key lever or dismiss it as low-impact? |
| Controllability | Can the parameter be changed safely and repeatably during the project? |
| Measurement linkage | Will the selected Y reveal the effect of this X? |
| Interaction risk | Does this X participate in a known important interaction? |
| Production relevance | Does moving this X affect cycle time, material, tool stress, or throughput? |
| Safe DOE range quality | Are realistic low/high or local levels known? |

X decision labels:

| Label | Meaning |
| --- | --- |
| Active X | included in the next DOE because it can answer the current decision |
| Fixed X | held at a chosen value because it is weak, risky, already acceptable, or not the bottleneck lever |
| Blocked X | controlled as a condition or block because it can confound results but is not the target |
| Deferred X | recorded for a later DOE, usually after baseline or guardrail stabilization |
| Excluded X | removed because it is not adjustable, not measurable, unsafe, or irrelevant to the chosen Y |

Rule:

```text
The first DOE should be wide only when knowledge is weak. When knowledge is
strong, the first DOE should be interpretable.
```

## First DOE Mode Selection

The first DOE mode is selected from knowledge confidence and run budget.

| Situation | Recommended first DOE | Notes |
| --- | --- | --- |
| 2 active X, 1-2 primary Y | 2^2 full factorial with baseline/center/repeat buffer | best interpretability per run under a 7-hour lab |
| 3 active X, low-to-medium interaction uncertainty | 2^3 full factorial only if 8 runs plus measurement buffer are realistic | good default only when execution time is credible |
| 3 active X plus one production objective | 2^3 factorial plus production measurement | do not add production X unless it can affect the decision |
| 4 active X, high uncertainty, limited budget | 2^(4-1) fractional screening only if factor setup is simple | record alias structure and interaction risks |
| known interaction dominates, e.g. epoxy amount * force | include both factors even if another X is dropped | protect mechanism interpretation |
| visual/count/categorical Y dominates | design around pass/fail, count, rate, or guardrail evidence | ANOVA-friendly design is secondary |

Seven-hour recommendation gate:

```text
If the team cannot realistically complete setup, runs, Y measurement,
guardrail logging, and summary review inside 7 hours, reduce the DOE before
starting. Prefer 2 active X with repeats over 4 active X with poor execution.
```

The planner should show the rejected alternatives. For example:

```text
Rejected 4-factor fractional screening because engineer/process knowledge
already identifies A/B/C as dominant and the project budget is too small to
spend runs on a low-confidence D.
```

or:

```text
Selected 4-factor fractional screening because no reliable ranking exists and
the goal is to locate the first bottleneck quickly.
```

## Effect Interpretability Gate

The planner must decide what the design can actually separate before it
recommends a DOE table. A design that creates more columns is not better if it
cannot separate the effect needed for the decision.

Required checks before table generation:

| Check | Required planner behavior |
| --- | --- |
| Main effect vs interaction | State whether each important X is interpreted as a standalone effect or as part of a suspected interaction |
| Interaction protection | If an interaction is mechanism-critical, keep those factors in the same interpretable full-factorial subset when possible |
| Main-effect-only screening | If the design is screening-only, label interaction conclusions as unresolved |
| Small main effect, large interaction risk | Do not drop an X only because its main effect is small when a plausible interaction could be large |

Decision rule:

```text
If the current question depends on A*B, prefer a smaller full factorial around
A and B over a wider fractional design that aliases the interaction.
```

## Aliasing And Resolution Gate

Fractional factorial and Plackett-Burman designs must include an aliasing
warning. The planner should never present these designs as direct root-cause
proof.

Minimum output for fractional or PB recommendations:

| Output | Meaning |
| --- | --- |
| design purpose | screening, interaction confirmation, robustness, optimization, or confirmation |
| expected resolution | III, IV, V, or unknown/NA |
| interpretable effects | effects the design can support with acceptable ambiguity |
| aliased effects | effects that may be confounded and should not be overclaimed |
| assumption | usually that higher-order interactions are small |
| follow-up requirement | focused factorial, confirmation, RSM, or robustness check |

Resolution guidance:

| Resolution | Interpretation boundary | Recommended use |
| --- | --- | --- |
| III | main effects may be aliased with 2-factor interactions | very fast screening only |
| IV | main effects are usually separable from 2-factor interactions, but 2-factor interactions may be aliased with each other | practical main-effect screening |
| V | main effects and 2-factor interactions are more interpretable | interaction-sensitive DOE when run budget allows |

Safe wording:

```text
This design can identify candidate factor signals, but it cannot prove the
factor is the root cause. Large effects may include aliased interaction
contributions and require follow-up confirmation.
```

## Execution Reliability Gate

Before accepting a DOE table, the planner should add reliability controls or
state why they are not feasible.

| Reliability control | Purpose | Planner action |
| --- | --- | --- |
| Center point | checks curvature and gives a practical baseline reference | add when low/high-only interpretation may miss a middle optimum |
| Replication | estimates process variation and guards against one lucky run | prioritize baseline, center, or candidate repeats when full replication is impossible |
| Randomization | prevents time/order drift from becoming a false factor effect | randomize when practical; otherwise record run-order constraint |
| Blocking | controls nuisance differences such as lot, operator, tool, chamber, or time window | identify block candidates and avoid treating them as active X unless intended |

If randomization or replication is constrained, the report must carry the
limitation into the claim boundary.

## RSM, Robust, And Mixture Profile Gate

Advanced designs should be profile- and stage-dependent rather than automatic.

| Design family | Eligibility | Common reason to reject or defer |
| --- | --- | --- |
| RSM / CCD / Box-Behnken | important X reduced to roughly 2-4, quantitative Y available, safe range defined, run budget sufficient | too early, too many candidate X, unsafe axial/extreme points, insufficient measurement quality |
| CCD | broader safe exploration is possible and axial points are acceptable | axial points exceed equipment/process safety range |
| Box-Behnken | quadratic modeling is needed but extreme corner combinations are risky | corner-region behavior is the decision-critical question |
| Taguchi / robust design | variation, noise factors, or stability are central to the decision | S/N ratio would hide hard-constraint or guardrail failures |
| Mixture design | factors are proportions whose total is constrained | factors are independently adjustable recipe settings |

RSM output must still end in confirmation. A predicted optimum is a model-based
candidate, not a final condition.

## Monitoring-Triggered DOE

The planner may receive follow-up requests from Risk AI Engine monitoring.
Examples include feature drift, risk_score drift, watch-zone rate increase, or
delayed FN increase.

The planner should diagnose these signals in this order:

```text
1. rule out data-quality or pipeline change
2. identify affected lot/tool/chamber/recipe segment
3. map predictive signal to controllable X factor candidates
4. define primary Y, hard constraints, guardrails, and monitor variables
5. choose diagnostic DOE, focused factorial, stabilization DOE, or confirmation
```

Monitoring-triggered DOE should not assume the monitored signal is the root
cause. It is a starting point for a controlled experiment or engineering review.

## Baseline Is A Decision Point, Not A Round Number

A baseline does not have to be found in the first DOE. The first DOE may only
produce a baseline candidate. If the candidate is not usable, the next DOE
should continue baseline search or guardrail stabilization.

User-facing confidence grades are defined in
`docs/recommendation-confidence-grading.md`. The baseline labels below remain
the engineering state labels used inside the DOE workflow.

Baseline states must be explicit. Do not let the planner silently move from
"one good result" to "final condition."

| State | Meaning | Next action |
| --- | --- | --- |
| Candidate | One DOE result looks promising, but repeatability is not established | Repeat, compare near conditions, or run local robustness |
| Provisional baseline | Good enough to use as a reference point under limited experiment budget | Include baseline repeats inside the next mixed DOE |
| Confirmed baseline | Repeated in an independent DOE with no guardrail failure | Run improvement or production-efficiency DOE |
| Production candidate | Confirmed baseline plus production burden is defensible | Final recommendation or pilot confirmation |
| Not usable yet | Too unstable, off-spec, or physically questionable | Run another DOE to find or stabilize a baseline |

Avoid overusing labels such as "C-grade baseline" in the product interface.
The user-facing decision should be simple:

```text
Can this condition be used as the next reference point?
yes -> diagnose it
no  -> keep searching or stabilizing
```

## Usable Baseline Criteria

Because the project will likely have limited experiment time and small sample
counts, the baseline criterion must be practical rather than production-grade.

A condition can be used as an operational baseline when:

- Primary numeric Y values satisfy specification, or are very close with a
  clear recovery path.
- No critical failure mode appears.
- The condition is physically plausible from the process mechanism.
- The condition is not an obviously extreme recipe that is likely to damage
  the part, tool, or material.
- Secondary production burden is not absurdly high, unless the purpose is a
  rescue DOE.

For small repetitions:

| Repetition count | Primary evidence |
| --- | --- |
| `n < 5` | mean, minimum value, pass count, failure mode, process plausibility |
| `n >= 5` | mean, standard deviation, lower bound such as mean - 2 sigma, failure frequency |

For a 3-repeat project situation:

| Result pattern | Baseline decision |
| --- | --- |
| 3/3 pass, no critical failure | Strong baseline candidate |
| 2/3 pass, mean spec pass, no critical failure | Usable operational baseline if experiment time is limited |
| mean good but critical failure appears | Not usable; run guardrail stabilization |
| one primary Y off-spec | Not usable; run baseline search or rescue DOE |

The key rule is:

> With limited data, the planner should create a decision grade, not pretend to
> have production-level statistical proof.

Practical project rule:

```text
If experiment budget is limited, a pure confirmation DOE can be skipped only
when the next DOE still contains baseline repeat runs.
```

This means the planner may move from a provisional baseline directly to a
mixed improvement DOE, but it must not remove the baseline from that DOE.
The baseline repeats are the internal check that the reference condition is
still stable.

## Baseline Diagnostic

Once a usable baseline exists, the next DOE direction is decided by diagnosing
the baseline's weakness.

Checklist:

| Diagnostic question | Why it matters |
| --- | --- |
| Do primary Y values satisfy spec? | Determines whether rescue or improvement is needed |
| Is the margin sufficient? | Prevents optimizing a condition that barely passes |
| Did any failure code/case appear? | Force values can look good while the failure mode is unacceptable |
| Is the result variable trade-off severe? | Multi-response DOE may be needed |
| Is the result noisy? | Repetition or noise-factor checks may come before optimization |
| Is the recipe physically plausible? | Prevents selecting a damaging or non-transferable condition |
| Is production burden high? | Energy, time, material, force, and thermal load may become the next target |
| Is the process window unknown? | Robustness DOE may be more valuable than pushing Y higher |

### Mandatory Decision Report Gate

The planner must not jump directly from analysis to a new DOE table. Before
proposing the next DOE, it must emit a decision report that explains how the
statistics, process mechanism, production burden, and current baseline state
were combined.

Required report fields:

| Field | Required content |
| --- | --- |
| Current DOE stage | first screening, confirmation, margin-budget, production improvement, robustness, or final recommendation |
| Primary Y | quality responses used for pass/fail or margin decisions |
| Secondary Y | production or monitoring responses that cannot override quality guardrails |
| Y type | continuous, count, proportion, categorical, ordinal, or mixed |
| Current bottleneck Y | weakest spec margin, unstable failure mode, or response blocking adoption |
| High-impact X | factors with large statistical effects or contribution ratios |
| Bottleneck-linked X | factors that can plausibly improve the current bottleneck Y |
| Risky X | factors that improve one Y while consuming margin or worsening another Y |
| Fixed X | fixed value and reason: weak effect, mechanism risk, block factor, or already-optimized lever |
| Active X | factors/ranges to move in the next DOE and why |
| Process interpretation | whether the proposed direction matches known mechanism |
| Production interpretation | time, material, tool stress, energy, or throughput effect |
| Next DOE purpose | what the next DOE is trying to prove |
| Success criteria | pass count, margin, guardrail, and production improvement targets |
| Stop/reject criteria | conditions that terminate the direction or keep the existing baseline |

If this report cannot be filled, the next DOE recommendation must be labeled
as exploratory rather than evidence-backed.

### Quality-First, Margin-Budget Improvement

When the baseline passes quality, the planner should not immediately maximize
production metrics. It should ask:

```text
How much quality margin remains, and how much of that margin would be consumed
by a faster, cheaper, lower-energy, or lower-material condition?
```

This adds a quality-margin budget gate:

| Baseline diagnosis | Next DOE intent |
| --- | --- |
| Quality does not pass | rescue / baseline search |
| Quality passes but weakest margin is thin | robust confirmation or small-step margin DOE |
| Quality passes with moderate margin and production burden is meaningful | mixed confirmation DOE with baseline repeat and conservative production candidate |
| Quality passes with strong margin and repeatability is confirmed | production-efficiency DOE |
| Production candidate fails or consumes too much margin | reject candidate and keep baseline |

Decision principle:

> Quality pass creates permission to consider production improvement. It does
> not automatically justify spending the entire quality margin.

This is especially important in small lab DOE, where one lucky pass can look
like an optimum. A production candidate should be treated as provisional until
its weakest margin survives repeated or robustness checks.

## Bottleneck-Y First Factor Selection

The planner must not choose the next DOE factors only from the largest overall
effect or contribution ratio.

A factor can have a large effect on a response that is already safe, while
having little ability to improve the response that is currently blocking the
decision.

The required order is:

```text
1. Convert each Y into a spec margin, guardrail state, or defect/risk rate.
2. Identify the bottleneck Y that prevents baseline confirmation or adoption.
3. Analyze which X factors can improve that bottleneck Y.
4. Check whether those X factors are process-plausible levers for that Y.
5. Design the next DOE around bottleneck-improvement factors, not merely the
   largest-effect factors.
```

Example from the second-bond wire-bonding simulator:

| Finding | Wrong interpretation | Correct interpretation |
| --- | --- | --- |
| US power had a strong effect on pull force | keep optimizing US power | pull force was already above spec, so US power was not the main bottleneck lever |
| Failure code kept appearing | treat it as noise while force improves | failure code is a hard guardrail and becomes the bottleneck Y |
| C and D looked like time/efficiency factors | reduce or fix them early | C and D may control bond formation stability and failure mode |

For this case, the next DOE should move from `A/B force-margin search` to
`C/D failure-mode stabilization`, because the blocking Y is categorical
failure code, not continuous pull force.

General mapping:

| Bottleneck Y | Do not over-focus on | First factors to reconsider |
| --- | --- | --- |
| Strength below spec | production efficiency | energy, time, force, material amount |
| Strength passes but failure code/case is bad | the factor that only raises strength | time, hold/force time, contact stability, stress balance |
| Defect count/rate is high | mean strength or average dimension only | mechanism-linked defect drivers and noise/special-cause factors |
| Production burden is high and quality is stable | additional quality margin | time, energy, material, force, temperature |

Rule:

> The next DOE factor is not necessarily the factor with the largest effect.
> It is the factor most likely to improve the current bottleneck Y while
> preserving hard guardrails and primary margins.

## Candidate Condition Labels

The planner should classify each candidate condition before choosing the next
DOE. These labels are user-facing evidence labels, not final production
qualification.

| Label | Meaning | Allowed decision |
| --- | --- | --- |
| Confirmed baseline | quality passes, hard guardrails pass, and repeated/robustness evidence is acceptable | use as reference or final quality recipe |
| Provisional baseline | quality appears usable but the sample count or robustness evidence is limited | use only with baseline repeats in the next DOE |
| Production candidate | confirmed/provisional baseline with a clear production benefit and acceptable margin loss | confirm, adopt with caveat, or compare against baseline |
| Provisional production candidate | production improves but the weakest quality margin is thin or repeat evidence is limited | run margin-budget confirmation |
| Risky candidate | average quality may pass but worst-case, defect code, or guardrail is concerning | boundary learning only; not final |
| Reject | primary spec, critical code, or hard guardrail fails | do not optimize further unless used as boundary evidence |

Ranking rule:

```text
hard guardrails first
-> primary Y pass and weakest margin
-> repeatability / worst-case stability
-> process plausibility
-> production benefit
```

Production benefit can only break ties among quality-acceptable candidates.

## Claim Boundary

Every DOE conclusion must separate three things:

| Field | Meaning |
| --- | --- |
| What we found | patterns directly observed in the current DOE result |
| What we can claim | claims supported by the design, sample size, execution quality, and evidence level |
| What remains uncertain | unresolved interactions, aliasing, noise factors, lot/tool/time stability, and confirmation gaps |

Unsafe claim:

```text
A is the root cause and this is the optimum condition.
```

Preferred claim:

```text
Within the current factor range and execution constraints, A showed the
strongest candidate signal. Because interaction/aliasing/repeatability limits
remain, this condition should be treated as a confirmation candidate rather
than a final optimum.
```

## Next DOE Purpose Selection

The next DOE mode is selected from the baseline diagnostic, not from a fixed
DOE ladder.

| Baseline state | Next DOE purpose | Typical DOE design |
| --- | --- | --- |
| Spec not met | Rescue / aggressive improvement | broad screening or targeted high-impact DOE |
| Spec met but margin weak | Conservative margin improvement | local factorial or one/two-factor local DOE |
| Spec met but failure appears | Guardrail stabilization | vary suspected stress/failure drivers, keep pass/fail and code as hard filters |
| Spec met, margin sufficient, no failure | Robustness DOE | small perturbation around baseline, center repeat |
| Spec met, margin sufficient, production burden high | Production-efficiency DOE | lower energy/time/material/force/temperature while guarding quality |
| Result noisy | Confirmation / repeatability DOE | repeat baseline and near-baseline conditions |
| Multiple Y trade off | Multi-response trade-off DOE | desirability or constrained optimization |
| Important interactions unresolved | Interaction confirmation | small full factorial on selected factors |
| Near optimum and smooth response expected | Local optimization / RSM | center points, axial/local response surface |

## Mixed DOE Eligibility

Mixed DOE is allowed when experiment time is limited and the planner needs to
test confirmation and improvement in the same round. It is not a license to
combine unrelated guesses.

Eligibility:

| Condition | Requirement |
| --- | --- |
| Baseline is only provisional | Include at least one or two baseline repeats |
| Improvement direction is quality-risky | Include conservative steps before aggressive steps |
| Production-efficiency factor is being reduced | Keep primary quality factors fixed unless the mechanism requires compensation |
| Guardrail Y has failed before | Include hard guardrail decision rules before ranking average values |
| Multiple directions are tested | Label each run purpose: repeat, conservative, moderate, aggressive, boundary |

Preferred 8-run mixed DOE structure:

| Run group | Purpose |
| --- | --- |
| 1-2 | Baseline repeat |
| 3-4 | Single-factor conservative/moderate improvement |
| 5-6 | Second single-factor conservative/moderate improvement |
| 7-8 | Combined or boundary improvement candidate |

Mixed DOE decision rule:

```text
If the baseline repeats fail, do not adopt any improvement condition from the
same DOE without rechecking the baseline problem first.
```

## Range Selection From Pass/Fail Boundaries

The planner must choose new levels from evidence, not from arbitrary nice
numbers.

Inputs:

- current baseline,
- best observed pass condition,
- nearest observed fail or risky condition,
- weakest primary-Y margin,
- hard guardrail history,
- engineer-provided feasible range,
- process mechanism,
- production improvement target.

Boundary examples:

| Evidence | Next range decision |
| --- | --- |
| `D=12` passes and `D=8` fails | test `D=10` or `D=11`, not below `D=8` |
| `D=10` also fails | stop reducing D or return to `D=12` |
| `C=800` passes and `C=650` fails | test `C=700/750` only if margin allows |
| Lower force fails by shear | do not reduce force further for production benefit |
| Higher epoxy fixes shear but creates bleed | use as conservative fallback, not default efficiency condition |

Aggressiveness must be capped by the weakest Y:

```text
If any primary Y has low margin or any guardrail has recently failed, choose a
small step or boundary check. Do not run an aggressive production-efficiency
DOE just because average values still look acceptable.
```

## Termination Logic

The planner must know when to stop. More DOE is not always better when the
experiment budget is small.

Stop or recommend final baseline when:

| Condition | Decision |
| --- | --- |
| Confirmed baseline exists | Can conclude if project scope is baseline creation |
| Improvement DOE causes guardrail failures | Stop improvement direction and keep baseline |
| Production benefit is smaller than quality risk | Keep quality baseline |
| Additional DOE would only retest already failed direction | Stop or redesign with new mechanism |
| Experiment budget is exhausted | Recommend best defensible condition and state residual risk |

Do not stop when:

| Condition | Required action |
| --- | --- |
| No usable pass condition exists | Continue baseline search or rescue DOE |
| Only one lucky pass exists | Repeat or run local robustness |
| Failure mode is unexplained | Run guardrail stabilization or collect process knowledge |
| Key Y has no spec or no decision rule | Define the rule before final recommendation |

## DOE Aggressiveness From Primary-Y Margins

After a usable baseline is selected, the planner should decide how aggressive
the next DOE can be from the margin of the primary Y responses, not from the
round number or from a fixed DOE sequence.

For each primary Y, calculate the relevant margin:

| Y type | Margin definition |
| --- | --- |
| Lower-bound spec | `Y - LSL` |
| Upper-bound spec | `USL - Y` |
| Target-range spec | `min(Y - LSL, USL - Y)` |
| Lower-is-better within range | first protect `Y - LSL`, then prefer lower values |
| Higher-is-better within range | first protect `USL - Y`, then prefer higher values |

Use the weakest primary-Y margin to limit aggressiveness.

| Margin / risk state | DOE aggressiveness |
| --- | --- |
| One primary Y has low margin | conservative or small-step DOE |
| Primary Y margins are moderate | balanced or mixed DOE |
| All primary Y margins are high and no failure appears | aggressive production-efficiency DOE is allowed |
| Improvement direction helps one Y but hurts another | mixed DOE with conservative, aggressive, and boundary candidates |
| Improvement direction hurts the weakest Y | avoid aggressive DOE; run guardrail or margin-protection DOE |
| Critical failure mode appears | guardrail stabilization overrides numeric margin |

For multiple primary Y values, the planner must explicitly check trade-off:

```text
1. Which Y improves if the proposed X direction changes?
2. Which Y gets worse?
3. Is the worsening Y already the weakest-margin response?
4. Is the failure mode numeric, categorical, or physical damage?
5. Should the next DOE be conservative, aggressive, or mixed?
```

The practical rule:

> Baseline grade decides whether the condition can be used as a reference.
> Primary-Y margin and trade-off decide how aggressively the next DOE should
> move.

If experiment budget is limited and the baseline is usable, avoid many
sequential micro-DOEs. Use a mixed DOE that includes:

- baseline repeat,
- conservative candidate,
- moderate candidate,
- aggressive candidate,
- boundary/failure-probe candidate,
- production-efficiency candidate when relevant.

If experiment budget is sufficient, sequential local DOE can be used instead.

## Preferred Direction After A Good Early Baseline

If a good baseline is found quickly, do not immediately switch to aggressive
Y maximization. That was a failure mode observed in the wire-bonding simulator:
the average force margin increased, but failure cases/codes appeared.

Preferred order:

1. Robustness DOE
2. Production-efficiency DOE
3. Conservative margin improvement DOE

This order is especially appropriate when the baseline already satisfies:

- primary specs,
- no critical failure code/case,
- plausible mechanism,
- acceptable energy/time/material burden.

## Guardrail-First Multi-Response Rule

Some response variables are not simple objectives. They are guardrails.

Examples:

- Wire pull force can be high while failure code is unacceptable.
- Ball shear force can be high while shear case indicates pad damage or
  interfacial failure.
- Die attach BLT can be inside spec while void or epoxy bleed is visually bad.

Analysis order:

```text
1. Apply hard guardrails.
2. Check primary numeric Y against spec and margin.
3. Check variability or lower bound if repetition count supports it.
4. Evaluate secondary production metrics.
5. Interpret results with process mechanism.
6. Select next DOE purpose.
```

Hard guardrails should not be converted blindly into weighted scores when the
failure mode is physically critical. A weighted score may be useful for ranking
acceptable candidates, but not for hiding a critical failure.

## Y-Type-Based Statistical Analysis Engine

The statistical analysis engine should not be an "ANOVA-only" engine. The
planner must first identify the type of each response variable, then select
the analysis method that matches that response type.

Response types:

| Y type | Semiconductor examples | Primary analysis | Supporting analysis / output |
| --- | --- | --- | --- |
| Continuous numeric | BLT, die shear, pull force, ball shear, warpage, kerf width | effect analysis, ANOVA/pooling, regression | correlation, interaction plots, min/max, standard deviation |
| Binary categorical | pass/fail, good/bad, normal/abnormal | pass rate comparison, logistic regression when enough data exists | pass count, fail reason table, odds-style comparison |
| Multiclass categorical | pull failure code, ball shear case, defect type | code frequency table, bad-code rate, risk grouping | code-by-condition table, guardrail flags |
| Ordinal categorical | visual defect grade 0/1/2/3, void severity grade | rank/ordinal comparison | median grade, worst grade, grade distribution |
| Count | chipping count, crack count, void count, defect count | count effect, Poisson or negative-binomial model when enough data exists | count reduction %, defect density, overdispersion warning |
| Proportion / rate | defect rate, yield, void rate, bad chip count / inspected chip count | binomial/proportion analysis, logistic model when enough data exists | numerator/denominator table, confidence-style caution |
| Image-derived | X-ray void image, high-scope chipping image | convert image into count, proportion, grade, or continuous measurement first | keep original image evidence linked to derived Y |

Analysis selection flow:

```text
DOE result input
-> identify Y type
-> choose analysis family
-> run response-specific analysis
-> apply hard guardrails
-> check multi-Y trade-off and margins
-> verify with process mechanism
-> recommend the next DOE purpose
```

Important rules:

- Do not force categorical, count, or proportion Y into ordinary ANOVA just
  because the DOE table looks factorial.
- For count or rate responses, always record the denominator: inspected chip
  count, inspected area, inspection time, image count, or opportunity count.
- For small sample counts, report simple evidence first: pass count, fail
  count, worst value, defect count, defect rate, and failure mode.
- Use p-values only as supporting evidence when repetition and sample size are
  adequate.
- For categorical failure codes, guardrail grouping can be more important than
  numerical optimization. For example, a high pull force is not acceptable if
  the failure code indicates a critical bond-interface problem.
- For wafer sawing, high-scope visual inspection may produce count, proportion,
  or ordinal Y rather than continuous Y. The planner should therefore expect
  chipping/crack counts, defect rate, defect type, and visual severity grade,
  not only ANOVA-friendly numeric measurements.

This turns the analysis module into a response-type router:

```text
continuous Y -> effect / ANOVA / regression
binary Y     -> pass-rate / logistic-style analysis
multiclass Y -> code-frequency and risk-group analysis
ordinal Y    -> grade / rank analysis
count Y      -> count-effect and count-model analysis
rate Y       -> proportion / binomial analysis
image Y      -> image-derived Y extraction, then route by extracted Y type
```

## Wire Bonding Lesson Captured

In the first-bond wire-bonding simulator, the condition
`A=80, B=60, C=10, D=180` became a strong baseline candidate because it met
ball shear, pull force, failure-code, and deformation requirements. The later
aggressive improvement path tried to increase force margin, but higher
ultrasonic energy/time activated bad shear cases and pull codes.

The algorithm lesson:

> When a baseline is already good, the planner should protect failure-mode
> stability first. It should explore robustness and production efficiency
> before attempting aggressive margin increase.

## Practical Product Output

Every DOE recommendation should explicitly output:

1. Baseline usability decision.
2. Baseline diagnostic table.
3. Selected next DOE purpose.
4. Why other DOE purposes were not chosen.
5. Proposed DOE table.
6. Expected analysis plan.
7. Guardrails that must override numeric improvement.

This makes the planner defensible: it can explain why the next DOE is a
robustness DOE, production-efficiency DOE, guardrail stabilization DOE, or
margin-improvement DOE.

The detailed presentation/report structure is defined in
`docs/doe-evidence-report-format.md`. The evidence report should connect:

```text
statistical result
-> process-mechanism validation
-> production/manufacturing validation
-> next DOE direction
-> proposed DOE table
```

The goal is to make every recommendation explainable under the question:

> Why did this data lead to this next DOE?

The rule-level decision logic for combining statistics, process mechanism, and
production evidence is defined in `docs/next-doe-recommendation-logic.md`.
This file should be treated as the planner's next-DOE recommendation engine.

Supporting MVP engine documents:

- `docs/scoring-engine.md`: converts DOE evidence into quality, guardrail,
  repeatability, process-plausibility, and production scores.
- `docs/process-knowledge-schema.md`: defines the reusable process/equipment
  knowledge records needed before first DOE and during process validation.
- `docs/knowledge/`: stores process-specific knowledge cards for wafer sawing,
  die attach, wire bonding, and molding. These cards provide the process
  mechanism, measurable Y, controllable X, guardrails, and first-DOE posture
  used by the general engine.
- `docs/report-automation-plan.md`: defines the automated Markdown report
  structure that explains the statistical, process, and production basis for
  each recommendation.
