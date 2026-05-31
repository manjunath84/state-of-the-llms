# ADR 0001 — Streamlit + CSV vibe stack

## Problem
Need a data app a non-frontend builder can finish in 5 days and demo live.

## Solution
Streamlit over CSVs. No DB, no JS build, no server. pandas for logic, Plotly for
charts, uv for packaging.

## Impact
- Fast: chart in a few lines; hot reload.
- Limited interactivity vs a SPA — acceptable for a data story.
- CSV is the contract; a schema check guards it.

## What I Learned
Streamlit's rerun-on-every-interaction model means data loaders must be wrapped in
`@st.cache_data` or every widget click re-reads the CSVs. The biggest concrete
gotcha was dtype: CSV cells like `"unknown"` make a whole numeric column `object`
dtype, so every chart/sort path needs `pd.to_numeric(col, errors="coerce")` plus a
`dropna` before plotting — otherwise Plotly and `.sort_values` fail or mis-order.
