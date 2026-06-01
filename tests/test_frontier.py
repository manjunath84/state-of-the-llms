# tests/test_frontier.py
import pandas as pd

from sotl.frontier import pareto_frontier


def _df():
    return pd.DataFrame([
        {"name": "cheap-weak", "price_out": 1.0, "swe_bench": 60.0},
        {"name": "mid", "price_out": 5.0, "swe_bench": 80.0},
        {"name": "pricey-strong", "price_out": 25.0, "swe_bench": 89.0},
        # dominated: pricier than "mid" AND weaker → must be excluded
        {"name": "dominated", "price_out": 10.0, "swe_bench": 75.0},
    ])


def test_frontier_excludes_dominated():
    front = pareto_frontier(_df())
    assert "dominated" not in set(front["name"])


def test_frontier_includes_extremes_sorted_by_price():
    front = pareto_frontier(_df())
    assert list(front["name"]) == ["cheap-weak", "mid", "pricey-strong"]
    # cheapest and most-capable endpoints are always present
    assert front.iloc[0]["name"] == "cheap-weak"
    assert front.iloc[-1]["name"] == "pricey-strong"


def test_frontier_drops_unparseable_rows():
    df = pd.DataFrame([
        {"name": "ok", "price_out": 2.0, "swe_bench": 70.0},
        {"name": "no-score", "price_out": 1.0, "swe_bench": "unknown"},
    ])
    front = pareto_frontier(df)
    assert list(front["name"]) == ["ok"]
