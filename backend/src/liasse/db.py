from collections.abc import Iterator
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import Request
from sqlalchemy import DateTime, Engine, ForeignKey, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from liasse.settings import Settings


class Base(DeclarativeBase):
    pass


class Owner(Base):
    __tablename__ = "owner"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "document"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("owner.id"), index=True)
    # processing → inbox, or failed (filed comes with automatic filing).
    status: Mapped[str]
    original_filename: Mapped[str]
    content_type: Mapped[str]
    page_count: Mapped[int]
    original_path: Mapped[str]
    archive_path: Mapped[str | None]
    failure_reason: Mapped[str | None]
    # clock_timestamp, not now(): files uploaded together still get distinct, ordered times.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.clock_timestamp()
    )


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
