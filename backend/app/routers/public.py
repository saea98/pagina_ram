import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import apply_preview
from app.schemas.public import (
    BioLinkOut,
    FaqOut,
    HomeOut,
    PlayEventIn,
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
from app.services import public_content

router = APIRouter(
    prefix="/api/v1/public",
    tags=["public"],
    dependencies=[Depends(apply_preview)],
)


@router.get("/site", response_model=SitePublic)
async def site(session: AsyncSession = Depends(get_session)) -> SitePublic:
    return await public_content.site_public(session)


@router.get("/home", response_model=HomeOut)
async def home(session: AsyncSession = Depends(get_session)) -> HomeOut:
    return await public_content.home(session)


@router.get("/services", response_model=list[ServiceCardOut])
async def services(session: AsyncSession = Depends(get_session)) -> list[ServiceCardOut]:
    return await public_content.list_services(session)


@router.get("/services/{slug}", response_model=ServiceDetailOut)
async def service(slug: str, session: AsyncSession = Depends(get_session)) -> ServiceDetailOut:
    return await public_content.service_detail(session, slug)


@router.get("/team", response_model=list[TeamCardOut])
async def team(session: AsyncSession = Depends(get_session)) -> list[TeamCardOut]:
    return await public_content.list_team(session)


@router.get("/team/{slug}", response_model=TeamDetailOut)
async def team_member(slug: str, session: AsyncSession = Depends(get_session)) -> TeamDetailOut:
    return await public_content.team_detail(session, slug)


@router.get("/portfolio", response_model=list[PortfolioCardOut])
async def portfolio(
    service: str | None = None,
    genre: str | None = None,
    featured: bool | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[PortfolioCardOut]:
    return await public_content.list_portfolio(
        session,
        service=service,
        genre=genre,
        featured=featured,
    )


@router.get("/portfolio/{slug}", response_model=PortfolioDetailOut)
async def portfolio_item(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> PortfolioDetailOut:
    return await public_content.portfolio_detail(session, slug)


@router.post("/portfolio/{slug}/events", status_code=204)
async def portfolio_event(
    slug: str,
    body: PlayEventIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> None:
    await public_content.record_play(session, request, slug, body.event)


@router.get("/testimonials", response_model=list[TestimonialOut])
async def testimonials(session: AsyncSession = Depends(get_session)) -> list[TestimonialOut]:
    return await public_content.list_testimonials(session)


@router.get("/faqs", response_model=list[FaqOut])
async def faqs(
    service: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[FaqOut]:
    return await public_content.list_faqs(session, service)


@router.get("/links", response_model=list[BioLinkOut])
async def links(session: AsyncSession = Depends(get_session)) -> list[BioLinkOut]:
    return await public_content.list_links(session)


@router.get("/links/{link_id}/go", response_model=None)
async def follow_link(
    link_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    target = await public_content.follow_link(
        session,
        link_id,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        country=request.headers.get("cf-ipcountry"),
    )
    return RedirectResponse(url=target, status_code=302, headers={"Cache-Control": "no-store"})


@router.get("/legal/privacy", response_model=PrivacyOut)
async def privacy(session: AsyncSession = Depends(get_session)) -> PrivacyOut:
    return await public_content.privacy(session)
