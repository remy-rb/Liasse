from functools import lru_cache

from pydantic import Field, PostgresDsn, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: PostgresDsn
    session_secret: SecretStr = Field(min_length=32)
    # Only send the session cookie over HTTPS; turn on once Liasse is served over HTTPS.
    session_cookie_secure: bool = False
    # Where the Archive lives, read through fsspec: a local path or file:// URL (s3:// comes later).
    storage_url: str
    upload_max_bytes: int = Field(default=50 * 1024 * 1024, gt=0)
    # The LLM that classifies Documents, as a LiteLLM model name, e.g. anthropic/claude-opus-5-5,
    # openai/<model> or ollama/<model>. Only the worker needs it.
    llm_model: str | None = None
    llm_api_key: SecretStr | None = None
    # For Ollama or any self-hosted endpoint, e.g. http://localhost:11434.
    llm_api_base: str | None = None
    # Below this confidence for Category, Correspondent or Document Date, a Document goes to the
    # Inbox instead of being Filed.
    inbox_threshold: float = Field(default=0.7, ge=0, le=1)


def load_settings() -> Settings:
    """Read settings from the environment, exiting with a readable message when invalid."""
    try:
        return Settings()
    except ValidationError as error:
        problems = "\n".join(
            f"  {'_'.join(str(part) for part in e['loc']).upper()}: {e['msg']}"
            for e in error.errors()
        )
        raise SystemExit(f"Liasse cannot start, invalid settings:\n{problems}") from None


@lru_cache
def get_settings() -> Settings:
    return load_settings()
