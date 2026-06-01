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


def _as_bool(s: pd.Series) -> pd.Series:
    # CSV booleans arrive as strings ("true"/"false"); normalize to real bools.
    if s.dtype == bool:
        return s
    return s.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "open"})


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
        top_swe = _num(pd.Series([top["swe_bench"]])).iloc[0]
        top_price = _num(pd.Series([top["price_out"]])).iloc[0]
        headline = (
            f"Best coding value: {top['name']} scores {top_swe:.0f}% on SWE-bench at just "
            f"${top_price:.2f} per 1M output tokens — the most coding skill per dollar here."
        )
        return ChipResult(chip_id, headline, d[cols])
    if chip_id == "open_vs_closed":
        # Prefer the explicit, sourced is_open column (guardrail #2); only fall back
        # to a notes heuristic for frames that lack it. The heuristic alone
        # misclassifies a closed model whose notes merely mention "open-source".
        if "is_open" in d.columns:
            d["kind"] = _as_bool(d["is_open"]).map({True: "open", False: "closed"})
        else:
            d["kind"] = d["metric_notes"].str.contains("open", case=False, na=False).map(
                {True: "open", False: "closed"})
        agg = d.groupby("kind", as_index=False).agg(
            avg_swe=("swe_bench", lambda s: _num(s).mean()),
            avg_price=("price_out", lambda s: _num(s).mean()))
        byk = agg.set_index("kind")
        if {"open", "closed"} <= set(byk.index):
            o, c = byk.loc["open"], byk.loc["closed"]
            headline = (
                f"Open models average {o['avg_swe']:.0f}% on SWE-bench vs {c['avg_swe']:.0f}% "
                f"for closed — and average ${o['avg_price']:.2f} vs ${c['avg_price']:.2f} "
                f"per 1M output tokens. The gap on skill is small; the gap on price is large."
            )
        else:
            headline = "Average SWE-bench and price, grouped by open vs closed weights."
        return ChipResult(chip_id, headline, agg)
    if chip_id == "context_leaders":
        d["context_window"] = _num(d["context_window"])
        d = d.dropna(subset=["context_window"]).sort_values("context_window", ascending=False)
        cols = ["name", "lab", "context_window"]
        if d.empty:  # no row has a parseable context window → don't crash on int(NaN)
            return ChipResult(chip_id, "No models with context-window data.", d[cols])
        top = d.iloc[0]
        return ChipResult(
            chip_id,
            f"Longest memory: {top['name']} holds {int(top['context_window']):,} tokens "
            f"of context at once — room for entire codebases in a single prompt.",
            d[cols].head(5),
        )
    raise ValueError(f"unknown chip_id: {chip_id}")
