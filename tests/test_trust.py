# tests/test_trust.py
import pandas as pd

from sotl.trust import trust_summary


def _df():
    return pd.DataFrame([
        {"metric_type": "measured", "last_verified": "2026-05-31", "swe_bench": 49},
        {"metric_type": "reported_by_lab", "last_verified": "2026-04-01", "swe_bench": 40},
        {"metric_type": "unknown", "last_verified": "2026-05-31", "swe_bench": "unknown"},
    ])


def test_trust_summary_counts_and_oldest():
    s = trust_summary(_df())
    assert s["counts"]["measured"] == 1
    assert s["counts"]["reported_by_lab"] == 1
    assert s["oldest_verified"] == "2026-04-01"
    assert s["missing_swe_bench"] == 1
