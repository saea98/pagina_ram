import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

import nh3
from app.core.config import get_settings
from app.core.errors import NotFound
from app.core.ratelimit import client_ip_hash, enforce_limit, play_events_per_minute
from app.core.storage import LocalStorage
from app.models.content import BioLink, BioLinkClick, PlayEvent, PortfolioItem, TeamMember
from app.models.enums import MediaKind, MediaStatus, PlayEventType
from app.models.media import MediaAsset
from app.models.mixins import new_uuid
from app.repositories import public as repo
from app.schemas.public import (
    AudioOut,
    BioLinkOut,
    CreditOut,
    FaqOut,
    HomeOut,
    ImageOut,
    PortfolioCardOut,
    PortfolioDetailOut,
    PrivacyOut,
    ServiceCardOut,
    ServiceDetailOut,
    SitePublic,
    TeamCardOut,
    TeamDetailOut,
    TestimonialOut,
)
from fastapi import Request
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


def _storage() -> LocalStorage:
    return LocalStorage(Path(get_settings().media_root))


def _variant_urls(group: object) -> dict[str, str]:
    if not isinstance(group, dict):
        return {}
    storage = _storage()
    urls: dict[str, str] = {}
    for key, value in group.items():
        if isinstance(value, str):
            urls[str(key)] = storage.url(value)
    return urls


def image_out(asset: MediaAsset | None) -> ImageOut | None:
    if asset is None or asset.kind is not MediaKind.IMAGE or asset.status is not MediaStatus.READY:
        return None
    return ImageOut(
        alt=asset.alt_text,
        width=asset.width,
        height=asset.height,
        lqip=asset.lqip,
        webp=_variant_urls(asset.variants.get("webp")),
        avif=_variant_urls(asset.variants.get("avif")),
    )


def audio_out(asset: MediaAsset | None) -> AudioOut | None:
    if asset is None or asset.kind is not MediaKind.AUDIO or asset.status is not MediaStatus.READY:
        return None
    storage = _storage()
    variants = asset.variants
    m4a = variants.get("m4a")
    mp3 = variants.get("mp3")
    return AudioOut(
        duration_s=None if asset.duration_s is None else float(asset.duration_s),
        lufs=None if asset.lufs_integrated is None else float(asset.lufs_integrated),
        m4a_url=storage.url(m4a) if isinstance(m4a, str) else None,
        mp3_url=storage.url(mp3) if isinstance(mp3, str) else None,
        peaks_url=storage.url(asset.peaks_key) if asset.peaks_key else None,
    )


def _service_card(service: object) -> ServiceCardOut:
    return ServiceCardOut.model_validate(service, from_attributes=True)


async def _cards(
    session: AsyncSession,
    items: list[PortfolioItem],
) -> list[PortfolioCardOut]:
    slugs = await repo.service_slugs_for(session, [item.id for item in items])
    media_ids: set[uuid.UUID] = set()
    for item in items:
        for media_id in (
            item.cover_media_id,
            item.audio_after_media_id,
            item.audio_before_media_id,
        ):
            if media_id is not None:
                media_ids.add(media_id)
    media = await repo.media_map(session, media_ids)
    return [
        PortfolioCardOut(
            slug=item.slug,
            title=item.title,
            artist_name=item.artist_name,
            year=item.year,
            genre=item.genre,
            kind=item.kind.value,
            external_url=item.external_url,
            external_id=item.external_id,
            youtube_start_s=item.youtube_start_s,
            is_featured=item.is_featured,
            is_ab_featured=item.is_ab_featured,
            play_count=item.play_count,
            cover=image_out(media.get(item.cover_media_id) if item.cover_media_id else None),
            audio=audio_out(
                media.get(item.audio_after_media_id) if item.audio_after_media_id else None
            ),
            audio_before=audio_out(
                media.get(item.audio_before_media_id) if item.audio_before_media_id else None
            ),
            service_slugs=slugs.get(item.id, []),
            updated_at=item.updated_at,
        )
        for item in items
    ]


async def _team_cards(session: AsyncSession, members: list[TeamMember]) -> list[TeamCardOut]:
    ids = {member.photo_media_id for member in members if member.photo_media_id is not None}
    media = await repo.media_map(session, ids)
    return [
        TeamCardOut(
            slug=member.slug,
            full_name=member.full_name,
            nickname=member.nickname,
            role_label=member.role_label,
            bio_short=member.bio_short,
            photo=image_out(media.get(member.photo_media_id) if member.photo_media_id else None),
            socials=member.socials,
            updated_at=member.updated_at,
        )
        for member in members
    ]


async def site_public(session: AsyncSession) -> SitePublic:
    row = await repo.get_settings(session)
    if row is None:
        raise NotFound("El sitio todavía no tiene contenido.")
    site = SitePublic.model_validate(row.data)
    media_ids: set[uuid.UUID] = set()
    _collect_media_ids(row.data, media_ids)
    assets = await repo.media_map(session, media_ids)
    site.media = {
        str(media_id): image
        for media_id, asset in assets.items()
        if (image := image_out(asset)) is not None
    }
    return site


async def home(session: AsyncSession) -> HomeOut:
    site = await site_public(session)
    services = [_service_card(item) for item in await repo.list_services(session)]
    team = await _team_cards(session, list(await repo.list_team(session)))
    featured = await _cards(
        session,
        await repo.list_portfolio(
            session,
            service_slug=None,
            genre=None,
            featured=True,
            ab_featured=None,
            limit=site.portfolio.featured_limit,
        ),
    )
    comparisons = await _cards(
        session,
        await repo.list_portfolio(
            session,
            service_slug=None,
            genre=None,
            featured=None,
            ab_featured=True,
            limit=3,
        ),
    )
    testimonials = await list_testimonials(session)
    return HomeOut(
        site=site,
        services=services,
        team=team,
        portfolio=featured,
        ab_comparisons=comparisons,
        testimonials=testimonials,
    )


async def list_services(session: AsyncSession) -> list[ServiceCardOut]:
    return [_service_card(item) for item in await repo.list_services(session)]


async def service_detail(session: AsyncSession, slug: str) -> ServiceDetailOut:
    service = await repo.get_service(session, slug)
    if service is None:
        raise NotFound("No encontramos ese servicio.")
    faqs = [
        FaqOut(question=faq.question, answer=faq.answer, service_slug=slug)
        for faq in await repo.faqs_for_service(session, service.id)
    ]
    portfolio = await _cards(
        session,
        await repo.list_portfolio(
            session,
            service_slug=slug,
            genre=None,
            featured=None,
            ab_featured=None,
            limit=None,
        ),
    )
    card = _service_card(service)
    return ServiceDetailOut(
        **card.model_dump(),
        long_description=service.long_description,
        faqs=faqs,
        portfolio=portfolio,
    )


async def list_team(session: AsyncSession) -> list[TeamCardOut]:
    return await _team_cards(session, list(await repo.list_team(session)))


async def team_detail(session: AsyncSession, slug: str) -> TeamDetailOut:
    member = await repo.get_team_member(session, slug)
    if member is None:
        raise NotFound("No encontramos a esa persona.")
    card = (await _team_cards(session, [member]))[0]
    credits = [
        CreditOut(
            portfolio_slug=item.slug,
            portfolio_title=item.title,
            role_label=credit.role_label,
        )
        for credit, item in await repo.credits_for_member(session, member.id)
    ]
    return TeamDetailOut(**card.model_dump(), bio_long=member.bio_long, credits=credits)


async def list_portfolio(
    session: AsyncSession,
    *,
    service: str | None,
    genre: str | None,
    featured: bool | None,
) -> list[PortfolioCardOut]:
    items = await repo.list_portfolio(
        session,
        service_slug=service,
        genre=genre,
        featured=featured,
        ab_featured=None,
        limit=None,
    )
    return await _cards(session, items)


async def portfolio_detail(session: AsyncSession, slug: str) -> PortfolioDetailOut:
    item = await repo.get_portfolio_item(session, slug)
    if item is None:
        raise NotFound("No encontramos esa pieza.")
    card = (await _cards(session, [item]))[0]
    return PortfolioDetailOut(
        **card.model_dump(),
        credits_text=item.credits_text,
        description=item.description,
    )


async def record_play(session: AsyncSession, request: Request, slug: str, event: str) -> None:
    enforce_limit(
        f"play:{client_ip_hash(request)}",
        limit=play_events_per_minute(),
        window_s=60,
    )
    item = await repo.get_portfolio_item(session, slug)
    if item is None:
        raise NotFound("No encontramos esa pieza.")
    today = datetime.now(ZoneInfo(get_settings().tz)).date()
    kind = PlayEventType(event)
    await session.execute(
        insert(PlayEvent)
        .values(
            id=new_uuid(),
            portfolio_item_id=item.id,
            event=kind,
            occurred_on=today,
            count=1,
        )
        .on_conflict_do_update(
            constraint="uq_play_events_daily",
            set_={"count": PlayEvent.count + 1},
        )
    )
    if kind is PlayEventType.PLAY:
        stored = await session.get(PortfolioItem, item.id)
        if stored is not None:
            stored.play_count += 1
    await session.commit()


async def list_testimonials(session: AsyncSession) -> list[TestimonialOut]:
    rows = await repo.list_testimonials(session)
    photo_ids = {item.photo_media_id for item, _slug in rows if item.photo_media_id}
    media = await repo.media_map(session, photo_ids)
    return [
        TestimonialOut(
            quote=item.quote,
            author_name=item.author_name,
            author_role=item.author_role,
            project_label=item.project_label,
            photo=image_out(media.get(item.photo_media_id) if item.photo_media_id else None),
            portfolio_slug=slug,
        )
        for item, slug in rows
    ]


async def list_faqs(session: AsyncSession, service: str | None) -> list[FaqOut]:
    return [
        FaqOut(question=faq.question, answer=faq.answer, service_slug=slug)
        for faq, slug in await repo.list_faqs(session, service)
    ]


async def list_links(session: AsyncSession) -> list[BioLinkOut]:
    now = datetime.now(UTC)
    return [_link_out(link) for link in await repo.list_links(session, now)]


async def follow_link(
    session: AsyncSession,
    link_id: uuid.UUID,
    *,
    referrer: str | None,
    user_agent: str | None,
    country: str | None,
) -> str:
    link = await repo.get_link(session, link_id, datetime.now(UTC))
    if link is None:
        raise NotFound("No encontramos ese enlace.")
    session.add(
        BioLinkClick(
            bio_link_id=link.id,
            clicked_at=datetime.now(UTC),
            referrer=referrer,
            user_agent_family=(user_agent or "")[:80] or None,
            country=country,
        )
    )
    await session.commit()
    if link.is_internal:
        return _with_utm(link.url, link.utm_overrides)
    return link.url


async def privacy(session: AsyncSession) -> PrivacyOut:
    site = await site_public(session)
    return PrivacyOut(
        html=nh3.clean(site.legal.privacy_html),
        updated_at=site.legal.privacy_updated_at,
    )


def _link_out(link: BioLink) -> BioLinkOut:
    return BioLinkOut(
        id=str(link.id),
        label=link.label,
        url=link.url,
        icon=link.icon,
        highlight=link.highlight,
        is_internal=link.is_internal,
    )


def _collect_media_ids(value: object, found: set[uuid.UUID]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).endswith("media_id") and isinstance(item, str):
                try:
                    found.add(uuid.UUID(item))
                except ValueError:
                    continue
            else:
                _collect_media_ids(item, found)
    elif isinstance(value, list):
        for item in value:
            _collect_media_ids(item, found)


def _with_utm(url: str, overrides: dict[str, object]) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    extra = {"utm_source": "instagram", "utm_medium": "bio"}
    for key, value in overrides.items():
        if isinstance(value, str) and value:
            extra[key] = value
    query.update(extra)
    return urlunsplit(parts._replace(query=urlencode(query)))
