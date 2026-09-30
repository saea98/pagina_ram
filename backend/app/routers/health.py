import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import error_body

log = structlog.get_logger()
router = APIRouter(prefix="/api")


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", response_model=None)
async def ready(session: AsyncSession = Depends(get_session)) -> dict[str, str] | JSONResponse:
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        log.exception("database_unavailable")
        return JSONResponse(
            status_code=503,
            content=error_body("unavailable", "La base de datos no está disponible."),
        )
    return {"status": "ok"}
