# CLAUDE.md — working agreement for AI agents

**Start here:** read `specs/` (the constitution) before changing scope —
`specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`, and the feature
spec under `specs/2026-05-30-state-of-the-llms/`. The `specs/` dir is canonical;
there is no `PLAN.md` (ADRs in `docs/decisions/`).

## Commands
- Install / sync: `uv sync`
- Run app: `uv run streamlit run app.py`
- Tests: `uv run pytest -q`
- Lint: `uv run ruff check .`
- Refresh cost data (offline): `uv run python scripts/derive_usage.py`

## The 8 binding guardrails (review-blockers — mirrored from `specs/tech-stack.md`)
1. **Pure core, thin view** — logic in `src/sotl/` is UI-agnostic + tested; `st.*`
   only in `app.py`.
2. **Every number is sourced** — no model metric without `source_url` +
   `last_verified`.
3. **The LLM never invents numbers** — `narrate` writes prose over computed inputs;
   introduces no figure not present in its input.
4. **No raw personal data in the repo** — `derive_usage.py` emits only aggregated,
   scrubbed `usage.csv`; raw JSONL / content / paths never committed.
5. **Config via pydantic-settings singleton** — never read `os.environ` directly.
6. **Demo-safe by default** — narration cached; app renders fully with no API key.
7. **Diverge from the Solution Kit** — no upload-first, no pie+metrics+table motif,
   no free-text chat.
8. **Audits require evidence** — run ruff + pytest and show output before claiming
   green.

## Workflow
TDD: failing test first (`tests/`), then implement. `uv run pytest -q` and
`uv run ruff check .` must pass before every commit.
