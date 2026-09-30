import uuid
from datetime import datetime

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, aliased

from app.models.content import (
    BioLink,
    Faq,
    PortfolioItem,
    PortfolioItemCredit,
    PortfolioItemService,
    Service,
    TeamMember,
    Testimonial,
)
from app.models.media import MediaAsset
from app.models.users import SiteSettings


def _live(
    published: InstrumentedAttribute[bool],
    deleted: InstrumentedAttribute[datetime | None],
) -> tuple[ColumnElement[bool], ColumnElement[bool]]:
    return published.is_(True), deleted.is_(None)


async def get_settings(session: AsyncSession) -> SiteSettings | None:
    return await session.get(SiteSettings, 1)


async def list_services(session: AsyncSession) -> list[Service]:
    published, alive = _live(Service.is_published, Service.deleted_at)
    rows = await session.scalars(
        select(Service).where(published, alive).order_by(Service.sort_order, Service.title)
    )
    return list(rows)


async def get_service(session: AsyncSession, slug: str) -> Service | None:
    published, alive = _live(Service.is_published, Service.deleted_at)
    return await session.scalar(select(Service).where(Service.slug == slug, published, alive))


async def faqs_for_service(session: AsyncSession, service_id: uuid.UUID) -> list[Faq]:
    published, alive = _live(Faq.is_published, Faq.deleted_at)
    rows = await session.scalars(
        select(Faq).where(Faq.service_id == service_id, published, alive).order_by(Faq.sort_order)
    )
    return list(rows)


async def list_faqs(
    session: AsyncSession,
    service_slug: str | None,
) -> list[tuple[Faq, str | None]]:
    published, alive = _live(Faq.is_published, Faq.deleted_at)
    query = (
        select(Faq, Service.slug)
        .outerjoin(Service, Service.id == Faq.service_id)
        .where(published, alive)
        .order_by(Faq.sort_order)
    )
    if service_slug is not None:
        query = query.where(Service.slug == service_slug)
    rows = await session.execute(query)
    return [(faq, slug) for faq, slug in rows.all()]


async def list_team(session: AsyncSession) -> list[TeamMember]:
    published, alive = _live(TeamMember.is_published, TeamMember.deleted_at)
    rows = await session.scalars(
        select(TeamMember).where(published, alive).order_by(TeamMember.sort_order)
    )
    return list(rows)


async def get_team_member(session: AsyncSession, slug: str) -> TeamMember | None:
    published, alive = _live(TeamMember.is_published, TeamMember.deleted_at)
    return await session.scalar(select(TeamMember).where(TeamMember.slug == slug, published, alive))


async def credits_for_member(
    session: AsyncSession,
    member_id: uuid.UUID,
) -> list[tuple[PortfolioItemCredit, PortfolioItem]]:
    published, alive = _live(PortfolioItem.is_published, PortfolioItem.deleted_at)
    rows = await session.execute(
        select(PortfolioItemCredit, PortfolioItem)
        .join(PortfolioItem, PortfolioItem.id == PortfolioItemCredit.portfolio_item_id)
        .where(PortfolioItemCredit.team_member_id == member_id, published, alive)
        .order_by(PortfolioItem.sort_order)
    )
    return [(credit, item) for credit, item in rows.all()]


async def list_portfolio(
    session: AsyncSession,
    *,
    service_slug: str | None,
    genre: str | None,
    featured: bool | None,
    ab_featured: bool | None,
    limit: int | None,
) -> list[PortfolioItem]:
    published, alive = _live(PortfolioItem.is_published, PortfolioItem.deleted_at)
    query = select(PortfolioItem).where(published, alive)
    if service_slug is not None:
        query = query.join(
            PortfolioItemService,
            PortfolioItemService.portfolio_item_id == PortfolioItem.id,
        ).join(Service, Service.id == PortfolioItemService.service_id)
        query = query.where(Service.slug == service_slug)
    if genre:
        query = query.where(PortfolioItem.genre == genre)
    if featured is not None:
        query = query.where(PortfolioItem.is_featured.is_(featured))
    if ab_featured is not None:
        query = query.where(PortfolioItem.is_ab_featured.is_(ab_featured))
    query = query.order_by(PortfolioItem.sort_order, PortfolioItem.title)
    if limit is not None:
        query = query.limit(limit)
    rows = await session.scalars(query)
    return list(rows)


async def get_portfolio_item(session: AsyncSession, slug: str) -> PortfolioItem | None:
    published, alive = _live(PortfolioItem.is_published, PortfolioItem.deleted_at)
    return await session.scalar(
        select(PortfolioItem).where(PortfolioItem.slug == slug, published, alive)
    )


async def service_slugs_for(
    session: AsyncSession,
    item_ids: list[uuid.UUID],
) -> dict[uuid.UUID, list[str]]:
    if not item_ids:
        return {}
    rows = await session.execute(
        select(PortfolioItemService.portfolio_item_id, Service.slug)
        .join(Service, Service.id == PortfolioItemService.service_id)
        .where(PortfolioItemService.portfolio_item_id.in_(item_ids))
        .order_by(Service.sort_order)
    )
    grouped: dict[uuid.UUID, list[str]] = {item_id: [] for item_id in item_ids}
    for item_id, slug in rows.all():
        grouped.setdefault(item_id, []).append(slug)
    return grouped


async def list_testimonials(session: AsyncSession) -> list[tuple[Testimonial, str | None]]:
    published, alive = _live(Testimonial.is_published, Testimonial.deleted_at)
    piece = aliased(PortfolioItem)
    rows = await session.execute(
        select(Testimonial, piece.slug)
        .outerjoin(piece, piece.id == Testimonial.portfolio_item_id)
        .where(published, alive)
        .order_by(Testimonial.sort_order)
    )
    return [(item, slug) for item, slug in rows.all()]


async def list_links(session: AsyncSession, now: datetime) -> list[BioLink]:
    published, alive = _live(BioLink.is_published, BioLink.deleted_at)
    rows = await session.scalars(
        select(BioLink)
        .where(
            published,
            alive,
            (BioLink.starts_at.is_(None)) | (BioLink.starts_at <= now),
            (BioLink.ends_at.is_(None)) | (BioLink.ends_at >= now),
        )
        .order_by(BioLink.sort_order)
    )
    return list(rows)


async def get_link(session: AsyncSession, link_id: uuid.UUID, now: datetime) -> BioLink | None:
    published, alive = _live(BioLink.is_published, BioLink.deleted_at)
    return await session.scalar(
        select(BioLink).where(
            BioLink.id == link_id,
            published,
            alive,
            (BioLink.starts_at.is_(None)) | (BioLink.starts_at <= now),
            (BioLink.ends_at.is_(None)) | (BioLink.ends_at >= now),
        )
    )


async def media_map(session: AsyncSession, ids: set[uuid.UUID]) -> dict[uuid.UUID, MediaAsset]:
    if not ids:
        return {}
    rows = await session.scalars(select(MediaAsset).where(MediaAsset.id.in_(ids)))
    return {asset.id: asset for asset in rows}
