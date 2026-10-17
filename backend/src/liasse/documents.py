from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from liasse.archive import Archive
from liasse.auth import CurrentOwner, require_owner
from liasse.db import Document, Job, get_db
from liasse.files import UnsupportedFile, inspect
from liasse.settings import Settings

MAX_FILES_PER_UPLOAD = 20

Db = Annotated[Session, Depends(get_db)]


class DocumentOut(BaseModel):
    id: UUID
    status: Literal["processing", "filed", "inbox", "failed"]
    original_filename: str
    title: str | None
    category: str | None
    correspondent: str | None
    document_date: date | None
    page_count: int
    failure_reason: str | None
    created_at: datetime

    @classmethod
    def of(cls, document: Document) -> "DocumentOut":
        return cls(
            id=document.id,
            status=document.status,
            original_filename=document.original_filename,
            title=document.title,
            category=document.category.name if document.category else None,
            correspondent=document.correspondent.name if document.correspondent else None,
            document_date=document.document_date,
            page_count=document.page_count,
            failure_reason=document.failure_reason,
            created_at=document.created_at,
        )


class Rejected(BaseModel):
    filename: str
    reason: str


class UploadResult(BaseModel):
    accepted: list[DocumentOut]
    rejected: list[Rejected]


class UploadLimits(BaseModel):
    max_bytes: int
    max_files: int


def get_archive(request: Request) -> Archive:
    archive: Archive = request.app.state.archive
    return archive


def get_settings_from_app(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


AppArchive = Annotated[Archive, Depends(get_archive)]
AppSettings = Annotated[Settings, Depends(get_settings_from_app)]


def readable_size(size: int) -> str:
    return f"{size // 1024**2} MB" if size >= 1024**2 else f"{size // 1024} KB"


def reject_oversized_request(request: Request, settings: AppSettings) -> None:
    """Refuse a request too big to be valid before reading its body."""
    length = request.headers.get("content-length")
    if (
        length
        and length.isdigit()
        and int(length) > settings.upload_max_bytes * MAX_FILES_PER_UPLOAD
    ):
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Upload is too large.")


router = APIRouter(prefix="/api", tags=["documents"], dependencies=[Depends(require_owner)])


@router.get("/upload-limits", operation_id="getUploadLimits")
def upload_limits(settings: AppSettings) -> UploadLimits:
    return UploadLimits(max_bytes=settings.upload_max_bytes, max_files=MAX_FILES_PER_UPLOAD)


@router.post(
    "/documents",
    operation_id="uploadDocuments",
    dependencies=[Depends(reject_oversized_request)],
)
def upload_documents(
    files: list[UploadFile], owner: CurrentOwner, db: Db, archive: AppArchive, settings: AppSettings
) -> UploadResult:
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Upload at most {MAX_FILES_PER_UPLOAD} files at once.",
        )
    accepted: list[Document] = []
    rejected: list[Rejected] = []
    for upload in files:
        filename = upload.filename or "document"
        data = upload.file.read(settings.upload_max_bytes + 1)
        try:
            if len(data) > settings.upload_max_bytes:
                raise UnsupportedFile(
                    f"This file is larger than {readable_size(settings.upload_max_bytes)}."
                )
            inspected = inspect(data)
        except UnsupportedFile as error:
            rejected.append(Rejected(filename=filename, reason=str(error)))
            continue
        document_id = uuid4()
        original_path = archive.original_path(owner.id, document_id, filename)
        # The untouched original is kept so the Document can be reprocessed later (ADR-0002).
        archive.write(original_path, data)
        document = Document(
            id=document_id,
            owner_id=owner.id,
            status="processing",
            original_filename=filename,
            content_type=inspected.content_type,
            page_count=inspected.page_count,
            original_path=original_path,
        )
        db.add_all([document, Job(document=document)])
        accepted.append(document)
    db.commit()
    return UploadResult(
        accepted=[DocumentOut.of(d) for d in accepted],
        rejected=rejected,
    )


@router.get("/documents", operation_id="listDocuments")
def list_documents(owner: CurrentOwner, db: Db) -> list[DocumentOut]:
    documents = db.scalars(
        select(Document)
        .options(selectinload(Document.category), selectinload(Document.correspondent))
        .where(Document.owner_id == owner.id)
        .order_by(Document.created_at.desc(), Document.id)
    )
    return [DocumentOut.of(d) for d in documents]
