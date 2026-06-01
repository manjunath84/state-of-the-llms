---
name: prep-demo
description: One-shot pre-recording setup for the "State of the LLMs" demo video. Restores any missing data CSVs from git, frees port 8501, pre-warms the narration cache, and prints the build-cost numbers to say on camera. Use right before recording the Week-1 demo, or whenever the app misbehaves from stale state or a missing data file.
---

# prep-demo — pre-recording setup

Everything needed to get the app demo-ready is in one script: `scripts/prep_demo.sh`.
It is idempotent and safe to re-run.

## What to do

1. Run the prep script **without launching** (so it doesn't block this session), and
   show the user its output — especially the build-cost figures:
   ```bash
   bash scripts/prep_demo.sh --no-launch
   ```
   The script: anchors to the repo root, restores any missing `data/*.csv` from git,
   kills stray Streamlit servers, frees port 8501, clears `.cache`, pre-warms the
   narration cache, and prints `whole effort / app-only / opus share / cost-component`
   figures from the current data.

2. Report the printed build-cost figures back to the user so they can check them
   against the spoken script in `demo-recording-guide.md` (Part 2 + the cheat sheet).

3. Tell the user to launch the app **in their own terminal** (the one their screen
   recorder captures), because Streamlit runs in the foreground:
   ```bash
   uv run streamlit run app.py
   ```
   Then open http://localhost:8501.

4. Remind them of the manual framing the script can't do: browser zoom ~125%,
   collapse the sidebar, one silent click-through of all three tabs, and set the
   picker combo (task = coding · budget = $10 · prefer-cheaper ON) so it caches.

## Options

- `bash scripts/prep_demo.sh` — full prep, then launches the app (use this when
  running it yourself in a normal terminal).
- `bash scripts/prep_demo.sh --refresh` — also re-derives `usage.csv` first. Only use
  this if you intend to update the on-camera numbers; it changes the dollar totals, so
  re-read them afterward and update the spoken script.

## Notes

- The script never re-derives `usage.csv` unless `--refresh` is passed, so the numbers
  you memorized stay stable.
- If a `data/*.csv` ever goes missing, this script restores it automatically; the files
  are all tracked in git, and restoring `models.csv` / `pricing.csv` does not touch
  `usage.csv`.
