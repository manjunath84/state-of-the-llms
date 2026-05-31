# tests/test_recommend.py
import pandas as pd

from sotl.recommend import recommend


def _df():
    return pd.DataFrame([
        {
            "name": "Cheap", "price_out": 1.0, "swe_bench": 40,
            "mmlu_pro": 60, "params": "7000000000",
        },
        {
            "name": "Mid", "price_out": 5.0, "swe_bench": 50,
            "mmlu_pro": 70, "params": "70000000000",
        },
        {
            "name": "Frontier", "price_out": 20.0, "swe_bench": 55,
            "mmlu_pro": 80, "params": "unknown",
        },
    ])


def test_picks_best_coder_within_budget():
    rec = recommend(_df(), task="coding", max_price_out=10.0, prefer_efficient=False)
    assert rec.pick == "Mid"          # best swe_bench at price_out <= 10
    assert rec.score_col == "swe_bench"
    assert "Frontier" not in set(rec.reason_rows["name"])  # filtered out by budget


def test_prefer_efficient_ranks_by_value_per_dollar():
    # within budget: Cheap (40/$1 = 40) beats Mid (50/$5 = 10) on score-per-dollar
    rec = recommend(_df(), task="coding", max_price_out=10.0, prefer_efficient=True)
    assert rec.pick == "Cheap"


def test_budget_filters_everything_returns_none():
    rec = recommend(_df(), task="coding", max_price_out=0.5, prefer_efficient=False)
    assert rec.pick is None
    assert rec.reason_rows.empty
