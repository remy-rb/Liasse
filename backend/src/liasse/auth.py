from datetime import datetime
from typing import Annotated
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from liasse.db import Owner, get_db

hasher = PasswordHasher()

Db = Annotated[Session, Depends(get_db)]


class AuthStatus(BaseModel):
    setup_required: bool
    authenticated: bool


class SetupRequest(BaseModel):
    password: str = Field(min_length=8, max_length=1024)


class LoginRequest(BaseModel):
    password: str = Field(max_length=1024)


class Me(BaseModel):
    id: UUID
    created_at: datetime


def current_owner(request: Request, db: Session) -> Owner | None:
    owner_id = request.session.get("owner_id")
    return db.get(Owner, UUID(owner_id)) if owner_id else None


def require_owner(request: Request, db: Db) -> Owner:
    owner = current_owner(request, db)
    if owner is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not logged in")
    return owner


CurrentOwner = Annotated[Owner, Depends(require_owner)]

public = APIRouter(prefix="/api/auth", tags=["auth"])


@public.get("/status", operation_id="getAuthStatus")
def auth_status(request: Request, db: Db) -> AuthStatus:
    setup_required = db.scalar(select(Owner.id).limit(1)) is None
    return AuthStatus(
        setup_required=setup_required,
        authenticated=current_owner(request, db) is not None,
    )


@public.post("/setup", status_code=status.HTTP_204_NO_CONTENT, operation_id="setUp")
def set_up(body: SetupRequest, request: Request, db: Db) -> None:
    # Lock so two first-run requests can't both create an Owner.
    db.execute(text("LOCK TABLE owner IN EXCLUSIVE MODE"))
    if db.scalar(select(Owner.id).limit(1)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Liasse is already set up")
    owner = Owner(password_hash=hasher.hash(body.password))
    db.add(owner)
    db.commit()
    request.session["owner_id"] = str(owner.id)


# shortcut: no rate limiting on login (argon2 makes each guess slow); add it before exposing
# Liasse to the internet.
@public.post("/login", status_code=status.HTTP_204_NO_CONTENT, operation_id="logIn")
def log_in(body: LoginRequest, request: Request, db: Db) -> None:
    # Single Owner per install for now (ADR-0001), so the password alone identifies them.
    owner = db.scalar(select(Owner).limit(1))
    try:
        if owner is None:
            raise VerifyMismatchError
        hasher.verify(owner.password_hash, body.password)
    except VerifyMismatchError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password") from None
    request.session["owner_id"] = str(owner.id)


@public.post("/logout", status_code=status.HTTP_204_NO_CONTENT, operation_id="logOut")
def log_out(request: Request) -> None:
    request.session.clear()


# Every route on this router needs a logged-in Owner.
protected = APIRouter(prefix="/api", dependencies=[Depends(require_owner)])


@protected.get("/me", operation_id="getMe")
def me(owner: CurrentOwner) -> Me:
    return Me(id=owner.id, created_at=owner.created_at)
