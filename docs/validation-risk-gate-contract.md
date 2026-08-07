# Validation And Risk Gate Contract

## Purpose

The planner needs a gate before it generates a DOE matrix.

This gate separates three questions:

1. Is the request structurally valid?
2. Is the proposed factor space inside an allowed or reviewable process window?
3. Is there enough evidence and context to recommend a DOE responsibly?

The gate protects the system from producing a confident-looking DOE table from weak, missing, or unsafe inputs.

## Gate Stack

```text
Structured DOE request
-> schema validation
-> completeness check
-> unit and type check
-> process window check
-> review-zone check
-> evidence check
-> unknown-context check
-> final PASS / HOLD / BLOCK
```

## Status Definitions

| Status | Meaning | DOE generator behavior |
| --- | --- | --- |
| PASS | Input is valid and the selected factor space is allowed | Generate DOE matrix |
| HOLD | Input may be usable, but a human review item remains | Generate review-marked draft only, or ask for review |
| BLOCK | Input is invalid, unsafe, or outside hard constraints | Do not generate DOE matrix |

## Validation Report Fields

| Field | Meaning |
| --- | --- |
| state | PASS, HOLD, or BLOCK |
| blocking_reasons | Issues that prevent DOE generation |
| review_reasons | Issues that require engineer/user review |
| missing_fields | Required or recommended fields not provided |
| unit_warnings | Missing, inconsistent, or suspicious units |
| y_type_warnings | Ambiguous response type or measurement type |
| factor_range_warnings | Low/high looks like equipment limit, not DOE range, or vice versa |
| recommended_questions | Questions to ask before proceeding |

## Risk Gate Fields

| Field | Meaning |
| --- | --- |
| state | PASS, HOLD, or BLOCK |
| hard_limit_violations | Conditions outside equipment or process hard limits |
| review_zone_hits | Conditions inside review zone but not blocked |
| allowed_factor_space | Factor ranges that the DOE generator is allowed to use |
| evidence_coverage | Whether each important rule has supporting evidence |
| unknown_context_score | Risk from missing history, missing evidence, or shifted chamber/equipment state |
| human_review_required | Explicit items that require engineer review |

## Window Types

| Window type | Meaning | Gate result |
| --- | --- | --- |
| hard_limit | Must not exceed | BLOCK |
| process_window | Known acceptable range | PASS if other checks pass |
| review_zone | Possible but uncertain | HOLD unless reviewed |
| practical_doe_range | Current experiment range selected within the allowed space | PASS if supported |

## Human Review Rule

HOLD should not mean failure.

HOLD means:

```text
The system found a review item that should be explicitly accepted, changed, or rejected by a human.
```

This is important for portfolio explanation because it shows the system is not pretending to replace process engineers.

## Contract With DOE Generator

The DOE generator must consume only the `allowed_factor_space` produced by the gate.

```text
Bad:
user low/high -> DOE table

Good:
user low/high -> validation/risk gate -> allowed factor space -> DOE table
```

The CLI follows this contract:

```bash
ai-doe validate --request request.yaml [--data results.csv]
ai-doe design --request request.yaml --explain
```

Design behavior:

- `PASS`: generate the DOE table normally.
- `HOLD`: stop by default; generate only when `--allow-hold` is explicitly used.
- `BLOCK`: stop and do not generate a DOE table.

The current implementation returns these practical fields:

- `state`
- `human_review_required`
- `allowed_factor_space`
- `findings`
- `blocking_reasons`
- `review_reasons`
- `missing_fields`
- `unit_warnings`
- `y_type_warnings`
- `factor_range_warnings`
- `recommended_questions`
