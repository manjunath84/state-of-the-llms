# ADR 0002 — Specs as source of truth (no PLAN.md)

## Problem
Earlier projects duplicated intent across PLAN.md and specs; they drifted.

## Solution
One canonical spec in `docs/superpowers/specs/`. The plan is a transient
task list; the spec governs.

## Impact
- Single source of truth.
- Less drift, less doc maintenance.
- Requires discipline to update the spec when scope changes.

## What I Learned
Keeping the spec canonical paid off when scope changed mid-build (Beat ③ was
relabelled to "equivalent API cost at list prices" and the narrator switched from
OpenAI to an OpenRouter open model): we edited the spec once and the plan followed,
with no contradictory second source to reconcile. The transient plan being
disposable is a feature, not a gap.
