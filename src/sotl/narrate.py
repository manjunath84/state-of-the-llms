# src/sotl/narrate.py
import hashlib
import json

from sotl.config import Settings

SYSTEM = (
    "You write ONE concise sentence summarizing a computed data result for a "
    "technical builder audience. Use only numbers present in the input. Never "
    "invent figures. No preamble, no markdown."
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
    except Exception:
        text = summary  # API/network error → demo-safe templated fallback (guardrail #6)
    cache[key] = text
    _save(settings, cache)
    return text
