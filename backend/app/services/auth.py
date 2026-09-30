from datetime import UTC, datetime, timedelta

from app.core.config import get_settings
from app.core.errors import Unauthorized
from app.core.security import (
    LOCK_MINUTES,
    MAX_FAILURES,
    PREVIEW_MINUTES,
    REFRESH_DAYS,
    RESET_MINUTES,
    clear_auth_cookies,
    encode_access,
    hash_password,
    hash_token,
    new_secret,
    set_auth_cookies,
    verify_password,
)
from app.models.auth import PasswordResetToken, PreviewToken, RefreshToken
from app.models.enums import JobType
from app.models.jobs import Job
from app.models.users import User
from app.schemas.auth import PreviewTokenOut, UserOut
from fastapi import Request, Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def login(session: AsyncSession, response: Response, email: str, password: str) -> UserOut:
    user = await session.scalar(select(User).where(User.email == email.strip().lower()))
    now = datetime.now(UTC)
    if user is None or not user.is_active:
        raise Unauthorized("Correo o contraseña incorrectos.")
    if user.locked_until is not None and user.locked_until > now:
        raise Unauthorized("Demasiados intentos. Intenta de nuevo más tarde.")
    if not verify_password(password, user.password_hash):
        user.failed_logins += 1
        if user.failed_logins >= MAX_FAILURES:
            user.locked_until = now + timedelta(minutes=LOCK_MINUTES)
            user.failed_logins = 0
        await session.commit()
        raise Unauthorized("Correo o contraseña incorrectos.")
    user.failed_logins = 0
    user.locked_until = None
    user.last_login_at = now
    refresh = new_secret()
    csrf = new_secret()
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh),
            expires_at=now + timedelta(days=REFRESH_DAYS),
        )
    )
    await session.commit()
    set_auth_cookies(response, encode_access(user.id, user.role.value), refresh, csrf)
    return UserOut.model_validate(user)


async def refresh_session(session: AsyncSession, request: Request, response: Response) -> UserOut:
    raw = request.cookies.get("refresh_token", "")
    if not raw:
        raise Unauthorized("La sesión expiró. Entra de nuevo.")
    row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw))
    )
    now = datetime.now(UTC)
    if row is None or row.expires_at <= now:
        raise Unauthorized("La sesión expiró. Entra de nuevo.")
    if row.revoked_at is not None:
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == row.user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await session.commit()
        raise Unauthorized("La sesión ya no es válida. Entra de nuevo.")
    user = await session.get(User, row.user_id)
    if user is None or not user.is_active:
        raise Unauthorized("Necesitas iniciar sesión.")
    row.revoked_at = now
    refresh = new_secret()
    csrf = request.cookies.get("csrf_token") or new_secret()
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh),
            expires_at=now + timedelta(days=REFRESH_DAYS),
        )
    )
    await session.commit()
    set_auth_cookies(response, encode_access(user.id, user.role.value), refresh, csrf)
    return UserOut.model_validate(user)


async def logout(session: AsyncSession, request: Request, response: Response) -> None:
    raw = request.cookies.get("refresh_token", "")
    if raw:
        row = await session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw))
        )
        if row is not None and row.revoked_at is None:
            row.revoked_at = datetime.now(UTC)
            await session.commit()
    clear_auth_cookies(response)


async def forgot_password(session: AsyncSession, email: str) -> None:
    user = await session.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not user.is_active:
        return
    now = datetime.now(UTC)
    token = new_secret()
    session.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=now + timedelta(minutes=RESET_MINUTES),
        )
    )
    settings = get_settings()
    link = f"{settings.public_site_url.rstrip('/')}/admin/restablecer?token={token}"
    session.add(
        Job(
            type=JobType.SEND_EMAIL,
            payload={
                "template": "password_reset",
                "to": [user.email],
                "subject": "Restablece tu acceso a Cherry Studios",
                "context": {"name": user.full_name, "link": link},
            },
            run_after=now,
        )
    )
    await session.commit()


async def reset_password(session: AsyncSession, token: str, new_password: str) -> None:
    row = await session.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == hash_token(token))
    )
    now = datetime.now(UTC)
    if row is None or row.used_at is not None or row.expires_at <= now:
        raise Unauthorized("El enlace ya no es válido. Pide otro.")
    user = await session.get(User, row.user_id)
    if user is None:
        raise Unauthorized("El enlace ya no es válido. Pide otro.")
    user.password_hash = hash_password(new_password)
    user.failed_logins = 0
    user.locked_until = None
    row.used_at = now
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    await session.commit()


async def issue_preview(session: AsyncSession, user: User) -> PreviewTokenOut:
    now = datetime.now(UTC)
    token = new_secret()
    expires = now + timedelta(minutes=PREVIEW_MINUTES)
    session.add(PreviewToken(user_id=user.id, token_hash=hash_token(token), expires_at=expires))
    await session.commit()
    return PreviewTokenOut(token=token, expires_at=expires.isoformat())
