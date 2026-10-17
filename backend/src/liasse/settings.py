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
