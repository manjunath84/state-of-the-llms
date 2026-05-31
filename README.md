# State of the LLMs

A vibe-coded, CSV-backed **Streamlit** data app — a *model-selection data story* for builders.
Gen Academy "Mastering Agentic AI Bootcamp", Week 1 project.

Given a task type, budget, and latency tolerance, it recommends a frontier model and **shows its work**
(price-vs-performance, the filtered rows, the math). It closes on a real, personal proof: at published
API list prices, what the tokens that built *this very app* would cost.

> **Status: design phase.** No application code yet — this commit is the spec + implementation plan.
> Build follows a brainstorm → spec → plan → TDD workflow.

## Design docs
- **Spec (source of truth):** [`docs/superpowers/specs/2026-05-30-state-of-the-llms-design.md`](docs/superpowers/specs/2026-05-30-state-of-the-llms-design.md)
- **Implementation plan (TDD):** [`docs/superpowers/plans/2026-05-30-state-of-the-llms.md`](docs/superpowers/plans/2026-05-30-state-of-the-llms.md)

## Planned stack
Python 3.12 · `uv` · Streamlit · pandas · Plotly · `openai` SDK (pointed at any OpenAI-compatible
endpoint; default an open-source model via OpenRouter) · ruff + pytest + GitHub Actions.

Architecture: pure-core / thin-view — all logic in `src/sotl/` (unit-tested), `st.*` only in `app.py`.
