# Project Constitution — State of the LLMs

## Purpose
A vibe-coded, CSV-backed Streamlit data app that helps a builder choose a frontier
model, then shows — using THIS project's own Claude Code token logs — what those
tokens would cost at API list prices.

## Principles
1. **Spec is the source of truth.** Specs in `docs/superpowers/specs/`. No PLAN.md
   duplication (see ADR 0002).
2. **Pure core, thin view.** All logic in `src/sotl/` (unit-tested, no `st.*`).
   `app.py` is the only Streamlit file.
3. **Determinism first.** Numbers come from pandas, never the LLM. The LLM narrates;
   it never computes (see ADR 0003).
4. **Honest numbers.** Token counts are real (measured). The dollar figure is a
   notional list-price conversion, never claimed as actual spend.
5. **Privacy.** Raw transcripts never leave the machine; only aggregated, scrubbed
   `usage.csv` is committed (guardrail #4).
6. **Demo-safe.** The recorded demo must never depend on a live API. Cache + fallback
   guarantee it (guardrail #6).
7. **TDD.** Every core module gets a failing test first.

## Tech
Python 3.12 · uv · Streamlit · pandas · Plotly · openai SDK (OpenAI-compatible
endpoint; default OpenRouter open models) · ruff + pytest + GitHub Actions.

## Definition of done
All MUST tasks complete, tests green, ruff clean, README with run steps + screenshots,
three ADRs, deliverable trio captured.
