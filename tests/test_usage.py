# tests/test_usage.py
import pandas as pd

from sotl.usage import by_model, total_spend


def _df():
    return pd.DataFrame([
        {"project": "GenAcademy", "model": "claude-opus-4-8",
         "input_tokens": 1_000_000, "output_tokens": 100_000,
         "cache_creation_tokens": 0, "cache_read_tokens": 0, "est_cost_usd": 22.5},
        {"project": "GenAcademy-Week1", "model": "claude-sonnet-4-6",
         "input_tokens": 500_000, "output_tokens": 50_000,
         "cache_creation_tokens": 0, "cache_read_tokens": 0, "est_cost_usd": 2.25},
    ])


def test_total_spend():
    assert total_spend(_df()) == 24.75


def test_by_model_sorted_desc():
    out = by_model(_df())
    assert list(out["model"]) == ["claude-opus-4-8", "claude-sonnet-4-6"]
    assert out.iloc[0]["est_cost_usd"] == 22.5
