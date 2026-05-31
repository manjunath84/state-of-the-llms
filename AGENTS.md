# AGENTS.md

The same working agreement applies to all AI agents (Claude, Codex, Cursor, etc.).
See **`CLAUDE.md`** for the full version.

**Start here:** read `specs/` (the constitution) before changing scope. The
`specs/` dir is canonical — no `PLAN.md`; ADRs live in `docs/decisions/`.

**Non-negotiables (the 8 guardrails, full text in `specs/tech-stack.md`):**
pure core / thin view (`st.*` only in `app.py`) · every number sourced · the LLM
never invents numbers · never commit raw transcripts (only scrubbed `usage.csv`) ·
config via pydantic-settings singleton · demo-safe (renders with no API key) ·
diverge from the Solution Kit · audits require evidence (ruff + pytest output).

**Commands:** `uv sync` · `uv run streamlit run app.py` · `uv run pytest -q` ·
`uv run ruff check .` · `uv run python scripts/derive_usage.py`.
