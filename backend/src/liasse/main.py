from typing import Literal

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.sessions import SessionMiddleware

from liasse import auth, documents
from liasse.archive import Archive
from liasse.db import make_engine
from liasse.settings import Settings, get_settings


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["ok", "unreachable"]


router = APIRouter(prefix="/api")


@router.get("/health", operation_id="getHealth")
def health(request: Request) -> Health:
    try:
        with request.app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return Health(status="degraded", database="unreachable")
    return Health(status="ok", database="ok")


SESSION_MAX_AGE = 60 * 60 * 24 * 30  # Stay logged in for 30 days.


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="Liasse", version="0.1.0")
    app.state.settings = settings
    app.state.engine = make_engine(settings)
    app.state.archive = Archive(settings.storage_url)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret.get_secret_value(),
        session_cookie="liasse_session",
        max_age=SESSION_MAX_AGE,
        same_site="lax",
        https_only=settings.session_cookie_secure,
    )
    app.include_router(router)
    app.include_router(auth.public)
    app.include_router(auth.protected)
    app.include_router(documents.router)
    return app
