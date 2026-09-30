import hashlib
import os
import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.errors import RateLimited, error_body

_HITS: dict[str, list[float]] = defaultdict(list)


def client_ip_hash(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        ip = forwarded.split(",", 1)[0].strip()
    elif request.client is not None:
        ip = request.client.host
    else:
        ip = "unknown"
    salt = get_settings().ip_hash_salt
    return hashlib.sha256(f"{ip}{salt}".encode()).hexdigest()


def enforce_limit(key: str, *, limit: int, window_s: float) -> None:
    now = time.monotonic()
    recent = [stamp for stamp in _HITS[key] if now - stamp < window_s]
    if len(recent) >= limit:
        _HITS[key] = recent
        raise RateLimited("Demasiadas solicitudes. Intenta más tarde.")
    recent.append(now)
    _HITS[key] = recent


limiter = Limiter(key_func=client_ip_hash, headers_enabled=False)


def register_rate_limit(app: FastAPI) -> None:
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def limited(_request: Request, _exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content=error_body("rate_limited", "Demasiadas solicitudes. Intenta más tarde."),
        )


def play_events_per_minute() -> int:
    raw = os.environ.get("PLAY_EVENTS_PER_MINUTE", "60")
    try:
        return max(1, int(raw))
    except ValueError:
        return 60
