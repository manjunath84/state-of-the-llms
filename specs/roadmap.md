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

> **Data note (MUST, author action):** `data/models.csv` currently ships 3
> placeholder rows. Replace with ~18–20 verified frontier models (each with
> `source_url` + `last_verified`) before recording — guardrail #2.

**SHOULD (only if ahead at the freeze):** full Data-Trust panel · counterfactual
savings · cache-ROI view · 4th/5th chips · deploy to Streamlit Community Cloud.

**Risk caps:** (1) log parser time-boxed to ~1–2 hrs — if it overruns, ship the
finale on a hand-compiled ~15-row real sample. (2) Always keep a demoable
skeleton; layer features on top.
