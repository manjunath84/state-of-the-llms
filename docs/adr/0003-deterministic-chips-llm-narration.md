# ADR 0003 — Deterministic chips, LLM only narrates

## Problem
A free-text "chat with your data" box demos poorly: it hallucinates numbers and
breaks live. The Solution Kit's own example scored zero for exactly this.

## Solution
Three fixed chips compute answers in pandas. The LLM gets the computed result and
writes ONE sentence. It never sees raw data or invents figures. An open-source model
(via OpenRouter) does the narration — fitting the app's "open models caught up" thesis.

## Impact
- Demo-safe, reproducible, honest numbers.
- Less "wow, it's a chatbot" — but far more trustworthy.
- Cache + fallback make the recorded demo independent of a live API.

## What I Learned
The narration cache key must include the model id, not just the chip — otherwise
switching narrators returns a stale sentence. A subtler trap: pre-warming the cache
with NO API key stores the deterministic fallback text, which then shadows a later
real-key warm on a cache hit. The fix is to clear `.cache/narration.json` before
warming with a real key. The fallback path (no key OR API error → return the raw
computed summary) is what makes the recorded demo genuinely cannot-break.
