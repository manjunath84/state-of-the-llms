# Mission

Build a **vibe-coded, CSV-backed Streamlit data app** that turns a frontier-model
taxonomy into an **interactive model-selection tool**, and ends on a **real,
personal proof**: at published API list prices, what the tokens that built **this
Week-1 project alone** would cost.

One line: **"State of the LLMs — a model-selection data story."** Given a task
type, budget, and latency tolerance, it recommends a model and *shows its work*;
then it closes by analysing the author's own real Claude Code token usage **for
this Week-1 project alone** — *"at API list prices, this is what the tokens that
built this very app would cost."*

> The author builds on a flat monthly Claude subscription, so the dollar figure is
> a **notional list-price conversion, not actual spend** — only the token counts
> are real. Measured tokens vs. notional dollars is itself a Data-Trust point.

This is **Idea 1 (chassis) + Idea 3 (real-usage engine)** from the tie-breaker
verdict: Idea 1 wins on reuse + demo range; it wins bigger by absorbing Idea 3's
real-usage data rather than dismissing it.

## Audience

Gen Academy cohort: technical builders (often Java/Spring) new to AI. Builder
examples beat academic ones. Keep AI terms verbatim, defined on first use.

## In scope (v1)

- Curated CSV of ~18–20 frontier models with provenance columns.
- 3 screens in a guided story stepper: price-vs-performance scatter · model picker
  · real-usage finale.
- Deterministic question chips + a live one-sentence takeaway from an
  **open-source model** (default), via a configurable OpenAI-compatible endpoint
  (`base_url` + model id; Groq/OpenRouter/Together/Ollama/OpenAI). Cached.
  On-theme: the app argues open models caught up, so an open model narrates it.
- At least one **literal filter widget** on the scatter (multiselect by lab) — to
  satisfy the handout's step-3 "filters" explicitly.
- Data-Trust provenance (inline badges in MUST; full panel is SHOULD).
- The three graded deliverables: GitHub repo, ≤5-min video, Google Doc write-up.

## Out of scope (v1)

- CSV-upload-first flow, pie-chart + metrics-row + holdings-table motif, free-text
  AI chatbot — **all three are the Solution Kit's shape; replicating it scores
  zero.**
- Live JSONL parsing inside the app (done offline, once).
- Designing the UI in Claude Artifacts then porting to Streamlit (double build).
- Docker/S3/MinIO, mypy-strict, heavy multi-LLM provider abstraction, standalone
  context-window-timeline and open-vs-closed screens.
