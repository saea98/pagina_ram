import hashlib
from collections.abc import AsyncIterator
from typing import cast

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_CACHE = "public, max-age=60, stale-while-revalidate=300"


class PublicCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if request.query_params.get("preview"):
            response.headers["Cache-Control"] = "private, no-store"
            return response
        if not _cacheable(request, response):
            return response
        iterator = cast(AsyncIterator[bytes], response.body_iterator)  # type: ignore[attr-defined]
        body = b"".join([chunk async for chunk in iterator])
        etag = '"' + hashlib.sha256(body).hexdigest()[:32] + '"'
        headers = dict(response.headers)
        headers.pop("content-length", None)
        headers["Cache-Control"] = _CACHE
        headers["ETag"] = etag
        if request.headers.get("if-none-match") == etag:
            return Response(status_code=304, headers={"Cache-Control": _CACHE, "ETag": etag})
        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )


def _cacheable(request: Request, response: Response) -> bool:
    path = request.url.path
    if request.method != "GET" or response.status_code != 200:
        return False
    if not path.startswith("/api/v1/public"):
        return False
    return not path.endswith("/go")
