# tests/test_usage.py
import pandas as pd

from sotl.usage import (
    by_model,
    by_model_detail,
    cost_components,
    filter_scope,
    total_spend,
)


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


def test_by_model_detail_share_and_tokens():
    out = by_model_detail(_df())
    assert list(out["model"]) == ["claude-opus-4-8", "claude-sonnet-4-6"]
    # opus = 22.5 / 24.75 = 90.9%; shares sum to 100
    assert out.iloc[0]["share_pct"] == 90.9
    assert round(out["share_pct"].sum()) == 100
    assert out.iloc[0]["output_tokens"] == 100_000


def test_filter_scope_app_only():
    df = pd.DataFrame([
        {"project": "state-of-the-llms", "model": "m", "input_tokens": 0,
         "output_tokens": 0, "cache_creation_tokens": 0, "cache_read_tokens": 0,
         "est_cost_usd": 5.0},
        {"project": "plans", "model": "m", "input_tokens": 0, "output_tokens": 0,
         "cache_creation_tokens": 0, "cache_read_tokens": 0, "est_cost_usd": 3.0},
    ])
    assert total_spend(filter_scope(df, app_only=True)) == 5.0
    assert total_spend(filter_scope(df, app_only=False)) == 8.0


def _pricing():
    return pd.DataFrame([
        {"model_id": "claude-opus-4-8", "price_in_per_mtok": 5,
         "price_out_per_mtok": 25, "cache_read_per_mtok": 0.5,
         "cache_write_per_mtok": 6.25},
    ])


def test_cost_components_buckets_sum_to_total():
    usage = pd.DataFrame([
        {"project": "p", "model": "claude-opus-4-8", "input_tokens": 1_000_000,
         "output_tokens": 1_000_000, "cache_creation_tokens": 1_000_000,
         "cache_read_tokens": 1_000_000, "est_cost_usd": 36.75},
    ])
    comp = cost_components(usage, _pricing())
    by = dict(zip(comp["component"], comp["cost"], strict=True))
    assert by == {"input": 5.0, "output": 25.0, "cache_read": 0.5, "cache_write": 6.25}
    # the four buckets must reconstruct the stored aggregate (within a cent)
    assert abs(comp["cost"].sum() - 36.75) < 0.01
