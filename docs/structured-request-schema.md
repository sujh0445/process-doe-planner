# Structured Request Schema

## Purpose

The AI DOE Planner should not generate a DOE matrix directly from free-form conversation.

The first step is to convert the user's request into a structured DOE request. This makes the planner inspectable, repeatable, and connectable to validation, risk gates, statistical tools, and report generation.

The LLM's role here is to extract intent, map the request into fields, identify missing information, and ask for review when needed.

The LLM should not decide that a condition is safe, relax equipment limits, guess units, invent process windows, or calculate statistical results from memory.

## Core Flow

```text
User natural language
-> LLM structured extraction
-> structured DOE request
-> schema validation
-> risk gate
-> allowed factor space
-> DOE generator
```

## Minimum Request Fields

| Field group | Required content | Why it matters |
| --- | --- | --- |
| Project identity | project name, process area, equipment, recipe family | Keeps evidence and decisions tied to the right context |
| Objective | problem statement, improvement direction, production goal | Prevents optimizing the wrong thing |
| Response variables | Y name, Y type, unit, spec, target direction, role | Determines analysis method and decision criteria |
| Candidate factors | X name, unit, current value, proposed low/high, controllability | Defines the DOE design space |
| Factor boundaries | equipment limit, process window, review zone, practical DOE range | Prevents unsafe or unrealistic DOE tables |
| Measurement plan | measurement tool, sampling rule, repeat count, known measurement risk | Determines whether the data can support a decision |
| Evidence links | source document, engineer comment, FMEA/manual reference, prior run | Makes the recommendation explainable |
| Constraints | max runs, available samples, time, materials, production priority | Drives DOE mode selection |

## Y Type Classification

Each response variable should be classified before analysis.

| Y type | Examples | Typical analysis route |
| --- | --- | --- |
| Continuous | chipping size, pull force, die shear, BLT, warpage | descriptive stats, effect analysis, ANOVA, regression, capability margin |
| Count | number of voids, over-spec count, defect count | count summary, rate comparison, proportion/Poisson-style checks |
| Binary | pass/fail, good/bad, normal/abnormal | pass rate, fail rate, proportion test, risk gating |
| Ordinal/code | failure code, defect class, visual grade | code distribution, bad-code rate, weighted risk only when justified |
| Image-derived | void area ratio, sweep ratio, defect area | image processing output first, then analyze as continuous/count/binary |

## Factor Range Tags

Low/high values in a DOE request are not automatically equipment minimum and maximum values.

They should be tagged as one of:

| Range type | Meaning |
| --- | --- |
| equipment_limit | physical or recipe-entry limit |
| process_window | known safe operating window |
| review_zone | possible but needs engineer review |
| practical_doe_range | range selected for the current DOE |
| refinement_range | narrowed range after previous DOE |

This prevents the planner from treating a screening low/high range as a machine limit.

## Example JSON Shape

```json
{
  "project": {
    "name": "Wafer sawing feed refinement",
    "process_area": "wafer_sawing",
    "equipment": "DISCO DAD 3241",
    "recipe_family": "8-inch silicon wafer sawing"
  },
  "objective": {
    "primary_goal": "increase feed speed while keeping chipping risk acceptable",
    "business_goal": "reduce cutting time",
    "decision_mode": "quality-first productivity improvement"
  },
  "responses": [
    {
      "name": "max_chipping_size",
      "type": "continuous",
      "unit": "um",
      "direction": "lower_is_better",
      "role": "primary_quality_y",
      "spec": {
        "upper_spec": null,
        "baseline_compare": true
      },
      "measurement_method": "measure the largest chipping depth on each sampled chip edge"
    }
  ],
  "factors": [
    {
      "name": "spindle_rpm",
      "unit": "rpm",
      "current": 50000,
      "practical_doe_range": [30000, 50000],
      "controllable": true
    },
    {
      "name": "feed_speed",
      "unit": "mm/s",
      "current": 50,
      "practical_doe_range": [50, 150],
      "controllable": true
    }
  ],
  "constraints": {
    "max_runs": 4,
    "samples_per_condition": 10,
    "measurement_bottleneck": "high-scope manual measurement"
  }
}
```

## Validation Outcome

The structured request should first produce one of:

| Status | Meaning |
| --- | --- |
| PASS | Required fields are present and interpretable |
| HOLD | DOE draft may be possible, but engineer review or missing detail is needed |
| BLOCK | DOE generation should stop because the request is invalid or unsafe |

## Implementation Note

This schema can be implemented with Pydantic or a similar structured validation layer. The exact framework is less important than the principle:

```text
LLM text -> typed object -> deterministic validation -> auditable downstream decision
```
