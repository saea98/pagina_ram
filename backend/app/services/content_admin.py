import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import nh3
from app.core.errors import Conflict, NotFound
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
from app.schemas.admin import (
    CreditIn,
    FaqAdminOut,
    FaqIn,
    FaqPatch,
    LinkAdminOut,
    LinkIn,
    LinkPatch,
    Page,
    PortfolioAdminOut,
    PortfolioIn,
    PortfolioPatch,
    ServiceAdminOut,
    ServiceIn,
    ServicePatch,
    TeamAdminOut,
    TeamIn,
    TeamPatch,
    TestimonialAdminOut,
    TestimonialIn,
    TestimonialPatch,
)
from app.services.revalidate import enqueue
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

_HTML_FIELDS = {"long_description", "bio_long", "answer", "description"}


def _clean(data: dict[str, object]) -> dict[str, object]:
    cleaned = dict(data)
    for key in _HTML_FIELDS:
        value = cleaned.get(key)
        if isinstance(value, str):
            cleaned[key] = nh3.clean(value)
    return cleaned


async def _unique_slug(
    session: AsyncSession,
    model: type[Service] | type[TeamMember] | type[PortfolioItem],
    slug: str,
    current: uuid.UUID | None,
) -> None:
    found = await session.scalar(select(model).where(model.slug == slug))
    found_id = getattr(found, "id", None)
    if found is not None and found_id != current:
        raise Conflict("Esa URL ya está en uso.")


async def _get[M: (Service, TeamMember, PortfolioItem, Testimonial, Faq, BioLink)](
    session: AsyncSession,
    model: type[M],
    item_id: uuid.UUID,
) -> M:
    row = await session.get(model, item_id)
    if row is None or row.deleted_at is not None:
        raise NotFound("No encontramos ese elemento.")
    return row


def _apply(row: object, data: dict[str, object], skip: set[str]) -> None:
    for key, value in data.items():
        if key in skip:
            continue
        setattr(row, key, value)


async def _next_order[M: (Service, TeamMember, PortfolioItem, Testimonial, Faq, BioLink)](
    session: AsyncSession,
    model: type[M],
) -> int:
    current = await session.scalar(select(func.max(model.sort_order)))
    return 0 if current is None else int(current) + 1


def _paths(kind: str, slug: str | None) -> list[str]:
    paths = ["/", "/sitemap.xml"]
    if kind == "services" and slug:
        paths.append(f"/servicios/{slug}")
    elif kind == "team" and slug:
        paths.append(f"/equipo/{slug}")
    elif kind == "portfolio":
        paths.append("/portafolio")
        if slug:
            paths.append(f"/portafolio/{slug}")
    elif kind == "links":
        paths.append("/links")
    return paths


async def list_services(
    session: AsyncSession,
    q: str | None,
    page: int,
    page_size: int,
) -> Page[ServiceAdminOut]:
    query = select(Service).where(Service.deleted_at.is_(None))
    if q:
        term = f"%{q.strip()}%"
        query = query.where(or_(Service.title.ilike(term), Service.slug.ilike(term)))
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = await session.scalars(
        query.order_by(Service.sort_order, Service.title)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return Page(
        items=[ServiceAdminOut.model_validate(row) for row in rows],
        total=int(total or 0),
        page=page,
        page_size=page_size,
    )


async def create_service(session: AsyncSession, body: ServiceIn) -> ServiceAdminOut:
    await _unique_slug(session, Service, body.slug, None)
    data = _clean(body.model_dump())
    if not data["number_label"]:
        data["number_label"] = f"{await _next_order(session, Service) + 1:02d}"
    row = Service(sort_order=await _next_order(session, Service))
    _apply(row, data, set())
    session.add(row)
    await session.flush()
    enqueue(session, _paths("services", row.slug))
    await session.commit()
    return ServiceAdminOut.model_validate(row)


async def get_service(session: AsyncSession, item_id: uuid.UUID) -> ServiceAdminOut:
    return ServiceAdminOut.model_validate(await _get(session, Service, item_id))


async def update_service(
    session: AsyncSession,
    item_id: uuid.UUID,
    body: ServicePatch,
) -> ServiceAdminOut:
    row = await _get(session, Service, item_id)
    data = _clean(body.model_dump(exclude_unset=True))
    slug = data.get("slug")
    if isinstance(slug, str):
        await _unique_slug(session, Service, slug, row.id)
    _apply(row, data, set())
    enqueue(session, _paths("services", row.slug))
    await session.commit()
    return ServiceAdminOut.model_validate(row)


async def remove_row[M: (Service, TeamMember, PortfolioItem, Testimonial, Faq, BioLink)](
    session: AsyncSession,
    model: type[M],
    item_id: uuid.UUID,
    kind: str,
) -> None:
    row = await _get(session, model, item_id)
    row.deleted_at = datetime.now(UTC)
    slug = getattr(row, "slug", None)
    enqueue(session, _paths(kind, slug if isinstance(slug, str) else None))
    await session.commit()


async def reorder[M: (Service, TeamMember, PortfolioItem, Testimonial, Faq, BioLink)](
    session: AsyncSession,
    model: type[M],
    ids: list[uuid.UUID],
    kind: str,
) -> None:
    for index, item_id in enumerate(ids):
        row = await _get(session, model, item_id)
        row.sort_order = index
    enqueue(session, _paths(kind, None))
    await session.commit()


async def list_team(
    session: AsyncSession, q: str | None, page: int, page_size: int
) -> Page[TeamAdminOut]:
    query = select(TeamMember).where(TeamMember.deleted_at.is_(None))
    if q:
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                TeamMember.full_name.ilike(term),
                TeamMember.nickname.ilike(term),
                TeamMember.slug.ilike(term),
            )
        )
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = await session.scalars(
        query.order_by(TeamMember.sort_order).offset((page - 1) * page_size).limit(page_size)
    )
    return Page(
        items=[TeamAdminOut.model_validate(row) for row in rows],
        total=int(total or 0),
        page=page,
        page_size=page_size,
    )


async def create_team(session: AsyncSession, body: TeamIn) -> TeamAdminOut:
    await _unique_slug(session, TeamMember, body.slug, None)
    row = TeamMember(sort_order=await _next_order(session, TeamMember))
    _apply(row, body.model_dump(), set())
    session.add(row)
    await session.flush()
    enqueue(session, _paths("team", row.slug))
    await session.commit()
    return TeamAdminOut.model_validate(row)


async def get_team(session: AsyncSession, item_id: uuid.UUID) -> TeamAdminOut:
    return TeamAdminOut.model_validate(await _get(session, TeamMember, item_id))


async def update_team(session: AsyncSession, item_id: uuid.UUID, body: TeamPatch) -> TeamAdminOut:
    row = await _get(session, TeamMember, item_id)
    data = body.model_dump(exclude_unset=True)
    slug = data.get("slug")
    if isinstance(slug, str):
        await _unique_slug(session, TeamMember, slug, row.id)
    if "bio_long" in data and isinstance(data["bio_long"], str):
        data["bio_long"] = nh3.clean(data["bio_long"])
    _apply(row, data, set())
    enqueue(session, _paths("team", row.slug))
    await session.commit()
    return TeamAdminOut.model_validate(row)


async def _portfolio_out(session: AsyncSession, row: PortfolioItem) -> PortfolioAdminOut:
    service_ids = list(
        await session.scalars(
            select(PortfolioItemService.service_id).where(
                PortfolioItemService.portfolio_item_id == row.id
            )
        )
    )
    credit_rows = (
        await session.execute(
            select(PortfolioItemCredit).where(PortfolioItemCredit.portfolio_item_id == row.id)
        )
    ).scalars()
    return PortfolioAdminOut(
        id=row.id,
        slug=row.slug,
        title=row.title,
        artist_name=row.artist_name,
        year=row.year,
        genre=row.genre,
        kind=row.kind,
        external_url=row.external_url,
        external_id=row.external_id,
        youtube_start_s=row.youtube_start_s,
        cover_media_id=row.cover_media_id,
        audio_after_media_id=row.audio_after_media_id,
        audio_before_media_id=row.audio_before_media_id,
        credits_text=row.credits_text,
        description=row.description,
        is_featured=row.is_featured,
        is_ab_featured=row.is_ab_featured,
        is_published=row.is_published,
        service_ids=service_ids,
        credits=[
            CreditIn(team_member_id=credit.team_member_id, role_label=credit.role_label)
            for credit in credit_rows
        ],
        sort_order=row.sort_order,
        play_count=row.play_count,
        updated_at=row.updated_at,
    )


async def _set_portfolio_links(
    session: AsyncSession,
    item_id: uuid.UUID,
    service_ids: list[uuid.UUID] | None,
    credits: Sequence[CreditIn] | None,
) -> None:
    if service_ids is not None:
        await session.execute(
            delete(PortfolioItemService).where(PortfolioItemService.portfolio_item_id == item_id)
        )
        for service_id in service_ids:
            session.add(PortfolioItemService(portfolio_item_id=item_id, service_id=service_id))
    if credits is not None:
        await session.execute(
            delete(PortfolioItemCredit).where(PortfolioItemCredit.portfolio_item_id == item_id)
        )
        for credit in credits:
            payload = credit.model_dump()
            session.add(
                PortfolioItemCredit(
                    portfolio_item_id=item_id,
                    team_member_id=payload["team_member_id"],
                    role_label=str(payload["role_label"]),
                )
            )


async def list_portfolio(
    session: AsyncSession, q: str | None, page: int, page_size: int
) -> Page[PortfolioAdminOut]:
    query = select(PortfolioItem).where(PortfolioItem.deleted_at.is_(None))
    if q:
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                PortfolioItem.title.ilike(term),
                PortfolioItem.artist_name.ilike(term),
                PortfolioItem.slug.ilike(term),
            )
        )
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = list(
        await session.scalars(
            query.order_by(PortfolioItem.sort_order).offset((page - 1) * page_size).limit(page_size)
        )
    )
    items = [await _portfolio_out(session, row) for row in rows]
    return Page(items=items, total=int(total or 0), page=page, page_size=page_size)


async def create_portfolio(session: AsyncSession, body: PortfolioIn) -> PortfolioAdminOut:
    await _unique_slug(session, PortfolioItem, body.slug, None)
    data = body.model_dump()
    service_ids = data.pop("service_ids")
    credits = body.credits
    if isinstance(data.get("description"), str):
        data["description"] = nh3.clean(data["description"])
    row = PortfolioItem(sort_order=await _next_order(session, PortfolioItem))
    _apply(row, data, {"service_ids", "credits"})
    session.add(row)
    await session.flush()
    await _set_portfolio_links(session, row.id, service_ids, credits)
    enqueue(session, _paths("portfolio", row.slug))
    await session.commit()
    return await _portfolio_out(session, row)


async def get_portfolio(session: AsyncSession, item_id: uuid.UUID) -> PortfolioAdminOut:
    return await _portfolio_out(session, await _get(session, PortfolioItem, item_id))


async def update_portfolio(
    session: AsyncSession, item_id: uuid.UUID, body: PortfolioPatch
) -> PortfolioAdminOut:
    row = await _get(session, PortfolioItem, item_id)
    data = body.model_dump(exclude_unset=True)
    slug = data.get("slug")
    if isinstance(slug, str):
        await _unique_slug(session, PortfolioItem, slug, row.id)
    service_ids = data.pop("service_ids", None)
    credits = body.credits if "credits" in body.model_fields_set else None
    if isinstance(data.get("description"), str):
        data["description"] = nh3.clean(data["description"])
    _apply(row, data, {"service_ids", "credits"})
    await _set_portfolio_links(session, row.id, service_ids, credits)
    enqueue(session, _paths("portfolio", row.slug))
    await session.commit()
    return await _portfolio_out(session, row)


async def list_testimonials(
    session: AsyncSession, q: str | None, page: int, page_size: int
) -> Page[TestimonialAdminOut]:
    query = select(Testimonial).where(Testimonial.deleted_at.is_(None))
    if q:
        term = f"%{q.strip()}%"
        query = query.where(or_(Testimonial.author_name.ilike(term), Testimonial.quote.ilike(term)))
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = await session.scalars(
        query.order_by(Testimonial.sort_order).offset((page - 1) * page_size).limit(page_size)
    )
    return Page(
        items=[TestimonialAdminOut.model_validate(row) for row in rows],
        total=int(total or 0),
        page=page,
        page_size=page_size,
    )


async def create_testimonial(session: AsyncSession, body: TestimonialIn) -> TestimonialAdminOut:
    row = Testimonial(sort_order=await _next_order(session, Testimonial))
    _apply(row, body.model_dump(), set())
    session.add(row)
    await session.flush()
    enqueue(session, _paths("testimonials", None))
    await session.commit()
    return TestimonialAdminOut.model_validate(row)


async def get_testimonial(session: AsyncSession, item_id: uuid.UUID) -> TestimonialAdminOut:
    return TestimonialAdminOut.model_validate(await _get(session, Testimonial, item_id))


async def update_testimonial(
    session: AsyncSession, item_id: uuid.UUID, body: TestimonialPatch
) -> TestimonialAdminOut:
    row = await _get(session, Testimonial, item_id)
    _apply(row, body.model_dump(exclude_unset=True), set())
    enqueue(session, _paths("testimonials", None))
    await session.commit()
    return TestimonialAdminOut.model_validate(row)


async def list_faqs(
    session: AsyncSession, q: str | None, page: int, page_size: int
) -> Page[FaqAdminOut]:
    query = select(Faq).where(Faq.deleted_at.is_(None))
    if q:
        query = query.where(Faq.question.ilike(f"%{q.strip()}%"))
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = await session.scalars(
        query.order_by(Faq.sort_order).offset((page - 1) * page_size).limit(page_size)
    )
    return Page(
        items=[FaqAdminOut.model_validate(row) for row in rows],
        total=int(total or 0),
        page=page,
        page_size=page_size,
    )


async def create_faq(session: AsyncSession, body: FaqIn) -> FaqAdminOut:
    data = body.model_dump()
    data["answer"] = nh3.clean(body.answer)
    row = Faq(sort_order=await _next_order(session, Faq))
    _apply(row, data, set())
    session.add(row)
    await session.flush()
    enqueue(session, _paths("faqs", None))
    await session.commit()
    return FaqAdminOut.model_validate(row)


async def get_faq(session: AsyncSession, item_id: uuid.UUID) -> FaqAdminOut:
    return FaqAdminOut.model_validate(await _get(session, Faq, item_id))


async def update_faq(session: AsyncSession, item_id: uuid.UUID, body: FaqPatch) -> FaqAdminOut:
    row = await _get(session, Faq, item_id)
    data = body.model_dump(exclude_unset=True)
    if isinstance(data.get("answer"), str):
        data["answer"] = nh3.clean(data["answer"])
    _apply(row, data, set())
    enqueue(session, _paths("faqs", None))
    await session.commit()
    return FaqAdminOut.model_validate(row)


async def list_links(
    session: AsyncSession, q: str | None, page: int, page_size: int
) -> Page[LinkAdminOut]:
    query = select(BioLink).where(BioLink.deleted_at.is_(None))
    if q:
        term = f"%{q.strip()}%"
        query = query.where(or_(BioLink.label.ilike(term), BioLink.url.ilike(term)))
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = await session.scalars(
        query.order_by(BioLink.sort_order).offset((page - 1) * page_size).limit(page_size)
    )
    return Page(
        items=[LinkAdminOut.model_validate(row) for row in rows],
        total=int(total or 0),
        page=page,
        page_size=page_size,
    )


async def create_link(session: AsyncSession, body: LinkIn) -> LinkAdminOut:
    row = BioLink(sort_order=await _next_order(session, BioLink))
    _apply(row, body.model_dump(), set())
    session.add(row)
    await session.flush()
    enqueue(session, _paths("links", None))
    await session.commit()
    return LinkAdminOut.model_validate(row)


async def get_link(session: AsyncSession, item_id: uuid.UUID) -> LinkAdminOut:
    return LinkAdminOut.model_validate(await _get(session, BioLink, item_id))


async def update_link(session: AsyncSession, item_id: uuid.UUID, body: LinkPatch) -> LinkAdminOut:
    row = await _get(session, BioLink, item_id)
    _apply(row, body.model_dump(exclude_unset=True), set())
    enqueue(session, _paths("links", None))
    await session.commit()
    return LinkAdminOut.model_validate(row)
