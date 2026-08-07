# Project-Specific Decision Criteria

## Purpose

The next DOE should not be selected by statistics alone.

For each DOE project, the planner should first generate project-specific decision criteria. Statistical analysis, process knowledge, and production constraints are then used as evidence to evaluate those criteria.

```text
Project criteria decide what matters.
Statistics provide evidence.
Process knowledge checks whether the evidence makes sense.
Production constraints decide whether the recommendation is usable.
```

## Why This Matters

Different DOE projects have different definitions of "better."

| Project type | Likely decision focus |
| --- | --- |
| Wafer sawing | worst-case chipping, tail risk, feed-speed productivity |
| Wire bonding | pull force pass rate, risky failure codes, bond mechanism |
| Die attach | BLT spec, die shear strength, epoxy/time trade-off |
| Molding | wire sweep, sagging risk, void/visual defects, cycle time |

## Criteria Sources

Project-specific criteria should be built from:

| Source | Example |
| --- | --- |
| Objective | improve productivity while maintaining quality |
| Primary Y | pull force, chipping size, BLT, wire sweep |
| Secondary Y | material usage, cycle time, visual defect grade |
| Spec or guardrail | pull force >= 7 g, no critical failure code |
| Measurement method | manual high-scope measurement, X-ray visual judgment |
| Process mechanism | force and epoxy amount jointly control BLT |
| Production constraint | feed speed improves throughput |
| Evidence | engineer comment, lecture note, FMEA, prior run |

## Portability Rule

The criterion framework is reusable, but the selected criteria and thresholds are not automatically portable.

For example, the wafer sawing project uses max chipping, over-spec count, p95/tail risk, and productivity trade-off because the project goal is:

```text
Raise feed speed while preventing unacceptable local chipping.
```

That does not mean a molding, wire bonding, or die attach DOE should use the same main criteria. A new project must regenerate its decision criteria from its own objective, Y type, failure mode, measurement method, and production constraint.

```text
Reuse the engine.
Do not blindly reuse another project's decision criteria.
```

## Universal Criterion Types

These are reusable criterion types, but each project chooses which ones matter.

| Criterion type | Meaning |
| --- | --- |
| spec_pass_fail | Does the condition satisfy hard quality requirements? |
| over_spec_count | How often does the condition exceed a limit? |
| worst_case_tail_risk | Is the worst or p95 behavior dangerous? |
| capability_margin | How far is the condition from the spec boundary? |
| productivity_tradeoff | Does a faster/cheaper setting harm quality too much? |
| measurement_confidence | Is the measurement reliable enough to decide? |
| mechanism_consistency | Does the statistical direction match process mechanism? |
| bottleneck_y_focus | Which Y currently blocks the next improvement? |
| next_doe_readiness | Is the evidence strong enough to confirm, refine, or screen again? |

## Decision Criteria Record

Each criterion should be stored as a structured record.

```json
{
  "criterion_id": "wafer_sawing_tail_risk",
  "name": "Worst-case chipping risk",
  "applies_to_y": "max_chipping_size",
  "priority": "primary",
  "decision_role": "quality_gate",
  "metric": "max and p95 by condition",
  "pass_rule": "must not show unacceptable tail risk versus baseline",
  "evidence_required": [
    "measurement_sop",
    "process_mechanism_note",
    "condition_summary_table"
  ],
  "next_doe_impact": "If tail risk increases, reduce feed range or confirm at safer feed."
}
```

## Criteria-To-DOE Routing

| Criteria state | Next DOE direction |
| --- | --- |
| No condition passes quality gate | Re-screen or move toward known safe region |
| One condition barely passes but margin is weak | Confirmation DOE or local refinement |
| Several conditions pass, productivity differs | Productivity trade-off DOE |
| Primary Y passes but secondary Y fails | Focus on bottleneck Y factors |
| Results conflict with process mechanism | Mechanism-check DOE or repeat key condition |
| Measurement confidence is weak | Repeat measurement or improve sampling before aggressive DOE |
| Good baseline found with strong margin | Conservative productivity improvement or mixed confirmation DOE |

## Example: Wafer Sawing

For the wafer sawing project, the criteria were built around the actual project logic:

| Criterion | Meaning |
| --- | --- |
| Spec/pass guardrail | Chipping behavior must remain acceptable |
| Worst-case/tail risk | A single severe chipping event can make a condition risky |
| Baseline comparison | Compare feed increase against a known safe baseline |
| Productivity trade-off | Higher feed speed improves cutting time |
| Measurement confidence | Manual chipping measurement has limited reliability |
| Mechanism consistency | Higher RPM is expected to reduce chipping; higher feed is expected to increase chipping |

This justifies:

```text
Fix RPM high after checking its direction,
then sweep feed speed to find how far productivity can be improved
without creating unacceptable chipping risk.
```

## Important Rule

Statistics should answer:

```text
Given our project-specific criteria, what does the data support?
```

not:

```text
Which condition has the best average, therefore what should we do?
```

Round-level pooled statistics are optional diagnostics. They should not become the default decision basis when the DOE contains multiple process conditions. The primary decision should normally be made from condition-level evidence evaluated against the active project criteria.
