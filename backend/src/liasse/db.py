from collections.abc import Iterator
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import Request
from sqlalchemy import DateTime, Engine, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from liasse.settings import Settings


class Base(DeclarativeBase):
    pass


class Owner(Base):
    __tablename__ = "owner"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def make_engine(settings: Settings) -> Engine:
    return create_engine(str(settings.database_url), pool_pre_ping=True)


def get_db(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session
