import hashlib
import hmac
import time
from uuid import UUID

from app.core.config import get_settings
from app.core.errors import AppError

_TTL_S = 60 * 60


class UploadTokenError(AppError):
    code = "validation_error"
    status_code = 422


def issue_upload_token(media_id: UUID) -> str:
    expires = int(time.time()) + _TTL_S
    payload = f"{media_id}.{expires}"
    return f"{payload}.{_sign(payload)}"


def read_upload_token(token: str) -> UUID:
    parts = token.split(".")
    if len(parts) != 3:
        raise UploadTokenError("La maqueta expiró o no es válida.")
    media_id, expires, signature = parts
    payload = f"{media_id}.{expires}"
    if not hmac.compare_digest(signature, _sign(payload)):
        raise UploadTokenError("La maqueta expiró o no es válida.")
    try:
        expiry = int(expires)
        parsed = UUID(media_id)
    except ValueError as exc:
        raise UploadTokenError("La maqueta expiró o no es válida.") from exc
    if expiry < int(time.time()):
        raise UploadTokenError("La maqueta expiró. Súbela de nuevo.")
    return parsed


def _sign(payload: str) -> str:
    secret = get_settings().secret_key.encode()
    return hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
