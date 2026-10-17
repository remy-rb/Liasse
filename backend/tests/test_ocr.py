import json
from collections.abc import Callable
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from liasse.archive import Archive
from liasse.db import Document, Page, make_engine
from liasse.settings import Settings

FIXTURES = Path(__file__).parent / "fixtures"
EXPECTED: dict[str, list[list[str]]] = json.loads((FIXTURES / "expected.json").read_text())


def process(client: TestClient, run_worker: Callable[[], int], name: str, data: bytes) -> str:
    response = client.post("/api/documents", files=[("files", (name, data))])
    [document] = response.json()["accepted"]
    run_worker()
    return str(document["id"])


def page_texts(settings: Settings, document_id: str) -> list[str]:
    with Session(make_engine(settings)) as db:
        pages = db.scalars(
            select(Page).where(Page.document_id == document_id).order_by(Page.number)
        )
        return [page.text for page in pages]


def archived_pdf(settings: Settings, archive: Archive, document_id: str) -> PdfReader:
    with Session(make_engine(settings)) as db:
        document = db.get(Document, document_id)
        assert document is not None and document.archive_path is not None
        return PdfReader(BytesIO(archive.read(document.archive_path)))


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_ocr_reads_each_page_in_french_and_english(
    name: str, owner_client: TestClient, run_worker: Callable[[], int], settings: Settings
) -> None:
    document_id = process(owner_client, run_worker, name, (FIXTURES / name).read_bytes())

    texts = page_texts(settings, document_id)

    assert len(texts) == len(EXPECTED[name])
    for text, words in zip(texts, EXPECTED[name], strict=True):
        for word in words:
            assert word in text, f"{word!r} not found on a page of {name}: {text!r}"


def test_the_archived_pdf_has_a_text_layer(
    owner_client: TestClient,
    run_worker: Callable[[], int],
    settings: Settings,
    archive: Archive,
) -> None:
    name = "fr-facture-electricite.pdf"
    document_id = process(owner_client, run_worker, name, (FIXTURES / name).read_bytes())

    reader = archived_pdf(settings, archive, document_id)

    assert "Facture" in reader.pages[0].extract_text()
    assert "consommation" in reader.pages[1].extract_text()


def test_a_pdf_that_already_has_text_keeps_it(
    owner_client: TestClient,
    run_worker: Callable[[], int],
    settings: Settings,
    archive: Archive,
) -> None:
    name = "fr-facture-electricite.pdf"
    first = process(owner_client, run_worker, name, (FIXTURES / name).read_bytes())
    already_searchable = archive.read(archived_pdf_path(settings, first))

    second = process(owner_client, run_worker, "copy.pdf", already_searchable)

    texts = page_texts(settings, second)
    assert "Facture" in texts[0]
    assert "312 kWh" in texts[1]


def archived_pdf_path(settings: Settings, document_id: str) -> str:
    with Session(make_engine(settings)) as db:
        document = db.get(Document, document_id)
        assert document is not None and document.archive_path is not None
        return document.archive_path
