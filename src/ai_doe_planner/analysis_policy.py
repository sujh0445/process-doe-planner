from __future__ import annotations

from typing import Any

from .schemas import DoeRequest, Response


_STAGE_ALIASES = {
    "screen": "screening",
    "screening_doe": "screening",
    "full": "full_factorial",
    "factorial": "full_factorial",
    "full-factorial": "full_factorial",
    "trend": "trend_refinement",
    "refinement": "trend_refinement",
    "boundary": "trend_refinement",
    "optimization": "trend_refinement",
    "confirm": "confirmation",
    "confirmation_doe": "confirmation",
    "capability_confirmation": "capability",
}


def _normalized(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _design_type(request: DoeRequest) -> str:
    explicit = _normalized(request.constraints.get("design_type"))
    aliases = {
        "full": "full_factorial",
        "factorial": "full_factorial",
        "fractional": "fractional_factorial",
        "half_fraction": "fractional_factorial",
        "fractional_factorial_half_fraction": "fractional_factorial",
    }
    if explicit and explicit != "auto":
        return aliases.get(explicit, explicit)

    factor_count = len(request.factors)
    full_runs = 2**factor_count
    max_runs = request.constraints.get("max_runs")
    try:
        if max_runs is not None and int(max_runs) < full_runs:
            return "fractional_factorial"
    except (TypeError, ValueError):
        pass
    def has_two_levels(factor: Any) -> bool:
        return len(factor.levels) == 2 or (
            factor.low is not None and factor.high is not None and factor.low != factor.high
        )

    if factor_count <= 3 and all(has_two_levels(factor) for factor in request.factors):
        return "full_factorial"
    return "custom_or_multilevel"


def _analysis_stage(request: DoeRequest, design_type: str) -> str:
    candidates = (
        request.constraints.get("analysis_stage"),
        request.constraints.get("doe_stage"),
        request.constraints.get("doe_purpose"),
        request.objective.get("analysis_stage"),
        request.objective.get("doe_stage"),
    )
    for candidate in candidates:
        normalized = _normalized(candidate)
        if normalized:
            return _STAGE_ALIASES.get(normalized, normalized)

    decision_mode = _normalized(request.objective.get("decision_mode"))
    primary_goal = _normalized(request.objective.get("primary_goal"))
    combined = f"{decision_mode}_{primary_goal}"
    if "confirm" in combined or "release" in combined:
        return "confirmation"
    if "capability" in combined or "process_capability" in combined:
        return "capability"
    if any(token in combined for token in ("refine", "trend", "boundary", "optimi")):
        return "trend_refinement"
    if design_type == "fractional_factorial":
        return "screening"
    if design_type == "full_factorial":
        return "full_factorial"
    return "exploratory"


def _spec_profile(response: Response) -> str:
    if response.spec.lower is not None and response.spec.upper is not None:
        return "two_sided"
    if response.spec.upper is not None:
        return "upper_only"
    if response.spec.lower is not None:
        return "lower_only"
    return "no_hard_spec"


def _decision_metrics(response: Response, spec_profile: str) -> list[str]:
    if response.y_type in {"binary", "categorical", "category", "class"}:
        return ["pass_fail_rate", "risk_code_count", "category_distribution"]
    if response.y_type == "count":
        metrics = ["defect_count", "mean_count", "max_count", "p95_count"]
    else:
        metrics = ["condition_mean", "repeatability", "confidence_interval"]

    if spec_profile == "upper_only":
        return [*metrics, "spec_pass_fail", "over_spec_count_rate", "max", "p95", "upper_margin", "Cpu_if_eligible"]
    if spec_profile == "lower_only":
        return [*metrics, "spec_pass_fail", "under_spec_count_rate", "min", "p05", "lower_margin", "Cpl_if_eligible"]
    if spec_profile == "two_sided":
        return [*metrics, "spec_pass_fail", "out_of_spec_count_rate", "min", "max", "p05", "p95", "Cpk_if_eligible"]
    return [*metrics, "baseline_delta", "distribution_shape"]


def build_analysis_policy(request: DoeRequest, response: Response) -> dict[str, Any]:
    design_type = _design_type(request)
    stage = _analysis_stage(request, design_type)
    spec_profile = _spec_profile(response)
    numeric = response.y_type in {"continuous", "image-derived", "count"}
    effect_capable = numeric or response.y_type == "binary"
    fractional = design_type == "fractional_factorial"

    run_effects = effect_capable and stage in {"screening", "full_factorial", "exploratory"}
    run_anova = numeric and stage in {"screening", "full_factorial", "exploratory"}
    run_trend = numeric and stage == "trend_refinement"
    run_confirmation = stage in {"confirmation", "capability"}
    include_interactions = run_effects and not fractional and stage in {"full_factorial", "exploratory", "screening"}

    selected: list[dict[str, str]] = [
        {"method": "condition_level_summary", "reason": "All decisions compare actual process conditions."},
    ]
    if spec_profile == "no_hard_spec":
        selected.append(
            {
                "method": "baseline_and_distribution_evidence",
                "reason": "No hard spec is defined, so evidence is relative to the baseline and observed distribution.",
            }
        )
    else:
        selected.append(
            {"method": "spec_and_tail_evidence", "reason": f"Y uses a {spec_profile} decision boundary."}
        )
    skipped: list[dict[str, str]] = []

    if run_effects:
        selected.append(
            {
                "method": "factor_effect_analysis",
                "reason": "The current DOE stage is intended to compare factor directions and relative influence.",
            }
        )
    else:
        skipped.append(
            {
                "method": "broad_factor_effect_ranking",
                "reason": f"The {stage} stage prioritizes local trend or candidate confirmation over global screening.",
            }
        )

    if run_anova:
        selected.append(
            {
                "method": "residual_inclusive_anova",
                "reason": "Replicated condition data can separate modeled terms from residual/error variation.",
            }
        )
    elif numeric:
        skipped.append(
            {
                "method": "factorial_anova",
                "reason": f"Factorial ANOVA is not the primary evidence for a {stage} round.",
            }
        )

    if run_trend:
        selected.extend(
            [
                {"method": "pearson_and_spearman", "reason": "Check linear and monotonic factor-Y trends."},
                {"method": "linear_regression", "reason": "Estimate local slope for the next search range."},
                {"method": "one_way_anova_and_kruskal", "reason": "Cross-check level differences parametrically and nonparametrically."},
                {"method": "boundary_welch_test", "reason": "Compare the two highest tested levels without assuming equal variance."},
            ]
        )

    if run_confirmation:
        selected.extend(
            [
                {"method": "candidate_repeatability", "reason": "Confirmation requires repeat-level min/max, spread, and confidence interval."},
                {"method": "capability_eligibility_check", "reason": "Capability is reported only when sample size and stability conditions are met."},
            ]
        )

    if fractional:
        skipped.append(
            {
                "method": "separate_pairwise_interaction_claims",
                "reason": "Pairwise interactions are aliased in the fractional design and cannot be identified independently.",
            }
        )

    interaction_policy = (
        "main_effects_only_alias_aware"
        if fractional
        else "main_and_pairwise_interactions_when_estimable"
        if include_interactions
        else "not_primary_for_this_stage"
    )
    return {
        "analysis_stage": stage,
        "design_type": design_type,
        "spec_profile": spec_profile,
        "decision_metrics": _decision_metrics(response, spec_profile),
        "selected_methods": selected,
        "skipped_methods": skipped,
        "interaction_policy": interaction_policy,
        "capability_policy": "formal_only_when_n_ge_33_and_process_is_stable",
        "run_effects": run_effects,
        "run_anova": run_anova,
        "include_interactions": include_interactions,
        "run_trend_tests": run_trend,
        "run_confirmation_checks": run_confirmation,
        "rationale": (
            f"Selected from project objective, Y type={response.y_type}, spec={spec_profile}, "
            f"DOE stage={stage}, and design={design_type}."
        ),
    }
