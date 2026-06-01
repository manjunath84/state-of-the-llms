# scripts/validate_models.py
"""Validate data/models.csv before a demo (guardrail #2: every number is sourced).

Fails (exit 1) if any row still carries placeholder text, is missing provenance
(source_url / last_verified), has an unparseable is_open, or if too few rows have
numeric price_out / mmlu_pro for the Beat-1 scatter to show a real spread. On
success prints the price/score spread and the open/closed split.

Run: uv run python scripts/validate_models.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from sotl.data import MODEL_REQUIRED

MODELS = Path("data/models.csv")
MIN_ROWS = 10          # below this the scatter looks sparse
MIN_NUMERIC = 10       # rows that must have BOTH numeric price_out and swe_bench (scatter axes)
PLACEHOLDER_MARKERS = ("seed row", "verify/replace", "todo", "tbd", "placeholder")
BOOL_TRUE = {"true", "1", "yes", "open"}
BOOL_FALSE = {"false", "0", "no", "closed"}


def _numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def validate(df: pd.DataFrame) -> list[str]:
    """Return a list of problem strings; empty list == valid."""
    problems: list[str] = []

    missing_cols = [c for c in MODEL_REQUIRED if c not in df.columns]
    if missing_cols:
        return [f"missing required columns: {missing_cols}"]  # nothing else is meaningful

    if len(df) < MIN_ROWS:
        problems.append(f"only {len(df)} rows; want >= {MIN_ROWS} for a real scatter")

    for i, row in df.iterrows():
        label = str(row.get("name", f"row {i}")).strip() or f"row {i}"

        # placeholder text anywhere in the row
        blob = " ".join(str(v) for v in row.values).lower()
        hit = next((m for m in PLACEHOLDER_MARKERS if m in blob), None)
        if hit:
            problems.append(f"{label}: placeholder text {hit!r} still present")

        # provenance required on every row (guardrail #2)
        for col in ("source_url", "last_verified"):
            val = str(row.get(col, "")).strip().lower()
            if val in ("", "nan", "unknown"):
                problems.append(f"{label}: {col} is blank")
        src = str(row.get("source_url", "")).strip()
        if src and not src.startswith(("http://", "https://")):
            problems.append(f"{label}: source_url is not a URL ({src!r})")

        # is_open must be a recognizable boolean
        is_open = str(row.get("is_open", "")).strip().lower()
        if is_open not in BOOL_TRUE | BOOL_FALSE:
            problems.append(f"{label}: is_open not boolean ({row.get('is_open')!r})")

    # enough rows with BOTH scatter axes numeric, or the scatter is empty/sparse.
    # Beat 1 plots price_out (X) vs swe_bench (Y) — keep this in sync with beat_scatter.
    both = _numeric(df["price_out"]).notna() & _numeric(df["swe_bench"]).notna()
    n_both = int(both.sum())
    if n_both < MIN_NUMERIC:
        problems.append(
            f"only {n_both} rows have numeric price_out AND swe_bench; "
            f"want >= {MIN_NUMERIC} or the scatter is sparse"
        )

    return problems


def _spread_report(df: pd.DataFrame) -> str:
    po = _numeric(df["price_out"]).dropna()
    mm = _numeric(df["mmlu_pro"]).dropna()
    sw = _numeric(df["swe_bench"]).dropna()
    is_open = df["is_open"].astype(str).str.strip().str.lower().isin(BOOL_TRUE)
    n_open = int(is_open.sum())
    lines = [
        f"rows: {len(df)}  (open: {n_open}, closed: {len(df) - n_open})",
        f"price_out $/1M out: {po.min():.2f} – {po.max():.2f} ({len(po)} numeric)"
        if len(po) else "price_out: no numeric values",
        f"mmlu_pro:           {mm.min():.1f} – {mm.max():.1f} ({len(mm)} numeric)"
        if len(mm) else "mmlu_pro: no numeric values",
        f"swe_bench:          {sw.min():.1f} – {sw.max():.1f} ({len(sw)} numeric)"
        if len(sw) else "swe_bench: no numeric values",
    ]
    return "\n".join(lines)


def main() -> int:
    if not MODELS.exists():
        print(f"✗ {MODELS} not found", file=sys.stderr)
        return 1
    df = pd.read_csv(MODELS)
    problems = validate(df)
    if problems:
        print(f"✗ {MODELS} has {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"✓ {MODELS} looks demo-ready")
    print(_spread_report(df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
