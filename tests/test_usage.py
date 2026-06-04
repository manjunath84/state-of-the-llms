# tests/test_usage.py
import pandas as pd

from sotl.usage import (
    by_model,
    by_model_detail,
    cost_components,
    filter_scope,
    reprice_uniform,
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


def _pricing_three():
    return pd.DataFrame([
        {"model_id": "claude-opus-4-8", "price_in_per_mtok": 5,
         "price_out_per_mtok": 25, "cache_read_per_mtok": 0.5,
         "cache_write_per_mtok": 6.25},
        {"model_id": "claude-sonnet-4-6", "price_in_per_mtok": 3,
         "price_out_per_mtok": 15, "cache_read_per_mtok": 0.3,
         "cache_write_per_mtok": 3.75},
        {"model_id": "claude-haiku-4-5-20251001", "price_in_per_mtok": 1,
         "price_out_per_mtok": 5, "cache_read_per_mtok": 0.1,
         "cache_write_per_mtok": 1.25},
    ])


def _usage_1m_each():
    # one row, 1M tokens in every bucket — makes each model's re-price equal the
    # straight sum of its four rates.
    return pd.DataFrame([
        {"project": "p", "model": "claude-opus-4-8", "input_tokens": 1_000_000,
         "output_tokens": 1_000_000, "cache_creation_tokens": 1_000_000,
         "cache_read_tokens": 1_000_000, "est_cost_usd": 36.75},
    ])


def test_reprice_uniform_prices_whole_volume_at_each_model_rate():
    out = reprice_uniform(_usage_1m_each(), _pricing_three())
    by = dict(zip(out["model"], out["total_cost"], strict=True))
    # 1M in each of 4 buckets → just the sum of that model's four list rates
    assert by["claude-opus-4-8"] == 36.75       # 5 + 25 + 0.5 + 6.25
    assert by["claude-sonnet-4-6"] == 22.05     # 3 + 15 + 0.3 + 3.75
    assert by["claude-haiku-4-5-20251001"] == 7.35  # 1 + 5 + 0.1 + 1.25


def test_reprice_uniform_sorted_cheapest_first_and_5x_spread():
    out = reprice_uniform(_usage_1m_each(), _pricing_three())
    # cheapest model leads the frame
    assert out.iloc[0]["model"] == "claude-haiku-4-5-20251001"
    assert out.iloc[-1]["model"] == "claude-opus-4-8"
    # the published Opus/Haiku list rates are exactly 5× apart, per row and total
    cheapest, dearest = out.iloc[0]["total_cost"], out.iloc[-1]["total_cost"]
    assert round(dearest / cheapest, 2) == 5.0


def test_reprice_uniform_aggregates_multiple_usage_rows():
    # two rows of differing models still re-price on the *token volume*, not the
    # model each row actually ran on — that's the counterfactual.
    usage = pd.DataFrame([
        {"project": "p", "model": "claude-opus-4-8", "input_tokens": 1_000_000,
         "output_tokens": 0, "cache_creation_tokens": 0, "cache_read_tokens": 0,
         "est_cost_usd": 5.0},
        {"project": "p", "model": "claude-sonnet-4-6", "input_tokens": 1_000_000,
         "output_tokens": 0, "cache_creation_tokens": 0, "cache_read_tokens": 0,
         "est_cost_usd": 3.0},
    ])
    out = reprice_uniform(usage, _pricing_three())
    by = dict(zip(out["model"], out["total_cost"], strict=True))
    # 2M input tokens priced at Opus input rate ($5/Mtok) = $10, regardless of
    # which model each row ran on
    assert by["claude-opus-4-8"] == 10.0
    assert by["claude-haiku-4-5-20251001"] == 2.0
