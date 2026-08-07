# Artifact Logging And Feedback Loop

## Purpose

The planner should leave behind artifacts for every DOE cycle.

This turns the system from a chat-based assistant into an inspectable engineering workflow.

The goal is:

```text
same input + same rules + same data
-> same validation result
-> same analysis outputs
-> traceable recommendation
```

## Run Folder Structure

Each DOE cycle should be saved as a run folder.

```text
runs/
  2026-08-03_wafer_sawing_feed_refinement/
    input_request.json
    structured_request.json
    validation_report.json
    risk_gate_result.json
    retrieved_evidence.json
    unknown_context_report.json
    allowed_factor_space.json
    doe_matrix.csv
    metrology_plan.json
    experiment_results.csv
    stats_outputs/
      summary_tables.csv
      effect_table.csv
      plots/
    decision_criteria_eval.json
    next_doe_recommendation.json
    decision_log.json
    report.md
```

## Decision Log

The decision log should capture not only the final decision but also why alternatives were rejected.

```json
{
  "cycle_id": "wafer5_feed110_confirmation",
  "recommendation": "adopt feed 110 mm/s at 50k rpm as provisional final condition",
  "basis": [
    "tail risk acceptable versus baseline",
    "productivity improved versus feed 50",
    "measurement confidence still limited"
  ],
  "alternatives": [
    {
      "option": "increase feed to 130 mm/s",
      "status": "rejected",
      "reason": "higher tail risk and weaker confirmation"
    }
  ],
  "human_review": {
    "required": true,
    "reason": "manual chipping measurement and limited sample size"
  }
}
```

## Feedback Loop

```text
planned DOE
-> measured result
-> statistical analysis
-> project-specific criteria evaluation
-> process/mechanism review
-> production trade-off review
-> next DOE or final recommendation
-> log what changed
```

## What Gets Updated

| Artifact | Update rule |
| --- | --- |
| process card | Add confirmed or contradicted mechanism observations |
| equipment card | Add practical DOE ranges and review zones |
| measurement card | Add sampling weakness or repeatability note |
| criteria file | Add project-specific decision rules |
| regression scenarios | Add PASS/HOLD/BLOCK examples |
| report template | Add recurring evidence pattern |

## Regression Scenarios

The system should keep small test scenarios so future changes do not silently alter the decision logic.

| Scenario | Expected result |
| --- | --- |
| missing unit | HOLD |
| factor above hard limit | BLOCK |
| all quality specs pass but measurement confidence is weak | HOLD or confirm |
| primary Y passes but bad failure code appears | risky candidate, not clean pass |
| productivity improves but tail risk worsens | trade-off review required |

## Reporting Principle

A DOE recommendation should show:

1. what data was analyzed
2. what statistical evidence was found
3. which project-specific criteria passed or failed
4. what process mechanism supports or contradicts the result
5. what production benefit or risk exists
6. why the next DOE mode was selected

## Portfolio Framing

```text
The system was designed not as a black-box optimizer, but as a structured DOE decision copilot.
It records request structure, validation, risk gate results, statistical evidence,
process-mechanism interpretation, production trade-off, and the final next-DOE rationale.
```
