from collections.abc import Sequence
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = structlog.get_logger()

_TYPE_MESSAGES: dict[str, str] = {
    "missing": "Este campo es obligatorio.",
    "string_type": "Debe ser texto.",
    "int_type": "Debe ser un número entero.",
    "int_parsing": "Debe ser un número entero.",
    "float_type": "Debe ser un número.",
    "float_parsing": "Debe ser un número.",
    "bool_type": "Debe ser verdadero o falso.",
    "bool_parsing": "Debe ser verdadero o falso.",
    "datetime_type": "Debe ser una fecha y hora.",
    "date_type": "Debe ser una fecha.",
    "url_type": "Debe ser una URL válida.",
    "url_parsing": "Debe ser una URL válida.",
    "uuid_type": "Debe ser un identificador válido.",
    "uuid_parsing": "Debe ser un identificador válido.",
    "string_too_short": "Es demasiado corto.",
    "string_too_long": "Es demasiado largo.",
    "extra_forbidden": "Este campo no está permitido.",
    "enum": "El valor no es válido.",
    "literal_error": "El valor no es válido.",
    "value_error": "El valor no es válido.",
}

_HTTP_ERRORS: dict[int, tuple[str, str]] = {
    400: ("bad_request", "La solicitud no es válida."),
    401: ("unauthorized", "Necesitas iniciar sesión."),
    403: ("forbidden", "No tienes permiso para hacer esto."),
    404: ("not_found", "No encontramos lo que buscas."),
    405: ("method_not_allowed", "Ese método no está permitido."),
    409: ("conflict", "El recurso ya existe o está en conflicto."),
    422: ("validation_error", "Revisa los datos enviados."),
    429: ("rate_limited", "Demasiadas solicitudes. Intenta más tarde."),
}


class AppError(Exception):
    code = "error"
    status_code = 400

    def __init__(self, message: str, *, fields: dict[str, str] | None = None) -> None:
        self.message = message
        self.fields = fields
        super().__init__(message)


class Unauthorized(AppError):
    code = "unauthorized"
    status_code = 401


class NotFound(AppError):
    code = "not_found"
    status_code = 404


class Conflict(AppError):
    code = "conflict"
    status_code = 409


class Forbidden(AppError):
    code = "forbidden"
    status_code = 403


class RateLimited(AppError):
    code = "rate_limited"
    status_code = 429


def error_body(
    code: str,
    message: str,
    fields: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    error: dict[str, Any] = {"code": code, "message": message}
    if fields:
        error["fields"] = fields
    return {"error": error}


def fields_from_validation(errors: Sequence[Any]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for item in errors:
        location = item.get("loc", ())
        parts = [str(part) for part in location if part not in {"body", "query", "path"}]
        name = ".".join(parts) or "body"
        if name in fields:
            continue
        error_type = str(item.get("type", ""))
        fields[name] = _TYPE_MESSAGES.get(error_type, "El valor no es válido.")
    return fields


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.code, exc.message, exc.fields),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_body(
                "validation_error",
                "Revisa los datos enviados.",
                fields_from_validation(exc.errors()),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, message = _HTTP_ERRORS.get(
            exc.status_code,
            ("http_error", "No se pudo completar la solicitud."),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(code, message),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled_error", error_type=type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content=error_body("internal_error", "Ocurrió un error interno."),
        )
