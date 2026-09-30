import hashlib
from datetime import UTC, datetime
from io import BytesIO
from typing import BinaryIO

import magic
from app.core.errors import AppError
from app.core.storage import LocalStorage
from app.models.enums import JobType, MediaKind, MediaStatus, MediaVisibility
from app.models.jobs import Job
from app.models.media import MediaAsset
from sqlalchemy.ext.asyncio import AsyncSession

_ALLOWED = {
    "image/jpeg": (MediaKind.IMAGE, ".jpg"),
    "image/png": (MediaKind.IMAGE, ".png"),
    "image/webp": (MediaKind.IMAGE, ".webp"),
    "image/avif": (MediaKind.IMAGE, ".avif"),
    "audio/mpeg": (MediaKind.AUDIO, ".mp3"),
    "audio/wav": (MediaKind.AUDIO, ".wav"),
    "audio/x-wav": (MediaKind.AUDIO, ".wav"),
    "audio/flac": (MediaKind.AUDIO, ".flac"),
    "audio/mp4": (MediaKind.AUDIO, ".m4a"),
    "audio/x-m4a": (MediaKind.AUDIO, ".m4a"),
    "audio/aac": (MediaKind.AUDIO, ".aac"),
}


class UnsupportedMedia(AppError):
    code = "validation_error"
    status_code = 422


class UploadTooLarge(AppError):
    code = "validation_error"
    status_code = 422


async def ingest_upload(
    session: AsyncSession,
    storage: LocalStorage,
    stream: BinaryIO,
    *,
    filename: str,
    visibility: MediaVisibility,
    max_bytes: int,
    alt_text: str | None = None,
    process: bool = True,
) -> MediaAsset:
    digest = hashlib.sha256()
    buffer = BytesIO()
    size = 0
    head = b""
    while chunk := stream.read(1024 * 1024):
        size += len(chunk)
        if size > max_bytes:
            raise UploadTooLarge("El archivo supera el tamaño permitido.")
        if len(head) < 2048:
            head += chunk[: 2048 - len(head)]
        digest.update(chunk)
        buffer.write(chunk)

    mime = magic.from_buffer(head, mime=True)
    kind_and_ext = _ALLOWED.get(mime)
    if kind_and_ext is None:
        raise UnsupportedMedia("Ese tipo de archivo no está permitido.")
    kind, extension = kind_and_ext
    sha = digest.hexdigest()
    key = f"private/originals/{sha}{extension}"
    buffer.seek(0)
    storage.save(buffer, key)

    asset = MediaAsset(
        kind=kind,
        visibility=visibility,
        original_filename=filename,
        mime_type=mime,
        size_bytes=size,
        storage_key=key,
        status=MediaStatus.PROCESSING if process else MediaStatus.READY,
        variants={},
        alt_text=alt_text,
        sha256=sha,
    )
    session.add(asset)
    await session.flush()
    if process:
        job_type = JobType.PROCESS_IMAGE if kind is MediaKind.IMAGE else JobType.PROCESS_AUDIO
        session.add(
            Job(
                type=job_type,
                payload={"media_id": str(asset.id)},
                run_after=datetime.now(UTC),
            )
        )
    await session.commit()
    return asset
