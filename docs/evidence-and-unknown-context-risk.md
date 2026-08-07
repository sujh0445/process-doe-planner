# Evidence And Unknown Context Risk

## Purpose

The planner should distinguish between:

```text
Known risk: risk supported by process window, FMEA, manual, or engineer evidence
Unknown risk: risk caused by missing evidence, unfamiliar recipe, shifted equipment state, or weak history
```

This prevents the system from treating "no known problem" as "safe."

## Evidence Sources

| Source type | Examples |
| --- | --- |
| process card | expected mechanism, key factors, known interactions |
| equipment card | model, controllable parameters, limits, review zones |
| measurement SOP | how Y is measured, sampling rule, known measurement weakness |
| FMEA/control plan | failure mode, cause, prevention/detection controls |
| lecture/transcript note | engineer explanation, lab constraint, practical warning |
| prior DOE/run | previous condition, result, recommended next action |
| manual/spec | equipment or quality requirement |

## Evidence Record

Evidence should be stored with an ID so a report can cite it.

```json
{
  "evidence_id": "WB2ND-ENG-001",
  "source_type": "engineer_comment",
  "process_area": "wire_bonding_2nd",
  "claim": "Second bond quality is sensitive to ultrasonic energy and bond force.",
  "used_for": [
    "factor_priority",
    "interaction_hypothesis",
    "mechanism_consistency"
  ],
  "confidence": "medium",
  "source_path": "docs/process-cards/wire-bonding-2nd.md"
}
```

## Unknown Context Components

| Component | Meaning |
| --- | --- |
| historical_distance | How far the proposed condition is from known prior runs |
| recipe_family_mismatch | Whether the recipe family differs from known context |
| evidence_gap | Whether important rules have no supporting evidence |
| equipment_state_shift | Whether PM, chamber state, blade wear, material batch, or setup changed |
| measurement_confidence_gap | Whether the measurement method is too weak for the decision |

## Gate Interpretation

| Unknown context state | Meaning | Action |
| --- | --- | --- |
| low | Context is familiar and evidence is adequate | Continue |
| medium | Some missing evidence or range expansion exists | HOLD or conservative DOE |
| high | Key context is unfamiliar or unsupported | BLOCK or require engineer review |

## Evidence Gap Rule

```text
No evidence of risk != evidence of no risk.
```

For example:

```text
If a new wire bonding setting has no prior data and no engineer comment,
the planner should not call it safe just because the failure code has not appeared yet.
```

## How Evidence Is Used

Evidence supports five parts of the engine:

1. request validation
2. factor prioritization
3. interaction hypothesis
4. decision criteria generation
5. next DOE recommendation

## MVP Search Strategy

The first version does not need a vector database.

Use a local evidence store first:

```text
process cards
equipment cards
measurement cards
FMEA/control plan notes
prior DOE reports
```

Then perform keyword or tag-based retrieval:

```text
process_area + factor + Y + failure mode + equipment
```

RAG/vector search can be added later, after the evidence format is stable.

## Report Requirement

Every major recommendation should include:

| Report item | Example |
| --- | --- |
| evidence used | engineer note says feed speed increases chipping risk |
| evidence missing | no data for feed above 150 mm/s |
| unknown risk | manual high-scope measurement has limited repeatability |
| action | propose confirmation DOE before final adoption |
