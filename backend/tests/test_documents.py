from collections.abc import Callable
from io import BytesIO

from fastapi.testclient import TestClient
from files import encrypted_pdf, image, pdf
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from liasse.archive import Archive
from liasse.db import Document, Job, Owner, make_engine
from liasse.main import create_app
from liasse.settings import Settings
from liasse.worker import claim_next_job

Upload = tuple[str, bytes]


def upload(client: TestClient, *files: Upload) -> dict:  # type: ignore[type-arg]
    response = client.post(
        "/api/documents", files=[("files", (name, data)) for name, data in files]
    )
    assert response.status_code == 200, response.text
    return response.json()  # type: ignore[no-any-return]


def documents(client: TestClient) -> list[dict]:  # type: ignore[type-arg]
    return client.get("/api/documents").json()  # type: ignore[no-any-return]


def inbox_pdf(archive: Archive, client: TestClient, filename: str) -> PdfReader:
    owner_id = client.get("/api/me").json()["id"]
    return PdfReader(BytesIO(archive.read(f"{owner_id}/Inbox/{filename}")))


def test_an_uploaded_pdf_is_processing_until_the_worker_runs(owner_client: TestClient) -> None:
    result = upload(owner_client, ("letter.pdf", pdf(pages=2)))

    assert result["rejected"] == []
    [document] = result["accepted"]
    assert document["status"] == "processing"
    assert document["original_filename"] == "letter.pdf"
    assert document["page_count"] == 2
    assert documents(owner_client) == [document]


def test_the_worker_puts_the_document_in_the_inbox(
    owner_client: TestClient, archive: Archive, run_worker: Callable[[], int]
) -> None:
    upload(owner_client, ("letter.pdf", pdf(pages=2)))

    assert run_worker() == 1

    [document] = documents(owner_client)
    assert document["status"] == "inbox"
    assert len(inbox_pdf(archive, owner_client, "letter.pdf").pages) == 2


def test_the_untouched_original_is_kept(owner_client: TestClient, archive: Archive) -> None:
    original = image("JPEG")

    [document] = upload(owner_client, ("photo.jpg", original))["accepted"]

    owner_id = owner_client.get("/api/me").json()["id"]
    assert archive.read(f"{owner_id}/.originals/{document['id']}/photo.jpg") == original


def test_images_become_one_page_pdfs(
    owner_client: TestClient, archive: Archive, run_worker: Callable[[], int]
) -> None:
    result = upload(
        owner_client,
        ("a.jpg", image("JPEG")),
        ("b.png", image("PNG")),
        ("c.heic", image("HEIF")),
    )
    assert [d["page_count"] for d in result["accepted"]] == [1, 1, 1]

    run_worker()

    for name in ("a.pdf", "b.pdf", "c.pdf"):
        assert len(inbox_pdf(archive, owner_client, name).pages) == 1


def test_phone_photos_are_turned_upright(
    owner_client: TestClient, archive: Archive, run_worker: Callable[[], int]
) -> None:
    # EXIF orientation 6: the camera was turned; stored landscape pixels show a portrait page.
    upload(owner_client, ("receipt.jpg", image("JPEG", size=(300, 200), orientation=6)))
    run_worker()

    page = inbox_pdf(archive, owner_client, "receipt.pdf").pages[0]
    assert page.mediabox.height > page.mediabox.width


def test_unsupported_damaged_and_protected_files_are_rejected_with_a_reason(
    owner_client: TestClient,
) -> None:
    result = upload(
        owner_client,
        ("notes.txt", b"just some text"),
        ("broken.pdf", b"%PDF-1.7 this is not really a pdf"),
        ("locked.pdf", encrypted_pdf()),
        ("good.pdf", pdf()),
    )

    assert result["rejected"] == [
        {"filename": "notes.txt", "reason": "Only PDF, JPEG, PNG and HEIC files are supported."},
        {"filename": "broken.pdf", "reason": "This PDF is damaged and can't be read."},
        {"filename": "locked.pdf", "reason": "Password-protected PDFs aren't supported."},
    ]
    assert [d["original_filename"] for d in result["accepted"]] == ["good.pdf"]
    assert len(documents(owner_client)) == 1


def test_files_over_the_size_limit_are_rejected(settings: Settings) -> None:
    small = settings.model_copy(update={"upload_max_bytes": 2048})
    with TestClient(create_app(small)) as client:
        client.post("/api/auth/setup", json={"password": "correct horse battery staple"})

        result = upload(client, ("big.png", image("PNG", size=(800, 800)) + b"\0" * 4096))

    assert result["accepted"] == []
    assert result["rejected"][0]["reason"] == "This file is larger than 2 KB."


def test_requests_too_big_to_be_valid_are_refused_before_reading(
    owner_client: TestClient, settings: Settings
) -> None:
    too_big = str(settings.upload_max_bytes * 20 + 1)

    response = owner_client.post("/api/documents", content=b"", headers={"content-length": too_big})

    assert response.status_code == 413


def test_at_most_twenty_files_per_upload(owner_client: TestClient) -> None:
    files = [("files", (f"{n}.pdf", pdf())) for n in range(21)]

    response = owner_client.post("/api/documents", files=files)

    assert response.status_code == 422
    assert documents(owner_client) == []


def test_same_names_never_overwrite_each_other(
    owner_client: TestClient, archive: Archive, run_worker: Callable[[], int]
) -> None:
    upload(owner_client, ("scan.pdf", pdf(pages=1)), ("scan.pdf", pdf(pages=2)))
    run_worker()

    assert len(inbox_pdf(archive, owner_client, "scan.pdf").pages) == 1
    assert len(inbox_pdf(archive, owner_client, "scan-2.pdf").pages) == 2


def test_unsafe_file_names_are_cleaned(
    owner_client: TestClient, archive: Archive, run_worker: Callable[[], int]
) -> None:
    upload(owner_client, ("b:c?d<e>|f.pdf", pdf()))
    run_worker()

    assert len(inbox_pdf(archive, owner_client, "b-c-d-e-f.pdf").pages) == 1


def test_newest_documents_come_first(owner_client: TestClient) -> None:
    upload(owner_client, ("first.pdf", pdf()))
    upload(owner_client, ("second.pdf", pdf()), ("third.pdf", pdf()))

    assert [d["original_filename"] for d in documents(owner_client)] == [
        "third.pdf",
        "second.pdf",
        "first.pdf",
    ]


def test_owners_only_see_their_own_documents(owner_client: TestClient, settings: Settings) -> None:
    with Session(make_engine(settings)) as db:
        other = Owner(password_hash="x")
        db.add(other)
        db.flush()
        db.add(
            Document(
                owner_id=other.id,
                status="inbox",
                original_filename="someone-else.pdf",
                content_type="application/pdf",
                page_count=1,
                original_path="elsewhere",
            )
        )
        db.commit()

    upload(owner_client, ("mine.pdf", pdf()))

    assert [d["original_filename"] for d in documents(owner_client)] == ["mine.pdf"]


def test_uploading_and_listing_need_a_session(client: TestClient) -> None:
    assert client.get("/api/documents").status_code == 401
    assert client.post("/api/documents", files=[("files", ("a.pdf", pdf()))]).status_code == 401
    assert client.get("/api/upload-limits").status_code == 401


def test_upload_limits_are_published(owner_client: TestClient, settings: Settings) -> None:
    assert owner_client.get("/api/upload-limits").json() == {
        "max_bytes": settings.upload_max_bytes,
        "max_files": 20,
    }


def test_a_document_that_cannot_be_processed_is_marked_failed(
    owner_client: TestClient, archive: Archive, run_worker: Callable[[], int]
) -> None:
    [document] = upload(owner_client, ("photo.png", image("PNG")))["accepted"]
    owner_id = owner_client.get("/api/me").json()["id"]
    archive.write(f"{owner_id}/.originals/{document['id']}/photo.png", b"corrupted later")

    run_worker()

    [failed] = documents(owner_client)
    assert failed["status"] == "failed"
    assert failed["failure_reason"] == "Liasse couldn't process this file."


def test_two_workers_never_take_the_same_job(owner_client: TestClient, settings: Settings) -> None:
    upload(owner_client, ("only.pdf", pdf()))
    engine = make_engine(settings)

    with Session(engine) as first, Session(engine) as second:
        locked = first.scalar(select(Job).with_for_update())
        assert locked is not None

        assert claim_next_job(second) is None
