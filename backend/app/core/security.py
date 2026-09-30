import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import Response
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.errors import Unauthorized

_HASHER = PasswordHash.recommended()
_ALGORITHM = "HS256"
ACCESS_MINUTES = 15
REFRESH_DAYS = 7
LOCK_MINUTES = 15
MAX_FAILURES = 5
RESET_MINUTES = 60
PREVIEW_MINUTES = 120


def hash_password(password: str) -> str:
    return _HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _HASHER.verify(password, password_hash)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_secret() -> str:
    return secrets.token_urlsafe(32)


def encode_access(user_id: UUID, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_MINUTES),
    }
    return jwt.encode(payload, get_settings().secret_key, algorithm=_ALGORITHM)


def decode_access(token: str) -> dict[str, object]:
    try:
        decoded = jwt.decode(token, get_settings().secret_key, algorithms=[_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise Unauthorized("Necesitas iniciar sesión.") from exc
    if not isinstance(decoded, dict):
        raise Unauthorized("Necesitas iniciar sesión.")
    return decoded


def set_auth_cookies(response: Response, access: str, refresh: str, csrf: str) -> None:
    secure = get_settings().environment == "production"
    response.set_cookie(
        "access_token",
        access,
        max_age=ACCESS_MINUTES * 60,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api",
    )
    response.set_cookie(
        "refresh_token",
        refresh,
        max_age=REFRESH_DAYS * 24 * 3600,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api",
    )
    response.set_cookie(
        "csrf_token",
        csrf,
        max_age=REFRESH_DAYS * 24 * 3600,
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    secure = get_settings().environment == "production"
    response.delete_cookie("access_token", path="/api", secure=secure, samesite="lax")
    response.delete_cookie("refresh_token", path="/api", secure=secure, samesite="lax")
    response.delete_cookie("csrf_token", path="/", secure=secure, samesite="lax")
