# tests/test_data.py
from pathlib import Path

import pandas as pd
import pytest

from sotl.data import (
    MODEL_REQUIRED,
    PRICING_REQUIRED,
    USAGE_REQUIRED,
    load_models,
    load_pricing,
    load_usage,
)


def _write(tmp_path: Path, rows: list[dict]) -> Path:
    p = tmp_path / "models.csv"
    pd.DataFrame(rows).to_csv(p, index=False)
    return p


def test_load_models_ok(tmp_path):
    row = {c: "x" for c in MODEL_REQUIRED}
    row.update(name="GPT-4o", price_out=10, context_window=128000)
    df = load_models(_write(tmp_path, [row]))
    assert list(df["name"]) == ["GPT-4o"]


def test_load_models_missing_column_raises(tmp_path):
    bad = {"name": "GPT-4o"}  # missing provenance + metrics
    with pytest.raises(ValueError, match="missing columns"):
        load_models(_write(tmp_path, [bad]))


def test_load_usage_ok(tmp_path):
    row = {c: 0 for c in USAGE_REQUIRED}
    row.update(date="2026-05-20", project="GenAcademy", task_type="notes", model="claude-opus-4-8")
    p = tmp_path / "usage.csv"
    pd.DataFrame([row]).to_csv(p, index=False)
    df = load_usage(p)
    assert df.loc[0, "model"] == "claude-opus-4-8"


def test_load_usage_missing_column_raises(tmp_path):
    p = tmp_path / "usage.csv"
    pd.DataFrame([{"date": "2026-05-20"}]).to_csv(p, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        load_usage(p)


def test_load_pricing_ok(tmp_path):
    row = {c: 0 for c in PRICING_REQUIRED}
    row.update(model_id="claude-opus-4-8", price_out_per_mtok=25)
    p = tmp_path / "pricing.csv"
    pd.DataFrame([row]).to_csv(p, index=False)
    df = load_pricing(p)
    assert df.loc[0, "model_id"] == "claude-opus-4-8"


def test_load_pricing_missing_column_raises(tmp_path):
    p = tmp_path / "pricing.csv"
    pd.DataFrame([{"model_id": "x"}]).to_csv(p, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        load_pricing(p)
