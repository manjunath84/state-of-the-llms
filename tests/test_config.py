# tests/test_config.py
from pathlib import Path

from sotl.config import Settings


def test_defaults_and_derived_paths(monkeypatch):
    monkeypatch.delenv("NARRATION_API_KEY", raising=False)
    monkeypatch.delenv("NARRATION_BASE_URL", raising=False)
    monkeypatch.delenv("NARRATION_MODEL", raising=False)
    # _env_file=None disables .env loading so this tests TRUE defaults — otherwise
    # a developer's local .env (real key) makes narration_api_key non-None here.
    s = Settings(data_dir=Path("data"), _env_file=None)
    assert s.narration_model == "meta-llama/llama-3.1-8b-instruct"
    assert s.narration_base_url == "https://openrouter.ai/api/v1"
    assert s.narration_api_key is None
    assert s.models_csv == Path("data/models.csv")
    assert s.pricing_csv == Path("data/pricing.csv")
    assert s.usage_csv == Path("data/usage.csv")


def test_narration_key_from_env(monkeypatch):
    monkeypatch.setenv("NARRATION_API_KEY", "or-test")
    s = Settings()
    assert s.narration_api_key == "or-test"


def test_base_url_and_model_overridable(monkeypatch):
    monkeypatch.delenv("NARRATION_API_KEY", raising=False)
    s = Settings(narration_base_url="http://localhost:11434/v1", narration_model="llama3")
    assert s.narration_base_url == "http://localhost:11434/v1"
    assert s.narration_model == "llama3"
