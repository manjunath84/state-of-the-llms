# ADR 0002 — Real usage derived offline into a scrubbed CSV
**Status:** accepted · **Date:** 2026-05-30

## Problem
The finale needs real personal token-usage data, but raw Claude Code transcripts
contain message content and absolute paths (privacy), and live parsing would make
the demo non-deterministic. The author builds on a flat monthly Claude
subscription, so there is no per-token bill — only the token counts are real.

## Solution
`scripts/derive_usage.py` runs once, aggregates token usage by (date, project,
task, model), joins published list pricing, derives an **equivalent API list-price
cost**, and writes a scrubbed `data/usage.csv`. The app reads only that CSV. Raw
`*.jsonl` is gitignored. The script is scoped to **this Week-1 project only**
(dirs matching `*Week1-GenAIBuildingBlocks*`), not the whole GenAcademy folder.

## Impact
Privacy-safe, deterministic demo, committed dataset. Cost is derived (tokens × list
pricing) = "show the math" — but it is a **notional list-price equivalent, not
actual spend** (flat subscription). The finale is labelled "Equivalent API cost at
published list prices"; measured tokens vs. notional dollars is itself a
Data-Trust point.

## What I Learned
Moving the risky/sensitive step offline de-risked privacy and the live demo at
once. Being explicit that the dollar figure is notional (not real spend) keeps the
claim honest — and the ~$1.2k notional figure for a $20/mo-plan build is a stronger
punchline *because* it is labelled honestly.
