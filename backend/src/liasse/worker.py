"""Processes Documents in the background: `python -m liasse.worker`."""

import logging
import posixpath
import time

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from liasse.archive import Archive
from liasse.db import Job, make_engine
from liasse.files import to_pdf
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


def process(job: Job, archive: Archive) -> None:
    document = job.document
    pdf = to_pdf(archive.read(document.original_path), document.content_type)
    stem = posixpath.splitext(document.original_filename)[0]
    path = archive.inbox_path(document.owner_id, stem)
    archive.write(path, pdf)
    document.archive_path = path
    # Until automatic filing exists, every Document waits in the Inbox.
    document.status = "inbox"


def run_pending_jobs(engine: Engine, archive: Archive) -> int:
    """Process every pending job, one at a time. Returns how many were taken."""
    count = 0
    while True:
        with Session(engine) as db:
            job = claim_next_job(db)
            if job is None:
                return count
            count += 1
            try:
                process(job, archive)
                job.state = "done"
            except Exception as error:
                # shortcut: a failure is final for now; retries come with ticket 07.
                log.exception("Processing document %s failed", job.document_id)
                db.rollback()
                job.state = "failed"
                job.error = repr(error)
                job.document.status = "failed"
                job.document.failure_reason = "Liasse couldn't process this file."
            db.commit()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    settings = get_settings()
    engine, archive = make_engine(settings), Archive(settings.storage_url)
    log.info("Worker started")
    while True:
        if run_pending_jobs(engine, archive) == 0:
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
