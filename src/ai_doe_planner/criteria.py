from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .schemas import DoeRequest, Factor, Response


@dataclass(frozen=True)
class ConditionDecision:
    condition: str
    condition_values: dict[str, Any]
    state: str
    quality_score: float
    production_score: float
    total_score: float
    reasons: tuple[str, ...]
    tail_risk_score: float = 100.0
    measurement_score: float = 100.0
    mechanism_score: float = 100.0
    criteria_evidence: tuple[dict[str, Any], ...] = ()


_STATE_RANK = {"candidate": 0, "borderline": 1, "rejected": 2}


def _condition_sort_key(item: ConditionDecision) -> tuple[int, float, float]:
    return (_STATE_RANK.get(item.state, 9), -item.total_score, -item.quality_score)


_CRITERION_ROLE_ALIASES = {
    "spec_gate": "quality_gate",
    "spec_pass_fail": "quality_gate",
    "hard_gate": "quality_gate",
    "over_spec_count": "quality_gate",
    "tail_risk": "risk_guardrail",
    "worst_case_tail_risk": "risk_guardrail",
    "worst_case": "risk_guardrail",
    "guardrail": "risk_guardrail",
    "productivity_tradeoff": "production_objective",
    "production_tradeoff": "production_objective",
    "productivity_objective": "production_objective",
    "production_factor": "production_objective",
    "process_mechanism": "mechanism_consistency",
    "mechanism": "mechanism_consistency",
    "measurement_reliability": "measurement_confidence",
    "sampling_confidence": "measurement_confidence",
}


def canonical_criterion_role(role: str) -> str:
    normalized = str(role).strip().lower()
    return _CRITERION_ROLE_ALIASES.get(normalized, normalized)


def _criterion_roles(request: DoeRequest) -> set[str]:
    return {canonical_criterion_role(criterion.decision_role) for criterion in request.criteria}


def _criterion_enabled(request: DoeRequest, role: str) -> bool:
    return canonical_criterion_role(role) in _criterion_roles(request)


def _worst_margin(summary: dict[str, Any], response: Response) -> float | None:
    if response.spec.upper is not None:
        return response.spec.upper - float(summary.get("max", summary.get("mean", 0.0)))
    if response.spec.lower is not None:
        return float(summary.get("min", summary.get("mean", 0.0))) - response.spec.lower
    return None


def _tail_margin(summary: dict[str, Any], response: Response) -> float | None:
    if response.spec.upper is not None:
        return response.spec.upper - float(summary.get("p95", summary.get("max", summary.get("mean", 0.0))))
    if response.spec.lower is not None:
        return float(summary.get("p05", summary.get("min", summary.get("mean", 0.0)))) - response.spec.lower
    return None


def _quality_score(summary: dict[str, Any], response: Response) -> tuple[float, list[str]]:
    reasons: list[str] = []
    fail_count = int(summary.get("fail_count", 0))
    warning_count = int(summary.get("warning_count", 0))
    if fail_count > 0:
        if response.y_type in {"binary", "categorical", "category", "class"} and response.fail_values:
            reasons.append(f"{response.name}: {fail_count} risk-coded failure measurement(s)")
        else:
            reasons.append(f"{response.name}: {fail_count} over-spec measurement(s)")
        return 0.0, reasons

    margin = _worst_margin(summary, response)
    score = 75.0
    if margin is not None:
        if margin < 0:
            reasons.append(f"{response.name}: negative spec margin")
            return 0.0, reasons
        score = min(100.0, 60.0 + margin * 5.0)
        reasons.append(f"{response.name}: worst-case margin {margin:.3g} {response.unit}".strip())
    else:
        reasons.append(f"{response.name}: no hard spec, compared by trend")

    if warning_count > 0:
        score = min(score, 65.0)
        reasons.append(f"{response.name}: {warning_count} warning-zone measurement(s)")
    return score, reasons


def _tail_risk_score(entry: dict[str, Any], request: DoeRequest) -> tuple[float, list[str], list[dict[str, Any]], bool]:
    if not _criterion_enabled(request, "risk_guardrail"):
        return 100.0, [], [], False

    scores: list[float] = []
    reasons: list[str] = []
    evidence: list[dict[str, Any]] = []
    borderline = False
    for response in request.responses:
        if response.role in {"production_y", "monitor"}:
            continue
        summary = entry["response_summaries"].get(response.name, {})
        fail_count = int(summary.get("fail_count", 0))
        warning_count = int(summary.get("warning_count", 0))
        worst_margin = _worst_margin(summary, response)
        tail_margin = _tail_margin(summary, response)

        if fail_count > 0:
            score = 0.0
            borderline = True
            reason = f"{response.name}: tail rejected by {fail_count} over-spec point(s)"
        elif warning_count > 0:
            score = 55.0
            borderline = True
            reason = f"{response.name}: tail warning by {warning_count} warning-zone point(s)"
        elif tail_margin is not None:
            score = min(100.0, max(60.0, 70.0 + tail_margin * 4.0))
            reason = f"{response.name}: p95/tail margin {tail_margin:.3g} {response.unit}".strip()
        elif worst_margin is not None:
            score = min(100.0, max(60.0, 70.0 + worst_margin * 4.0))
            reason = f"{response.name}: worst-case margin {worst_margin:.3g} {response.unit}".strip()
        else:
            score = 80.0
            reason = f"{response.name}: no numeric tail spec, reviewed by fail/warning evidence"

        scores.append(score)
        reasons.append(reason)
        evidence.append(
            {
                "criterion": "Tail risk",
                "role": "risk_guardrail",
                "score": round(score, 3),
                "state": _evidence_state(score, hard_failed=fail_count > 0),
                "evidence": reason,
            }
        )

    score = sum(scores) / len(scores) if scores else 100.0
    return round(score, 3), reasons, evidence, borderline or score < 70


def _measurement_confidence_score(entry: dict[str, Any], request: DoeRequest) -> tuple[float, list[str], list[dict[str, Any]], bool]:
    if not _criterion_enabled(request, "measurement_confidence"):
        return 100.0, [], [], False

    target_n = request.constraints.get("samples_per_condition")
    try:
        target = float(target_n) if target_n is not None else None
    except (TypeError, ValueError):
        target = None

    reasons: list[str] = []
    evidence: list[dict[str, Any]] = []
    response_scores: list[float] = []
    for response in request.responses:
        if response.role in {"production_y", "monitor"}:
            continue
        summary = entry["response_summaries"].get(response.name, {})
        n = float(summary.get("n", 0) or 0)
        fail_count = int(summary.get("fail_count", 0))
        warning_count = int(summary.get("warning_count", 0))
        if target and target > 0:
            sample_score = min(100.0, (n / target) * 100.0)
            reason = f"{response.name}: n={int(n)}/{int(target)} versus planned samples"
        else:
            sample_score = 80.0 if n > 0 else 0.0
            reason = f"{response.name}: n={int(n)}, no planned sample target supplied"

        if fail_count > 0:
            sample_score = min(sample_score, 60.0)
            reason += f", {fail_count} over-spec point(s) require confirmation"
        elif warning_count > 0:
            sample_score = min(sample_score, 75.0)
            reason += f", {warning_count} warning-zone point(s) reduce confidence"

        response_scores.append(sample_score)
        reasons.append(reason)
        evidence.append(
            {
                "criterion": "Measurement confidence",
                "role": "measurement_confidence",
                "score": round(sample_score, 3),
                "state": "borderline" if sample_score < 80 else "pass",
                "evidence": reason,
            }
        )

    score = sum(response_scores) / len(response_scores) if response_scores else 100.0
    return round(score, 3), reasons, evidence, score < 80


def _production_score(condition_values: dict[str, Any], request: DoeRequest, all_values: pd.Series | None) -> float:
    factor = request.production_factor
    if factor is None or all_values is None or factor.column not in condition_values:
        return 0.0
    try:
        value = float(condition_values[factor.column])
        low = float(all_values.min())
        high = float(all_values.max())
    except Exception:
        return 0.0
    if high == low:
        return 50.0
    normalized = (value - low) / (high - low)
    if factor.production_direction == "lower_is_better":
        normalized = 1.0 - normalized
    return round(normalized * 100.0, 3)


def _expected_quality_direction(factor: Factor) -> str | None:
    note = factor.mechanism_note.lower()
    risk_tokens = ("risk", "increase chipping", "increase defect", "worse", "악화", "증가", "커질", "커짐", "위험")
    improve_tokens = ("reduce", "decrease", "lower", "less", "improve", "줄", "감소", "낮", "완화", "개선")
    if any(token in note for token in risk_tokens):
        return "risk"
    if any(token in note for token in improve_tokens):
        return "improve"
    return None


def _observed_quality_direction(effect: float, response: Response) -> str | None:
    if effect == 0:
        return None
    if response.direction == "lower_is_better":
        return "improve" if effect < 0 else "risk"
    if response.direction == "higher_is_better":
        return "improve" if effect > 0 else "risk"
    return None


def _mechanism_consistency_score(request: DoeRequest, response_analysis: dict[str, Any]) -> tuple[float, list[str], list[dict[str, Any]], bool]:
    if not _criterion_enabled(request, "mechanism_consistency"):
        return 100.0, [], [], False

    factors = {factor.column: factor for factor in request.factors}
    supported: list[str] = []
    conflicts: list[str] = []
    unknown: list[str] = []

    for response in request.responses:
        if response.role in {"production_y", "monitor"}:
            continue
        analysis = response_analysis.get(response.name, {})
        for effect in analysis.get("effects", []):
            if effect.get("kind") != "main":
                continue
            factor = factors.get(effect["term"])
            if factor is None:
                continue
            try:
                weight = float(effect.get("relative_effect_weight", 0.0))
                effect_value = float(effect.get("effect", 0.0))
            except (TypeError, ValueError):
                continue
            if weight < 0.05:
                continue

            expected = _expected_quality_direction(factor)
            observed = _observed_quality_direction(effect_value, response)
            if expected is None or observed is None:
                unknown.append(f"{factor.column}->{response.name}: mechanism direction not explicit")
            elif expected == observed:
                supported.append(f"{factor.column}->{response.name}: expected {expected}, observed {observed}")
            else:
                conflicts.append(f"{factor.column}->{response.name}: expected {expected}, observed {observed}")

    if conflicts:
        score = 50.0
        state = "borderline"
        reason = "; ".join(conflicts[:2])
        borderline = True
    elif supported:
        score = 100.0
        state = "pass"
        reason = "; ".join(supported[:2])
        borderline = False
    else:
        score = 80.0
        state = "borderline"
        reason = "; ".join(unknown[:2]) if unknown else "No strong main-effect mechanism check was available"
        borderline = True

    evidence = [
        {
            "criterion": "Mechanism consistency",
            "role": "mechanism_consistency",
            "score": score,
            "state": state,
            "evidence": reason,
        }
    ]
    return score, [reason], evidence, borderline


def _evidence_state(score: float, hard_failed: bool = False) -> str:
    if hard_failed or score <= 0:
        return "rejected"
    if score < 80:
        return "borderline"
    return "pass"


def _total_score(
    quality_score: float,
    tail_risk_score: float,
    measurement_score: float,
    mechanism_score: float,
    production_score: float,
    request: DoeRequest,
) -> float:
    roles = _criterion_roles(request)
    if not roles:
        return round(quality_score * 0.75 + production_score * 0.25, 3)
    weights = {
        "quality": 0.55,
        "tail": 0.15 if "risk_guardrail" in roles else 0.0,
        "measurement": 0.10 if "measurement_confidence" in roles else 0.0,
        "mechanism": 0.10 if "mechanism_consistency" in roles else 0.0,
        "production": 0.10 if "production_objective" in roles else 0.0,
    }
    active_weight = sum(weights.values())
    if active_weight <= 0:
        return round(quality_score * 0.75 + production_score * 0.25, 3)
    total = (
        quality_score * weights["quality"]
        + tail_risk_score * weights["tail"]
        + measurement_score * weights["measurement"]
        + mechanism_score * weights["mechanism"]
        + production_score * weights["production"]
    )
    return round(total / active_weight, 3)


def evaluate_conditions(df: pd.DataFrame, request: DoeRequest, response_analysis: dict[str, Any]) -> dict[str, Any]:
    condition_map: dict[str, dict[str, Any]] = {}
    for response in request.responses:
        analysis = response_analysis[response.name]
        for row in analysis["by_condition"]:
            entry = condition_map.setdefault(
                row["condition"],
                {
                    "condition": row["condition"],
                    "condition_values": row["condition_values"],
                    "response_summaries": {},
                },
            )
            entry["response_summaries"][response.name] = row

    production_series = None
    if request.production_factor is not None:
        production_series = pd.to_numeric(df[request.production_factor.column], errors="coerce")

    mechanism_score, mechanism_reasons, mechanism_evidence, mechanism_borderline = _mechanism_consistency_score(
        request, response_analysis
    )

    decisions: list[ConditionDecision] = []
    for condition, entry in condition_map.items():
        quality_scores: list[float] = []
        reasons: list[str] = []
        criteria_evidence: list[dict[str, Any]] = []
        hard_failed = False
        borderline = False
        for response in request.responses:
            if response.role in {"production_y", "monitor"}:
                continue
            summary = entry["response_summaries"].get(response.name, {})
            score, response_reasons = _quality_score(summary, response)
            quality_scores.append(score)
            reasons.extend(response_reasons)
            if score <= 0:
                hard_failed = True
            if int(summary.get("warning_count", 0)) > 0:
                borderline = True
            criteria_evidence.append(
                {
                    "criterion": "Spec pass/fail",
                    "role": "quality_gate",
                    "score": round(score, 3),
                    "state": _evidence_state(score, hard_failed=score <= 0),
                    "evidence": "; ".join(response_reasons),
                }
            )

        quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        if 0.0 < quality_score < 80.0:
            borderline = True
            reasons.append(f"quality score {quality_score:.3g} is below the strong-candidate margin threshold")
        tail_risk_score, tail_reasons, tail_evidence, tail_borderline = _tail_risk_score(entry, request)
        measurement_score, measurement_reasons, measurement_evidence, measurement_borderline = _measurement_confidence_score(
            entry, request
        )
        production_score = _production_score(entry["condition_values"], request, production_series)
        total_score = _total_score(
            quality_score,
            tail_risk_score,
            measurement_score,
            mechanism_score,
            production_score,
            request,
        )
        criteria_evidence.extend(tail_evidence)
        criteria_evidence.extend(measurement_evidence)
        criteria_evidence.extend(mechanism_evidence)
        if _criterion_enabled(request, "production_objective"):
            criteria_evidence.append(
                {
                    "criterion": "Production trade-off",
                    "role": "production_objective",
                    "score": production_score,
                    "state": "secondary",
                    "evidence": f"Production score from {request.production_factor.column if request.production_factor else 'no production factor'}",
                }
            )
        reasons.extend(tail_reasons[:1])
        reasons.extend(measurement_reasons[:1])
        if mechanism_reasons:
            reasons.extend(mechanism_reasons[:1])
        if hard_failed:
            state = "rejected"
        elif borderline or tail_borderline or measurement_borderline or mechanism_borderline:
            state = "borderline"
        else:
            state = "candidate"
        decisions.append(
            ConditionDecision(
                condition=condition,
                condition_values=entry["condition_values"],
                state=state,
                quality_score=round(quality_score, 3),
                production_score=production_score,
                total_score=total_score,
                reasons=tuple(reasons),
                tail_risk_score=tail_risk_score,
                measurement_score=measurement_score,
                mechanism_score=mechanism_score,
                criteria_evidence=tuple(criteria_evidence),
            )
        )

    decisions.sort(key=_condition_sort_key)
    bottleneck = identify_bottleneck_y(response_analysis, request)
    return {
        "condition_decisions": decisions,
        "best_condition": decisions[0] if decisions else None,
        "bottleneck_y": bottleneck,
    }


def identify_bottleneck_y(response_analysis: dict[str, Any], request: DoeRequest) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for response in request.responses:
        if response.role in {"production_y", "monitor"}:
            continue
        total_fail = 0
        weakest_margin = None
        for row in response_analysis[response.name]["by_condition"]:
            total_fail += int(row.get("fail_count", 0))
            margin = _worst_margin(row, response)
            if margin is not None:
                weakest_margin = margin if weakest_margin is None else min(weakest_margin, margin)
        candidates.append(
            {
                "response": response.name,
                "fail_count": total_fail,
                "weakest_margin": weakest_margin,
            }
        )
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item["fail_count"], item["weakest_margin"] if item["weakest_margin"] is not None else 999999))
    return candidates[0]
