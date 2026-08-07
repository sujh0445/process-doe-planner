from __future__ import annotations

from pathlib import Path

import pandas as pd

from .schemas import DoeRequest


def load_experiment_data(path: str | Path) -> pd.DataFrame:
    data_path = Path(path)
    suffix = data_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(data_path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(data_path)
    raise ValueError(f"Unsupported data file type: {suffix}")


def validate_data_columns(df: pd.DataFrame, request: DoeRequest) -> None:
    required = set(request.factor_columns + request.response_columns)
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Experiment data is missing required columns: {', '.join(missing)}")
