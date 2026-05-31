# State of the LLMs — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A vibe-coded, CSV-backed Streamlit data app that turns the Lesson 7 frontier-model taxonomy into an interactive model-selection tool, ending on a real, personal proof — the equivalent API list-price cost of the tokens that built **this Week-1 project alone** (not the whole GenAcademy folder; the author is on a flat subscription, so the dollar figure is notional, not actual spend — only the token counts are real).

**Architecture:** Pure-core / thin-view. All logic lives in `src/sotl/` (UI-agnostic, unit-tested); `st.*` calls live only in `app.py`. A guided 3-beat story stepper (scatter → model picker → real-usage finale). Deterministic pandas computes every number; an open-source model (default, via a configurable OpenAI-compatible endpoint) only writes one-sentence takeaways (cached to disk for demo safety). Personal usage is derived **offline once** into a scrubbed `data/usage.csv` (token counts real; dollar figure is a notional API list-price equivalent).

**Tech Stack:** Python 3.12, `uv`, Streamlit, pandas, Plotly, `openai`, `pydantic-settings`; ruff + pytest + GitHub Actions CI.

**Source of truth:** `docs/superpowers/specs/2026-05-30-state-of-the-llms-design.md`. Follow its MUST/SHOULD/CUT scope, the 8 guardrails, and the module contracts.

**Repo root:** `state-of-the-llms/` (inside `Week1-GenAIBuildingBlocks/`). All paths below are relative to the repo root unless absolute.

**Guardrails (review-blockers, from spec §6):**
1. Pure core, thin view — `st.*` only in `app.py`.
2. Every model number has `source_url` + `last_verified`.
3. The LLM never invents numbers — `narrate` writes prose over computed inputs only.
4. No raw personal data in the repo — `usage.csv` is aggregated + scrubbed.
5. Config via `pydantic-settings`; never read `os.environ` directly.
6. Demo-safe — app renders fully with no API key (cached/fallback narration).
7. Diverge from the Solution Kit — no upload-first, no pie+metrics+table, no free-text chat.
8. Audits require evidence — run ruff + pytest and show output.

**Commit cadence:** every task ends in a commit. Conventional Commit messages.

**Vibe-coding capture cadence (handout deliverable — do this throughout):** as each task is built by an AI agent, **screenshot the agent session and paste the prompt(s)** into `docs/learn/vibe-coding-log.md`. The handout grades *"screenshots of how you went about the vibe coding"* + *"prompts you used"*; they cannot be reconstructed after the fact. This log feeds the Google Doc (Task 18).

---

## Phase 0 — Bootstrap (Day 1)

### Task 1: Initialize repo + packaging

**Files:**
- Create: `state-of-the-llms/pyproject.toml`
- Create: `state-of-the-llms/.gitignore`
- Create: `state-of-the-llms/src/sotl/__init__.py`
- Create: `state-of-the-llms/README.md`

- [ ] **Step 1: Create the project directory and git repo**

Run:
```bash
cd /Users/manjunathans/projects/GenAcademy/Week1-GenAIBuildingBlocks/state-of-the-llms
git init
```

- [ ] **Step 2: Write `pyproject.toml`**

```toml
[project]
name = "sotl"
version = "0.1.0"
description = "State of the LLMs — a model-selection data story (Gen Academy Week 1)."
requires-python = ">=3.12,<3.13"
dependencies = [
    "streamlit>=1.40",
    "pandas>=2.2",
    "plotly>=5.24",
    "openai>=1.55",
    "pydantic-settings>=2.6",
]

[dependency-groups]
dev = [
    "ruff>=0.8",
    "pytest>=8.3",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/sotl"]

[tool.ruff]
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 3: Write `.gitignore`**

```gitignore
.DS_Store
__pycache__/
*.pyc
.venv/
.env
*.egg-info/
.ruff_cache/
.pytest_cache/
dist/
.cache/
# Guardrail #4: never commit raw personal logs
raw-logs/
*.jsonl
```

- [ ] **Step 4: Create the package marker and README stub**

`src/sotl/__init__.py`:
```python
"""State of the LLMs — model-selection data story."""
```

`README.md`:
```markdown
# State of the LLMs

A model-selection data story (Gen Academy Week 1). Pick a model by task + budget; see the math; then see the equivalent API list-price cost of the tokens that built it (notional — the author is on a flat subscription).

See `docs/superpowers/specs/2026-05-30-state-of-the-llms-design.md` for the design.

## Run
```bash
uv sync
uv run streamlit run app.py
```
```

- [ ] **Step 5: Sync and verify the toolchain**

Run: `uv sync`
Expected: resolves and installs; creates `.venv` and `uv.lock`.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: bootstrap uv project, packaging, gitignore"
```

---

### Task 2: CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - name: Sync
        run: uv sync --frozen
      - name: Ruff
        run: uv run ruff check .
      - name: Pytest
        run: uv run pytest -q
```

- [ ] **Step 2: Verify ruff runs clean locally**

Run: `uv run ruff check .`
Expected: `All checks passed!`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add ruff + pytest workflow"
```

---

### Task 3: `config.py` (pydantic-settings singleton — guardrail #5)

**Files:**
- Create: `src/sotl/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from pathlib import Path

from sotl.config import Settings


def test_defaults_and_derived_paths(monkeypatch):
    monkeypatch.delenv("NARRATION_API_KEY", raising=False)
    s = Settings(data_dir=Path("data"))
    assert s.narration_model == "meta-llama/llama-3.1-8b-instruct"
    assert s.narration_base_url == "https://openrouter.ai/api/v1"
    assert s.narration_api_key is None
    assert s.models_csv == Path("data/models.csv")
    assert s.pricing_csv == Path("data/pricing.csv")
    assert s.usage_csv == Path("data/usage.csv")


def test_narration_key_from_env(monkeypatch):
    monkeypatch.setenv("NARRATION_API_KEY", "or-test")
    s = Settings()
    assert s.narration_api_key == "or-test"


def test_base_url_and_model_overridable(monkeypatch):
    monkeypatch.delenv("NARRATION_API_KEY", raising=False)
    s = Settings(narration_base_url="http://localhost:11434/v1", narration_model="llama3")
    assert s.narration_base_url == "http://localhost:11434/v1"
    assert s.narration_model == "llama3"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sotl.config'`

- [ ] **Step 3: Implement `config.py`**

```python
# src/sotl/config.py
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # Narration via any OpenAI-compatible endpoint (default: an open model on
    # OpenRouter). Override base_url/model for Groq / Together / Ollama / OpenAI.
    narration_api_key: str | None = None  # env: NARRATION_API_KEY
    narration_base_url: str = "https://openrouter.ai/api/v1"  # env: NARRATION_BASE_URL
    narration_model: str = "meta-llama/llama-3.1-8b-instruct"  # env: NARRATION_MODEL
    data_dir: Path = Path("data")
    cache_path: Path = Path(".cache/narration.json")

    @property
    def models_csv(self) -> Path:
        return self.data_dir / "models.csv"

    @property
    def pricing_csv(self) -> Path:
        return self.data_dir / "pricing.csv"

    @property
    def usage_csv(self) -> Path:
        return self.data_dir / "usage.csv"


settings = Settings()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/config.py tests/test_config.py
git commit -m "feat: pydantic-settings config singleton"
```

---

## Phase 1 — Data layer (Day 1)

### Task 4: Seed `data/models.csv` and `data/pricing.csv`

**Files:**
- Create: `data/models.csv`
- Create: `data/pricing.csv`

> **Guardrail #2:** every value below must be copied from a real source (Artificial Analysis — https://artificialanalysis.ai/leaderboards/models — or llm-stats.com — https://llm-stats.com/) with `source_url` + `last_verified` filled per row. Do **not** invent numbers. The three rows below are the **exact schema + format template**; extend to **~18–20 rows** of current frontier + efficient models (mix of open and closed) before moving on. Replace the example values with verified ones and set `last_verified` to the date you pull them.

- [ ] **Step 1: Create `data/models.csv` with this exact header, then populate ~18–20 rows**

```csv
name,lab,release_date,params,context_window,price_in,price_out,mmlu_pro,swe_bench,arena_elo,source_url,last_verified,metric_type,confidence,metric_notes
GPT-4o,OpenAI,2024-05-13,unknown,128000,2.5,10,74.7,33.2,1285,https://artificialanalysis.ai/models/gpt-4o,2026-05-31,reported_by_lab,high,prices per 1M tokens
Claude 3.5 Sonnet,Anthropic,2024-10-22,unknown,200000,3,15,77.0,49.0,1268,https://artificialanalysis.ai/models/claude-35-sonnet,2026-05-31,reported_by_lab,high,swe-bench verified
Llama 3.1 70B,Meta,2024-07-23,70000000000,128000,0.3,0.3,66.4,unknown,1206,https://llm-stats.com/models/llama-3-1-70b,2026-05-31,third_party,medium,open weights
```

- [ ] **Step 2: Create `data/pricing.csv` (drives offline cost derivation; one row per model id you actually used to build, plus the models above)**

```csv
model_id,price_in_per_mtok,price_out_per_mtok,cache_read_per_mtok,cache_write_per_mtok,source_url,last_verified
claude-opus-4-7,15,75,1.5,18.75,https://www.anthropic.com/pricing,2026-05-31
claude-sonnet-4-6,3,15,0.3,3.75,https://www.anthropic.com/pricing,2026-05-31
gpt-4o-mini,0.15,0.6,0.075,0,https://openai.com/api/pricing,2026-05-31
```

> The `model_id` values in `pricing.csv` MUST match the `model` strings that appear in your Claude Code transcripts (e.g. `claude-opus-4-7`), because `derive_usage.py` (Task 10) joins on them. Verify by grepping a transcript: `grep -o '"model":"[^"]*"' ~/.claude/projects/*/*.jsonl | sort -u`.

- [ ] **Step 3: Commit**

```bash
git add data/models.csv data/pricing.csv
git commit -m "data: seed models.csv (provenance) and pricing.csv"
```

---

### Task 5: `data.py` — `load_models` (schema validation)

**Files:**
- Create: `src/sotl/data.py`
- Test: `tests/test_data.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_data.py
from pathlib import Path

import pandas as pd
import pytest

from sotl.data import MODEL_REQUIRED, load_models


def _write(tmp_path: Path, rows: list[dict]) -> Path:
    p = tmp_path / "models.csv"
    pd.DataFrame(rows).to_csv(p, index=False)
    return p


def test_load_models_ok(tmp_path):
    row = {c: "x" for c in MODEL_REQUIRED}
    row.update(name="GPT-4o", price_out=10, context_window=128000)
    df = load_models(_write(tmp_path, [row]))
    assert list(df["name"]) == ["GPT-4o"]


def test_load_models_missing_column_raises(tmp_path):
    bad = {"name": "GPT-4o"}  # missing provenance + metrics
    with pytest.raises(ValueError, match="missing columns"):
        load_models(_write(tmp_path, [bad]))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_data.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sotl.data'`

- [ ] **Step 3: Implement `load_models`**

```python
# src/sotl/data.py
from pathlib import Path

import pandas as pd

MODEL_REQUIRED = [
    "name", "lab", "release_date", "params", "context_window",
    "price_in", "price_out", "mmlu_pro", "swe_bench", "arena_elo",
    "source_url", "last_verified", "metric_type", "confidence", "metric_notes",
]


def load_models(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in MODEL_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"models.csv missing columns: {missing}")
    return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_data.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/data.py tests/test_data.py
git commit -m "feat: data.load_models with schema validation"
```

---

### Task 6: `data.py` — `load_usage`

**Files:**
- Modify: `src/sotl/data.py`
- Test: `tests/test_data.py` (add)

- [ ] **Step 1: Add the failing test**

```python
# append to tests/test_data.py
from sotl.data import USAGE_REQUIRED, load_usage


def test_load_usage_ok(tmp_path):
    row = {c: 0 for c in USAGE_REQUIRED}
    row.update(date="2026-05-20", project="GenAcademy", task_type="notes", model="claude-opus-4-7")
    p = tmp_path / "usage.csv"
    pd.DataFrame([row]).to_csv(p, index=False)
    df = load_usage(p)
    assert df.loc[0, "model"] == "claude-opus-4-7"


def test_load_usage_missing_column_raises(tmp_path):
    p = tmp_path / "usage.csv"
    pd.DataFrame([{"date": "2026-05-20"}]).to_csv(p, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        load_usage(p)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'USAGE_REQUIRED'`

- [ ] **Step 3: Implement `load_usage` (append to `data.py`)**

```python
# append to src/sotl/data.py
USAGE_REQUIRED = [
    "date", "project", "task_type", "model",
    "input_tokens", "output_tokens",
    "cache_creation_tokens", "cache_read_tokens", "est_cost_usd",
]


def load_usage(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in USAGE_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"usage.csv missing columns: {missing}")
    return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_data.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/data.py tests/test_data.py
git commit -m "feat: data.load_usage with schema validation"
```

---

## Phase 2 — Walking skeleton: theme + stepper + Beat 1 (Day 1)

### Task 7: `app.py` skeleton — theme CSS, stepper shell, Beat 1 scatter

**Files:**
- Create: `app.py`
- Create: `src/sotl/theme.py`

- [ ] **Step 1: Write the theme CSS injector (pure, no `st.*`)**

```python
# src/sotl/theme.py
THEME_CSS = """
<style>
:root{
  --paper:#FDFCEF; --ink:#0F1419; --accent:#EAFF00; --dark:#1E3A5F;
  --grid:rgba(232,228,208,.4);
}
.stApp{
  background-color:var(--paper);
  background-image:
    linear-gradient(var(--grid) 1px,transparent 1px),
    linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:40px 40px;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  color:var(--ink);
}
[data-testid="stMetric"], .stButton>button{
  border:2px solid var(--ink)!important;
  box-shadow:4px 4px 0 var(--ink)!important;
  background:var(--paper)!important; border-radius:4px;
}
h1,h2,h3{font-weight:800;letter-spacing:-.01em;}
mark,.hl{background:var(--accent);padding:0 .15em;}
</style>
"""
```

> Streamlit `data-testid` selectors drift across versions (spec note). After the first run, if a card isn't themed, inspect the element and adjust the selector — budget 15 min, no more.

- [ ] **Step 2: Write `app.py` (Streamlit ONLY — guardrail #1)**

```python
# app.py
import plotly.express as px
import streamlit as st

from sotl.config import settings
from sotl.data import load_models
from sotl.theme import THEME_CSS

st.set_page_config(page_title="State of the LLMs", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)


@st.cache_data
def _models():
    return load_models(settings.models_csv)


def beat_scatter(df):
    st.header("① The price collapse")
    st.caption("Frontier quality is getting cheaper fast. Bubble size = context window.")
    fig = px.scatter(
        df, x="price_out", y="mmlu_pro", size="context_window",
        color="lab", hover_name="name", log_x=True,
        labels={"price_out": "$ / 1M output tokens", "mmlu_pro": "MMLU-Pro"},
    )
    fig.update_layout(paper_bgcolor="#FDFCEF", plot_bgcolor="#FDFCEF", font_color="#0F1419")
    st.plotly_chart(fig, use_container_width=True)


def beat_picker(df):
    st.header("② Pick a model")
    st.info("Built in Task 9.")


def beat_finale(df):
    st.header("③ Equivalent API cost")
    st.info("Built in Task 12.")


def main():
    df = _models()
    st.title("State of the LLMs")
    st.caption("A model-selection data story · Gen Academy Week 1")
    tab1, tab2, tab3 = st.tabs(["① Price collapse", "② Pick a model", "③ Equivalent API cost"])
    with tab1:
        beat_scatter(df)
    with tab2:
        beat_picker(df)
    with tab3:
        beat_finale(df)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the app and verify end-to-end**

Run: `uv run streamlit run app.py`
Expected: cream/grid theme loads; tab ① shows a Plotly scatter from `models.csv`; tabs ②/③ show placeholders. Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add app.py src/sotl/theme.py
git commit -m "feat: streamlit skeleton — theme, stepper, Beat 1 scatter"
```

---

### Task 7B: Add a literal filter widget to the scatter (handout step 3 "filters")

**Files:**
- Modify: `app.py` (`beat_scatter`)

- [ ] **Step 1: Add a `lab` multiselect filter and apply it to the scatter**

```python
# app.py — replace beat_scatter
def beat_scatter(df):
    st.header("① The price collapse")
    st.caption("Frontier quality is getting cheaper fast. Bubble size = context window.")
    labs = sorted(df["lab"].dropna().unique().tolist())
    picked = st.multiselect("Filter by lab", labs, default=labs)
    view = df[df["lab"].isin(picked)] if picked else df
    fig = px.scatter(
        view, x="price_out", y="mmlu_pro", size="context_window",
        color="lab", hover_name="name", log_x=True,
        labels={"price_out": "$ / 1M output tokens", "mmlu_pro": "MMLU-Pro"},
    )
    fig.update_layout(paper_bgcolor="#FDFCEF", plot_bgcolor="#FDFCEF", font_color="#0F1419")
    st.plotly_chart(fig, use_container_width=True)
    # NOTE: Task 16 appends `_chip_rail(view)` here (operates on the filtered frame).
```

- [ ] **Step 2: Run and verify the filter**

Run: `uv run streamlit run app.py`
Expected: deselecting a lab removes its bubbles from the scatter live. Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: lab filter on Beat 1 scatter"
```

---

## Phase 3 — Beat 2: model picker (Day 2)

### Task 8: `recommend.py` — the picker logic

> **Spec mapping:** the spec's "task + budget + latency" becomes `task` (coding → `swe_bench`, else → `mmlu_pro`), `max_price_out` (budget), and `prefer_efficient` (latency proxy). When `prefer_efficient` is **on**, candidates are ranked by **score-per-dollar** (value); **off**, by raw score (price breaks ties). `models.csv` has no latency column, so we approximate; note this in ADR 0001.

**Files:**
- Create: `src/sotl/recommend.py`
- Test: `tests/test_recommend.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_recommend.py
import pandas as pd

from sotl.recommend import recommend


def _df():
    return pd.DataFrame([
        {"name": "Cheap", "price_out": 1.0, "swe_bench": 40, "mmlu_pro": 60, "params": "7000000000"},
        {"name": "Mid", "price_out": 5.0, "swe_bench": 50, "mmlu_pro": 70, "params": "70000000000"},
        {"name": "Frontier", "price_out": 20.0, "swe_bench": 55, "mmlu_pro": 80, "params": "unknown"},
    ])


def test_picks_best_coder_within_budget():
    rec = recommend(_df(), task="coding", max_price_out=10.0, prefer_efficient=False)
    assert rec.pick == "Mid"          # best swe_bench at price_out <= 10
    assert rec.score_col == "swe_bench"
    assert "Frontier" not in set(rec.reason_rows["name"])  # filtered out by budget


def test_prefer_efficient_ranks_by_value_per_dollar():
    # within budget: Cheap (40/$1 = 40) beats Mid (50/$5 = 10) on score-per-dollar
    rec = recommend(_df(), task="coding", max_price_out=10.0, prefer_efficient=True)
    assert rec.pick == "Cheap"


def test_budget_filters_everything_returns_none():
    rec = recommend(_df(), task="coding", max_price_out=0.5, prefer_efficient=False)
    assert rec.pick is None
    assert rec.reason_rows.empty
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_recommend.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sotl.recommend'`

- [ ] **Step 3: Implement `recommend.py`**

```python
# src/sotl/recommend.py
from dataclasses import dataclass

import pandas as pd


@dataclass
class Recommendation:
    pick: str | None
    score_col: str
    reason_rows: pd.DataFrame  # candidates within budget, best first


def recommend(
    df: pd.DataFrame, task: str, max_price_out: float, prefer_efficient: bool
) -> Recommendation:
    score_col = "swe_bench" if task == "coding" else "mmlu_pro"
    cand = df.copy()
    cand["price_out"] = pd.to_numeric(cand["price_out"], errors="coerce")
    cand[score_col] = pd.to_numeric(cand[score_col], errors="coerce")
    cand = cand[cand["price_out"] <= max_price_out].dropna(subset=[score_col, "price_out"])
    if cand.empty:
        return Recommendation(pick=None, score_col=score_col, reason_rows=cand)
    if prefer_efficient:
        # value: score per $ (clip price to avoid div-by-zero for free models)
        cand["_rank"] = cand[score_col] / cand["price_out"].clip(lower=0.01)
        rank_col = "_rank"
    else:
        rank_col = score_col
    cand = cand.sort_values([rank_col, "price_out"], ascending=[False, True]).reset_index(drop=True)
    return Recommendation(pick=str(cand.loc[0, "name"]), score_col=score_col, reason_rows=cand)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_recommend.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/recommend.py tests/test_recommend.py
git commit -m "feat: recommend.py model picker logic"
```

---

### Task 9: Wire Beat 2 into `app.py`

**Files:**
- Modify: `app.py` (`beat_picker`)

- [ ] **Step 1: Replace `beat_picker` with the real implementation**

```python
# app.py — replace beat_picker
from sotl.recommend import recommend


def beat_picker(df):
    st.header("② Pick a model")
    c1, c2, c3 = st.columns(3)
    task = c1.selectbox("Task", ["coding", "general / reasoning"])
    budget = c2.slider("Max $ / 1M output tokens", 0.5, 30.0, 10.0, 0.5)
    prefer_eff = c3.toggle("Prefer faster/cheaper on ties", value=True)
    rec = recommend(
        df,
        task="coding" if task == "coding" else "general",
        max_price_out=budget,
        prefer_efficient=prefer_eff,
    )
    if rec.pick is None:
        st.warning("No model fits that budget — raise the slider.")
        return
    st.success(f"**Pick: {rec.pick}** — best {rec.score_col} at ≤ ${budget:.1f}/1M out")
    with st.expander("Show the math", expanded=True):
        st.dataframe(
            rec.reason_rows[["name", "lab", "price_out", rec.score_col]],
            use_container_width=True, hide_index=True,
        )
```

- [ ] **Step 2: Run and verify**

Run: `uv run streamlit run app.py`
Expected: tab ② lets you choose task/budget; shows a pick + a "Show the math" table of the ranked candidates. Ctrl+C to stop.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: wire Beat 2 model picker into app"
```

---

## Phase 4 — Offline usage + Beat 3 finale (Day 3)

### Task 10: `scripts/derive_usage.py` — offline log → scrubbed `usage.csv` (guardrail #4)

**Files:**
- Create: `scripts/derive_usage.py`
- Generates: `data/usage.csv`

> **Time-box: ~1–2 hours (spec §5 risk cap).** If parsing overruns, hand-compile a ~15-row real `data/usage.csv` with the same header and move on.

- [ ] **Step 1: Write the script**

```python
# scripts/derive_usage.py
"""Offline: parse THIS Week-1 project's Claude Code transcripts into a scrubbed usage.csv.

Reads only the ~/.claude/projects dirs matching PROJECT_FILTER (this Week-1 project,
NOT the whole GenAcademy folder), extracts per-assistant-message token usage, joins
per-model list pricing, derives an equivalent API list-price cost, aggregates, and
writes data/usage.csv. NO message content or absolute paths are written (guardrail #4).
Re-run right before recording the demo so it captures the full build — including the
sessions that produced the app you're showing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PROJECTS = Path.home() / ".claude" / "projects"
# Scope to THIS Week-1 project ONLY: the Week1 folder and the state-of-the-llms
# subfolder both carry this substring in their ~/.claude/projects dir name.
# (We are NOT summing the whole GenAcademy folder.)
PROJECT_FILTER = "Week1-GenAIBuildingBlocks"
PRICING = Path("data/pricing.csv")
OUT = Path("data/usage.csv")


def iter_assistant_usages(root: Path):
    for jf in root.rglob("*.jsonl"):
        if PROJECT_FILTER not in str(jf):
            continue  # skip other projects — Week-1 scope only
        for line in jf.read_text(errors="ignore").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = rec.get("message") or {}
            usage = msg.get("usage")
            if not usage or msg.get("role") != "assistant":
                continue
            cwd = rec.get("cwd", "")
            project = Path(cwd).name or jf.parent.name  # scrub: basename only
            yield {
                "date": (rec.get("timestamp", "") or "")[:10],
                "project": project,
                "task_type": project,  # coarse; refine later if time
                "model": msg.get("model", "unknown"),
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
                "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
            }


def main() -> int:
    if not PROJECTS.exists():
        print(f"No transcripts at {PROJECTS}", file=sys.stderr)
        return 1
    rows = list(iter_assistant_usages(PROJECTS))
    if not rows:
        print("No assistant usage records found", file=sys.stderr)
        return 1
    df = pd.DataFrame(rows)
    pricing = pd.read_csv(PRICING).rename(columns={"model_id": "model"})
    df = df.merge(pricing, on="model", how="left")
    df["est_cost_usd"] = (
        df["input_tokens"] / 1e6 * df["price_in_per_mtok"].fillna(0)
        + df["output_tokens"] / 1e6 * df["price_out_per_mtok"].fillna(0)
        + df["cache_read_tokens"] / 1e6 * df["cache_read_per_mtok"].fillna(0)
        + df["cache_creation_tokens"] / 1e6 * df["cache_write_per_mtok"].fillna(0)
    )
    agg = (
        df.groupby(["date", "project", "task_type", "model"], as_index=False)[
            ["input_tokens", "output_tokens", "cache_creation_tokens",
             "cache_read_tokens", "est_cost_usd"]
        ].sum()
    )
    agg["est_cost_usd"] = agg["est_cost_usd"].round(4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(OUT, index=False)
    print(f"Wrote {len(agg)} rows → {OUT}; total ${agg['est_cost_usd'].sum():.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run it and spot-check**

Run: `uv run python scripts/derive_usage.py`
Expected: prints `Wrote N rows → data/usage.csv; total $X.XX`. Open `data/usage.csv`; hand-verify one row's `est_cost_usd` ≈ tokens × pricing. Confirm no file paths or message text leaked.

- [ ] **Step 3: Commit (the scrubbed CSV + the script)**

```bash
git add scripts/derive_usage.py data/usage.csv
git commit -m "feat: offline derive_usage.py → scrubbed usage.csv"
```

---

### Task 11: `usage.py` — rollups (total + by-model)

**Files:**
- Create: `src/sotl/usage.py`
- Test: `tests/test_usage.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_usage.py
import pandas as pd

from sotl.usage import by_model, total_spend


def _df():
    return pd.DataFrame([
        {"project": "GenAcademy", "model": "claude-opus-4-7",
         "input_tokens": 1_000_000, "output_tokens": 100_000,
         "cache_creation_tokens": 0, "cache_read_tokens": 0, "est_cost_usd": 22.5},
        {"project": "GenAcademy-Week1", "model": "claude-sonnet-4-6",
         "input_tokens": 500_000, "output_tokens": 50_000,
         "cache_creation_tokens": 0, "cache_read_tokens": 0, "est_cost_usd": 2.25},
    ])


def test_total_spend():
    assert total_spend(_df()) == 24.75


def test_by_model_sorted_desc():
    out = by_model(_df())
    assert list(out["model"]) == ["claude-opus-4-7", "claude-sonnet-4-6"]
    assert out.iloc[0]["est_cost_usd"] == 22.5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_usage.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sotl.usage'`

- [ ] **Step 3: Implement `usage.py`**

```python
# src/sotl/usage.py
import pandas as pd


def total_spend(df: pd.DataFrame) -> float:
    return round(float(df["est_cost_usd"].sum()), 2)


def by_model(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("model", as_index=False)["est_cost_usd"].sum()
        .sort_values("est_cost_usd", ascending=False)
        .reset_index(drop=True)
    )


def by_task(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("task_type", as_index=False)["est_cost_usd"].sum()
        .sort_values("est_cost_usd", ascending=False)
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_usage.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/usage.py tests/test_usage.py
git commit -m "feat: usage rollups (total + by-model)"
```

---

### Task 12: Wire Beat 3 finale + recursive close into `app.py`

**Files:**
- Modify: `app.py` (`beat_finale`, loader)

- [ ] **Step 1: Add a usage loader and replace `beat_finale`**

```python
# app.py — add near _models()
from sotl.data import load_usage
from sotl.usage import by_model as usage_by_model
from sotl.usage import total_spend


@st.cache_data
def _usage():
    # usage.csv is already scoped to THIS Week-1 project by scripts/derive_usage.py
    return load_usage(settings.usage_csv)


# app.py — replace beat_finale
# Set to your actual flat Claude subscription price (e.g. 20 / 100 / 200).
MONTHLY_PLAN_USD = 20


def beat_finale(_models_df):
    st.header("③ Equivalent API cost — to build THIS app")
    u = _usage()
    total = total_spend(u)
    bym = usage_by_model(u)
    st.metric("Equivalent API cost to build this app (published list prices)", f"${total:,.2f}")
    st.caption(
        f"Built on a flat ${MONTHLY_PLAN_USD}/mo Claude plan — the tokens that built "
        f"this very Week-1 app (brainstorm, plan, code) would cost ~${total:,.2f} at API "
        "list prices. Token counts are real (measured from transcripts); the dollar "
        "figure is a notional list-price conversion, **not** actual spend."
    )
    st.plotly_chart(
        px.bar(bym, x="model", y="est_cost_usd",
               labels={"est_cost_usd": "equiv. API cost ($)"}).update_layout(
            paper_bgcolor="#FDFCEF", plot_bgcolor="#FDFCEF", font_color="#0F1419"),
        use_container_width=True,
    )
    top = bym.iloc[0]["model"] if not bym.empty else "n/a"
    st.markdown(
        f"> **Every token that built the app you're looking at — brainstorm, plan, and "
        f"code — would cost <mark>${total:,.2f}</mark> at API list prices** (mostly "
        f"{top}). I built it on a flat ${MONTHLY_PLAN_USD}/mo plan.",
        unsafe_allow_html=True,
    )
```

> Set `MONTHLY_PLAN_USD` to your real plan price. No `project=` filter needed — `derive_usage.py` already scoped `usage.csv` to this Week-1 project. Re-run `derive_usage.py` right before recording so the number includes the full build.

- [ ] **Step 2: Run and verify the relabelled finale + recursive close**

Run: `uv run streamlit run app.py`
Expected: tab ③ shows the "Equivalent API cost to build this app" metric (scoped to this Week-1 project only), the flat-plan/notional-cost note, a by-model bar chart, and the highlighted "every token that built the app you're looking at would cost $X at API list prices (mostly <model>)" line. Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: Beat 3 finale + recursive close"
```

---

## Phase 5 — Chips + narration + trust (Day 4, freeze tonight)

### Task 13: `chips.py` — 3 deterministic queries

**Files:**
- Create: `src/sotl/chips.py`
- Test: `tests/test_chips.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_chips.py
import pandas as pd

from sotl.chips import CHIP_IDS, run_chip


def _df():
    return pd.DataFrame([
        {"name": "A", "lab": "OpenAI", "price_out": 2.0, "swe_bench": 40,
         "context_window": 128000, "metric_notes": "", "params": "x"},
        {"name": "B", "lab": "Meta", "price_out": 1.0, "swe_bench": 50,
         "context_window": 1000000, "metric_notes": "open weights", "params": "x"},
    ])


def test_chip_ids_are_three():
    assert len(CHIP_IDS) == 3


def test_coding_per_dollar_picks_best_ratio():
    res = run_chip("coding_per_dollar", _df())
    assert res.frame.iloc[0]["name"] == "B"  # 50/1.0 beats 40/2.0
    assert "B" in res.headline


def test_context_leaders_orders_by_window():
    res = run_chip("context_leaders", _df())
    assert res.frame.iloc[0]["name"] == "B"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_chips.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sotl.chips'`

- [ ] **Step 3: Implement `chips.py`**

```python
# src/sotl/chips.py
from dataclasses import dataclass

import pandas as pd

CHIP_IDS = ["coding_per_dollar", "open_vs_closed", "context_leaders"]
CHIP_LABELS = {
    "coding_per_dollar": "Best coding per dollar",
    "open_vs_closed": "Open vs closed",
    "context_leaders": "Context window leaders",
}


@dataclass
class ChipResult:
    chip_id: str
    headline: str
    frame: pd.DataFrame


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def run_chip(chip_id: str, df: pd.DataFrame) -> ChipResult:
    d = df.copy()
    if chip_id == "coding_per_dollar":
        d["coding_per_dollar"] = _num(d["swe_bench"]) / _num(d["price_out"])
        d = d.sort_values("coding_per_dollar", ascending=False).dropna(subset=["coding_per_dollar"])
        top = d.iloc[0]
        return ChipResult(chip_id,
                          f"{top['name']}: {top['coding_per_dollar']:.1f} SWE-bench pts per $/1M out",
                          d[["name", "lab", "swe_bench", "price_out", "coding_per_dollar"]])
    if chip_id == "open_vs_closed":
        d["kind"] = d["metric_notes"].str.contains("open", case=False, na=False).map(
            {True: "open", False: "closed"})
        agg = d.groupby("kind", as_index=False).agg(
            avg_swe=("swe_bench", lambda s: _num(s).mean()),
            avg_price=("price_out", lambda s: _num(s).mean()))
        return ChipResult(chip_id, "Average SWE-bench and price by open vs closed", agg)
    if chip_id == "context_leaders":
        d["context_window"] = _num(d["context_window"])
        d = d.sort_values("context_window", ascending=False)
        top = d.iloc[0]
        return ChipResult(chip_id,
                          f"{top['name']} leads at {int(top['context_window']):,} tokens",
                          d[["name", "lab", "context_window"]].head(5))
    raise ValueError(f"unknown chip_id: {chip_id}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_chips.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/chips.py tests/test_chips.py
git commit -m "feat: 3 deterministic data chips"
```

---

### Task 14: `narrate.py` — open-model takeaway (any OpenAI-compatible endpoint) + cache fallback (guardrails #3, #6)

**Files:**
- Create: `src/sotl/narrate.py`
- Test: `tests/test_narrate.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_narrate.py
from pathlib import Path

from sotl.config import Settings
from sotl.narrate import takeaway


class _BoomClient:
    class chat:  # noqa: N801
        class completions:  # noqa: N801
            @staticmethod
            def create(**_):
                raise AssertionError("API must not be called")


class _RaiseClient:  # simulates an API/network error at call time
    class chat:  # noqa: N801
        class completions:  # noqa: N801
            @staticmethod
            def create(**_):
                raise RuntimeError("api down")


class _FakeResp:
    def __init__(self, text):
        self.choices = [type("C", (), {"message": type("M", (), {"content": text})()})()]


class _FakeClient:
    def __init__(self, text):
        self._text = text

    class _Comp:
        def __init__(self, outer):
            self._outer = outer

        def create(self, **_):
            return _FakeResp(self._outer._text)

    class _Chat:
        def __init__(self, outer):
            self._outer = outer

        @property
        def completions(self):
            return _FakeClient._Comp(self._outer)

    @property
    def chat(self):
        return _FakeClient._Chat(self)


def _settings(tmp_path: Path, *, key=None, base_url="https://openrouter.ai/api/v1") -> Settings:
    return Settings(
        narration_api_key=key, narration_base_url=base_url,
        cache_path=tmp_path / "n.json", data_dir=tmp_path,
    )


def test_no_api_key_returns_fallback_and_caches(tmp_path):
    s = _settings(tmp_path)
    out = takeaway("coding_per_dollar", "B: 50 pts/$", s, client=_BoomClient())
    assert "B: 50 pts/$" in out
    assert s.cache_path.exists()


def test_cache_hit_does_not_call_api(tmp_path):
    s = _settings(tmp_path, key="or-x")
    takeaway("c1", "summary one", s, client=_FakeClient("cached!"))
    again = takeaway("c1", "summary one", s, client=_BoomClient())  # must hit cache
    assert again == "cached!"


def test_api_path_returns_model_text(tmp_path):
    s = _settings(tmp_path, key="or-x")
    out = takeaway("c2", "summary two", s, client=_FakeClient("frontier got cheap"))
    assert out == "frontier got cheap"


def test_api_error_falls_back_to_summary(tmp_path):
    s = _settings(tmp_path, key="or-x")  # key present, but the call raises
    out = takeaway("c5", "B leads on coding/$", s, client=_RaiseClient())
    assert out == "B leads on coding/$"  # demo-safe fallback (guardrail #6)


def test_cache_key_includes_model(tmp_path):
    s = _settings(tmp_path, key="or-x")
    a = takeaway("c4", "same summary", s,
                 model="meta-llama/llama-3.1-8b-instruct", client=_FakeClient("A"))
    b = takeaway("c4", "same summary", s,
                 model="qwen/qwen-2.5-7b-instruct", client=_FakeClient("B"))
    assert (a, b) == ("A", "B")  # distinct cache entries per narrator
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_narrate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sotl.narrate'`

- [ ] **Step 3: Implement `narrate.py`**

```python
# src/sotl/narrate.py
import hashlib
import json

from sotl.config import Settings

SYSTEM = (
    "You write ONE concise sentence summarizing a computed data result for a "
    "technical builder audience. Use only numbers present in the input. Never "
    "invent figures. No preamble, no markdown."
)


def _key(chip_id: str, model: str, summary: str) -> str:
    h = hashlib.sha1(f"{model}|{summary}".encode()).hexdigest()[:12]
    return f"{chip_id}:{model}:{h}"


def _load(settings: Settings) -> dict:
    p = settings.cache_path
    return json.loads(p.read_text()) if p.exists() else {}


def _save(settings: Settings, cache: dict) -> None:
    settings.cache_path.parent.mkdir(parents=True, exist_ok=True)
    settings.cache_path.write_text(json.dumps(cache, indent=2))


def takeaway(
    chip_id: str, summary: str, settings: Settings, model: str | None = None, client=None
) -> str:
    model = model or settings.narration_model
    cache = _load(settings)
    key = _key(chip_id, model, summary)
    if key in cache:
        return cache[key]
    if not settings.narration_api_key:
        cache[key] = summary  # demo-safe templated fallback (no key)
        _save(settings, cache)
        return summary
    if client is None:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.narration_api_key, base_url=settings.narration_base_url
        )
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": summary}],
            max_tokens=60,
            temperature=0.3,
        )
        text = resp.choices[0].message.content.strip()
    except Exception:
        text = summary  # API/network error → demo-safe templated fallback (guardrail #6)
    cache[key] = text
    _save(settings, cache)
    return text
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_narrate.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/narrate.py tests/test_narrate.py
git commit -m "feat: narrate.py open-model takeaway (OpenAI-compatible) with cache + fallback"
```

---

### Task 15: `trust.py` — provenance summary

**Files:**
- Create: `src/sotl/trust.py`
- Test: `tests/test_trust.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_trust.py
import pandas as pd

from sotl.trust import trust_summary


def _df():
    return pd.DataFrame([
        {"metric_type": "measured", "last_verified": "2026-05-31", "swe_bench": 49},
        {"metric_type": "reported_by_lab", "last_verified": "2026-04-01", "swe_bench": 40},
        {"metric_type": "unknown", "last_verified": "2026-05-31", "swe_bench": "unknown"},
    ])


def test_trust_summary_counts_and_oldest():
    s = trust_summary(_df())
    assert s["counts"]["measured"] == 1
    assert s["counts"]["reported_by_lab"] == 1
    assert s["oldest_verified"] == "2026-04-01"
    assert s["missing_swe_bench"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_trust.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sotl.trust'`

- [ ] **Step 3: Implement `trust.py`**

```python
# src/sotl/trust.py
import pandas as pd


def trust_summary(df: pd.DataFrame) -> dict:
    counts = df["metric_type"].value_counts().to_dict()
    missing = int((pd.to_numeric(df["swe_bench"], errors="coerce").isna()).sum())
    return {
        "counts": counts,
        "oldest_verified": str(df["last_verified"].min()),
        "missing_swe_bench": missing,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_trust.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sotl/trust.py tests/test_trust.py
git commit -m "feat: trust.py provenance summary"
```

---

### Task 16: Wire chips + takeaways + trust badges into all beats; pre-warm cache

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add chips + takeaway to Beat 1, trust badge, and a chip rail**

```python
# app.py — add imports + narrator presets
from sotl.chips import CHIP_IDS, CHIP_LABELS, run_chip
from sotl.narrate import takeaway
from sotl.trust import trust_summary

# Open-source narrators on the configured OpenAI-compatible endpoint (default
# OpenRouter). Confirm exact ids at scaffold per the Reference-calls-verbatim rule.
NARRATORS = {
    "Llama 3.1 8B (open)": "meta-llama/llama-3.1-8b-instruct",
    "Llama 3.3 70B (open)": "meta-llama/llama-3.3-70b-instruct",
    "Qwen 2.5 7B (open)": "qwen/qwen-2.5-7b-instruct",
}


def _chip_rail(df):
    st.caption("Ask the data:")
    cols = st.columns(len(CHIP_IDS))
    for col, cid in zip(cols, CHIP_IDS, strict=True):
        if col.button(CHIP_LABELS[cid], key=f"chip_{cid}", use_container_width=True):
            st.session_state["active_chip"] = cid
    cid = st.session_state.get("active_chip")
    if cid and df.empty:
        st.info("No rows in the current filter — clear a lab to see a takeaway.")
    elif cid:
        res = run_chip(cid, df)  # safe: df non-empty (run_chip uses .iloc[0])
        model = st.session_state.get("narrator_model", settings.narration_model)
        st.markdown(f"**{takeaway(cid, res.headline, settings, model=model)}**")
        st.caption(f"narrated by `{model}`")
        with st.expander("Show the rows behind it"):
            st.dataframe(res.frame, use_container_width=True, hide_index=True)
```

Call `_chip_rail(view)` at the end of `beat_scatter(df)` — operate on the filtered `view` frame introduced in Task 7B.

- [ ] **Step 2: Add the Data-Trust badge (inline, MUST level) to the sidebar**

```python
# app.py — in main(), after df = _models()
with st.sidebar:
    st.subheader("🗣️ Narrator")
    choice = st.selectbox("Who writes the takeaways?", list(NARRATORS))
    st.session_state["narrator_model"] = NARRATORS[choice]
    st.caption("Open-source narrators via OpenRouter — the app argues open models caught up, so an open model narrates it.")

    s = trust_summary(df)
    st.subheader("🔒 Data Trust")
    st.write(f"Sources verified as of **{s['oldest_verified']}** (oldest).")
    st.write({k: int(v) for k, v in s["counts"].items()})
    if s["missing_swe_bench"]:
        st.warning(f"{s['missing_swe_bench']} model(s) missing SWE-bench.")
```

- [ ] **Step 3: Pre-warm the narration cache for the demo (guardrail #6)**

Run (with `NARRATION_API_KEY` — your OpenRouter key — set in `.env`):
```bash
uv run python - <<'PY'
from sotl.chips import CHIP_IDS, run_chip
from sotl.config import settings
from sotl.data import load_models
from sotl.narrate import takeaway

df = load_models(settings.models_csv)
models = [
    "meta-llama/llama-3.1-8b-instruct",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-7b-instruct",
]
for m in models:
    for c in CHIP_IDS:
        takeaway(c, run_chip(c, df).headline, settings, model=m)
print(f"cache warmed for {len(models)} narrators x {len(CHIP_IDS)} chips")
PY
```
Expected: prints the warmed count; `.cache/narration.json` has an entry per (narrator, chip). The recorded demo hits the cache and never blocks on the API. (With no key, narration caches a templated fallback instead — still demo-safe, just not LLM-written.)

- [ ] **Step 4: Run the full app and verify all three beats + chips + trust badge**

Run: `uv run streamlit run app.py`
Expected: chips render takeaways; sidebar shows the trust panel; all 3 beats work. Ctrl+C.

- [ ] **Step 5: Run the full test suite + lint (guardrail #8)**

Run: `uv run ruff check . && uv run pytest -q`
Expected: ruff clean; all tests pass.

- [ ] **Step 6: Commit — APP FREEZE**

```bash
git add app.py
git commit -m "feat: wire chips, takeaways, trust badge — app feature-freeze"
```

---

## Phase 6 — Constitution, docs, deliverables (Day 5)

### Task 17: SDD constitution + ADRs + agent context files

**Files (create):**
- `specs/README.md`, `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`, `specs/REQUIREMENTS_TEMPLATE.md`
- `specs/2026-05-30-state-of-the-llms/requirements.md`, `.../plan.md`, `.../validation.md`
- `docs/decisions/0001-streamlit-chassis-pure-core.md`
- `docs/decisions/0002-real-usage-derived-offline.md`
- `docs/decisions/0003-chips-not-chatbot.md`
- `CLAUDE.md`, `AGENTS.md`

- [ ] **Step 1: Generate the constitution from the design spec**

Copy content directly from the design doc sections into the constitution files (no new content needed):
- `specs/mission.md` ← design §1 (mission, audience, in/out of scope)
- `specs/tech-stack.md` ← design §3 (layers) + §6 (the 8 guardrails, verbatim)
- `specs/roadmap.md` ← design §5 (the 5-session schedule as phases with status)
- `specs/README.md` ← short note: "`specs/` is canonical (ADR-style, no PLAN.md); read before changing scope."
- `specs/REQUIREMENTS_TEMPLATE.md` ← copy from SSM-PDFTool's template (Goal / Non-goals / Scenarios / Constraints / **Reference calls (verbatim)** / Output contracts / Dependencies).
- `specs/2026-05-30-state-of-the-llms/requirements.md` ← design §1+§4+§5 for this feature; `plan.md` ← link to this plan; `validation.md` ← fill in Step 3.

- [ ] **Step 2: Write the three ADRs (Problem → Solution → Impact → What I Learned)**

`docs/decisions/0001-streamlit-chassis-pure-core.md`:
```markdown
# ADR 0001 — Streamlit chassis + pure-logic core
**Status:** accepted · **Date:** 2026-05-30
## Problem
A vibe-coded Streamlit app tends to tangle UI and logic, making it untestable and the "technical thinking" invisible.
## Solution
All logic lives in `src/sotl/` (UI-agnostic, unit-tested); `st.*` calls live only in `app.py`. The picker's "latency" input is approximated by a `prefer_efficient` value-per-dollar ranking because `models.csv` has no latency column.
## Impact
Logic is unit-tested in CI; the view is a thin render layer; swapping Streamlit later is cheap.
## What I Learned
Separating compute from view is what let the LLM stay a *narrator* (it never touches numbers).
```

`docs/decisions/0002-real-usage-derived-offline.md`:
```markdown
# ADR 0002 — Real usage derived offline into a scrubbed CSV
**Status:** accepted · **Date:** 2026-05-30
## Problem
The finale needs real personal token-usage data, but raw Claude Code transcripts contain message content and absolute paths (privacy), and live parsing would make the demo non-deterministic. The author builds on a flat monthly Claude subscription, so there is no per-token bill — only the token counts are real.
## Solution
`scripts/derive_usage.py` runs once, aggregates token usage by (date, project, task, model), joins published list pricing, derives an **equivalent API list-price cost**, and writes a scrubbed `data/usage.csv`. The app reads only that CSV. Raw `*.jsonl` is gitignored.
## Impact
Privacy-safe, deterministic demo, committed dataset. Cost is derived (tokens × list pricing) = "show the math" — but it is a **notional list-price equivalent, not actual spend** (flat subscription). The finale is labelled "Equivalent API cost at published list prices"; measured tokens vs. notional dollars is itself a Data-Trust point.
## What I Learned
Moving the risky/sensitive step offline de-risked privacy and the live demo at once — and being explicit that the dollar figure is notional (not real spend) keeps the claim honest.
```

`docs/decisions/0003-chips-not-chatbot.md`:
```markdown
# ADR 0003 — Deterministic chips + open-model narration, not a free-text chatbot
**Status:** accepted · **Date:** 2026-05-30
## Problem
A free-text "ask the data" chatbot is the Solution Kit's Tab 4 (replicating it scores zero) and is the likeliest thing to break live on camera.
## Solution
Deterministic chips compute results in pandas; the narrator model only writes a one-sentence takeaway, cached to disk. Narration goes through any OpenAI-compatible endpoint via a configurable `base_url` + model id (default: an open-source model on OpenRouter); no vendor SDK beyond `openai`. The app renders with no API key.
## Impact
Demo-safe, divergent from the kit, provider-agnostic, and the LLM never invents numbers. Using an **open model** is on-theme — the app argues open models caught up, so an open model narrates it.
## What I Learned
Constraining the LLM to a narrator role removed the single biggest demo risk; keeping the endpoint configurable made "closed vs open" a one-line swap.
```

- [ ] **Step 3: Write `CLAUDE.md` + `AGENTS.md`**

Both files: a short "Start here → `specs/`" pointer, the run commands (`uv sync`, `uv run streamlit run app.py`, `uv run pytest`, `uv run ruff check .`), and the 8 guardrails mirrored from `specs/tech-stack.md`.

- [ ] **Step 4: Commit**

```bash
git add specs docs/decisions CLAUDE.md AGENTS.md
git commit -m "docs: SDD constitution, ADRs, agent context"
```

---

### Task 18: README, validation evidence, GitHub, deliverable checklist

**Files:**
- Modify: `README.md`
- Modify: `specs/2026-05-30-state-of-the-llms/validation.md`

- [ ] **Step 1: Flesh out `README.md`**

Add: one-paragraph overview, a screenshot of each beat, the run instructions, a `.env.example` note (`NARRATION_API_KEY=` — your OpenRouter key for the default open narrator; optional `NARRATION_BASE_URL=` / `NARRATION_MODEL=` to point at Groq/Together/Ollama/OpenAI — app runs without any key), the "diverges from the Solution Kit" table (design §7), and a data-provenance note (token counts real; dollar figures are notional API list-price equivalents).

- [ ] **Step 2: Record validation evidence**

Run: `uv run ruff check . && uv run pytest -q`
Paste the passing output into `specs/2026-05-30-state-of-the-llms/validation.md` with the date (guardrail #8).

- [ ] **Step 3: Create the GitHub repo and push**

```bash
gh repo create state-of-the-llms --public --source=. --remote=origin --push
```
Expected: repo created; `main` pushed; CI runs green on GitHub.

- [ ] **Step 4: Finalize the vibe-coding log**

Compile `docs/learn/vibe-coding-log.md` from the per-task screenshots + prompts captured during the build (see the capture-cadence note at the top of this plan). This is the source for the Google Doc's prompts/iterations sections.

```bash
git add docs/learn/vibe-coding-log.md
git commit -m "docs: vibe-coding prompt + screenshot log"
```

- [ ] **Step 5: Produce the two graded artifacts (non-code) — meeting handout §11**

- **≤5-min video:** the 3 beats (price collapse → pick a model + show the math → the "equivalent API cost at list prices" recursive close), **plus ~30s explicitly on "how I used AI coding tools"** (brainstorming agent → subagent-driven dev → Codex/Claude). Pre-warmed cache makes narration instant.
- **Google Doc (Path B):** must include a **problem statement** (spec §1) and a **step-by-step build breakdown** (this plan's phases + ADRs), *and* project overview, datasets (+ provenance), **prompts** (from `vibe-coding-log.md`), **iterations**, **learnings** (ADRs' "What I Learned"), the design §7 "diverges from the Solution Kit" table, and process screenshots.
- Submit repo + video + doc to the form before **June 4, 11pm PT**.

- [ ] **Step 6: Final commit**

```bash
git add README.md specs/2026-05-30-state-of-the-llms/validation.md
git commit -m "docs: README, validation evidence; ship"
git push
```

---

## SHOULD tasks (optional — only after the Day-4 freeze)

### Task S1: Counterfactual savings in the finale
`usage.py: counterfactual_savings(df, cheap_model, expensive_models, ratio=0.85)` → estimated $ saved if `ratio` of expensive-model spend had been routed to `cheap_model` (using `pricing.csv`). TDD with a fixture; render as a metric + one-line takeaway in Beat 3.

### Task S2: Cache-ROI view
`usage.py: cache_roi(df)` → `cache_read_tokens` vs `cache_creation_tokens` and the $ saved by cache reads (from `pricing.csv` cache columns). Render a small bar + takeaway in Beat 3.

### Task S3: Full Data-Trust panel
Promote the sidebar badge to a dedicated expander on each beat: per-metric source links, freshness, and an "apples-to-oranges" warning when comparing benchmarks of different `metric_type`.

### Task S4: Deploy to Streamlit Community Cloud
Add `NARRATION_API_KEY` as a Cloud secret, point it at the repo, verify the cached narration renders even if the secret is absent. Add the public URL to the README and the Google Doc.

---

## Self-Review (completed by plan author)

**Spec coverage:** §1 mission → Tasks 7/17; §1 literal filter → Task 7B; §2 decisions → ADRs (Task 17); §3 architecture/modules → Tasks 3,5,6,8,11,13,14,15 (each module) + 7,7B,9,12,16 (thin view); §4 data model → Tasks 4,10,11; §5 MUST scope → Tasks 1–18; §5 SHOULD → S1–S4; §6 guardrails → enforced per task (#1 Task 7, #2 Task 4, #3/#6 Task 14, #4 Task 10, #5 Task 3, #7 ADR 0003, #8 Tasks 16/18); §7 divergence → Tasks 17/18; §8 constitution → Task 17; §9 testing → every code task is TDD; §10 defaults → encoded (name `sotl`, open narrator `meta-llama/llama-3.1-8b-instruct` via OpenRouter, Plotly, local-first); §11 deliverable-capture → top-of-plan capture cadence + Task 18 Steps 4–5. No gaps.

**Placeholder scan:** Task 4 model values are a real data-curation step (verified sources required), not code placeholders. No "TODO/handle edge cases/similar to Task N" anywhere.

**Type consistency:** `Recommendation(pick, score_col, reason_rows)`, `ChipResult(chip_id, headline, frame)`, `Settings` (`models_csv/pricing_csv/usage_csv/cache_path/narration_model/narration_base_url/narration_api_key`), `takeaway(chip_id, summary, settings, model=None, client=None)` (builds the client from `settings.narration_base_url`+`narration_api_key`; cache key includes `model`; app passes `model=` from the sidebar narrator selector), `run_chip(chip_id, df)`, `trust_summary(df)`, `total_spend(df)` + `by_model(df)` (finale uses these on the pre-scoped Week-1 `usage.csv`; no per-project filter in the app) — all consistent between definition and call sites.
