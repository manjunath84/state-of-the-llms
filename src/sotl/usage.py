# src/sotl/usage.py
import pandas as pd


def total_spend(df: pd.DataFrame) -> float:
    return round(float(df["est_cost_usd"].sum()), 2)


def by_model(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("model", as_index=False)["est_cost_usd"].sum()
        .sort_values("est_cost_usd", ascending=False)
        .reset_index(drop=True)
    )


def by_task(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("task_type", as_index=False)["est_cost_usd"].sum()
        .sort_values("est_cost_usd", ascending=False)
        .reset_index(drop=True)
    )
