import secrets
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import Forbidden, Unauthorized
from app.core.preview import preview_active
from app.core.security import decode_access, hash_token
from app.models.auth import PreviewToken
from app.models.enums import UserRole
from app.models.users import User


async def require_csrf(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    cookie = request.cookies.get("csrf_token", "")
    header = request.headers.get("x-csrf-token", "")
    if not cookie or len(cookie) != len(header) or not secrets.compare_digest(cookie, header):
        raise Forbidden("Falta la verificación de seguridad. Recarga e intenta de nuevo.")


async def current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    raw = request.cookies.get("access_token")
    if not raw:
        raise Unauthorized("Necesitas iniciar sesión.")
    payload = decode_access(raw)
    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise Unauthorized("Necesitas iniciar sesión.")
    user = await session.get(User, UUID(subject))
    if user is None or not user.is_active:
        raise Unauthorized("Necesitas iniciar sesión.")
    return user


async def require_superadmin(user: Annotated[User, Depends(current_user)]) -> User:
    if user.role is not UserRole.SUPERADMIN:
        raise Forbidden("Solo un superadmin puede hacer esto.")
    return user


async def apply_preview(
    session: Annotated[AsyncSession, Depends(get_session)],
    preview: Annotated[str | None, Query()] = None,
) -> AsyncIterator[None]:
    token = preview_active.set(False)
    try:
        if preview:
            row = await session.scalar(
                select(PreviewToken).where(PreviewToken.token_hash == hash_token(preview))
            )
            if row is not None and row.expires_at > datetime.now(UTC):
                preview_active.set(True)
        yield
    finally:
        preview_active.reset(token)
