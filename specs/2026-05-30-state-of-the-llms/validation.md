# State of the LLMs — Validation

Evidence that the build meets its requirements (guardrail #8: audits require
evidence). Refresh this immediately before submission.

## Automated checks — 2026-05-31

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q
...............................                                           [100%]
31 passed
```

Coverage by module (unit tests over the pure core, fixtures not live data):
`config`, `data`, `recommend`, `usage`, `chips` (incl. empty-after-coerce edge
cases + is_open beats the notes heuristic), `narrate` (cache hit / no-key
fallback / API-error fallback / per-model cache key), `trust`, and
`validate_models` (placeholder / provenance / is_open / sparse-scatter checks).

## App smoke (headless)

`uv run streamlit run app.py --server.headless true` → HTTP 200, all three beats
render, sidebar narrator + Data-Trust panel render, no traceback.

## Model data check — 2026-05-31

```
$ uv run python scripts/validate_models.py
✓ data/models.csv looks demo-ready
rows: 12  (open: 3, closed: 9)
price_out $/1M out: 0.28 – 75.00 (11 numeric)
mmlu_pro:           86.2 – 89.6 (4 numeric)
swe_bench:          73.3 – 88.6 (11 numeric)
```

Refreshed 2026-05-31 to current models from live vendor pricing pages (Anthropic,
OpenAI, Google, DeepSeek) + llm-stats.com SWE-bench. Scatter axis = SWE-bench
Verified (dense + fully sourced); unsourceable cells left `unknown` per guardrail #2.

## Guardrail audit

| # | Guardrail | Status |
|---|---|---|
| 1 | Pure core / thin view (`st.*` only in `app.py`) | ✅ verified |
| 2 | Every number sourced (`source_url` + `last_verified`) | ✅ 12 current models, each cell sourced or `unknown` (never guessed); `validate_models.py` exits 0. ⚠️ 2 DeepSeek rows `confidence,low` (reasoning-tier benchmark attribution — see `metric_notes`) |
| 3 | LLM never invents numbers (narrates computed inputs only) | ✅ by construction (chips compute; narrate prompts "introduce no number") |
| 4 | No raw personal data in repo (scrubbed `usage.csv` only) | ✅ raw `*.jsonl` gitignored; `usage.csv` columns aggregated, basenames only |
| 5 | Config via pydantic-settings singleton | ✅ `config.py` |
| 6 | Demo-safe (renders with no API key; cache + fallback) | ✅ `narrate.py` falls back on no-key AND API error |
| 7 | Diverges from the Solution Kit | ✅ scatter/picker/cost vs. upload/pie/table; chips not chatbot |

Note: open/closed classification uses an explicit, sourced `is_open` column in
`models.csv` (not a notes heuristic) — a closed model whose notes mention
"open-source" still classifies as closed.
| 8 | Audits require evidence | ✅ this file |

## Open items before submission
- Replace 3 placeholder rows in `data/models.csv` with ~18–20 verified models.
  Gate it with `uv run python scripts/validate_models.py` (must exit 0 — it
  currently fails on the seed rows by design).
- Re-run `scripts/derive_usage.py` right before recording so the cost reflects the
  full build.
- Pre-warm `.cache/narration.json` with a real `NARRATION_API_KEY` (clear the file
  first so no-key fallback entries don't shadow real narration).
