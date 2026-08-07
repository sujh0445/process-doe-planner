import pandas as pd

from ai_doe_planner.criteria import (
    ConditionDecision,
    _condition_sort_key,
    canonical_criterion_role,
    evaluate_conditions,
)
from ai_doe_planner.schemas import DoeRequest
from ai_doe_planner.statistics import analyze_responses


def test_condition_sort_key_prioritizes_state_before_score():
    decisions = [
        ConditionDecision("rejected", {}, "rejected", 0.0, 100.0, 99.0, ()),
        ConditionDecision("borderline", {}, "borderline", 40.0, 0.0, 10.0, ()),
        ConditionDecision("candidate", {}, "candidate", 20.0, 0.0, 1.0, ()),
    ]

    ordered = sorted(decisions, key=_condition_sort_key)

    assert [item.state for item in ordered] == ["candidate", "borderline", "rejected"]


def test_decision_role_aliases_drive_production_evidence_and_scoring():
    request = DoeRequest.from_dict(
        {
            "project": {"name": "Alias role DOE"},
            "objective": {
                "primary_goal": "Keep chipping under spec while increasing feed speed.",
                "decision_mode": "criteria_first",
            },
            "factors": [
                {
                    "name": "Feed speed",
                    "column": "feed",
                    "unit": "mm/s",
                    "levels": [50, 150],
                    "role": "productivity_factor",
                    "production_direction": "higher_is_better",
                }
            ],
            "responses": [
                {
                    "name": "Max chipping",
                    "column": "chipping",
                    "type": "continuous",
                    "role": "primary_quality_y",
                    "direction": "lower_is_better",
                    "unit": "um",
                    "spec": {"upper_spec": 12.0},
                    "measurement_method": "High-scope max chipping measurement.",
                }
            ],
            "criteria": [
                {
                    "name": "Spec pass/fail",
                    "decision_role": "spec_pass_fail",
                    "metric": "fail_count",
                    "pass_rule": "fail_count == 0",
                },
                {
                    "name": "Productivity trade-off",
                    "decision_role": "production_tradeoff",
                    "metric": "feed speed",
                    "pass_rule": "prefer higher feed only after quality passes",
                },
            ],
            "mechanism_hypotheses": ["Higher feed can improve throughput but may increase chipping risk."],
        }
    )
    df = pd.DataFrame(
        [
            {"feed": 50, "chipping": 4.5},
            {"feed": 50, "chipping": 4.7},
            {"feed": 150, "chipping": 5.5},
            {"feed": 150, "chipping": 5.8},
        ]
    )

    analysis = analyze_responses(df, request)
    decisions = evaluate_conditions(df, request, analysis)
    by_feed = {item.condition_values["feed"]: item for item in decisions["condition_decisions"]}

    assert canonical_criterion_role("spec_pass_fail") == "quality_gate"
    assert canonical_criterion_role("production_tradeoff") == "production_objective"
    assert by_feed[150].production_score == 100.0
    assert by_feed[50].production_score == 0.0
    assert any(item["role"] == "production_objective" for item in by_feed[150].criteria_evidence)
