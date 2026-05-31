# State of the LLMs — Requirements

## Goal
A vibe-coded, CSV-backed Streamlit data app: a model-selection data story for
builders. Given a task type, budget, and efficiency preference, recommend a
frontier model and **show the math**; close on a real, personal proof — at
published API list prices, what the tokens that built *this Week-1 app* would cost.

## Non-goals
- No CSV-upload-first flow, pie+metrics+holdings-table motif, or free-text chatbot
  (the Solution Kit's shape — scores zero).
- No live in-app JSONL parsing (offline, once).
- No Docker/S3, mypy-strict, or broad multi-provider SDK abstraction.

## Scenarios
1. **Price collapse (Beat 1):** user filters the scatter by lab; clicks a chip
   ("best coding per dollar"); sees a deterministic answer + a one-sentence
   open-model takeaway.
2. **Pick a model (Beat 2):** user sets task = coding, a budget slider, and an
   efficiency toggle; gets a recommended model + the scored candidate rows.
3. **Equivalent API cost (Beat 3):** user sees the equivalent API list-price cost
   to build this very app, a by-model bar, and the recursive closing line — token
   counts real, dollars notional.

## Constraints
- Deadline 2026-06-04, 11pm PT. Solo, ~5 days.
- Privacy: raw transcripts never committed; only aggregated/scrubbed `usage.csv`.
- Demo-safe: app renders fully with no API key (cache + fallback).
- Honest labelling: notional list-price cost, not actual spend (flat subscription).

## Reference calls (verbatim)
- **Narrator default:** `narration_base_url = "https://openrouter.ai/api/v1"`,
  `narration_model = "meta-llama/llama-3.1-8b-instruct"`, key from
  `NARRATION_API_KEY`. Open presets also offered:
  `meta-llama/llama-3.3-70b-instruct`, `qwen/qwen-2.5-7b-instruct`.
- **pricing.csv schema:** `model_id, price_in_per_mtok, price_out_per_mtok,
  cache_read_per_mtok, cache_write_per_mtok, source_url, last_verified`.
- **usage.csv schema:** `date, project, task_type, model, input_tokens,
  output_tokens, cache_creation_tokens, cache_read_tokens, est_cost_usd`.
- **models.csv schema:** `name, lab, release_date, params, context_window,
  price_in, price_out, mmlu_pro, swe_bench, arena_elo, is_open, source_url,
  last_verified, metric_type, confidence, metric_notes`.

## Output contracts
- `recommend(df, task, max_price_out, prefer_efficient) -> Recommendation(pick,
  score_col, reason_rows)`.
- `run_chip(chip_id, df) -> ChipResult(chip_id, headline, frame)`.
- `total_spend(df) -> float`; `by_model(df) -> DataFrame[model, est_cost_usd]`.
- `takeaway(chip_id, summary, settings, model=None, client=None) -> str`.
- `trust_summary(df) -> {counts, oldest_verified, missing_swe_bench}`.

## Dependencies
`src/sotl/{config,data,recommend,usage,chips,narrate,trust,theme}.py`;
`data/{models,pricing,usage}.csv`; `scripts/derive_usage.py`; `openai`, `pandas`,
`plotly`, `streamlit`, `pydantic-settings`.
