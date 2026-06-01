# src/sotl/usage.py
import pandas as pd

# The app folder vs the whole Week-1 effort. derive_usage.py tags every row with
# the cwd basename; "state-of-the-llms" is the app itself, the rest (plans,
# superpowers, Week1-…) is the brainstorm/plan scaffolding around it.
APP_PROJECT = "state-of-the-llms"

# The four billable buckets, paired with their per-Mtok price column in
# pricing.csv. Kept here (not in the view) so cost_components stays pure.
_COMPONENTS = [
    ("input", "input_tokens", "price_in_per_mtok"),
    ("output", "output_tokens", "price_out_per_mtok"),
    ("cache_read", "cache_read_tokens", "cache_read_per_mtok"),
    ("cache_write", "cache_creation_tokens", "cache_write_per_mtok"),
]


def total_spend(df: pd.DataFrame) -> float:
    return round(float(df["est_cost_usd"].sum()), 2)


def by_model(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("model", as_index=False)["est_cost_usd"].sum()
        .sort_values("est_cost_usd", ascending=False)
        .reset_index(drop=True)
    )


def by_model_detail(df: pd.DataFrame) -> pd.DataFrame:
    # Per-model output tokens + cost + share, sorted by cost. Powers the
    # finale's "which model actually ran" reveal — the Opus-vs-Sonnet story.
    out = (
        df.groupby("model", as_index=False)
        .agg(output_tokens=("output_tokens", "sum"), est_cost_usd=("est_cost_usd", "sum"))
        .sort_values("est_cost_usd", ascending=False)
        .reset_index(drop=True)
    )
    total = out["est_cost_usd"].sum()
    out["share_pct"] = (out["est_cost_usd"] / total * 100).round(1) if total else 0.0
    return out


def filter_scope(df: pd.DataFrame, app_only: bool) -> pd.DataFrame:
    # app_only=True → just the app folder; False → the whole Week-1 effort.
    if app_only:
        return df[df["project"] == APP_PROJECT].reset_index(drop=True)
    return df.reset_index(drop=True)


def cost_components(usage_df: pd.DataFrame, pricing_df: pd.DataFrame) -> pd.DataFrame:
    # Recompute the dollar split across the four billable buckets. usage.csv only
    # stores the aggregate est_cost_usd, so we re-join list pricing and derive
    # each component — this is what shows the headline is mostly cache writes,
    # not output. Returns columns: component, cost (one row per bucket).
    d = usage_df.merge(
        pricing_df.rename(columns={"model_id": "model"}), on="model", how="left"
    )
    rows = []
    for name, tok_col, price_col in _COMPONENTS:
        cost = (d[tok_col] / 1e6 * d[price_col].fillna(0)).sum()
        rows.append({"component": name, "cost": round(float(cost), 2)})
    return pd.DataFrame(rows)


def by_task(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("task_type", as_index=False)["est_cost_usd"].sum()
        .sort_values("est_cost_usd", ascending=False)
        .reset_index(drop=True)
    )
