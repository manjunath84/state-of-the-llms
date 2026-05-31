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
