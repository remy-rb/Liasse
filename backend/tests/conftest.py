import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from liasse.db import make_engine
from liasse.main import create_app
from liasse.settings import Settings, get_settings

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://liasse:liasse@localhost:5432/liasse_test"
)
TEST_SESSION_SECRET = "test-session-secret-not-for-production"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(database_url=TEST_DATABASE_URL, session_secret=TEST_SESSION_SECRET)


@pytest.fixture(scope="session", autouse=True)
def migrated_database(settings: Settings) -> None:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["SESSION_SECRET"] = TEST_SESSION_SECRET
    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
def empty_database(settings: Settings) -> None:
    with make_engine(settings).begin() as connection:
        connection.execute(text("TRUNCATE owner CASCADE"))


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
