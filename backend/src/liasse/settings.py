from functools import lru_cache

from pydantic import PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: PostgresDsn


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
