from pathlib import Path

import magic
from app.core.config import get_settings
from app.core.errors import NotFound
from app.core.storage import LocalStorage
from app.models.enums import MediaKind, MediaStatus, MediaVisibility
from app.models.media import MediaAsset
from app.schemas.admin import MediaAdminOut, Page
from app.services.media import UnsupportedMedia, ingest_upload
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _storage() -> LocalStorage:
    return LocalStorage(Path(get_settings().media_root))


def _preview(asset: MediaAsset) -> str | None:
    storage = _storage()
    if asset.kind is MediaKind.IMAGE and asset.status is MediaStatus.READY:
        webp = asset.variants.get("webp")
        if isinstance(webp, dict):
            key = webp.get("480") or webp.get("960") or next(iter(webp.values()), None)
            if isinstance(key, str):
                return storage.url(key)
    if asset.kind is MediaKind.AUDIO and asset.status is MediaStatus.READY:
        m4a = asset.variants.get("m4a")
        if isinstance(m4a, str):
            return storage.url(m4a)
    return None


def _out(asset: MediaAsset) -> MediaAdminOut:
    return MediaAdminOut(
        id=asset.id,
        kind=asset.kind,
        status=asset.status,
        original_filename=asset.original_filename,
        mime_type=asset.mime_type,
        alt_text=asset.alt_text,
        width=asset.width,
        height=asset.height,
        duration_s=None if asset.duration_s is None else float(asset.duration_s),
        lufs_integrated=None if asset.lufs_integrated is None else float(asset.lufs_integrated),
        preview_url=_preview(asset),
        created_at=asset.created_at,
    )


async def list_media(
    session: AsyncSession,
    kind: MediaKind | None,
    page: int,
    page_size: int,
) -> Page[MediaAdminOut]:
    query = select(MediaAsset).where(MediaAsset.visibility == MediaVisibility.PUBLIC)
    if kind is not None:
        query = query.where(MediaAsset.kind == kind)
    rows = list(await session.scalars(query.order_by(MediaAsset.created_at.desc())))
    sliced = rows[(page - 1) * page_size : page * page_size]
    return Page(
        items=[_out(asset) for asset in sliced],
        total=len(rows),
        page=page,
        page_size=page_size,
    )


async def get_media(session: AsyncSession, media_id: object) -> MediaAdminOut:
    asset = await session.get(MediaAsset, media_id)
    if asset is None:
        raise NotFound("No encontramos ese archivo.")
    return _out(asset)


async def upload_media(
    session: AsyncSession,
    upload: UploadFile,
    alt_text: str | None,
) -> MediaAdminOut:
    head = await upload.read(2048)
    await upload.seek(0)
    mime = magic.from_buffer(head, mime=True)
    if mime.startswith("image/") and not (alt_text and alt_text.strip()):
        raise UnsupportedMedia("Escribe el texto alternativo antes de guardar la imagen.")
    settings = get_settings()
    asset = await ingest_upload(
        session,
        _storage(),
        upload.file,
        filename=upload.filename or "archivo",
        visibility=MediaVisibility.PUBLIC,
        max_bytes=settings.max_upload_mb_admin * 1024 * 1024,
        alt_text=alt_text.strip() if alt_text else None,
    )
    return _out(asset)


async def set_alt(session: AsyncSession, media_id: object, alt_text: str) -> MediaAdminOut:
    asset = await session.get(MediaAsset, media_id)
    if asset is None:
        raise NotFound("No encontramos ese archivo.")
    asset.alt_text = alt_text.strip()
    await session.commit()
    return _out(asset)
