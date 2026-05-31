# Roadmap (5 sessions, hard app-freeze on Day 4)

The graded artifacts are the repo / video / doc — not the app. The app freezes on
Day 4 so Day 5 is reserved for the deliverables.

| Day | Phase | Status |
|---|---|---|
| D1 | Walking skeleton: theme + `models.csv` + scatter + stepper, end-to-end | ✅ done |
| D2 | Model picker + show-the-math | ✅ done |
| D3 | `derive_usage.py` + finale + recursive close | ✅ done |
| D4 | 3 chips + open-model takeaway + cache; **freeze tonight** | ✅ done (frozen) |
| D5 | Video + Google Doc + repo polish + submit | 🟡 in progress |

**MUST (the spine)** — all complete: `models.csv` + provenance · Beat 1 scatter ·
Beat 2 picker (+ math) · Beat 3 real-usage finale (+ recursive close) · story
stepper · 3 chips + open-model takeaway + disk cache · theme CSS · SDD scaffold
(this `specs/` + CLAUDE.md + pyproject + CI + unit tests) · the three deliverables.

> **Data note:** `data/models.csv` now ships **18 frontier models** (7 open / 11
> closed), each with `source_url` + `last_verified`; `validate_models.py` exits 0.
> ⚠️ **Author action remaining:** rows tagged `confidence,low` (models released
> after the assistant's knowledge cutoff — GPT-4.1, o3-mini, Gemini 2.0 Flash,
> DeepSeek-R1, Llama 3.3 70B, Mistral Large 2) carry provisional numbers;
> reconfirm each at its cited source before recording — guardrail #2.

**SHOULD (only if ahead at the freeze):** full Data-Trust panel · counterfactual
savings · cache-ROI view · 4th/5th chips · deploy to Streamlit Community Cloud.

**Risk caps:** (1) log parser time-boxed to ~1–2 hrs — if it overruns, ship the
finale on a hand-compiled ~15-row real sample. (2) Always keep a demoable
skeleton; layer features on top.
