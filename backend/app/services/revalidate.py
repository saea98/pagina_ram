from datetime import UTC, datetime

import httpx
from app.core.config import get_settings
from app.models.enums import JobType
from app.models.jobs import Job
from sqlalchemy.ext.asyncio import AsyncSession


def enqueue(session: AsyncSession, paths: list[str]) -> None:
    session.add(
        Job(
            type=JobType.REVALIDATE,
            payload={"paths": paths},
            run_after=datetime.now(UTC),
        )
    )


async def deliver(payload: dict[str, object]) -> None:
    settings = get_settings()
    if not settings.internal_revalidate_token:
        return
    paths = payload.get("paths")
    if not isinstance(paths, list):
        paths = []
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(
            f"{settings.web_internal_url.rstrip('/')}/api/_revalidate",
            json={"paths": paths},
            headers={"X-Internal-Token": settings.internal_revalidate_token},
        )
