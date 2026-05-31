# src/sotl/chips.py
from dataclasses import dataclass

import pandas as pd

CHIP_IDS = ["coding_per_dollar", "open_vs_closed", "context_leaders"]
CHIP_LABELS = {
    "coding_per_dollar": "Best coding per dollar",
    "open_vs_closed": "Open vs closed",
    "context_leaders": "Context window leaders",
}


@dataclass
class ChipResult:
    chip_id: str
    headline: str
    frame: pd.DataFrame


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def run_chip(chip_id: str, df: pd.DataFrame) -> ChipResult:
    d = df.copy()
    if chip_id == "coding_per_dollar":
        d["coding_per_dollar"] = _num(d["swe_bench"]) / _num(d["price_out"])
        d = d.dropna(subset=["coding_per_dollar"]).sort_values(
            "coding_per_dollar", ascending=False)
        cols = ["name", "lab", "swe_bench", "price_out", "coding_per_dollar"]
        if d.empty:  # no row has both SWE-bench and price → don't crash on .iloc[0]
            return ChipResult(chip_id, "No models with both SWE-bench and price data.", d[cols])
        top = d.iloc[0]
        headline = (f"{top['name']}: {top['coding_per_dollar']:.1f} "
                    "SWE-bench pts per $/1M out")
        return ChipResult(chip_id, headline, d[cols])
    if chip_id == "open_vs_closed":
        d["kind"] = d["metric_notes"].str.contains("open", case=False, na=False).map(
            {True: "open", False: "closed"})
        agg = d.groupby("kind", as_index=False).agg(
            avg_swe=("swe_bench", lambda s: _num(s).mean()),
            avg_price=("price_out", lambda s: _num(s).mean()))
        return ChipResult(chip_id, "Average SWE-bench and price by open vs closed", agg)
    if chip_id == "context_leaders":
        d["context_window"] = _num(d["context_window"])
        d = d.dropna(subset=["context_window"]).sort_values("context_window", ascending=False)
        cols = ["name", "lab", "context_window"]
        if d.empty:  # no row has a parseable context window → don't crash on int(NaN)
            return ChipResult(chip_id, "No models with context-window data.", d[cols])
        top = d.iloc[0]
        return ChipResult(chip_id,
                          f"{top['name']} leads at {int(top['context_window']):,} tokens",
                          d[cols].head(5))
    raise ValueError(f"unknown chip_id: {chip_id}")
