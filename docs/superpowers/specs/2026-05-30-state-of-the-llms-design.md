# Design — State of the LLMs (Week 1 Project)

**Date:** 2026-05-30 · **Status:** draft (awaiting author review) · **Deadline:** 2026-06-04, 11pm PT
**Author:** Manjunath · **Process:** SDD constitution adapted from SSM-PDFTool / SSM-Transcriber; goal from the Week 1 handout.

> This is the design source of truth. The `specs/` constitution files (mission/tech-stack/roadmap) and the per-feature `requirements.md`/`plan.md` are generated from this doc during the implementation phase. Per SSM-PDFTool **ADR 0002**, `specs/` is canonical — there is no `docs/PLAN.md`.

---

## 1. Mission (goal — from the handout, not from SSM)

Build a **vibe-coded, CSV-backed Streamlit data app** that turns the Lesson 7 frontier-model taxonomy into an **interactive model-selection tool**, and ends on a **real, personal proof**: at published API list prices, what the tokens that built **this Week-1 project alone** would cost.

One line: **"State of the LLMs — a model-selection data story."** Given a task type, budget, and latency tolerance, it recommends a model and *shows its work*; then it closes by analysing the author's own real Claude Code token usage **for this Week-1 project alone** — *"at API list prices, this is what the tokens that built this very app would cost."* (The author builds on a flat monthly subscription, so the dollar figure is a **notional list-price conversion, not actual spend** — only the token counts are real.)

This is **Idea 1 (chassis) + Idea 3 (engine)** from the tie-breaker verdict (`../../../../claude-code-tiebreaker.md`). Idea 1 wins on Lesson-7 reuse (consistency + initiative — named Builder-of-the-Week criteria) and demo range; it wins *bigger* by absorbing Idea 3's real-usage data instead of dismissing it.

### Audience
GenAcademy cohort: technical builders (often Java/Spring) new to AI. Builder examples beat academic ones. Keep AI terms verbatim, defined on first use.

### In scope (v1)
- Curated CSV of ~18–20 frontier models with provenance columns.
- 3 screens in a guided story stepper: price-vs-performance scatter · model picker · real-usage finale.
- Deterministic question chips + a live one-sentence takeaway from an **open-source model** (default), via a configurable OpenAI-compatible endpoint (`base_url` + model id; e.g. Groq/OpenRouter/Together/Ollama). Selectable among open narrators; any OpenAI-compatible endpoint (incl. OpenAI) works by overriding `base_url`. Cached. On-theme: the app argues open models caught up, so an open model narrates it.
- At least one **literal filter widget** on the scatter (multiselect by lab / open-vs-closed) — to satisfy the handout's step-3 "filters" explicitly.
- Data-Trust provenance (inline badges in MUST; full panel is SHOULD).
- GenAcademy cream/grid/electric-yellow theme via CSS injection.
- The three graded deliverables: GitHub repo, ≤5-min video, Google Doc write-up — meeting the handout-specific capture rules in §11.

### Out of scope (v1)
- CSV-upload-first flow, pie-chart + metrics-row + holdings-table motif, free-text AI chatbot — **all three are the Solution Kit's shape; replicating it scores zero** (see §7).
- Live JSONL parsing inside the app (done offline, once).
- Designing the UI in Claude Artifacts then porting to Streamlit (double build — cut).
- Docker/S3/MinIO, mypy-strict, multi-LLM provider abstraction, standalone context-window-timeline and open-vs-closed screens (demoted to scatter annotations).

---

## 2. Decisions locked during brainstorming

| # | Decision | Rationale |
|---|---|---|
| D1 | **Idea-1 chassis + Idea-3 real-usage finale** (full 3rd screen + recursive close) | Differentiator; resolves the verdict's contradiction by grounding the router in real data. |
| D2 | **App shell = guided story stepper (3 beats)** | Serves the 5-min demo arc; reads editorial, not like the kit's static Tab1–4. |
| D3 | **LLM = deterministic chips compute results; an open-source narrator writes the one-sentence takeaway; disk-cache fallback** | Real live-LLM moment, demo-safe; a free-text chatbot = the kit's Tab 4 (zero-score risk) + on-camera break risk. Default narrator is an **open model** via a configurable OpenAI-compatible endpoint (`base_url` + model id; Groq/OpenRouter/Together/Ollama); any OpenAI-compatible endpoint (incl. OpenAI) works by overriding `base_url`. On-theme: the app argues open models caught up, so an open model narrates it. |
| D4 | **Adopt SSM SDD constitution + tooling** (uv, ruff, pytest, thin CI, `src/` pure-logic + thin Streamlit view); **goal from handout** | Professional repo = technical-thinking/initiative rubric points + write-up fuel. Skip SSM's product-specific Docker/S3. |
| D5 | **Real usage derived offline → committed `usage.csv`**; app never reads raw JSONL | De-risks the parser, protects privacy, keeps the demo deterministic. |
| D6 | **Scope locked MUST/SHOULD/CUT** with a hard app-freeze on Day 4 | The graded artifacts are the repo/video/doc, not the app; reserve Day 5. |

---

## 3. Architecture

**Principle: pure core, thin view.** All logic lives in `src/sotl/` and is UI-agnostic + unit-tested. `st.*` calls live *only* in `app.py`. (Mirrors SSM's "library stays sync; orchestration at the boundary.")

```
state-of-the-llms/                  ← the GitHub repo (default name; confirm at review)
├── app.py                          ← Streamlit ONLY: stepper, charts, wiring
├── src/sotl/
│   ├── __init__.py
│   ├── config.py     # pydantic-settings: NARRATION_API_KEY + narration base_url + model id (OpenAI-compatible; default open), data paths
│   ├── data.py       # load + validate models.csv / usage.csv → typed frames; fail loud on schema drift
│   ├── recommend.py  # picker: (task, budget, latency) → ranked models + the scoring used
│   ├── usage.py      # cost derivation, by-model/by-task rollups, savings, cache-ROI
│   ├── chips.py      # the deterministic chip queries (pure pandas), keyed by chip id
│   ├── narrate.py    # LLM takeaway via any OpenAI-compatible endpoint (default open model): prompt + call + disk-cache fallback
│   └── trust.py      # provenance / freshness / measured-vs-claimed summarization
├── data/
│   ├── models.csv    # ~18–20 models + provenance columns
│   ├── pricing.csv   # per-model $/M input & output (for cost derivation)
│   └── usage.csv     # derived, scrubbed personal usage (committed)
├── scripts/
│   └── derive_usage.py   # one-time: ~/.claude/projects/**/*.jsonl → data/usage.csv
├── tests/            # unit tests for the pure modules (fixtures, not live data)
├── specs/            # SDD constitution (see §8) — canonical, no PLAN.md
├── docs/
│   ├── superpowers/specs/2026-05-30-state-of-the-llms-design.md   # this doc
│   └── decisions/    # ADRs 0001–0003 (see §8)
├── .github/workflows/ci.yml   # uv sync → ruff → pytest
├── pyproject.toml    # uv; ruff (E/F/I/UP/B, line 100); pytest (pythonpath=src)
├── .gitignore        # + .cache/, .env, raw-log guards
├── CLAUDE.md         # context → points at specs/, mirrors the 8 guardrails
├── AGENTS.md
└── README.md
```

Packaging: hatchling builds `src/sotl`, so `uv sync` makes `sotl` importable from `app.py`. Run: `uv run streamlit run app.py`.

### Module responsibilities (the isolation contract)
- **config.py** — one `Settings` object (pydantic-settings). Nothing else reads `os.environ`. Holds `narration_api_key` (env `NARRATION_API_KEY` — your OpenRouter key for the default endpoint), `narration_base_url` (an OpenAI-compatible endpoint; default OpenRouter `https://openrouter.ai/api/v1`), the default open `narration_model` id, and `data/` paths. Provider-agnostic: pointing `narration_base_url` at Groq / Together / Ollama / OpenAI just works.
- **data.py** — the only loader. Validates schema on load; raises with a clear message if a required/provenance column is missing. Returns typed DataFrames. Consumers never read CSVs directly.
- **recommend.py** — `recommend(df, task, max_price_out, prefer_efficient) -> Recommendation` (latency tolerance is approximated by `prefer_efficient`, which ranks by score-per-dollar; `models.csv` has no latency column — see ADR 0001). Pure ranking over the model frame on the Lesson-7 axes (closed/open, standard/reasoning, frontier/efficient). Returns the pick **and** the filtered/scored rows so the UI can "show the math."
- **usage.py** — `total_spend`, `by_model`, `by_task`, `counterfactual_savings` (SHOULD), `cache_roi` (SHOULD). Operates on `usage.csv` already scoped to **this Week-1 project** (so no per-project filtering in the app). Cost = tokens × published list pricing; never stored, always derived → that derivation *is* "show the math." **Notional, not actual spend:** the author is on a flat monthly subscription, so this is the *equivalent API list-price cost* of real token usage (measured tokens vs. notional dollars — a Data-Trust point).
- **chips.py** — a registry of ~3 (MUST) named queries, each `(df) -> ChipResult{frame, headline_number}`. Deterministic pandas. No LLM here.
- **narrate.py** — `takeaway(chip_id, summary, settings, model=None, client=None) -> str`. Builds a constrained prompt ("here is the computed result; write ONE sentence; introduce no number not present above"), calls the selected `model` through an OpenAI-compatible client built from `settings.narration_base_url` + `settings.narration_api_key`, caches by `(chip_id, model, hash(summary))` to `.cache/narration.json`. On missing key/API error → return cached or a templated fallback. Provider-agnostic — no vendor SDK beyond `openai`. **The app renders fully with no API key.**
- **trust.py** — summarizes `models.csv` provenance into freshness/measured-vs-claimed/missing badges.

### Data flow
1. **Offline (once; re-run before demo):** `derive_usage.py` walks **only this Week-1 project's** logs (dirs matching `*Week1-GenAIBuildingBlocks*`, not the whole GenAcademy folder), pulls each assistant message's `usage` (`input/output/cache_creation/cache_read`) + `model` + timestamp + `cwd`→project/task tag, joins `pricing.csv`, computes the equivalent list-price cost, **scrubs** (no message content, no absolute paths beyond a project label), aggregates, writes `data/usage.csv`. Committed.
2. **Runtime:** `app.py` → `data.load()` → render stepper:
   - **Beat 1 — Price collapse (scatter):** `data` → scatter (price_in vs a benchmark, size = context, color = open/closed); chips compute filtered views; `narrate` adds the takeaway.
   - **Beat 2 — Pick a model:** controls → `recommend()` → pick card + "show the math" (scored rows) + `narrate` takeaway.
   - **Beat 3 — Equivalent API cost (finale):** `usage` rollups over **this Week-1 project's logs only** → equivalent API list-price cost + by-model; (SHOULD) savings + cache-ROI; `trust` badges noting **measured tokens (real) vs. notional list-price dollars**; `narrate` closing takeaway. The whole screen **is** the recursive close — every token that built the app you're watching. Headline metric labelled *"Equivalent API cost to build this app at published list prices"* with a one-line note: built on a flat $X/mo plan; the same token usage would cost ~$Y at API rates.

---

## 4. Data model

### models.csv (~18–20 rows)
`name, lab, release_date, params, context_window, price_in, price_out, mmlu_pro, swe_bench, arena_elo` + **provenance:** `source_url, last_verified, metric_type` (measured | reported_by_lab | third_party | unknown), `confidence`, `metric_notes`.
Source from Artificial Analysis and llm-stats.com; every number gets `source_url` + `last_verified` (the "Reference calls verbatim" discipline, §8).

### pricing.csv
`model_id, price_in_per_mtok, price_out_per_mtok, cache_read_per_mtok, cache_write_per_mtok, source_url, last_verified` — drives offline cost derivation; cache columns enable the cache-ROI view.

### usage.csv (derived, scrubbed, committed)
`date, project, task_type, model, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, est_cost_usd` — aggregated; no raw content, no absolute paths.

---

## 5. Scope — MUST / SHOULD / CUT (locked)

### ✅ MUST (the spine; no demo / no submission without these)
- `models.csv` ~18–20 rows + provenance columns
- Beat 1 scatter · Beat 2 model picker (+ show-the-math) · Beat 3 real-usage finale (+ recursive close)
- Guided story stepper shell (B) via `st.tabs`/radio + progress bar (no custom JS)
- 3 chips + open-model takeaway (configurable OpenAI-compatible endpoint) + disk cache
- Theme CSS (config.toml + one CSS block) — "on-brand enough"
- Light SDD scaffold: mission/tech-stack/roadmap.md, one requirements.md, CLAUDE.md, pyproject (uv), .gitignore, ~4 unit tests, basic CI
- **GitHub repo + ≤5-min video + Google Doc** (graded — non-negotiable)

### 🟡 SHOULD (only if ahead at the Day-4 freeze)
Full Data-Trust panel · counterfactual savings ("if you'd routed 85%…") · cache-ROI view · 4th/5th chips · deploy to Streamlit Community Cloud

### ✂️ CUT NOW (YAGNI)
Claude-Artifacts-then-port double build · live in-app JSONL parsing · standalone timeline/open-vs-closed screens · free-text chatbot · mypy-strict · Docker/S3 · *heavy* multi-provider abstraction (OpenAI + OpenRouter share the OpenAI SDK, so that pair is **IN** and cheap; a broader Anthropic-SDK layer stays cut) · separate "Story Mode" narration engine (the stepper *is* story mode)

### Schedule (5 sessions, hard app-freeze D4)
- **D1** walking skeleton: theme + `models.csv` + scatter + stepper, running end-to-end
- **D2** model picker + show-the-math
- **D3** `derive_usage.py` + finale + recursive close
- **D4** 3 chips + open-model takeaway + cache; **freeze tonight**
- **D5** video + Google Doc + repo polish + submit

**Risk caps:** (1) log parser time-boxed to ~1–2 hrs — if it overruns, ship the finale on a hand-compiled ~15-row real sample and move on. (2) Always keep a demoable skeleton; layer features on top.

---

## 6. Binding guardrails (review-blockers; mirror into CLAUDE.md)
1. **Pure core, thin view** — logic in `src/sotl/` is UI-agnostic + tested; `st.*` only in `app.py`.
2. **Every number is sourced** — no model metric without `source_url` + `last_verified`.
3. **The LLM never invents numbers** — `narrate` writes prose over computed inputs; introduces no figure not present in its input.
4. **No raw personal data in the repo** — `derive_usage.py` emits only aggregated, scrubbed `usage.csv`; raw JSONL/content/paths never committed; `.gitignore` guards.
5. **Config via pydantic-settings singleton** — never read `os.environ` directly.
6. **Demo-safe by default** — narration cached; app renders fully with no API key; pre-warm cache before recording.
7. **Diverge from the Solution Kit** — no upload-first, no pie+metrics+table motif, no free-text chat (§7).
8. **Audits require evidence** — run ruff + pytest and show output before claiming green.

---

## 7. How we deliberately diverge from the Solution Kit

The handout: *replicating the provided solution kit scores zero.* The kit is a **Stock Portfolio Analyzer**. The actual session build prompts (saved here as the reference for what we deliberately do **not** build) were:

> **P1.** "Build a simple stock market portfolio analyzer… three tabs. Tab 1: upload a CSV with my stock-market transaction history **and** manually enter transactions; infer the format from a sample CSV."
> **P2.** "Tab 2: a snapshot view of my consolidated portfolio — a **pie chart** for portfolio allocation and a stock-wise breakdown of current holdings (current quantity, **average cost basis**, current prices, profits)."
> **P3.** "Tab 3: historical performance — **metric cards** (total lifetime investment, total proceeds from sales, current portfolio value, total returns, **XIRR**) and a **trend line** for portfolio value over time."
> (P4 from the wireframe: a free-text **"AI Analyst" chatbot**.)

| Kit (from the prompts above) | Ours |
|---|---|
| Upload + manual-entry transactions, infer CSV format (P1) | Ships curated `models.csv` + derived `usage.csv` — instant demo, no upload |
| Pie allocation + holdings table with cost-basis/quantity/profit (P2) | Price-vs-performance **scatter** + interactive **picker** + real-usage **finale** |
| 6-cell metric grid (XIRR, returns, proceeds…) (P3) | **One** headline metric (equivalent API cost at list prices) + a by-model bar — not a metric grid |
| Portfolio-value **trend line over time** (P3) | We do **not** lead with a time-trend; finale leads with by-model + the recursive row |
| Free-text "AI Analyst" chatbot (P4) | Deterministic chips + one-sentence **open-model** takeaway (D3) |
| Generic finance domain | Frontier-model selection + the real token cost of building this very Week-1 app (equivalent API list prices) |

**On the 3-tab overlap:** the kit uses 3 tabs and so do we (a generic Streamlit pattern). The zero-score rule targets replicating the *solution*, not the tab count — and our three sections share **zero** content, charts, metrics, or domain with theirs (landscape → pick → personal cost vs. input → snapshot → historical). We frame ours as a guided **story stepper**, not a portfolio tool. This is defensible; the prompt-level divergence table above is the evidence.

This table goes in the Google Doc verbatim — it's both the zero-score safeguard and a strong "initiative" talking point. A **side-by-side of the session prompts (P1–P4) vs. my own prompts** makes the divergence undeniable.

---

## 8. SDD constitution to scaffold (post-approval)

Per SSM, create under the new repo (these are created during implementation, not now):
- `specs/README.md` (SDD intro), `specs/mission.md` (§1), `specs/tech-stack.md` (§3 layers + §6 guardrails), `specs/roadmap.md` (§5 schedule as phases), `specs/REQUIREMENTS_TEMPLATE.md`, and `specs/2026-05-30-state-of-the-llms/{requirements,plan,validation}.md`.
- ADRs in `docs/decisions/` (Problem → Solution → Impact → What I Learned):
  - **0001** — Streamlit chassis + pure-logic core (why thin view).
  - **0002** — Real-usage data from Claude Code JSONL, derived offline (privacy + de-risk).
  - **0003** — Deterministic chips, not a chatbot (kit divergence + demo safety).
- `CLAUDE.md` / `AGENTS.md` pointing at `specs/` and mirroring the 8 guardrails.

---

## 9. Testing
Unit tests over the pure modules with small CSV fixtures (not live logs):
- `recommend` — within budget returns the expected model; `prefer_efficient` ranks by score-per-dollar.
- `usage` — total spend + by-model rollups on a fixture.
- `chips` — each chip returns the expected rows/headline on a fixture.
- `trust` — provenance summary flags missing/measured/claimed correctly.
- `narrate` — prompt construction contains the computed result; cache-fallback path returns cached text when the API is unavailable (mock the client).
CI: `uv sync --frozen` → `ruff check .` → `pytest -q`.

---

## 10. Resolved defaults
- **Repo/folder name** `state-of-the-llms`, **package** `sotl`. ✓
- **Narrator** — default an **open-source model via OpenRouter** (OpenAI-compatible): `narration_base_url` = `https://openrouter.ai/api/v1`, `narration_model` = `meta-llama/llama-3.1-8b-instruct`, key from `NARRATION_API_KEY`. Selectable among open presets (e.g. `meta-llama/llama-3.1-8b-instruct`, `meta-llama/llama-3.3-70b-instruct`, `qwen/qwen-2.5-7b-instruct`). Any OpenAI-compatible endpoint (Groq / Together / Ollama / OpenAI) works by overriding base_url + model. Confirm exact ids at scaffold (Reference-calls-verbatim rule). ✓
- **Charting lib** `plotly` — interactive hover for the scatter (size = context, color = open/closed), themeable to the GenAcademy palette. ✓
- **Deploy** local-first (the graded artifact is the video). Streamlit Community Cloud is a SHOULD/stretch, attempted only after the Day-4 freeze. ✓

---

## 11. Handout deliverable-capture requirements

This is Path B. The handout asks for specifics beyond "ship the app" — capture them *during* the build, not at the end:

1. **Process screenshots + prompt log (graded).** The handout asks for *"screenshots of how you went about the vibe coding"* and *"prompts you used."* Our build runs through AI agents (this brainstorming session → subagent-driven dev, optionally Codex CLI). Screenshot the agent sessions and save the prompts **as we go** into `docs/learn/vibe-coding-log.md`. This *is* the vibe-coding story — a richer one than ad-hoc prompting — but it's unreconstructable after the fact.
2. **Path-B Google Doc must include:** a **problem statement** (spec §1) and a **step-by-step build breakdown** (this plan's phases/ADRs), *plus* the standard overview, datasets (+ provenance), prompts, iterations, and learnings (the ADRs' "What I Learned").
3. **Video (≤5 min) must explicitly cover "how you used AI coding tools"** — reserve ~30s for the AI-collaboration workflow, not only the 3-beat app walkthrough.
4. **Frame the rigor as initiative — and as the taught method.** The handout's vibe is rapid beginner prototyping; our SDD/TDD/CI is heavier. But the instructor's own demo workflow prompt was: *"first brainstorm with me about your plan… give me the file structure and the architecture… do not write any code until I give you the go ahead."* That is exactly this project's process (brainstorm → spec §3 file structure + architecture → wait for go). So the write-up/video should frame our discipline as **the instructor's recommended workflow, executed thoroughly** — not as ignoring the assignment. This brainstorming session is the evidence; cite it.
