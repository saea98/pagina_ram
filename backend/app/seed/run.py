import asyncio
import hashlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import UUID

import nh3
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import SessionMaker
from app.core.storage import LocalStorage
from app.models.content import BioLink, PortfolioItem, Service, TeamMember
from app.models.enums import MediaStatus, MediaVisibility, PortfolioKind, UserRole
from app.models.media import MediaAsset
from app.models.users import SiteSettings, User
from app.schemas.site import SiteSettingsSchema
from app.seed.catalog import (
    CONSENT_TEXT,
    CONTACT_EMAIL,
    INSTAGRAM_URL,
    PRIVACY_UPDATED_AT,
    SERVICES,
    STUDIO_ALT,
    TEAM,
)
from app.services.media import ingest_upload
from app.workers.loop import run_once

_HASHER = PasswordHash.recommended()
_READY_TIMEOUT_S = 180


@dataclass(frozen=True)
class _Piece:
    slug: str
    title: str
    artist_name: str
    kind: PortfolioKind
    external_url: str
    external_id: str
    sort_order: int
    youtube_start_s: int | None = None
    audio_key: str | None = None


def template_root() -> Path:
    configured = get_settings().template_root
    fallback = Path(__file__).resolve().parents[3] / "cherry-studios-site"
    path = Path(configured) if configured else fallback
    if not path.is_dir():
        raise RuntimeError(f"No se encontró el template en {path}")
    return path


def privacy_html(root: Path) -> str:
    raw = (root / "aviso-de-privacidad.html").read_text(encoding="utf-8")
    start = raw.index("<main>") + len("<main>")
    end = raw.index("</main>")
    return nh3.clean(raw[start:end].strip())


async def run_seed() -> None:
    settings = get_settings()
    if not settings.seed_admin_email or not settings.seed_admin_password:
        raise RuntimeError("Faltan SEED_ADMIN_EMAIL y SEED_ADMIN_PASSWORD.")
    root = template_root()
    storage = LocalStorage(Path(settings.media_root))
    media = await _load_media(root, storage)
    async with SessionMaker() as session:
        admin = await _ensure_admin(session)
        await _ensure_settings(session, root, media, admin.id)
        await _ensure_services(session)
        await _ensure_team(session, media)
        await _ensure_portfolio(session, media)
        await _ensure_links(session)
        await session.commit()


async def _load_media(root: Path, storage: LocalStorage) -> dict[str, MediaAsset]:
    images = root / "images"
    loaded = {
        "hero": await _ensure_media(storage, images / "hero.jpg", "Portada de Cherry Studios"),
        "studio": await _ensure_media(storage, images / "estudio.jpg", STUDIO_ALT),
        "logo": await _ensure_media(storage, images / "logo-fused-crudo.png", "Cherry Studios"),
        "logo_alt": await _ensure_media(
            storage,
            images / "logo-fused-color-noborde.png",
            "Cherry Studios",
        ),
    }
    for member in TEAM:
        loaded[member["photo"]] = await _ensure_media(
            storage,
            images / member["photo"],
            member["alt"],
        )
    loaded["neto"] = await _ensure_media(
        storage,
        root / "audio" / "neto-live-session.mp3",
        None,
    )
    return loaded


async def _ensure_media(storage: LocalStorage, path: Path, alt_text: str | None) -> MediaAsset:
    payload = await asyncio.to_thread(path.read_bytes)
    digest = hashlib.sha256(payload).hexdigest()
    async with SessionMaker() as session:
        existing = await session.scalar(select(MediaAsset).where(MediaAsset.sha256 == digest))
        existing_id = existing.id if existing is not None else None
        existing_status = existing.status if existing is not None else None
    if existing_id is not None and existing_status is MediaStatus.READY:
        async with SessionMaker() as session:
            ready = await session.get(MediaAsset, existing_id)
            assert ready is not None
            return ready
    if existing_id is None:
        async with SessionMaker() as session:
            created = await ingest_upload(
                session,
                storage,
                BytesIO(payload),
                filename=path.name,
                visibility=MediaVisibility.PUBLIC,
                max_bytes=get_settings().max_upload_mb_admin * 1024 * 1024,
                alt_text=alt_text,
            )
            existing_id = created.id
    return await _wait_ready(storage, existing_id)


async def _wait_ready(storage: LocalStorage, asset_id: object) -> MediaAsset:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + _READY_TIMEOUT_S
    while loop.time() < deadline:
        await run_once(storage)
        async with SessionMaker() as session:
            asset = await session.get(MediaAsset, asset_id)
            if asset is not None and asset.status is MediaStatus.READY:
                return asset
            if asset is not None and asset.status is MediaStatus.FAILED:
                raise RuntimeError(f"El medio {asset_id} falló al procesarse.")
        await asyncio.sleep(0.2)
    raise RuntimeError(f"El medio {asset_id} no quedó listo a tiempo.")


async def _ensure_admin(session: AsyncSession) -> User:
    settings = get_settings()
    found = await session.scalar(select(User).where(User.email == settings.seed_admin_email))
    if found is not None:
        return found
    user = User(
        email=settings.seed_admin_email,
        full_name="Cherry Studios",
        password_hash=_HASHER.hash(settings.seed_admin_password),
        role=UserRole.SUPERADMIN,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return user


async def _ensure_settings(
    session: AsyncSession,
    root: Path,
    media: dict[str, MediaAsset],
    updated_by: UUID,
) -> None:
    if await session.get(SiteSettings, 1) is not None:
        return
    schema = SiteSettingsSchema.model_validate(
        {
            "brand": {
                "name": "Cherry Studios",
                "tagline": "Que la emoción te lleve a donde la mente no puede",
                "logo_media_id": str(media["logo"].id),
                "logo_alt_media_id": str(media["logo_alt"].id),
            },
            "hero": {
                "quote": "Que la emoción te lleve a donde la mente no puede",
                "title_html": "Tu música, tu proceso y <em>nuestra cereza.</em>",
                "cta_primary_text": "Ver servicios",
                "cta_secondary_text": "Cuéntanos tu proyecto",
                "image_media_id": str(media["hero"].id),
            },
            "studio": {
                "eyebrow": "El estudio",
                "title": "Cada canción parte de una emoción real.",
                "body": (
                    "Bajo esa premisa trabajan Chemita y Ramzy: en Cherry Studios el objetivo "
                    "no es solo un sonido impecable, es una producción que comunique lo que tu "
                    "música realmente quiere decir. Por eso combinamos criterio técnico con una "
                    "escucha cercana a cada artista, cuidando el detalle sin perder de vista la "
                    "idea original detrás de cada tema."
                ),
                "image_media_id": str(media["studio"].id),
                "image_caption": "Sesión en estudio",
            },
            "team": {
                "eyebrow": "¿Quiénes somos?",
                "title": "Dos maneras de escuchar la misma canción.",
            },
            "services": {
                "eyebrow": "Servicios",
                "title": "De la idea al máster.",
                "lede": (
                    "Ocho formas de trabajar tu proyecto, del primer boceto a la entrega final."
                ),
                "hint": "Toca una tarjeta para ver el detalle",
            },
            "portfolio": {
                "eyebrow": "Portafolio",
                "title": "Algunos de nuestro proyectos.",
                "note": "Escucha las pistas completas directo desde Spotify y YouTube.",
                "featured_limit": 4,
            },
            "contact": {
                "eyebrow": "Contacto",
                "title": "Cuéntanos de tu proyecto.",
                "email": CONTACT_EMAIL,
                "whatsapp_e164": "",
                "whatsapp_default_msg": "",
                "notify_emails": [CONTACT_EMAIL],
                "consent_text": CONSENT_TEXT,
            },
            "social": {"instagram": INSTAGRAM_URL},
            "seo": {
                "default_title": "Cherry Studios",
                "title_template": "%s · Cherry Studios",
                "default_description": (
                    "Estudio de producción musical en Ciudad de México. "
                    "Composición, grabación, mezcla y máster."
                ),
                "og_image_media_id": str(media["hero"].id),
            },
            "legal": {
                "privacy_html": privacy_html(root),
                "privacy_updated_at": PRIVACY_UPDATED_AT,
            },
            "features": {
                "ab_player": False,
                "testimonials": False,
                "turnstile": False,
                "whatsapp_float": False,
            },
        }
    )
    session.add(
        SiteSettings(
            id=1,
            data=schema.model_dump(mode="json"),
            updated_by=updated_by,
        )
    )


async def _ensure_services(session: AsyncSession) -> None:
    for index, item in enumerate(SERVICES):
        found = await session.scalar(select(Service).where(Service.slug == item["slug"]))
        if found is not None:
            continue
        session.add(
            Service(
                slug=item["slug"],
                number_label=item["number_label"],
                title=item["title"],
                short_description=item["short_description"],
                long_description=item["short_description"],
                icon=item["icon"],
                sort_order=index,
                is_published=True,
            )
        )


async def _ensure_team(session: AsyncSession, media: dict[str, MediaAsset]) -> None:
    for index, item in enumerate(TEAM):
        found = await session.scalar(select(TeamMember).where(TeamMember.slug == item["slug"]))
        if found is not None:
            continue
        session.add(
            TeamMember(
                slug=item["slug"],
                full_name=item["full_name"],
                nickname=item["nickname"],
                role_label=item["role_label"],
                bio_short=item["bio_short"],
                bio_long=item["bio_short"],
                photo_media_id=media[item["photo"]].id,
                socials={},
                sort_order=index,
                is_published=True,
            )
        )


async def _ensure_portfolio(session: AsyncSession, media: dict[str, MediaAsset]) -> None:
    pieces = (
        _Piece(
            slug="palenque",
            title="Palenque",
            artist_name="Alan Säräs",
            kind=PortfolioKind.SPOTIFY,
            external_url="https://open.spotify.com/track/7KYnE3dclseuAX5pect1TM",
            external_id="7KYnE3dclseuAX5pect1TM",
            sort_order=0,
        ),
        _Piece(
            slug="esta-noche",
            title="Esta Noche",
            artist_name="Ramzy",
            kind=PortfolioKind.SPOTIFY,
            external_url="https://open.spotify.com/album/7yU2Q7sAuPpaSsdU1claQr",
            external_id="7yU2Q7sAuPpaSsdU1claQr",
            sort_order=1,
        ),
        _Piece(
            slug="neto-tec-live-session",
            title="Neto — Tec Live Session",
            artist_name="Me llamo Neto",
            kind=PortfolioKind.OWN_AUDIO,
            external_url="https://youtu.be/pLuaWY0WsTI?t=137",
            external_id="pLuaWY0WsTI",
            youtube_start_s=137,
            audio_key="neto",
            sort_order=2,
        ),
    )
    for item in pieces:
        found = await session.scalar(select(PortfolioItem).where(PortfolioItem.slug == item.slug))
        if found is not None:
            continue
        audio_id = media[item.audio_key].id if item.audio_key else None
        session.add(
            PortfolioItem(
                slug=item.slug,
                title=item.title,
                artist_name=item.artist_name,
                kind=item.kind,
                external_url=item.external_url,
                external_id=item.external_id,
                youtube_start_s=item.youtube_start_s,
                audio_after_media_id=audio_id,
                is_featured=True,
                is_ab_featured=False,
                sort_order=item.sort_order,
                is_published=True,
            )
        )


async def _ensure_links(session: AsyncSession) -> None:
    links = (
        ("Contacto", f"mailto:{CONTACT_EMAIL}", "mail", False, True),
        ("WhatsApp", "https://wa.me/", "whatsapp", False, False),
        ("Instagram", INSTAGRAM_URL, "instagram", False, True),
        ("Spotify", "https://open.spotify.com", "spotify", False, False),
        ("Portafolio", "/portafolio", "portfolio", True, True),
    )
    for index, (label, url, icon, internal, published) in enumerate(links):
        found = await session.scalar(select(BioLink).where(BioLink.label == label))
        if found is not None:
            continue
        session.add(
            BioLink(
                label=label,
                url=url,
                icon=icon,
                is_internal=internal,
                highlight=False,
                sort_order=index,
                is_published=published,
            )
        )
