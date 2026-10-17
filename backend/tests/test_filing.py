from collections.abc import Callable
from datetime import date
from typing import Any

import pytest
from conftest import FakeModels
from fastapi.testclient import TestClient
from files import pdf
from sqlalchemy import select
from sqlalchemy.orm import Session

from liasse.archive import Archive
from liasse.categories import DEFAULT_CATEGORIES
from liasse.db import Correspondent, Document, make_engine
from liasse.models import Classification, InvalidModelOutput, LiteLLMModels, parse_classification
from liasse.settings import Settings
from liasse.worker import run_pending_jobs

EDF_INVOICE = Classification(
    category="Invoices",
    category_confidence=0.95,
    correspondent="EDF",
    correspondent_confidence=0.9,
    document_date=date(2025, 3, 14),
    document_date_confidence=0.92,
    title="Facture électricité",
)


def upload(client: TestClient, name: str = "scan.pdf") -> None:
    response = client.post("/api/documents", files=[("files", (name, pdf()))])
    assert response.status_code == 200


def documents(client: TestClient) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = client.get("/api/documents").json()
    return result


def owner_id(client: TestClient) -> str:
    return str(client.get("/api/me").json()["id"])


def test_a_confident_classification_files_the_document(
    owner_client: TestClient,
    run_worker: Callable[[], int],
    models: FakeModels,
    archive: Archive,
) -> None:
    models.classification = EDF_INVOICE
    upload(owner_client)

    run_worker()

    [document] = documents(owner_client)
    assert document["status"] == "filed"
    assert document["category"] == "Invoices"
    assert document["correspondent"] == "EDF"
    assert document["document_date"] == "2025-03-14"
    assert document["title"] == "Facture électricité"
    owner = owner_id(owner_client)
    assert archive.exists(f"{owner}/Invoices/EDF/2025-03-14_EDF_Facture-électricité.pdf")
    assert not archive.exists(f"{owner}/Inbox/scan.pdf")


def test_the_model_sees_the_text_and_the_owners_categories_and_correspondents(
    owner_client: TestClient, run_worker: Callable[[], int], models: FakeModels
) -> None:
    models.classification = EDF_INVOICE
    upload(owner_client)
    run_worker()
    upload(owner_client)
    run_worker()

    [(_, categories, first_correspondents), (_, _, second_correspondents)] = models.calls
    assert sorted(categories) == sorted(DEFAULT_CATEGORIES)
    assert first_correspondents == []
    assert second_correspondents == ["EDF"]


def test_ocr_text_is_what_gets_classified(
    owner_client: TestClient, run_worker: Callable[[], int], models: FakeModels
) -> None:
    from test_ocr import FIXTURES

    name = "fr-facture-electricite.pdf"
    owner_client.post("/api/documents", files=[("files", (name, (FIXTURES / name).read_bytes()))])
    run_worker()

    [(text, _, _)] = models.calls
    assert "Facture" in text
    assert "312 kWh" in text  # the second page too


def test_an_existing_correspondent_is_reused_whatever_the_case(
    owner_client: TestClient,
    run_worker: Callable[[], int],
    models: FakeModels,
    archive: Archive,
    settings: Settings,
) -> None:
    models.classification = EDF_INVOICE
    upload(owner_client)
    run_worker()
    models.classification = EDF_INVOICE.model_copy(update={"correspondent": "edf"})
    upload(owner_client)
    run_worker()

    assert [d["correspondent"] for d in documents(owner_client)] == ["EDF", "EDF"]
    assert archive.exists(
        f"{owner_id(owner_client)}/Invoices/EDF/2025-03-14_EDF_Facture-électricité-2.pdf"
    )
    with Session(make_engine(settings)) as db:
        assert db.scalars(select(Correspondent.name)).all() == ["EDF"]


@pytest.mark.parametrize(
    "unsure",
    [
        {"category_confidence": 0.4},
        {"correspondent_confidence": 0.69},
        {"document_date_confidence": 0.2},
        {"category": None},
        {"category": "Groceries"},
        {"correspondent": None},
        {"document_date": None},
    ],
)
def test_anything_uncertain_goes_to_the_inbox_with_the_guesses_kept(
    unsure: dict[str, Any],
    owner_client: TestClient,
    run_worker: Callable[[], int],
    models: FakeModels,
    archive: Archive,
    settings: Settings,
) -> None:
    models.classification = EDF_INVOICE.model_copy(update=unsure)
    upload(owner_client)

    run_worker()

    [document] = documents(owner_client)
    assert document["status"] == "inbox"
    assert document["category"] is None and document["correspondent"] is None
    assert archive.exists(f"{owner_id(owner_client)}/Inbox/scan.pdf")
    with Session(make_engine(settings)) as db:
        stored = db.scalars(select(Document)).one()
        assert stored.classification == models.classification.model_dump(mode="json")
        # Only Filed Documents create Correspondents.
        assert db.scalars(select(Correspondent)).all() == []


def test_the_inbox_threshold_is_a_setting(
    owner_client: TestClient, models: FakeModels, archive: Archive, settings: Settings
) -> None:
    models.classification = EDF_INVOICE.model_copy(update={"category_confidence": 0.6})
    upload(owner_client)

    run_pending_jobs(make_engine(settings), archive, models, threshold=0.5)

    assert documents(owner_client)[0]["status"] == "filed"


def test_names_are_made_safe_for_every_filesystem(
    owner_client: TestClient,
    run_worker: Callable[[], int],
    models: FakeModels,
    archive: Archive,
) -> None:
    models.classification = EDF_INVOICE.model_copy(
        update={"correspondent": "AC/DC: Énergie", "title": "Avis d'échéance?"}
    )
    upload(owner_client)

    run_worker()

    folder = f"{owner_id(owner_client)}/Invoices/AC-DC- Énergie"
    assert archive.exists(f"{folder}/2025-03-14_AC-DC- Énergie_Avis-d'échéance.pdf")


def test_unreadable_model_output_marks_the_document_failed(
    owner_client: TestClient, run_worker: Callable[[], int], models: FakeModels
) -> None:
    def broken(*_: object) -> Classification:
        raise InvalidModelOutput("The model's classification couldn't be read.")

    models.classify = broken  # type: ignore[method-assign, assignment]
    upload(owner_client)

    run_worker()

    [document] = documents(owner_client)
    assert document["status"] == "failed"
    assert document["failure_reason"] == "The model's classification couldn't be read."


def test_new_owners_start_with_the_default_categories(
    owner_client: TestClient, run_worker: Callable[[], int], models: FakeModels
) -> None:
    upload(owner_client)
    run_worker()

    [(_, categories, _)] = models.calls
    assert "Other" not in categories
    assert len(categories) == 10


class TestParsingTheModelsAnswer:
    ANSWER = (
        '{"category": "Payslips", "category_confidence": 0.9, "correspondent": "Acme", '
        '"correspondent_confidence": 0.8, "document_date": "2025-03-31", '
        '"document_date_confidence": 0.95, "title": "Payslip"}'
    )

    def test_plain_json(self) -> None:
        assert parse_classification(self.ANSWER).correspondent == "Acme"

    def test_json_in_a_code_fence_after_a_preamble(self) -> None:
        answer = f"Here is the classification:\n```json\n{self.ANSWER}\n```"
        assert parse_classification(answer).document_date == date(2025, 3, 31)

    @pytest.mark.parametrize(
        "answer",
        [
            "I can't tell what this is.",
            "{not json}",
            '{"category": "Payslips"}',
            ANSWER.replace("0.9", "1.7"),
        ],
    )
    def test_unusable_answers_are_rejected(self, answer: str) -> None:
        with pytest.raises(InvalidModelOutput):
            parse_classification(answer)


def test_the_worker_refuses_to_start_without_an_llm(settings: Settings) -> None:
    with pytest.raises(SystemExit) as exit_info:
        LiteLLMModels(settings.model_copy(update={"llm_model": None}))

    assert "LLM_MODEL" in str(exit_info.value)
