# ADR 0003 — Deterministic chips + open-model narration, not a free-text chatbot
**Status:** accepted · **Date:** 2026-05-30

## Problem
A free-text "ask the data" chatbot is the Solution Kit's Tab 4 (replicating it
scores zero) and is the likeliest thing to break live on camera.

## Solution
Deterministic chips compute results in pandas; the narrator model only writes a
one-sentence takeaway, cached to disk. Narration goes through any OpenAI-compatible
endpoint via a configurable `base_url` + model id (default: an open-source model on
OpenRouter); no vendor SDK beyond `openai`. The app renders with no API key.

## Impact
Demo-safe, divergent from the kit, provider-agnostic, and the LLM never invents
numbers. Using an **open model** is on-theme — the app argues open models caught
up, so an open model narrates it.

## What I Learned
Constraining the LLM to a narrator role removed the single biggest demo risk;
keeping the endpoint configurable made "closed vs open" a one-line swap. Two cache
traps surfaced: (1) the cache key must include the model id or switching narrators
returns a stale sentence; (2) pre-warming with no API key stores the fallback text,
which then shadows a later real-key warm on a cache hit — clear `.cache/` before
warming with a real key.
