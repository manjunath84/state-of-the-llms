# src/sotl/data.py
from pathlib import Path

import pandas as pd

MODEL_REQUIRED = [
    "name", "lab", "release_date", "params", "context_window",
    "price_in", "price_out", "mmlu_pro", "swe_bench", "arena_elo",
    "source_url", "last_verified", "metric_type", "confidence", "metric_notes",
]


def load_models(path: Path) -> pd.DataFrame:
    # Validation is column-PRESENCE only (right altitude for Week 1). Numeric cells
    # may be non-parseable (e.g. "unknown"); downstream callers coerce with
    # pd.to_numeric(errors="coerce") + dropna rather than failing the whole load.
    df = pd.read_csv(path)
    missing = [c for c in MODEL_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"models.csv missing columns: {missing}")
    return df


USAGE_REQUIRED = [
    "date", "project", "task_type", "model",
    "input_tokens", "output_tokens",
    "cache_creation_tokens", "cache_read_tokens", "est_cost_usd",
]


def load_usage(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in USAGE_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"usage.csv missing columns: {missing}")
    return df
