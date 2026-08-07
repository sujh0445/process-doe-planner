# DOE Report Automation Plan

## Purpose

The planner should generate a repeatable evidence report, not only a final
recommendation.

The report must let the presenter answer:

```text
Why did the engine recommend this DOE direction from this data?
```

This document defines the report-generation pipeline that uses:

- DOE result data,
- scoring engine,
- process knowledge schema,
- next DOE recommendation logic.

Process-specific report templates can specialize this generic structure:

- `docs/wire-bonding-2nd-bond-report-template.md`: report surface for 2nd-bond
  wire bonding with Pull Force, Failure Code, and Ball Shear guardrails.

## Inputs

| Input | Source |
| --- | --- |
| DOE design table | user / planner |
| DOE result table | experiment / simulator |
| Y catalog | process knowledge file |
| X catalog | process knowledge file |
| Mechanism map | process knowledge file |
| Previous DOE state | planner memory / experiment folder |
| Experiment budget | user / project settings |

Required result columns:

| Column type | Examples |
| --- | --- |
| Run identifiers | Run, Rep |
| X values | A, B, C, D |
| Y values | BLT, die shear, void grade, bleed grade |
| Derived pass/fail | Spec Pass, Failure Reason |
| Secondary metrics | process time, material usage |

## Output Sections

Every report should have the same structure.

```text
1. DOE round summary
2. X/Y definition
3. Y-type and analysis method
4. Run-level result table
5. Response-level analysis
6. Score table
7. Bottleneck Y decision
8. Process-mechanism validation
9. Production validation
10. Baseline state decision
11. Next DOE recommendation or final conclusion
12. Remaining risk
```

## 1. DOE Round Summary

Required fields:

| Field | Example |
| --- | --- |
| DOE round | Round 5 |
| DOE purpose | mixed time-improvement DOE |
| Baseline condition | A0.85/B425/C800/D12 |
| Runs | 8 |
| Repeats | 3 |
| Main question | Can C/D time be reduced without breaking quality? |

## 2. X/Y Definition

X table:

| X | Name | Unit | Role tag | Tested levels |
| --- | --- | --- | --- | --- |
| A | Epoxy amount | mg-equivalent | quality primary | 0.85 |
| B | Bond force | gf | quality primary | 425 |
| C | Bond time | ms | quality-production mixed | 800, 750, 700 |
| D | Wetting time | sec | quality-production mixed | 12, 10, 9 |

Y table:

| Y | Type | Role | Spec | Preference |
| --- | --- | --- | --- | --- |
| BLT | continuous | primary | 35-55 um | lower within spec |
| Die shear | continuous | primary | >= 22 MPa | higher |
| Void grade | ordinal | guardrail | <= 1 | lower |
| Bleed grade | ordinal | guardrail | <= 1 | lower |
| Process time | continuous | secondary | none | lower |

## 3. Y-Type and Analysis Method

The report should explicitly justify the analysis method.

| Y type | Reported analysis |
| --- | --- |
| Continuous | mean, min, max, margin, effect when design supports it |
| Ordinal grade | worst grade, risky count, pass/fail decision |
| Categorical | code counts, bad-code rate |
| Count | defect count, defect density |
| Proportion | numerator/denominator, rate |

Example sentence:

```text
BLT and die shear are continuous Y values, so the report uses mean, min/max,
and spec margin. Void and bleed are ordinal guardrails, so worst grade controls
the decision rather than average grade.
```

## 4. Run-Level Result Table

For each run:

| Run | X condition | Pass count | BLT min/max | Shear min | Void worst | Bleed worst | Time avg | Decision |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |

Decision vocabulary:

- pass,
- candidate,
- borderline,
- guardrail fail,
- spec fail,
- rejected boundary,
- confirmed baseline repeat.

## 5. Response-Level Analysis

For each Y:

### Continuous Y

| Candidate | mean | min | max | spec margin | pass count | interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |

### Guardrail Y

| Candidate | good count | risky count | worst grade/code | decision |
| --- | ---: | ---: | --- | --- |

### Secondary Production Y

| Candidate | quality status | time/material value | benefit vs baseline | decision |
| --- | --- | ---: | ---: | --- |

## 6. Score Table

Use the scoring engine output.

| Candidate | Quality | Guardrail | Repeatability | Process | Production | State |
| --- | ---: | ---: | ---: | ---: | ---: | --- |

The score table must be followed by gate decisions:

| Gate | Pass/fail | Evidence |
| --- | --- | --- |
| Hard guardrail | pass | void/bleed worst <= 1 |
| Primary spec | pass | BLT and shear pass |
| Repeatability | pass | repeated baseline pass |
| Production | partial | time remains high |

## 7. Bottleneck Y Decision

The report must name the current bottleneck Y.

| Candidate issue | Bottleneck Y | Why |
| --- | --- | --- |
| C/D reduction fails by shear/void/bleed | shear + guardrail | time reduction consumes quality margin |

Possible bottleneck categories:

- primary spec fail,
- weak margin,
- guardrail fail,
- repeatability instability,
- production burden,
- measurement uncertainty.

## 8. Process-Mechanism Validation

Mechanism validation comes from the process knowledge schema.

| Statistical finding | Mechanism rule | Plausibility | Decision impact |
| --- | --- | --- | --- |
| Reducing D creates void risk | wetting time supports spread/settling | high | reject D reduction |
| Reducing C lowers shear margin | bond time supports contact/strength | high | reject C reduction |

## 9. Production Validation

Production validation is only allowed after quality pass.

| Candidate | Quality | Time/material benefit | Risk | Production decision |
| --- | --- | ---: | --- | --- |

Example:

```text
D=10 reduces process time materially, but it creates void and low-shear risk.
The production benefit is rejected because quality guardrails fail.
```

## 10. Baseline State Decision

| Candidate | Evidence | State |
| --- | --- | --- |
| A0.85/B425/C800/D12 | repeated pass, no guardrail fail | confirmed baseline |
| A0.85/B425/C750/D12 | one bleed risk | rejected boundary |
| A0.85/B425/C800/D10 | void/shear risk | rejected boundary |

## 11. Next DOE Recommendation or Final Conclusion

If continuing:

| Next DOE | Reason |
| --- | --- |
| confirmation DOE | baseline is promising but repeatability unknown |
| production-efficiency DOE | confirmed baseline and quality margin is sufficient |
| guardrail stabilization DOE | failure code/defect/void/bleed blocks adoption |

If ending:

```text
Recommend [condition] as [decision state].
Reject [directions] because [evidence].
Residual risk: [small sample, lab transfer, measurement uncertainty].
```

## 12. Remaining Risk

Every final report must include residual risk.

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Small sample count | cannot prove production stability | repeat final candidate if time allows |
| Visual grade subjectivity | inspector variation | define image/grade rules |
| Lab tool transfer | practice equipment is not production line | engineer/pilot validation |
| Fixed upstream conditions | hidden confounders possible | log materials, lot, operator, tool state |

## Implementation Sequence

The report generator should be built in this order:

1. Parse DOE result CSV.
2. Load process knowledge file.
3. Classify Y values from Y catalog.
4. Calculate run-level summaries.
5. Calculate margins and guardrail decisions.
6. Calculate scores.
7. Identify bottleneck Y.
8. Select next DOE purpose or final conclusion.
9. Render Markdown report.
10. Optionally render charts/tables for presentation.

## Minimum MVP Output

For the portfolio MVP, the first automated report only needs:

- run-level summary table,
- Y-type classification,
- score table,
- bottleneck Y,
- process validation table,
- production validation table,
- next DOE/final recommendation.

Do not start with a web app. A Markdown report generated from CSV is enough to
prove the decision engine.
