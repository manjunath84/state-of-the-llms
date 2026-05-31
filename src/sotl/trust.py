# src/sotl/trust.py
import pandas as pd


def trust_summary(df: pd.DataFrame) -> dict:
    counts = df["metric_type"].value_counts().to_dict()
    missing = int((pd.to_numeric(df["swe_bench"], errors="coerce").isna()).sum())
    return {
        "counts": counts,
        "oldest_verified": str(df["last_verified"].min()),
        "missing_swe_bench": missing,
    }
