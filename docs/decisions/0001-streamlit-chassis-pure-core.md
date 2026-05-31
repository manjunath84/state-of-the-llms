# ADR 0001 — Streamlit chassis + pure-logic core
**Status:** accepted · **Date:** 2026-05-30

## Problem
A vibe-coded Streamlit app tends to tangle UI and logic, making it untestable and
the "technical thinking" invisible.

## Solution
All logic lives in `src/sotl/` (UI-agnostic, unit-tested); `st.*` calls live only
in `app.py`. The picker's "latency" input is approximated by a `prefer_efficient`
value-per-dollar ranking because `models.csv` has no latency column.

## Impact
Logic is unit-tested in CI; the view is a thin render layer; swapping Streamlit
later is cheap.

## What I Learned
Separating compute from view is what let the LLM stay a *narrator* — it never
touches numbers. The concrete Streamlit gotcha was dtype: CSV cells like
`"unknown"` make a whole numeric column `object` dtype, so every chart/sort path
needs `pd.to_numeric(col, errors="coerce")` + `dropna` before plotting, and that
`dropna` can empty a frame — guard `.iloc[0]` accordingly.
