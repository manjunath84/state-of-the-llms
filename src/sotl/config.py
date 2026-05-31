# src/sotl/config.py
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # Narration via any OpenAI-compatible endpoint (default: an open model on
    # OpenRouter). Override base_url/model for Groq / Together / Ollama / OpenAI.
    narration_api_key: str | None = None  # env: NARRATION_API_KEY
    narration_base_url: str = "https://openrouter.ai/api/v1"  # env: NARRATION_BASE_URL
    narration_model: str = "meta-llama/llama-3.1-8b-instruct"  # env: NARRATION_MODEL
    data_dir: Path = Path("data")
    cache_path: Path = Path(".cache/narration.json")

    @property
    def models_csv(self) -> Path:
        return self.data_dir / "models.csv"

    @property
    def pricing_csv(self) -> Path:
        return self.data_dir / "pricing.csv"

    @property
    def usage_csv(self) -> Path:
        return self.data_dir / "usage.csv"


settings = Settings()
