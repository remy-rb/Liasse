from typing import Literal

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

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


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="Liasse", version="0.1.0")
    app.state.engine = make_engine(settings)
    app.include_router(router)
    return app
