#!/usr/bin/env bash
# scripts/prep_demo.sh — one-shot pre-recording setup for "State of the LLMs".
#
# Does the whole pre-flight in the right order, idempotently and safe to re-run:
#   1. anchors to the repo root (works from any directory)
#   2. restores any missing tracked data CSVs from git
#   3. kills stray Streamlit servers and frees port 8501
#   4. clears + pre-warms the narration cache
#   5. prints the build-cost numbers you'll say on camera
#   6. launches the app (unless --no-launch)
#
# Usage:
#   bash scripts/prep_demo.sh              # full prep, then launch the app
#   bash scripts/prep_demo.sh --no-launch  # prep only; you launch streamlit yourself
#   bash scripts/prep_demo.sh --refresh    # also re-derive usage.csv first (changes the $ totals)
set -euo pipefail

LAUNCH=1
REFRESH=0
for arg in "$@"; do
  case "$arg" in
    --no-launch) LAUNCH=0 ;;
    --refresh)   REFRESH=1 ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown option: $arg (try --help)"; exit 2 ;;
  esac
done

# 1. Anchor to the repo root, no matter where this was called from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
echo "→ repo root: $REPO_ROOT"

# 2. Restore any missing tracked data files. models.csv / pricing.csv are reference
#    data — restoring them never touches your freshly-derived usage.csv.
for f in data/models.csv data/pricing.csv; do
  if [ ! -f "$f" ]; then
    echo "→ $f is missing — restoring it from git"
    git restore "$f" 2>/dev/null || git checkout -- "$f"
  fi
done
# usage.csv must exist for the finale; fall back to the committed copy if it's gone.
if [ ! -f data/usage.csv ]; then
  echo "→ data/usage.csv is missing — restoring the committed copy from git"
  git restore data/usage.csv 2>/dev/null || git checkout -- data/usage.csv
fi
echo "→ data files present:"; ls -1 data/*.csv | sed 's/^/     /'

# 3. (Optional) refresh the build-cost data. OFF by default so the numbers you
#    memorized stay stable on camera. Pass --refresh to re-derive.
if [ "$REFRESH" = "1" ]; then
  echo "→ refreshing usage.csv via derive_usage.py …"
  uv run python scripts/derive_usage.py
fi

# 4. Kill any running Streamlit servers and free port 8501 (zombies serve old data).
echo "→ stopping any running Streamlit servers …"
pkill -f streamlit 2>/dev/null || true
sleep 1
if lsof -ti :8501 >/dev/null 2>&1; then
  lsof -ti :8501 | xargs kill -9 2>/dev/null || true
  sleep 1
fi
echo "→ port 8501 is free"

# 5. Clear stale narration and pre-warm the cache (so there's no spinner on camera).
echo "→ warming the narration cache …"
rm -rf .cache
uv run python - <<'PY'
from sotl.data import load_models
from sotl.chips import CHIP_IDS, run_chip
from sotl.narrate import takeaway
from sotl.config import settings
m = load_models(settings.models_csv)
for cid in CHIP_IDS:
    print("    ", cid, "->", takeaway(cid, run_chip(cid, m).headline, settings))
PY

# 6. Print the figures you'll say out loud, straight from the current data.
echo "→ build-cost figures (say these on camera):"
uv run python - <<'PY'
from sotl.data import load_usage, load_pricing
from sotl.usage import total_spend, by_model_detail, filter_scope, cost_components
from sotl.config import settings
u = load_usage(settings.usage_csv); p = load_pricing(settings.pricing_csv)
d = by_model_detail(u)
c = cost_components(u, p).sort_values("cost", ascending=False); t = c.cost.sum()
print("     whole effort: $%.2f" % total_spend(u))
print("     app-only:     $%.2f" % total_spend(filter_scope(u, app_only=True)))
print("     opus share:   %.1f%%" % d.iloc[0]["share_pct"])
print("     " + "  ".join("%s=%.0f%%" % (r["component"], r["cost"] / t * 100) for _, r in c.iterrows()))
PY

echo ""
echo "✓ pre-flight done. Manual framing steps the script can't do:"
echo "    • browser zoom ~125% (Cmd-+) and collapse the sidebar («)"
echo "    • click silently through all three tabs once to confirm they render"
echo "    • set the picker combo: task=coding · budget=\$10 · prefer-cheaper ON (caches it)"
echo ""

if [ "$LAUNCH" = "1" ]; then
  echo "→ launching the app (Ctrl-C to stop) … open http://localhost:8501"
  exec uv run streamlit run app.py
else
  echo "  Ready. Launch it yourself when you are:  uv run streamlit run app.py"
fi
