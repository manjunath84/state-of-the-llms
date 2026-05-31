# CLAUDE.md — working agreement for AI agents

This is a vibe-coded Streamlit data app. Read `docs/constitution.md` first.

## Architecture (do not violate)
- All logic in `src/sotl/` — pure, unit-tested, NO `st.*` imports.
- `app.py` is the ONLY Streamlit file.
- Numbers come from pandas. The LLM narrates; it never computes.

## Workflow
- TDD: failing test first (`tests/`), then implement.
- `uv run pytest -q` and `uv run ruff check .` must pass before commit.
- Specs in `docs/superpowers/specs/` are the source of truth (ADR 0002).

## Data & privacy
- Raw `~/.claude` transcripts NEVER get committed. Only aggregated, scrubbed
  `data/usage.csv` (guardrail #4).
- Token counts are real; the dollar figure is a notional list-price conversion.

## Commands
- Run app: `uv run streamlit run app.py`
- Refresh cost data: `uv run python scripts/derive_usage.py`
- Tests: `uv run pytest -q`
