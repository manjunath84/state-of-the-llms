# tests/test_chips.py
import pandas as pd

from sotl.chips import CHIP_IDS, run_chip


def _df():
    return pd.DataFrame([
        {"name": "A", "lab": "OpenAI", "price_out": 2.0, "swe_bench": 40,
         "context_window": 128000, "is_open": "false", "metric_notes": "", "params": "x"},
        {"name": "B", "lab": "Meta", "price_out": 1.0, "swe_bench": 50,
         "context_window": 1000000, "is_open": "true", "metric_notes": "open weights",
         "params": "x"},
    ])


def test_chip_ids_are_three():
    assert len(CHIP_IDS) == 3


def test_coding_per_dollar_picks_best_ratio():
    res = run_chip("coding_per_dollar", _df())
    assert res.frame.iloc[0]["name"] == "B"  # 50/1.0 beats 40/2.0
    assert "B" in res.headline


def test_context_leaders_orders_by_window():
    res = run_chip("context_leaders", _df())
    assert res.frame.iloc[0]["name"] == "B"


def _all_unknown_df():
    # every metric cell is non-numeric — the degenerate case real data can hit
    return pd.DataFrame([
        {"name": "A", "lab": "OpenAI", "price_out": "unknown", "swe_bench": "unknown",
         "context_window": "unknown", "metric_notes": "", "params": "x"},
    ])


def test_coding_per_dollar_empty_metric_does_not_crash():
    res = run_chip("coding_per_dollar", _all_unknown_df())
    assert res.frame.empty
    assert "No models" in res.headline


def test_context_leaders_empty_metric_does_not_crash():
    res = run_chip("context_leaders", _all_unknown_df())
    assert res.frame.empty
    assert "No models" in res.headline


def test_open_vs_closed_uses_is_open_not_notes():
    # A closed model whose notes mention "open-source" must classify as CLOSED:
    # the explicit is_open column wins over the notes heuristic.
    df = pd.DataFrame([
        {"name": "Trap", "lab": "OpenAI", "price_out": 5.0, "swe_bench": 45,
         "context_window": 128000, "is_open": "false",
         "metric_notes": "competes with open-source models", "params": "x"},
        {"name": "RealOpen", "lab": "Meta", "price_out": 0.5, "swe_bench": 50,
         "context_window": 128000, "is_open": "true", "metric_notes": "", "params": "x"},
    ])
    res = run_chip("open_vs_closed", df)
    kinds = dict(zip(res.frame["kind"], res.frame["avg_swe"], strict=True))
    assert set(kinds) == {"open", "closed"}
    # the trap row landed in closed (swe 45), the real open row in open (swe 50)
    assert kinds["closed"] == 45
    assert kinds["open"] == 50
