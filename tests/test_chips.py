# tests/test_chips.py
import pandas as pd

from sotl.chips import CHIP_IDS, run_chip


def _df():
    return pd.DataFrame([
        {"name": "A", "lab": "OpenAI", "price_out": 2.0, "swe_bench": 40,
         "context_window": 128000, "metric_notes": "", "params": "x"},
        {"name": "B", "lab": "Meta", "price_out": 1.0, "swe_bench": 50,
         "context_window": 1000000, "metric_notes": "open weights", "params": "x"},
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
