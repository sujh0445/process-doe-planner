from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

import yaml


class RequestValidationError(ValueError):
    """Raised when a DOE request is missing required planning fields."""


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(value)
    return (value,)


@dataclass(frozen=True)
class Spec:
    lower: float | None = None
    upper: float | None = None
    warning_lower: float | None = None
    warning_upper: float | None = None
    baseline_compare: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> "Spec":
        raw = raw or {}
        return cls(
            lower=_as_float(raw.get("lower_spec", raw.get("lower"))),
            upper=_as_float(raw.get("upper_spec", raw.get("upper"))),
            warning_lower=_as_float(raw.get("warning_lower")),
            warning_upper=_as_float(raw.get("warning_upper")),
            baseline_compare=bool(raw.get("baseline_compare", False)),
        )


@dataclass(frozen=True)
class Response:
    name: str
    column: str
    y_type: str
    unit: str = ""
    direction: str = "lower_is_better"
    role: str = "primary_quality_y"
    spec: Spec = field(default_factory=Spec)
    measurement_method: str = ""
    pass_values: tuple[Any, ...] = ()
    fail_values: tuple[Any, ...] = ()
    warning_values: tuple[Any, ...] = ()
    positive_values: tuple[Any, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Response":
        name = str(raw["name"])
        return cls(
            name=name,
            column=str(raw.get("column", name)),
            y_type=str(raw.get("type", raw.get("y_type", "continuous"))).strip().lower().replace("_", "-"),
            unit=str(raw.get("unit", "")),
            direction=str(raw.get("direction", "lower_is_better")).strip().lower().replace("-", "_"),
            role=str(raw.get("role", "primary_quality_y")),
            spec=Spec.from_dict(raw.get("spec")),
            measurement_method=str(raw.get("measurement_method", "")),
            pass_values=_as_tuple(raw.get("pass_values")),
            fail_values=_as_tuple(raw.get("fail_values")),
            warning_values=_as_tuple(raw.get("warning_values")),
            positive_values=_as_tuple(raw.get("positive_values")),
        )


@dataclass(frozen=True)
class Factor:
    name: str
    column: str
    unit: str = ""
    low: float | str | None = None
    high: float | str | None = None
    current: float | str | None = None
    practical_range: tuple[float, float] | None = None
    levels: tuple[Any, ...] = ()
    controllable: bool = True
    role: str = "process_factor"
    production_direction: str = "higher_is_better"
    mechanism_note: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Factor":
        name = str(raw["name"])
        practical = raw.get("practical_doe_range") or raw.get("practical_range")
        practical_range = None
        if practical:
            practical_range = (float(practical[0]), float(practical[1]))
        levels = tuple(raw.get("levels", ()))
        return cls(
            name=name,
            column=str(raw.get("column", name)),
            unit=str(raw.get("unit", "")),
            low=raw.get("low"),
            high=raw.get("high"),
            current=raw.get("current"),
            practical_range=practical_range,
            levels=levels,
            controllable=bool(raw.get("controllable", True)),
            role=str(raw.get("role", "process_factor")),
            production_direction=str(raw.get("production_direction", "higher_is_better")),
            mechanism_note=str(raw.get("mechanism_note", "")),
        )


@dataclass(frozen=True)
class Criterion:
    criterion_id: str
    name: str
    applies_to_y: str | None = None
    decision_role: str = "quality_gate"
    metric: str = ""
    pass_rule: str = ""
    next_doe_impact: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Criterion":
        return cls(
            criterion_id=str(raw.get("criterion_id", raw.get("id", raw["name"]))),
            name=str(raw["name"]),
            applies_to_y=raw.get("applies_to_y"),
            decision_role=str(raw.get("decision_role", "quality_gate")),
            metric=str(raw.get("metric", "")),
            pass_rule=str(raw.get("pass_rule", "")),
            next_doe_impact=str(raw.get("next_doe_impact", "")),
        )


@dataclass(frozen=True)
class DoeRequest:
    project: dict[str, Any]
    objective: dict[str, Any]
    responses: tuple[Response, ...]
    factors: tuple[Factor, ...]
    criteria: tuple[Criterion, ...] = ()
    constraints: dict[str, Any] = field(default_factory=dict)
    baseline_condition: dict[str, Any] = field(default_factory=dict)
    mechanism_hypotheses: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "DoeRequest":
        required_top = ["project", "objective", "responses", "factors"]
        missing = [key for key in required_top if key not in raw]
        if missing:
            raise RequestValidationError(f"Missing required request sections: {', '.join(missing)}")
        responses = tuple(Response.from_dict(item) for item in raw["responses"])
        factors = tuple(Factor.from_dict(item) for item in raw["factors"])
        if not responses:
            raise RequestValidationError("At least one response variable is required.")
        if not factors:
            raise RequestValidationError("At least one candidate factor is required.")
        criteria = tuple(Criterion.from_dict(item) for item in raw.get("criteria", ()))
        return cls(
            project=dict(raw["project"]),
            objective=dict(raw["objective"]),
            responses=responses,
            factors=factors,
            criteria=criteria,
            constraints=dict(raw.get("constraints", {})),
            baseline_condition=dict(raw.get("baseline_condition", {})),
            mechanism_hypotheses=tuple(str(item) for item in raw.get("mechanism_hypotheses", ())),
        )

    @property
    def factor_columns(self) -> list[str]:
        return [factor.column for factor in self.factors]

    @property
    def response_columns(self) -> list[str]:
        return [response.column for response in self.responses]

    @property
    def production_factor(self) -> Factor | None:
        for factor in self.factors:
            if "product" in factor.role or "throughput" in factor.role:
                return factor
        return None


def load_request(path: str | Path) -> DoeRequest:
    request_path = Path(path)
    text = request_path.read_text(encoding="utf-8")
    if request_path.suffix.lower() == ".json":
        raw = json.loads(text)
    else:
        raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise RequestValidationError("Request file must contain a mapping/object.")
    return DoeRequest.from_dict(raw)
