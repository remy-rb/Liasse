import os
from collections.abc import Callable, Iterator

import fsspec
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from liasse.archive import Archive
from liasse.db import make_engine
from liasse.main import create_app
from liasse.models import Classification
from liasse.settings import Settings, get_settings
from liasse.worker import run_pending_jobs

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://liasse:liasse@localhost:5432/liasse_test"
)
TEST_SESSION_SECRET = "test-session-secret-not-for-production"
PASSWORD = "correct horse battery staple"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        database_url=TEST_DATABASE_URL,
        session_secret=TEST_SESSION_SECRET,
        storage_url="memory://archive",
    )


@pytest.fixture(scope="session", autouse=True)
def migrated_database(settings: Settings) -> None:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["SESSION_SECRET"] = TEST_SESSION_SECRET
    os.environ["STORAGE_URL"] = settings.storage_url
    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
def empty_database_and_archive(settings: Settings) -> None:
    with make_engine(settings).begin() as connection:
        connection.execute(
            text("TRUNCATE owner, document, job, page, category, correspondent CASCADE")
        )
    memory = fsspec.filesystem("memory")
    memory.store.clear()
    memory.pseudo_dirs.clear()
    memory.pseudo_dirs.append("")


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def owner_client(client: TestClient) -> TestClient:
    """A client logged in as the Owner of a freshly set-up install."""
    response = client.post("/api/auth/setup", json={"password": PASSWORD})
    assert response.status_code == 204
    return client


@pytest.fixture
def archive(settings: Settings) -> Archive:
    return Archive(settings.storage_url)


UNSURE = Classification(
    category=None,
    category_confidence=0.0,
    correspondent=None,
    correspondent_confidence=0.0,
    document_date=None,
    document_date_confidence=0.0,
    title="Unknown document",
)


class FakeModels:
    """Stands in for the LLM: returns `classification`, and records what it was asked."""

    def __init__(self) -> None:
        self.classification = UNSURE
        self.calls: list[tuple[str, list[str], list[str]]] = []

    def classify(
        self, text: str, categories: list[str], correspondents: list[str]
    ) -> Classification:
        self.calls.append((text, categories, correspondents))
        return self.classification


@pytest.fixture
def models() -> FakeModels:
    return FakeModels()


@pytest.fixture
def run_worker(settings: Settings, archive: Archive, models: FakeModels) -> Callable[[], int]:
    engine = make_engine(settings)
    return lambda: run_pending_jobs(engine, archive, models, settings.inbox_threshold)
