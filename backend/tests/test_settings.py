import pytest

from liasse.settings import load_settings


def test_missing_database_url_stops_startup_naming_the_setting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit) as exit_info:
        load_settings()

    assert "DATABASE_URL" in str(exit_info.value)


def test_invalid_database_url_stops_startup_naming_the_setting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "not-a-url")

    with pytest.raises(SystemExit) as exit_info:
        load_settings()

    assert "DATABASE_URL" in str(exit_info.value)


def test_short_session_secret_stops_startup_naming_the_setting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://liasse:liasse@localhost/liasse")
    monkeypatch.setenv("SESSION_SECRET", "too-short")

    with pytest.raises(SystemExit) as exit_info:
        load_settings()

    assert "SESSION_SECRET" in str(exit_info.value)
