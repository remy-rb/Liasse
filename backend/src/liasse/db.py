from collections.abc import Iterator
from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Request
from sqlalchemy import JSON, DateTime, Engine, ForeignKey, UniqueConstraint, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from liasse.settings import Settings


class Base(DeclarativeBase):
    pass


class Owner(Base):
    __tablename__ = "owner"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "category"
    __table_args__ = (UniqueConstraint("owner_id", "name"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("owner.id"), index=True)
    name: Mapped[str]


class Correspondent(Base):
    __tablename__ = "correspondent"
    __table_args__ = (UniqueConstraint("owner_id", "name"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("owner.id"), index=True)
    name: Mapped[str]


class Document(Base):
    __tablename__ = "document"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("owner.id"), index=True)
    # processing → filed or inbox; failed when processing breaks.
    status: Mapped[str]
    original_filename: Mapped[str]
    content_type: Mapped[str]
    page_count: Mapped[int]
    original_path: Mapped[str]
    archive_path: Mapped[str | None]
    failure_reason: Mapped[str | None]
    title: Mapped[str | None]
    category_id: Mapped[UUID | None] = mapped_column(ForeignKey("category.id"))
    correspondent_id: Mapped[UUID | None] = mapped_column(ForeignKey("correspondent.id"))
    document_date: Mapped[date | None]
    # What the model proposed and how sure it was, kept so the Inbox can show why.
    classification: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    category: Mapped[Category | None] = relationship()
    correspondent: Mapped[Correspondent | None] = relationship()
    # clock_timestamp, not now(): files uploaded together still get distinct, ordered times.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.clock_timestamp()
    )


class Page(Base):
    """The text of one page of a Document, as read by OCR."""

    __tablename__ = "page"
    __table_args__ = (UniqueConstraint("document_id", "number"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("document.id"))
    number: Mapped[int]  # 1-based, as people count pages
    text: Mapped[str]


class Job(Base):
    __tablename__ = "job"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("document.id"), index=True)
    # pending → running → done or failed
    state: Mapped[str] = mapped_column(default="pending")
    attempts: Mapped[int] = mapped_column(default=0)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped[Document] = relationship()


def make_engine(settings: Settings) -> Engine:
    return create_engine(str(settings.database_url), pool_pre_ping=True)


def get_db(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session
