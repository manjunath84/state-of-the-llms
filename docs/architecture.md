# Architecture — State of the LLMs

**Principle: pure core, thin view.** All logic lives in `src/sotl/` (UI-agnostic,
unit-tested, never imports Streamlit). `st.*` calls live *only* in `app.py`. Numbers are
computed in the core; the LLM only writes prose over already-computed values and can never
become a source of figures.

```mermaid
flowchart TB
    subgraph offline["Offline — run once, before the demo"]
        logs[("~/.claude transcripts<br/>*.jsonl · gitignored")]
        derive["scripts/derive_usage.py<br/>scrub · aggregate · price"]
        logs --> derive
    end

    subgraph data["Data — committed CSVs (data/)"]
        models[("models.csv<br/>17 models + provenance")]
        pricing[("pricing.csv<br/>per-model $/1M tokens")]
        usage[("usage.csv<br/>scrubbed token rollups")]
    end
    derive --> usage

    subgraph core["Pure core — src/sotl/ · no Streamlit · unit-tested"]
        cfg["config.py<br/>pydantic-settings"]
        load["data.py<br/>load + validate schema"]
        rec["recommend.py<br/>picker ranking"]
        use["usage.py<br/>cost rollups + split"]
        chip["chips.py<br/>3 deterministic queries"]
        front["frontier.py<br/>price–skill Pareto"]
        narr["narrate.py<br/>LLM takeaway + number gate"]
        trust["trust.py<br/>provenance summary"]
    end

    subgraph view["Thin view — app.py · Streamlit only"]
        b1["Beat 1 · See the landscape<br/>scatter + chips"]
        b2["Beat 2 · Pick a model<br/>recommendation + math"]
        b3["Beat 3 · Cost to build this app<br/>finale"]
    end

    llm{{"Open model<br/>via OpenRouter<br/>(OpenAI-compatible)"}}

    models --> load
    pricing --> load
    usage --> load
    cfg --> load
    cfg --> narr

    load --> rec
    load --> use
    load --> chip
    load --> front
    load --> trust

    chip --> narr
    narr <-->|"computed summary →<br/>← one gated sentence"| llm

    front --> b1
    chip --> b1
    narr --> b1
    rec --> b2
    use --> b3
    trust --> b3
```

## How to read it

- **Offline (top):** `derive_usage.py` parses this Week-1 project's Claude Code
  transcripts, scrubs them to aggregates (no message content or paths — guardrail #4),
  prices them, and writes `data/usage.csv`. Raw `*.jsonl` is gitignored and never read at
  runtime, which keeps the demo deterministic.
- **Data:** three committed CSVs. Every model metric carries a `source_url` +
  `last_verified` date (guardrail #2).
- **Pure core:** `data.py` is the only loader (validates schema, fails loud). The other
  modules are pure functions over typed DataFrames — `recommend` (picker), `usage` (cost
  rollups + the input/output/cache split), `chips` (the 3 "ask the data" queries),
  `frontier` (the price–skill Pareto line), `trust` (provenance), and `narrate`.
- **The narration gate:** `narrate.py` sends the *computed* result to an open model and
  asks for one sentence, then validates every number in the reply against the input —
  any figure not in the source data is rejected and the deterministic line is shown
  instead (guardrail #3). The app renders fully with no API key.
- **Thin view:** `app.py` wires the core into the three-beat Streamlit story. It holds no
  business logic — only layout, widgets, and chart rendering.

See [`docs/decisions/`](decisions/) for the ADRs behind these choices.
