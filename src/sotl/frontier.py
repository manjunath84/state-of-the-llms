# src/sotl/frontier.py
import pandas as pd


def pareto_frontier(df: pd.DataFrame) -> pd.DataFrame:
    # The price-for-skill frontier: models you cannot beat on BOTH axes at once.
    # X = price_out (lower is better), Y = swe_bench (higher is better). A model
    # is on the frontier unless some OTHER model is at least as cheap AND at
    # least as capable, and strictly better on one axis (i.e. it dominates).
    # Returns the frontier sorted by price so the view can draw a line through it.
    d = df.copy()
    d["price_out"] = pd.to_numeric(d["price_out"], errors="coerce")
    d["swe_bench"] = pd.to_numeric(d["swe_bench"], errors="coerce")
    d = d.dropna(subset=["price_out", "swe_bench"])
    keep = []
    for i, row in d.iterrows():
        dominated = (
            (d["price_out"] <= row["price_out"])
            & (d["swe_bench"] >= row["swe_bench"])
            & ((d["price_out"] < row["price_out"]) | (d["swe_bench"] > row["swe_bench"]))
        )
        if not dominated.any():
            keep.append(i)
    return d.loc[keep].sort_values("price_out").reset_index(drop=True)
