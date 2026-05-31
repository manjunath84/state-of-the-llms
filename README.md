# State of the LLMs

A vibe-coded, CSV-backed **Streamlit** data app — a *model-selection data story* for
builders. Gen Academy "Mastering Agentic AI Bootcamp", Week 1 project.

Given a task type, budget, and efficiency preference, it recommends a frontier model
and **shows its work** (price-vs-performance, the filtered rows, the math). It closes
on a real, personal proof: at published API list prices, what the tokens that built
*this very app* would cost.

> **The three beats**
> 1. **Price collapse** — a price-vs-MMLU-Pro scatter (bubble = context window),
>    filterable by lab, with deterministic "ask the data" chips narrated by an open LLM.
> 2. **Pick a model** — task + budget + efficiency → a recommended model and the
>    scored candidate rows behind it.
> 3. **Equivalent API cost** — the equivalent API list-price cost to build this app,
>    by model. Token counts are real; the dollar figure is notional (see *Provenance*).

## Run it

```bash
uv sync
uv run streamlit run app.py
```

Quality gates:

```bash
uv run ruff check .
uv run pytest -q          # 33 tests
```

The app **renders fully with no API key** — narration falls back to the computed
headline (guardrail #6). To get live one-sentence takeaways from an open model,
create a `.env`:

```bash
# .env  (all optional; the app runs without any of these)
NARRATION_API_KEY=sk-or-...                      # your OpenRouter key (default endpoint)
# NARRATION_BASE_URL=https://openrouter.ai/api/v1  # or Groq / Together / Ollama / OpenAI
# NARRATION_MODEL=meta-llama/llama-3.1-8b-instruct # any model on that endpoint
```

Narration is provider-agnostic: it uses the `openai` SDK pointed at any
OpenAI-compatible `base_url`. The default is an **open-source** model via OpenRouter —
on-theme, since the app argues open models caught up.

## Refresh the cost data (offline)

```bash
uv run python scripts/derive_usage.py
```

This parses **only this Week-1 project's** Claude Code transcripts into a scrubbed,
aggregated `data/usage.csv` (raw `*.jsonl` is gitignored — guardrail #4). Re-run it
right before recording so the finale reflects the full build.

## Provenance & honesty

- **Token counts are real** — measured from the build's own transcripts.
- **The dollar figure is notional** — the author builds on a flat monthly Claude
  subscription, so there is no per-token bill. Beat 3 reports the *equivalent API
  cost at published list prices*, not actual spend.
- **Every model metric carries `source_url` + `last_verified`** (guardrail #2).
  > ⚠️ `data/models.csv` currently ships 3 placeholder rows; replace with ~18–20
  > verified frontier models before the demo.

## How this deliberately diverges from the Week-1 Solution Kit

Replicating the provided kit (a Stock Portfolio Analyzer) scores zero. Ours shares
zero content, charts, or domain:

| Solution Kit | This project |
|---|---|
| Upload + manual-entry transactions, infer CSV format | Ships curated `models.csv` + derived `usage.csv` — instant, no upload |
| Pie allocation + holdings table (cost basis / quantity / profit) | Price-vs-performance **scatter** + interactive **picker** + real-usage **finale** |
| 6-cell metric grid (XIRR, returns, proceeds…) | **One** headline metric (equivalent API cost) + a by-model bar |
| Portfolio-value trend line over time | No time-trend lead; finale leads with by-model + the recursive row |
| Free-text "AI Analyst" chatbot | Deterministic chips + a one-sentence **open-model** takeaway |
| Generic finance domain | Frontier-model selection + the real token cost of building this very app |

## Architecture

Pure core / thin view: all logic in `src/sotl/` (unit-tested, no `st.*`); Streamlit
only in `app.py`. Constitution in [`specs/`](specs/README.md); decisions in
[`docs/decisions/`](docs/decisions/). Design source of truth:
[`docs/superpowers/specs/2026-05-30-state-of-the-llms-design.md`](docs/superpowers/specs/2026-05-30-state-of-the-llms-design.md).

Stack: Python 3.12 · `uv` · Streamlit · pandas · Plotly · `openai` SDK · ruff +
pytest + GitHub Actions.
