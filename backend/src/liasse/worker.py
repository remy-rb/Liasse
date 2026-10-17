"""Processes Documents in the background: `python -m liasse.worker`."""

import logging
import posixpath
import time
from uuid import UUID

from sqlalchemy import Engine, delete, func, select
from sqlalchemy.orm import Session

from liasse.archive import Archive
from liasse.db import Category, Correspondent, Document, Job, Page, make_engine
from liasse.files import to_pdf
from liasse.models import Classification, InvalidModelOutput, LiteLLMModels, Models
from liasse.ocr import ocr
from liasse.settings import get_settings

log = logging.getLogger("liasse.worker")
POLL_SECONDS = 1.0


def claim_next_job(db: Session) -> Job | None:
    # SKIP LOCKED lets several workers run without ever taking the same job.
    job = db.scalar(
        select(Job)
        .where(Job.state == "pending")
        .order_by(Job.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    if job is not None:
        job.state = "running"
        job.attempts += 1
        job.claimed_at = func.now()
        db.commit()
    return job


def is_confident(classification: Classification, threshold: float) -> bool:
    return (
        classification.category is not None
        and bool(classification.correspondent)
        and classification.document_date is not None
        and min(
            classification.category_confidence,
            classification.correspondent_confidence,
            classification.document_date_confidence,
        )
        >= threshold
    )


def find_or_create_correspondent(db: Session, owner_id: UUID, name: str) -> Correspondent:
    existing = db.scalars(select(Correspondent).where(Correspondent.owner_id == owner_id))
    # The model is asked to reuse existing names exactly; this also forgives a change of case.
    for correspondent in existing:
        if correspondent.name.casefold() == name.strip().casefold():
            return correspondent
    correspondent = Correspondent(owner_id=owner_id, name=name.strip())
    db.add(correspondent)
    return correspondent


def file_document(
    document: Document,
    text: str,
    db: Session,
    archive: Archive,
    models: Models,
    threshold: float,
) -> str:
    """Classify the Document, then file it or leave it in the Inbox. Returns its Archive path."""
    owner_id = document.owner_id
    categories = list(db.scalars(select(Category).where(Category.owner_id == owner_id)))
    correspondents = db.scalars(
        select(Correspondent.name).where(Correspondent.owner_id == owner_id)
    )
    classification = models.classify(text, [c.name for c in categories], list(correspondents))
    document.title = classification.title
    document.classification = classification.model_dump(mode="json")
    category = next((c for c in categories if c.name == classification.category), None)

    if category is None or not is_confident(classification, threshold):
        document.status = "inbox"
        return archive.inbox_path(owner_id, posixpath.splitext(document.original_filename)[0])

    assert classification.correspondent and classification.document_date
    correspondent = find_or_create_correspondent(db, owner_id, classification.correspondent)
    document.category = category
    document.correspondent = correspondent
    document.document_date = classification.document_date
    document.status = "filed"
    return archive.filed_path(
        owner_id,
        category.name,
        correspondent.name,
        classification.document_date,
        classification.title,
    )


def process(job: Job, db: Session, archive: Archive, models: Models, threshold: float) -> None:
    document = job.document
    pdf = to_pdf(archive.read(document.original_path), document.content_type)
    searchable, texts = ocr(pdf)
    # Replace, not add: a Document may be processed again.
    db.execute(delete(Page).where(Page.document_id == document.id))
    db.add_all(
        Page(document_id=document.id, number=number, text=text)
        for number, text in enumerate(texts, start=1)
    )
    path = file_document(document, "\n\n".join(texts), db, archive, models, threshold)
    archive.write(path, searchable)
    document.archive_path = path


def run_pending_jobs(engine: Engine, archive: Archive, models: Models, threshold: float) -> int:
    """Process every pending job, one at a time. Returns how many were taken."""
    count = 0
    while True:
        with Session(engine) as db:
            job = claim_next_job(db)
            if job is None:
                return count
            count += 1
            try:
                process(job, db, archive, models, threshold)
                job.state = "done"
            except Exception as error:
                # shortcut: a failure is final for now; retries come with ticket 07.
                log.exception("Processing document %s failed", job.document_id)
                db.rollback()
                job.state = "failed"
                job.error = repr(error)
                job.document.status = "failed"
                job.document.failure_reason = (
                    str(error)
                    if isinstance(error, InvalidModelOutput)
                    else "Liasse couldn't process this file."
                )
            db.commit()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    settings = get_settings()
    engine, archive = make_engine(settings), Archive(settings.storage_url)
    models = LiteLLMModels(settings)
    log.info("Worker started, classifying with %s", settings.llm_model)
    while True:
        if run_pending_jobs(engine, archive, models, settings.inbox_threshold) == 0:
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
