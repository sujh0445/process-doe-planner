from __future__ import annotations

from itertools import product
from typing import Any

import pandas as pd

from .schemas import DoeRequest, Factor


def _factor_levels(factor: Factor) -> list[Any]:
    if factor.levels:
        return list(factor.levels)
    if factor.low is not None and factor.high is not None:
        return [factor.low, factor.high]
    if factor.practical_range is not None:
        return [factor.practical_range[0], factor.practical_range[1]]
    if factor.current is not None:
        return [factor.current]
    raise ValueError(f"Factor {factor.name} has no levels, low/high, range, or current value.")


def generate_full_factorial(request: DoeRequest) -> pd.DataFrame:
    factor_columns = [factor.column for factor in request.factors]
    level_sets = [_factor_levels(factor) for factor in request.factors]
    rows = []
    for run, values in enumerate(product(*level_sets), start=1):
        row = {"run": run}
        row.update(dict(zip(factor_columns, values)))
        rows.append(row)
    return pd.DataFrame(rows)


def _normalized_design_type(request: DoeRequest) -> str:
    raw = str(request.constraints.get("design_type", "auto")).strip().lower()
    return raw.replace("-", "_").replace(" ", "_")


def _max_runs(request: DoeRequest) -> int | None:
    raw = request.constraints.get("max_runs")
    if raw is None or raw == "":
        return None
    return int(raw)


def _level_counts(request: DoeRequest) -> dict[str, int]:
    return {factor.column: len(_factor_levels(factor)) for factor in request.factors}


def _full_run_count(request: DoeRequest) -> int:
    run_count = 1
    for factor in request.factors:
        run_count *= len(_factor_levels(factor))
    return run_count


def _is_two_level_request(request: DoeRequest) -> bool:
    return all(len(_factor_levels(factor)) == 2 for factor in request.factors)


def _fractional_run_count(request: DoeRequest) -> int:
    return 2 ** (len(request.factors) - 1)


def _coded_half_fraction_rows(factor_count: int) -> list[tuple[int, ...]]:
    if factor_count not in {4, 5}:
        raise ValueError("Half-fraction screening is currently supported for 4 or 5 two-level factors.")

    base_factor_count = factor_count - 1
    rows: list[tuple[int, ...]] = []
    for base_levels in product((-1, 1), repeat=base_factor_count):
        generated_level = 1
        for level in base_levels:
            generated_level *= level
        rows.append((*base_levels, generated_level))
    return rows


def _alias_summary(factor_columns: list[str]) -> str:
    if len(factor_columns) == 4:
        a, b, c, d = factor_columns
        defining_relation = " * ".join([a, b, c, d])
        return (
            f"half-fraction; generator {d} = {a} * {b} * {c}; "
            f"defining relation I = {defining_relation}; "
            f"two-factor aliases: {a}*{b} = {c}*{d}, "
            f"{a}*{c} = {b}*{d}, {a}*{d} = {b}*{c}"
        )
    if len(factor_columns) == 5:
        a, b, c, d, e = factor_columns
        defining_relation = " * ".join([a, b, c, d, e])
        return (
            f"half-fraction; generator {e} = {a} * {b} * {c} * {d}; "
            f"defining relation I = {defining_relation}; "
            "main effects are aliased with four-factor interactions and two-factor effects with three-factor interactions"
        )
    return "half-fraction screening"


def generate_fractional_factorial(request: DoeRequest) -> pd.DataFrame:
    if not _is_two_level_request(request):
        raise ValueError("Fractional factorial generation requires exactly two levels for every factor.")

    factor_columns = [factor.column for factor in request.factors]
    coded_rows = _coded_half_fraction_rows(len(request.factors))
    level_sets = [_factor_levels(factor) for factor in request.factors]
    alias_summary = _alias_summary(factor_columns)

    rows = []
    for run, coded_values in enumerate(coded_rows, start=1):
        row = {"run": run}
        for column, levels, coded_value in zip(factor_columns, level_sets, coded_values):
            row[column] = levels[0] if coded_value == -1 else levels[1]
        row["design_type"] = "fractional_factorial_half_fraction"
        row["alias_structure"] = alias_summary
        rows.append(row)
    return pd.DataFrame(rows)


def describe_design_plan(request: DoeRequest) -> dict[str, Any]:
    design_type = _normalized_design_type(request)
    full_run_count = _full_run_count(request)
    max_runs = _max_runs(request)
    factor_columns = [factor.column for factor in request.factors]
    common = {
        "requested_design_type": design_type,
        "factor_count": len(request.factors),
        "level_counts": _level_counts(request),
        "full_factorial_runs": full_run_count,
        "max_runs": max_runs,
        "alias_structure": "",
        "warnings": [],
        "rejected_alternatives": [],
    }

    if design_type in {"full", "full_factorial"}:
        warnings = []
        if max_runs is not None and full_run_count > max_runs:
            warnings.append(
                f"Explicit full factorial request requires {full_run_count} runs, exceeding max_runs={max_runs}."
            )
        return {
            **common,
            "selected_design_type": "full_factorial",
            "selected_runs": full_run_count,
            "rationale": "A full factorial design was explicitly requested.",
            "warnings": warnings,
        }

    if design_type in {"fractional", "fractional_factorial", "half_fraction", "screening_fractional"}:
        if not _is_two_level_request(request):
            raise ValueError("Fractional factorial generation requires exactly two levels for every factor.")
        selected_runs = _fractional_run_count(request)
        if len(request.factors) not in {4, 5}:
            raise ValueError("Half-fraction screening is currently supported for 4 or 5 two-level factors.")
        warnings = [
            "Fractional screening reduces run count but aliases some effects; resolve important aliases in a follow-up DOE."
        ]
        if max_runs is not None and selected_runs > max_runs:
            warnings.append(
                f"Requested half-fraction requires {selected_runs} runs, exceeding max_runs={max_runs}."
            )
        return {
            **common,
            "selected_design_type": "fractional_factorial_half_fraction",
            "selected_runs": selected_runs,
            "rationale": "A half-fraction screening design was explicitly requested.",
            "alias_structure": _alias_summary(factor_columns),
            "warnings": warnings,
        }

    if design_type != "auto":
        raise ValueError(f"Unsupported design_type: {request.constraints.get('design_type')}")

    if max_runs is None or full_run_count <= max_runs:
        return {
            **common,
            "selected_design_type": "full_factorial",
            "selected_runs": full_run_count,
            "rationale": (
                "Full factorial was selected because the requested factor levels fit within the run budget."
                if max_runs is not None
                else "Full factorial was selected because no max_runs constraint was provided."
            ),
        }

    if _is_two_level_request(request) and len(request.factors) in {4, 5}:
        fractional_run_count = _fractional_run_count(request)
        if fractional_run_count <= max_runs:
            return {
                **common,
                "selected_design_type": "fractional_factorial_half_fraction",
                "selected_runs": fractional_run_count,
                "rationale": (
                    f"Full factorial requires {full_run_count} runs, exceeding max_runs={max_runs}. "
                    f"A half-fraction screening design fits in {fractional_run_count} runs."
                ),
                "alias_structure": _alias_summary(factor_columns),
                "warnings": [
                    "Use process mechanism knowledge to interpret aliased effects; schedule follow-up DOE if an aliased term becomes decision-critical."
                ],
                "rejected_alternatives": [
                    {
                        "design_type": "full_factorial",
                        "reason": f"requires {full_run_count} runs, exceeding max_runs={max_runs}",
                    }
                ],
            }

    raise ValueError(
        f"Full factorial requires {full_run_count} runs, but max_runs is {max_runs}. "
        "Reduce active factors/levels or set a supported fractional design for 4 or 5 two-level factors."
    )


def generate_design(request: DoeRequest) -> pd.DataFrame:
    plan = describe_design_plan(request)
    selected_design_type = plan["selected_design_type"]
    if selected_design_type == "full_factorial":
        return generate_full_factorial(request)
    if selected_design_type == "fractional_factorial_half_fraction":
        return generate_fractional_factorial(request)
    raise ValueError(f"Unsupported selected design type: {selected_design_type}")


def _as_float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_level(value: float) -> float | int:
    rounded = round(value, 6)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def _single_condition_table(condition_values: dict[str, Any]) -> pd.DataFrame:
    row = {"run": 1}
    row.update(condition_values)
    return pd.DataFrame([row])


def _ranked_decisions(criteria_result: dict[str, Any], states: set[str] | None = None) -> list[Any]:
    decisions = list(criteria_result.get("condition_decisions", []))
    if states is not None:
        decisions = [decision for decision in decisions if decision.state in states]
    return decisions


def _production_bounds(factor: Factor, current_value: float) -> tuple[float, float]:
    if factor.practical_range is not None:
        return factor.practical_range
    low = _as_float_or_none(factor.low)
    high = _as_float_or_none(factor.high)
    if low is not None and high is not None:
        return low, high
    return current_value, current_value


def _productivity_refinement_option(request: DoeRequest, best: Any, priority: int) -> dict[str, Any] | None:
    factor = request.production_factor
    if factor is None:
        return None

    base = dict(best.condition_values)
    current_value = _as_float_or_none(base.get(factor.column))
    if current_value is None:
        return None

    low, high = _production_bounds(factor, current_value)
    if factor.production_direction == "higher_is_better":
        candidate_levels = sorted({current_value, min(high, current_value * 1.10), high})
    else:
        candidate_levels = sorted({current_value, max(low, current_value * 0.90), low}, reverse=True)

    rows = []
    for run, level in enumerate(candidate_levels, start=1):
        row = {"run": run}
        row.update(base)
        row[factor.column] = _format_level(level)
        rows.append(row)

    rationale = (
        f"Best current condition passes quality criteria. Keep other factors fixed and refine "
        f"{factor.column} to quantify the productivity trade-off without changing the full process window."
    )
    return {
        "mode": "productivity_refinement_or_confirmation",
        "title": "Productivity refinement or confirmation",
        "priority": priority,
        "rationale": rationale,
        "decision_basis": [
            f"Best condition state is {best.state}, so production refinement is allowed after quality screening.",
            f"{factor.column} is marked as the production trade-off factor.",
            f"Refinement stays inside the practical factor bounds {low} to {high}.",
        ],
        "table": pd.DataFrame(rows),
    }


def _confirmation_option(best: Any, priority: int) -> dict[str, Any]:
    return {
        "mode": "confirmation_doe",
        "title": "Best-condition confirmation",
        "priority": priority,
        "rationale": (
            "Repeat the current best condition to confirm measurement stability, tail risk, and repeatability "
            "before treating it as a baseline or final candidate."
        ),
        "decision_basis": [
            f"Current best condition is {best.condition}.",
            "Confirmation is useful when sample size, measurement confidence, or tail risk is still limited.",
        ],
        "table": _single_condition_table(best.condition_values),
    }


def _quality_margin_option(criteria_result: dict[str, Any], best: Any, priority: int) -> dict[str, Any] | None:
    candidates = _ranked_decisions(criteria_result, {"candidate"})
    if not candidates:
        return None

    margin_first = sorted(candidates, key=lambda item: (-item.quality_score, -item.total_score))[0]
    if margin_first.condition == best.condition:
        return None

    return {
        "mode": "quality_margin_confirmation",
        "title": "Quality-margin confirmation",
        "priority": priority,
        "rationale": (
            "If the review prioritizes quality margin over productivity gain, confirm the candidate with the "
            "strongest quality score before pushing the production factor further."
        ),
        "decision_basis": [
            f"Quality-first candidate is {margin_first.condition}.",
            f"Quality score {margin_first.quality_score:.3g} is stronger than the primary best-condition quality margin.",
            "This option protects quality margin before attempting additional productivity gain.",
        ],
        "table": _single_condition_table(margin_first.condition_values),
    }


def _candidate_contrast_option(criteria_result: dict[str, Any], priority: int) -> dict[str, Any] | None:
    ranked = _ranked_decisions(criteria_result, {"candidate", "borderline"})[:3]
    if len(ranked) < 2:
        return None

    rows = []
    for run, decision in enumerate(ranked, start=1):
        row = {
            "run": run,
            "purpose": "candidate_contrast",
            "decision_state": decision.state,
            "quality_score": decision.quality_score,
            "production_score": decision.production_score,
        }
        row.update(decision.condition_values)
        rows.append(row)

    return {
        "mode": "candidate_contrast_confirmation",
        "title": "Candidate contrast confirmation",
        "priority": priority,
        "rationale": (
            "Compare the top candidate conditions under the same measurement plan when the decision is sensitive "
            "to a quality-production trade-off or small sample noise."
        ),
        "decision_basis": [
            f"{len(ranked)} candidate or borderline conditions remain close enough to compare.",
            "Contrast testing separates a real process improvement from small-sample or measurement noise.",
            "Use this when quality and production scores point to different preferred conditions.",
        ],
        "table": pd.DataFrame(rows),
    }


def _response_from_analysis(response_analysis: dict[str, Any] | None, response_name: str) -> Any | None:
    if response_analysis is None:
        return None
    analysis = response_analysis.get(response_name)
    if analysis is None:
        return None
    return analysis.get("response")


def _top_main_effects_for_bottleneck(
    response_analysis: dict[str, Any] | None,
    response_name: str,
    limit: int = 2,
) -> list[dict[str, Any]]:
    if response_analysis is None:
        return []
    analysis = response_analysis.get(response_name)
    if analysis is None:
        return []
    effects = [item for item in analysis.get("effects", []) if item.get("kind") == "main"]
    effects.sort(key=lambda item: abs(float(item.get("effect", 0.0))), reverse=True)
    return effects[:limit]


def _preferred_level_for_effect(effect: dict[str, Any], response: Any) -> Any:
    effect_value = _as_float_or_none(effect.get("effect")) or 0.0
    low_level = effect.get("low_level")
    high_level = effect.get("high_level")
    if response.direction == "higher_is_better":
        return high_level if effect_value >= 0 else low_level
    return high_level if effect_value <= 0 else low_level


def _bottleneck_followup_option(
    request: DoeRequest,
    criteria_result: dict[str, Any],
    best: Any,
    response_analysis: dict[str, Any] | None,
    priority: int,
) -> dict[str, Any] | None:
    bottleneck = criteria_result.get("bottleneck_y")
    if not bottleneck:
        return None
    response_name = bottleneck.get("response")
    response = _response_from_analysis(response_analysis, response_name)
    if response is None:
        return None

    top_effects = _top_main_effects_for_bottleneck(response_analysis, response_name)
    if not top_effects:
        return None

    base = dict(best.condition_values)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[tuple[str, Any], ...]] = set()

    def add_row(values: dict[str, Any], purpose: str, effect_note: str) -> None:
        key = tuple(sorted(values.items()))
        if key in seen:
            return
        seen.add(key)
        row = {"run": len(rows) + 1, "purpose": purpose, "effect_basis": effect_note}
        row.update(values)
        rows.append(row)

    add_row(base, "current_best_reference", "baseline for bottleneck-focused comparison")

    combined = dict(base)
    basis_lines = [
        f"Bottleneck response is {response_name}; fail count={bottleneck.get('fail_count')}, "
        f"weakest margin={bottleneck.get('weakest_margin')}.",
        "Top main-effect terms are used only as statistical evidence; process mechanism review still decides whether the shift is allowed.",
    ]
    for effect in top_effects:
        column = effect["term"]
        preferred = _preferred_level_for_effect(effect, response)
        candidate = dict(base)
        candidate[column] = preferred
        combined[column] = preferred
        effect_note = (
            f"{column}: effect={_format_level(float(effect.get('effect', 0.0)))}, "
            f"relative_weight={_format_level(float(effect.get('relative_effect_weight', 0.0)))}"
        )
        add_row(candidate, f"bottleneck_shift_{column}", effect_note)
        basis_lines.append(
            f"{column} is a top effect for {response_name}; preferred level from current evidence is {preferred}."
        )

    if len(top_effects) >= 2:
        add_row(combined, "combined_bottleneck_shift", "combined shift of top bottleneck factors")

    if len(rows) <= 1:
        return None

    return {
        "mode": "bottleneck_y_focused_followup",
        "title": "Bottleneck-Y focused follow-up",
        "priority": priority,
        "rationale": (
            "Use the response that currently limits the decision as the next DOE focus, then vary the factors "
            "with the strongest evidence for that response while keeping the rest of the process stable."
        ),
        "decision_basis": basis_lines,
        "table": pd.DataFrame(rows),
    }


def _measurement_confidence_option(
    response_analysis: dict[str, Any] | None,
    best: Any,
    priority: int,
    minimum_repeats: int = 3,
) -> dict[str, Any] | None:
    if response_analysis is None:
        return None
    observed_ns: list[int] = []
    for analysis in response_analysis.values():
        for row in analysis.get("by_condition", []):
            try:
                observed_ns.append(int(row.get("n", 0)))
            except (TypeError, ValueError):
                continue
    if not observed_ns or min(observed_ns) >= minimum_repeats:
        return None

    return {
        "mode": "measurement_confidence_confirmation",
        "title": "Measurement-confidence confirmation",
        "priority": priority,
        "rationale": (
            "Repeat the current best condition before changing factors because at least one condition has fewer "
            f"than {minimum_repeats} measurements."
        ),
        "decision_basis": [
            f"Smallest condition-level sample count is {min(observed_ns)}.",
            "The next DOE should separate true process behavior from measurement/sampling noise before widening the factor space.",
        ],
        "table": _single_condition_table(best.condition_values),
    }


def recommend_next_doe_options(
    request: DoeRequest,
    criteria_result: dict[str, Any],
    response_analysis: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    best = criteria_result.get("best_condition")
    if best is None:
        return [
            {
                "mode": "no_recommendation",
                "title": "No recommendation",
                "priority": 1,
                "rationale": "No evaluable conditions were found.",
                "decision_basis": ["No condition-level decisions were available for ranking."],
                "table": pd.DataFrame(),
            }
        ]

    if best.state == "rejected":
        options: list[dict[str, Any]] = []
        priority = 1
        bottleneck_option = _bottleneck_followup_option(request, criteria_result, best, response_analysis, priority)
        if bottleneck_option is not None:
            options.append(bottleneck_option)
            priority += 1
        rationale = "No condition fully passed the quality gate. Move back toward safer known settings or reduce the factor range."
        options.extend(
            [
                {
                    "mode": "rescreen_safer_region",
                    "title": "Safer rescreen",
                    "priority": priority,
                    "rationale": rationale,
                    "decision_basis": [
                        "The best available condition is still rejected by the quality gate.",
                        "Next DOE should move toward safer process settings before productivity optimization.",
                    ],
                    "table": _single_condition_table(best.condition_values),
                },
                {
                    "mode": "measurement_review_before_redesign",
                    "title": "Measurement review before redesign",
                    "priority": priority + 1,
                    "rationale": (
                        "Before widening the DOE, confirm whether the rejection is caused by process behavior, "
                        "sampling bias, or measurement error."
                    ),
                    "decision_basis": [
                        "Rejected conditions may reflect process behavior or weak measurement confidence.",
                        "Measurement review prevents redesigning around a false signal.",
                    ],
                    "table": _single_condition_table(best.condition_values),
                },
            ]
        )
        return options

    options: list[dict[str, Any]] = []
    priority = 1

    if best.state == "borderline":
        bottleneck_option = _bottleneck_followup_option(request, criteria_result, best, response_analysis, priority)
        if bottleneck_option is not None:
            options.append(bottleneck_option)
            priority += 1

    productivity_option = _productivity_refinement_option(request, best, priority)
    if productivity_option is not None:
        options.append(productivity_option)
        priority += 1

    options.append(_confirmation_option(best, priority))
    priority += 1

    confidence_option = _measurement_confidence_option(response_analysis, best, priority)
    if confidence_option is not None:
        options.append(confidence_option)
        priority += 1

    if best.state != "borderline":
        bottleneck_option = _bottleneck_followup_option(request, criteria_result, best, response_analysis, priority)
        if bottleneck_option is not None:
            options.append(bottleneck_option)
            priority += 1

    quality_option = _quality_margin_option(criteria_result, best, priority)
    if quality_option is not None:
        options.append(quality_option)
        priority += 1

    contrast_option = _candidate_contrast_option(criteria_result, priority)
    if contrast_option is not None:
        options.append(contrast_option)

    return options


def recommend_next_doe(request: DoeRequest, criteria_result: dict[str, Any]) -> dict[str, Any]:
    return recommend_next_doe_options(request, criteria_result)[0]
