from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "dev-insecure-secret-key-change-me-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI-Powered Q&A Platform"
    database_url: str = "sqlite:///./qa_platform.db"

    secret_key: str = DEFAULT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    bcrypt_rounds: int = 12

    # "claude" uses the Anthropic API, "mock" returns canned answers,
    # "auto" picks claude when an API key is configured.
    ai_provider: str = "auto"
    anthropic_api_key: str | None = None
    ai_model: str = "claude-opus-5-5"
    ai_effort: str = "medium"
    ai_max_tokens: int = 16000

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    frontend_dist: str = "../frontend/dist"

    default_page_size: int = 20
    max_page_size: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()
