import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionMaker
from app.core.storage import LocalStorage
from app.models.enums import JobStatus, JobType, MediaStatus
from app.models.jobs import Job
from app.models.media import MediaAsset
from app.workers.processing import (
    apply_audio_result,
    apply_image_result,
    render_audio,
    render_image,
)

log = structlog.get_logger()
_MAX_ATTEMPTS = 5


async def run_once(storage: LocalStorage) -> bool:
    async with SessionMaker() as session, session.begin():
        job = await _claim(session)
        if job is None:
            return False
        job_id = job.id
        job_type = job.type
        payload = dict(job.payload)
        attempts = job.attempts
    try:
        await _dispatch(storage, job_type, payload)
    except Exception as exc:
        log.exception("job_failed", job_id=str(job_id))
        await _mark_failed(job_id, attempts, exc)
        return True
    await _mark_done(job_id)
    return True


async def _claim(session: AsyncSession) -> Job | None:
    stmt = (
        select(Job)
        .where(Job.status == JobStatus.QUEUED, Job.run_after <= datetime.now(UTC))
        .order_by(Job.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = (await session.execute(stmt)).scalar_one_or_none()
    if job is None:
        return None
    job.status = JobStatus.RUNNING
    job.attempts += 1
    return job


async def _dispatch(storage: LocalStorage, job_type: JobType, payload: dict[str, object]) -> None:
    if job_type is JobType.SEND_EMAIL:
        from app.core.email import deliver

        await deliver(payload)
        return
    if job_type is JobType.REVALIDATE:
        from app.services.revalidate import deliver as revalidate

        await revalidate(payload)
        return
    media_id = UUID(str(payload["media_id"]))
    async with SessionMaker() as session:
        asset = await session.get(MediaAsset, media_id)
        if asset is None:
            raise LookupError(media_id)
        source = storage.path(asset.storage_key)
        sha = asset.sha256
    if job_type is JobType.PROCESS_IMAGE:
        variants, width, height, lqip = await asyncio.to_thread(render_image, source, sha, storage)
        async with SessionMaker() as session:
            await apply_image_result(session, media_id, variants, width, height, lqip)
            await session.commit()
        return
    if job_type is JobType.PROCESS_AUDIO:
        rendered = await asyncio.to_thread(render_audio, source, sha, storage)
        async with SessionMaker() as session:
            await apply_audio_result(session, media_id, rendered)
            await session.commit()
        return
    raise RuntimeError(f"Tipo de job no soportado: {job_type}")


async def _mark_done(job_id: UUID) -> None:
    async with SessionMaker() as session:
        job = await session.get(Job, job_id)
        if job is None:
            return
        job.status = JobStatus.DONE
        job.last_error = None
        await session.commit()


async def _mark_failed(job_id: UUID, attempts: int, exc: Exception) -> None:
    async with SessionMaker() as session:
        job = await session.get(Job, job_id)
        if job is None:
            return
        job.last_error = str(exc)[:2000]
        if attempts >= _MAX_ATTEMPTS:
            job.status = JobStatus.FAILED
            media_id = job.payload.get("media_id")
            if isinstance(media_id, str):
                asset = await session.get(MediaAsset, UUID(media_id))
                if asset is not None:
                    asset.status = MediaStatus.FAILED
        else:
            job.status = JobStatus.QUEUED
            job.run_after = datetime.now(UTC) + timedelta(seconds=2**attempts)
        await session.commit()
