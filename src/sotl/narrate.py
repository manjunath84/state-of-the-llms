# src/sotl/narrate.py
import hashlib
import json
import re
from dataclasses import dataclass

from sotl.config import Settings

SYSTEM = (
    "You write ONE concise sentence summarizing a computed data result for a "
    "technical builder audience. Use only numbers present in the input. Never "
    "invent figures. No preamble, no markdown."
)


def _numbers(s: str) -> set[str]:
    # Numeric tokens, comma-thousands stripped, trailing-zero-normalized so
    # "80" == "80.0". Used to enforce guardrail #3: the narrator may not emit a
    # number absent from the input it was given.
    out = set()
    for tok in re.findall(r"\d+(?:\.\d+)?", s.replace(",", "")):
        out.add(str(float(tok)) if "." in tok else str(float(tok)))
    return out


def _faithful(summary: str, text: str) -> bool:
    # True iff every number in `text` also appears in `summary` (number-free
    # prose is fine). If the model invented a figure, this is False → reject it.
    return _numbers(text) <= _numbers(summary)


@dataclass
class GateDemo:
    source: str  # the sourced sentence — every number traces to our computed data
    ungated: str  # the same sentence carrying an INVENTED number (what could ship raw)
    gated: str  # what the gate actually emits (== source when it catches a fabrication)
    injected: str | None  # the fabricated number token, for display
    caught: bool  # did the gate reject the invented number?


def _tamper(summary: str, bump: float = 12.0) -> tuple[str, str | None]:
    # Fabricate a hallucination DETERMINISTICALLY: inflate the first
    # percentage-like number (50-100, i.e. a skill score) so the gate demo always
    # shows a catch — offline, without relying on a live model to misbehave on cue.
    for m in re.finditer(r"\d+(?:\.\d+)?", summary):
        v = float(m.group(0))
        if 50 <= v <= 100:
            fake = f"{min(v + bump, 99):g}"
            return summary[: m.start()] + fake + summary[m.end() :], fake
    return summary, None


def gate_demo(summary: str, bump: float = 12.0) -> GateDemo:
    # Make guardrail #3 visible: hand the gate a sentence with an invented score
    # and prove it rejects it. The identical _faithful() check runs inside
    # takeaway() on every live narration — this just lets a viewer see it work.
    ungated, injected = _tamper(summary, bump)
    caught = injected is not None and not _faithful(summary, ungated)
    gated = summary if caught else ungated
    return GateDemo(
        source=summary, ungated=ungated, gated=gated, injected=injected, caught=caught
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
        # Guardrail #3, mechanically enforced: if the narrator introduced any
        # number not in the computed input, it hallucinated — reject and fall
        # back to the deterministic headline (which is always accurate).
        if not _faithful(summary, text):
            text = summary
    except Exception:
        text = summary  # API/network error → demo-safe templated fallback (guardrail #6)
    cache[key] = text
    _save(settings, cache)
    return text
