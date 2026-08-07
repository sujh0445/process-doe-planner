from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from .analysis_policy import build_analysis_policy
from .schemas import DoeRequest, Response


NUMERIC_Y_TYPES = {"continuous", "image-derived", "count"}
EFFECT_Y_TYPES = {"continuous", "image-derived", "count", "binary"}
CAPABILITY_MIN_N = 33


def _std(series: pd.Series) -> float:
    value = series.astype(float).std(ddof=1)
    if pd.isna(value):
        return 0.0
    return float(value)


def _capability(n: int, mean: float, std: float, response: Response) -> dict[str, Any]:
    base: dict[str, Any] = {
        "cpu": None,
        "cpl": None,
        "cpk": None,
        "capability_n": n,
        "capability_min_n": CAPABILITY_MIN_N,
        "capability_status": "not_available",
        "capability_note": "Capability requires a spec limit and non-zero within-condition variation.",
    }
    if response.spec.upper is None and response.spec.lower is None:
        base["capability_note"] = "Capability is not available because no spec limit is defined."
        return base
    if std <= 0:
        base["capability_note"] = "Capability is not available because the sample standard deviation is zero."
        return base

    cpu = None
    cpl = None
    if response.spec.upper is not None:
        cpu = (response.spec.upper - mean) / (3 * std)
    if response.spec.lower is not None:
        cpl = (mean - response.spec.lower) / (3 * std)
    cpk_values = [item for item in [cpu, cpl] if item is not None]
    base.update({"cpu": cpu, "cpl": cpl, "cpk": min(cpk_values) if cpk_values else None})
    if n < CAPABILITY_MIN_N:
        base["capability_status"] = f"exploratory_n_lt_{CAPABILITY_MIN_N}"
        base["capability_note"] = (
            f"n={n} is below the {CAPABILITY_MIN_N}-repeat threshold; treat capability as a "
            "screening reference, not a formal process-capability claim."
        )
    else:
        base["capability_status"] = f"eligible_n_ge_{CAPABILITY_MIN_N}"
        base["capability_note"] = (
            f"n={n} meets the repeat-count threshold; capability is still conditional on stable, "
            "representative sampling and a valid measurement method."
        )
    return base


def _matches_values(series: pd.Series, values: tuple[Any, ...]) -> pd.Series:
    if not values:
        return pd.Series(False, index=series.index)
    direct = series.isin(values)
    string_values = {str(value) for value in values}
    string_match = series.astype(str).isin(string_values)
    return direct | string_match


def _spec_counts(series: pd.Series, response: Response) -> dict[str, int]:
    numeric = series.astype(float)
    fail = pd.Series(False, index=numeric.index)
    warning = pd.Series(False, index=numeric.index)
    if response.spec.upper is not None:
        fail = fail | (numeric > response.spec.upper)
    if response.spec.lower is not None:
        fail = fail | (numeric < response.spec.lower)
    if response.spec.warning_upper is not None:
        warning = warning | (numeric > response.spec.warning_upper)
    if response.spec.warning_lower is not None:
        warning = warning | (numeric < response.spec.warning_lower)
    return {
        "n": int(numeric.count()),
        "fail_count": int(fail.sum()),
        "warning_count": int((warning & ~fail).sum()),
        "pass_count": int((~fail).sum()),
    }


def _rate(count: int, n: int) -> float | None:
    if n <= 0:
        return None
    return float(count / n)


def _finite_or_none(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(numeric):
        return None
    return numeric


def summarize_continuous(series: pd.Series, response: Response) -> dict[str, Any]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return {"n": 0}
    mean = float(numeric.mean())
    std = _std(numeric)
    n = int(numeric.count())
    sem = std / np.sqrt(n) if n > 1 else 0.0
    ci_half_width = float(stats.t.ppf(0.975, n - 1) * sem) if n > 1 else 0.0
    summary = {
        "n": n,
        "mean": mean,
        "std": std,
        "min": float(numeric.min()),
        "max": float(numeric.max()),
        "p05": float(numeric.quantile(0.05)),
        "p50": float(numeric.quantile(0.50)),
        "p95": float(numeric.quantile(0.95)),
        "mean_ci95_lower": mean - ci_half_width,
        "mean_ci95_upper": mean + ci_half_width,
    }
    summary.update(_spec_counts(numeric, response))
    summary.update(_capability(int(summary["n"]), mean, std, response))
    summary["fail_rate"] = _rate(int(summary["fail_count"]), int(summary["n"]))
    summary["warning_rate"] = _rate(int(summary["warning_count"]), int(summary["n"]))
    return summary


def summarize_count(series: pd.Series, response: Response) -> dict[str, Any]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return {"n": 0}
    summary = {
        "n": int(numeric.count()),
        "sum": float(numeric.sum()),
        "mean": float(numeric.mean()),
        "min": float(numeric.min()),
        "max": float(numeric.max()),
        "p05": float(numeric.quantile(0.05)),
        "p95": float(numeric.quantile(0.95)),
    }
    summary.update(_spec_counts(numeric, response))
    summary["fail_rate"] = _rate(int(summary["fail_count"]), int(summary["n"]))
    summary["warning_rate"] = _rate(int(summary["warning_count"]), int(summary["n"]))
    return summary


def summarize_binary(series: pd.Series, response: Response) -> dict[str, Any]:
    values = series.dropna()
    if values.empty:
        return {"n": 0}

    n = int(values.count())
    fail = _matches_values(values, response.fail_values)
    warning = _matches_values(values, response.warning_values)
    positive = _matches_values(values, response.positive_values)

    numeric = pd.to_numeric(values, errors="coerce")
    if response.fail_values:
        fail_mask = fail
    elif numeric.notna().all() and (response.spec.upper is not None or response.spec.lower is not None):
        fail_mask = pd.Series(False, index=values.index)
        if response.spec.upper is not None:
            fail_mask = fail_mask | (numeric > response.spec.upper)
        if response.spec.lower is not None:
            fail_mask = fail_mask | (numeric < response.spec.lower)
    elif numeric.notna().all() and response.direction == "lower_is_better":
        fail_mask = numeric > 0
    else:
        fail_mask = fail

    if response.positive_values:
        positive_mask = positive
    elif numeric.notna().all():
        positive_mask = numeric > 0
    else:
        positive_mask = fail_mask

    if response.warning_values:
        warning_mask = warning & ~fail_mask
    else:
        warning_mask = pd.Series(False, index=values.index)

    fail_count = int(fail_mask.sum())
    warning_count = int(warning_mask.sum())
    positive_count = int(positive_mask.sum())
    summary = {
        "n": n,
        "positive_count": positive_count,
        "positive_rate": _rate(positive_count, n),
        "fail_count": fail_count,
        "fail_rate": _rate(fail_count, n),
        "warning_count": warning_count,
        "warning_rate": _rate(warning_count, n),
        "pass_count": n - fail_count,
    }
    if numeric.notna().any():
        valid_numeric = numeric.dropna()
        summary.update(
            {
                "mean": float(valid_numeric.mean()),
                "min": float(valid_numeric.min()),
                "max": float(valid_numeric.max()),
            }
        )
    return summary


def summarize_categorical(series: pd.Series, response: Response) -> dict[str, Any]:
    values = series.dropna()
    if values.empty:
        return {"n": 0}
    n = int(values.count())
    fail_mask = _matches_values(values, response.fail_values)
    warning_mask = _matches_values(values, response.warning_values) & ~fail_mask
    counts = values.astype(str).value_counts()
    top_value = str(counts.index[0]) if not counts.empty else None
    top_count = int(counts.iloc[0]) if not counts.empty else 0
    compact_counts = ", ".join(f"{idx}:{int(count)}" for idx, count in counts.head(5).items())
    fail_count = int(fail_mask.sum())
    warning_count = int(warning_mask.sum())
    return {
        "n": n,
        "distinct_count": int(counts.count()),
        "top_value": top_value,
        "top_count": top_count,
        "value_counts": compact_counts,
        "fail_count": fail_count,
        "fail_rate": _rate(fail_count, n),
        "warning_count": warning_count,
        "warning_rate": _rate(warning_count, n),
        "pass_count": n - fail_count,
    }


def summarize_response(series: pd.Series, response: Response) -> dict[str, Any]:
    if response.y_type in {"continuous", "image-derived"}:
        return summarize_continuous(series, response)
    if response.y_type == "count":
        return summarize_count(series, response)
    if response.y_type == "binary":
        return summarize_binary(series, response)
    if response.y_type in {"categorical", "category", "class"}:
        return summarize_categorical(series, response)
    return summarize_categorical(series, response)


def condition_label(values: tuple[Any, ...], factor_columns: list[str]) -> str:
    return " / ".join(f"{column}={value}" for column, value in zip(factor_columns, values))


def response_by_condition(df: pd.DataFrame, request: DoeRequest, response: Response) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    factor_cols = request.factor_columns
    grouped = df.groupby(factor_cols, dropna=False, sort=True)
    for condition_values, group in grouped:
        if not isinstance(condition_values, tuple):
            condition_values = (condition_values,)
        summary = summarize_response(group[response.column], response)
        row = {
            "condition": condition_label(condition_values, factor_cols),
            "condition_values": dict(zip(factor_cols, condition_values)),
        }
        row.update(summary)
        rows.append(row)
    return rows


def _two_level_code(series: pd.Series) -> tuple[pd.Series, tuple[Any, Any]] | None:
    levels = sorted(series.dropna().unique().tolist())
    if len(levels) != 2:
        return None
    low, high = levels
    coded = series.map({low: -1, high: 1})
    return coded, (low, high)


def _effect_response_vector(df: pd.DataFrame, response: Response) -> pd.Series | None:
    if response.y_type in NUMERIC_Y_TYPES:
        numeric = pd.to_numeric(df[response.column], errors="coerce")
        return numeric if numeric.notna().any() else None
    if response.y_type == "binary":
        values = df[response.column]
        if response.fail_values:
            return _matches_values(values, response.fail_values).astype(float)
        numeric = pd.to_numeric(values, errors="coerce")
        if numeric.notna().any():
            return numeric
    if response.y_type in {"categorical", "category", "class"} and response.fail_values:
        return _matches_values(df[response.column], response.fail_values).astype(float)
    return None


def effect_table(
    df: pd.DataFrame,
    request: DoeRequest,
    response: Response,
    *,
    include_interactions: bool = True,
) -> list[dict[str, Any]]:
    y = _effect_response_vector(df, response)
    if y is None:
        return []
    effects: list[dict[str, Any]] = []
    coded_columns: dict[str, pd.Series] = {}
    level_labels: dict[str, tuple[Any, Any]] = {}

    for factor in request.factors:
        coded = _two_level_code(df[factor.column])
        if coded is None:
            continue
        code, labels = coded
        coded_columns[factor.column] = code
        level_labels[factor.column] = labels
        high_mean = float(y[code == 1].mean())
        low_mean = float(y[code == -1].mean())
        effects.append(
            {
                "term": factor.column,
                "kind": "main",
                "low_level": labels[0],
                "high_level": labels[1],
                "low_mean": low_mean,
                "high_mean": high_mean,
                "effect": high_mean - low_mean,
                "metric": "mean_or_rate_delta",
            }
        )

    if include_interactions:
        for left, right in combinations(coded_columns.keys(), 2):
            interaction_code = coded_columns[left] * coded_columns[right]
            high_mean = float(y[interaction_code == 1].mean())
            low_mean = float(y[interaction_code == -1].mean())
            effects.append(
                {
                    "term": f"{left}:{right}",
                    "kind": "interaction",
                    "low_level": "-1 product",
                    "high_level": "+1 product",
                    "low_mean": low_mean,
                    "high_mean": high_mean,
                    "effect": high_mean - low_mean,
                    "metric": "mean_or_rate_delta",
                }
            )

    total = sum(item["effect"] ** 2 for item in effects)
    for item in effects:
        contribution = (item["effect"] ** 2 / total) if total else 0.0
        item["contribution_ratio"] = contribution
        item["relative_effect_weight"] = contribution
        item["contribution_basis"] = "modeled_effects_only_no_error"
    return sorted(effects, key=lambda item: abs(item["effect"]), reverse=True)


def _categorical_formula_term(column: str) -> str:
    return f'C(Q("{column}"))'


def _anova_term_candidates(
    request: DoeRequest, *, include_interactions: bool = True
) -> list[tuple[str, list[str]]]:
    main_terms = [_categorical_formula_term(factor.column) for factor in request.factors]
    candidates: list[tuple[str, list[str]]] = []
    if include_interactions and len(main_terms) >= 2:
        interaction_terms = [
            f"{_categorical_formula_term(left.column)}:{_categorical_formula_term(right.column)}"
            for left, right in combinations(request.factors, 2)
        ]
        candidates.append(("main_plus_pairwise_interactions", [*main_terms, *interaction_terms]))
    candidates.append(("main_effects_only", main_terms))
    return candidates


def _friendly_anova_term(term: str, request: DoeRequest) -> str:
    if term == "Residual":
        return "Residual/Error"
    label = term
    for factor in request.factors:
        label = label.replace(_categorical_formula_term(factor.column), factor.column)
    return label


def _anova_term_kind(term: str) -> str:
    if term == "Residual":
        return "error"
    if ":" in term:
        return "interaction"
    return "main"


def anova_table(
    df: pd.DataFrame,
    request: DoeRequest,
    response: Response,
    *,
    include_interactions: bool = True,
) -> list[dict[str, Any]]:
    if response.y_type not in NUMERIC_Y_TYPES:
        return []
    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
    except Exception:
        return []

    factor_columns = request.factor_columns
    if not factor_columns:
        return []

    required_columns = [response.column, *factor_columns]
    if any(column not in df.columns for column in required_columns):
        return []

    data = df[required_columns].copy()
    data[response.column] = pd.to_numeric(data[response.column], errors="coerce")
    data = data.dropna(subset=required_columns)
    if data.empty:
        return []

    selected_table: pd.DataFrame | None = None
    selected_scope: str | None = None
    for scope, terms in _anova_term_candidates(request, include_interactions=include_interactions):
        if not terms:
            continue
        formula = f'Q("{response.column}") ~ ' + " + ".join(terms)
        try:
            model = smf.ols(formula, data=data).fit()
            table = sm.stats.anova_lm(model, typ=2)
        except Exception:
            continue
        if table.empty or "Residual" not in table.index:
            continue
        residual_df = _finite_or_none(table.loc["Residual"].get("df", np.nan))
        if residual_df is None or residual_df <= 0:
            continue
        selected_table = table
        selected_scope = scope
        break

    if selected_table is None or selected_scope is None:
        return []

    total_sum_sq = float(selected_table["sum_sq"].dropna().sum())
    rows: list[dict[str, Any]] = []
    for term, values in selected_table.iterrows():
        raw_term = str(term)
        sum_sq = _finite_or_none(values.get("sum_sq", np.nan))
        df_value = _finite_or_none(values.get("df", np.nan))
        mean_sq = (sum_sq / df_value) if sum_sq is not None and df_value and df_value > 0 else None
        rows.append(
            {
                "term": _friendly_anova_term(raw_term, request),
                "raw_term": raw_term,
                "term_kind": _anova_term_kind(raw_term),
                "model_scope": selected_scope,
                "sum_sq": sum_sq,
                "df": df_value,
                "mean_sq": mean_sq,
                "F": _finite_or_none(values.get("F", np.nan)),
                "p_value": _finite_or_none(values.get("PR(>F)", np.nan)),
                "contribution_ratio": (sum_sq / total_sum_sq)
                if sum_sq is not None and total_sum_sq > 0
                else None,
            }
        )
    return rows


def trend_analysis(df: pd.DataFrame, request: DoeRequest, response: Response) -> list[dict[str, Any]]:
    if response.y_type not in NUMERIC_Y_TYPES:
        return []
    y = pd.to_numeric(df[response.column], errors="coerce")
    rows: list[dict[str, Any]] = []
    for factor in request.factors:
        x = pd.to_numeric(df[factor.column], errors="coerce")
        valid = pd.DataFrame({"x": x, "y": y}).dropna()
        levels = sorted(valid["x"].unique().tolist())
        if len(valid) < 3 or len(levels) < 2:
            continue
        pearson_r, pearson_p = stats.pearsonr(valid["x"], valid["y"])
        spearman_r, spearman_p = stats.spearmanr(valid["x"], valid["y"])
        regression = stats.linregress(valid["x"], valid["y"])
        groups = [valid.loc[valid["x"] == level, "y"].to_numpy() for level in levels]
        anova_f, anova_p = stats.f_oneway(*groups)
        kruskal_h, kruskal_p = stats.kruskal(*groups)
        row: dict[str, Any] = {
            "factor": factor.column,
            "levels": levels,
            "n": len(valid),
            "pearson_r": _finite_or_none(pearson_r),
            "pearson_p": _finite_or_none(pearson_p),
            "spearman_r": _finite_or_none(spearman_r),
            "spearman_p": _finite_or_none(spearman_p),
            "regression_slope": _finite_or_none(regression.slope),
            "regression_intercept": _finite_or_none(regression.intercept),
            "regression_r_squared": _finite_or_none(regression.rvalue**2),
            "regression_p": _finite_or_none(regression.pvalue),
            "one_way_anova_F": _finite_or_none(anova_f),
            "one_way_anova_p": _finite_or_none(anova_p),
            "kruskal_H": _finite_or_none(kruskal_h),
            "kruskal_p": _finite_or_none(kruskal_p),
        }
        high_two = levels[-2:]
        boundary_groups = [valid.loc[valid["x"] == level, "y"].to_numpy() for level in high_two]
        if all(len(group) >= 2 for group in boundary_groups):
            welch_t, welch_p = stats.ttest_ind(*boundary_groups, equal_var=False)
            row.update(
                {
                    "boundary_levels": high_two,
                    "boundary_welch_t": _finite_or_none(welch_t),
                    "boundary_welch_p": _finite_or_none(welch_p),
                }
            )
        rows.append(row)
    return rows


def confirmation_analysis(by_condition: list[dict[str, Any]]) -> dict[str, Any]:
    if not by_condition:
        return {}
    capability_eligible = [
        row["condition"]
        for row in by_condition
        if str(row.get("capability_status", "")).startswith("eligible_")
    ]
    return {
        "condition_count": len(by_condition),
        "all_conditions_pass": all(int(row.get("fail_count", 0)) == 0 for row in by_condition),
        "minimum_condition_n": min(int(row.get("n", 0)) for row in by_condition),
        "capability_eligible_conditions": capability_eligible,
        "capability_claim_allowed": bool(capability_eligible),
    }


def analyze_responses(df: pd.DataFrame, request: DoeRequest) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for response in request.responses:
        policy = build_analysis_policy(request, response)
        overall = summarize_response(df[response.column], response)
        by_condition = response_by_condition(df, request, response)
        output[response.name] = {
            "response": response,
            "overall": overall,
            "by_condition": by_condition,
            "analysis_policy": policy,
            "effects": effect_table(
                df,
                request,
                response,
                include_interactions=policy["include_interactions"],
            )
            if policy["run_effects"] and response.y_type in EFFECT_Y_TYPES
            else [],
            "anova": anova_table(
                df,
                request,
                response,
                include_interactions=policy["include_interactions"],
            )
            if policy["run_anova"]
            else [],
            "trend": trend_analysis(df, request, response) if policy["run_trend_tests"] else [],
            "confirmation": confirmation_analysis(by_condition)
            if policy["run_confirmation_checks"]
            else {},
        }
    return output
