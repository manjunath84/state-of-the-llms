# Tech stack & architecture

Python 3.12 · **uv** (packaging + venv) · **Streamlit** (view) · **pandas**
(logic) · **Plotly** (charts) · **openai** SDK pointed at any OpenAI-compatible
endpoint (default an open model via OpenRouter) · **ruff** + **pytest** +
GitHub Actions CI.

## Principle: pure core, thin view

All logic lives in `src/sotl/` and is UI-agnostic + unit-tested. `st.*` calls live
**only** in `app.py`. (Mirrors SSM's "library stays sync; orchestration at the
boundary.")

```
app.py                ← Streamlit ONLY: stepper, charts, wiring
src/sotl/
  config.py    # pydantic-settings: NARRATION_API_KEY + base_url + model id, data paths
  data.py      # load + validate models.csv / usage.csv → typed frames
  recommend.py # picker: (task, budget, prefer_efficient) → ranked models + the math
  usage.py     # cost rollups (total / by-model / by-task)
  chips.py     # deterministic chip queries (pure pandas), keyed by chip id
  narrate.py   # LLM takeaway via any OpenAI-compatible endpoint + disk-cache fallback
  trust.py     # provenance / freshness / measured-vs-claimed summary
  theme.py     # the GenAcademy cream/grid/electric-yellow CSS block
data/           # models.csv · pricing.csv · usage.csv (derived, scrubbed, committed)
scripts/derive_usage.py   # offline: ~/.claude transcripts → scrubbed data/usage.csv
tests/          # unit tests over the pure modules (fixtures, not live data)
```

`uv run streamlit run app.py` to run; `uv run pytest -q` for tests;
`uv run ruff check .` for lint.

## The 8 binding guardrails (review-blockers)

These are mirrored verbatim into `CLAUDE.md` / `AGENTS.md`.

1. **Pure core, thin view** — logic in `src/sotl/` is UI-agnostic + tested; `st.*`
   only in `app.py`.
2. **Every number is sourced** — no model metric without `source_url` +
   `last_verified`.
3. **The LLM never invents numbers** — `narrate` writes prose over computed inputs;
   introduces no figure not present in its input.
4. **No raw personal data in the repo** — `derive_usage.py` emits only aggregated,
   scrubbed `usage.csv`; raw JSONL / content / paths never committed; `.gitignore`
   guards.
5. **Config via pydantic-settings singleton** — never read `os.environ` directly.
6. **Demo-safe by default** — narration cached; app renders fully with no API key;
   pre-warm the cache before recording.
7. **Diverge from the Solution Kit** — no upload-first, no pie+metrics+table motif,
   no free-text chat.
8. **Audits require evidence** — run ruff + pytest and show output before claiming
   green.
