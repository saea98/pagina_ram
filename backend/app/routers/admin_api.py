import uuid
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import current_user, require_csrf, require_superadmin
from app.core.storage import LocalStorage
from app.models.content import BioLink, Faq, PortfolioItem, Service, TeamMember, Testimonial
from app.models.enums import LeadStatus, MediaKind
from app.models.users import User
from app.schemas.admin import (
    FaqAdminOut,
    FaqIn,
    FaqPatch,
    InspectIn,
    InspectOut,
    LeadAdminOut,
    LeadDetailOut,
    LeadNoteIn,
    LeadStatusIn,
    LinkAdminOut,
    LinkIn,
    LinkPatch,
    MediaAdminOut,
    MediaAltIn,
    Page,
    PortfolioAdminOut,
    PortfolioIn,
    PortfolioPatch,
    ReorderIn,
    ServiceAdminOut,
    ServiceIn,
    ServicePatch,
    StatsOut,
    TeamAdminOut,
    TeamIn,
    TeamPatch,
    TestimonialAdminOut,
    TestimonialIn,
    TestimonialPatch,
    UserAdminOut,
    UserCreateIn,
    UserPasswordIn,
    UserPatchIn,
)
from app.schemas.auth import PreviewTokenOut
from app.schemas.site import SiteSettingsSchema
from app.services import (
    admin_leads,
    admin_media,
    admin_settings,
    admin_stats,
    admin_users,
    auth,
    content_admin,
    embeds,
)

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(current_user), Depends(require_csrf)],
)


SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[User, Depends(current_user)]


@router.get("/services", response_model=Page[ServiceAdminOut])
async def list_services(
    session: SessionDep,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
) -> Page[ServiceAdminOut]:
    return await content_admin.list_services(session, q, page, page_size)


@router.post("/services", response_model=ServiceAdminOut, status_code=201)
async def create_service(body: ServiceIn, session: SessionDep) -> ServiceAdminOut:
    return await content_admin.create_service(session, body)


@router.post("/services/reorder", status_code=204)
async def reorder_services(body: ReorderIn, session: SessionDep) -> None:
    await content_admin.reorder(session, Service, body.ids, "services")


@router.get("/services/{item_id}", response_model=ServiceAdminOut)
async def get_service(item_id: uuid.UUID, session: SessionDep) -> ServiceAdminOut:
    return await content_admin.get_service(session, item_id)


@router.patch("/services/{item_id}", response_model=ServiceAdminOut)
async def update_service(
    item_id: uuid.UUID, body: ServicePatch, session: SessionDep
) -> ServiceAdminOut:
    return await content_admin.update_service(session, item_id, body)


@router.delete("/services/{item_id}", status_code=204)
async def delete_service(item_id: uuid.UUID, session: SessionDep) -> None:
    await content_admin.remove_row(session, Service, item_id, "services")


@router.get("/team", response_model=Page[TeamAdminOut])
async def list_team(
    session: SessionDep,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
) -> Page[TeamAdminOut]:
    return await content_admin.list_team(session, q, page, page_size)


@router.post("/team", response_model=TeamAdminOut, status_code=201)
async def create_team(body: TeamIn, session: SessionDep) -> TeamAdminOut:
    return await content_admin.create_team(session, body)


@router.post("/team/reorder", status_code=204)
async def reorder_team(body: ReorderIn, session: SessionDep) -> None:
    await content_admin.reorder(session, TeamMember, body.ids, "team")


@router.get("/team/{item_id}", response_model=TeamAdminOut)
async def get_team(item_id: uuid.UUID, session: SessionDep) -> TeamAdminOut:
    return await content_admin.get_team(session, item_id)


@router.patch("/team/{item_id}", response_model=TeamAdminOut)
async def update_team(item_id: uuid.UUID, body: TeamPatch, session: SessionDep) -> TeamAdminOut:
    return await content_admin.update_team(session, item_id, body)


@router.delete("/team/{item_id}", status_code=204)
async def delete_team(item_id: uuid.UUID, session: SessionDep) -> None:
    await content_admin.remove_row(session, TeamMember, item_id, "team")


@router.get("/portfolio", response_model=Page[PortfolioAdminOut])
async def list_portfolio(
    session: SessionDep,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
) -> Page[PortfolioAdminOut]:
    return await content_admin.list_portfolio(session, q, page, page_size)


@router.post("/portfolio", response_model=PortfolioAdminOut, status_code=201)
async def create_portfolio(body: PortfolioIn, session: SessionDep) -> PortfolioAdminOut:
    return await content_admin.create_portfolio(session, body)


@router.post("/portfolio/reorder", status_code=204)
async def reorder_portfolio(body: ReorderIn, session: SessionDep) -> None:
    await content_admin.reorder(session, PortfolioItem, body.ids, "portfolio")


@router.post("/portfolio/inspect", response_model=InspectOut)
async def inspect_portfolio(body: InspectIn) -> InspectOut:
    return await embeds.inspect_url(body.url)


@router.get("/portfolio/{item_id}", response_model=PortfolioAdminOut)
async def get_portfolio(item_id: uuid.UUID, session: SessionDep) -> PortfolioAdminOut:
    return await content_admin.get_portfolio(session, item_id)


@router.patch("/portfolio/{item_id}", response_model=PortfolioAdminOut)
async def update_portfolio(
    item_id: uuid.UUID, body: PortfolioPatch, session: SessionDep
) -> PortfolioAdminOut:
    return await content_admin.update_portfolio(session, item_id, body)


@router.delete("/portfolio/{item_id}", status_code=204)
async def delete_portfolio(item_id: uuid.UUID, session: SessionDep) -> None:
    await content_admin.remove_row(session, PortfolioItem, item_id, "portfolio")


@router.get("/testimonials", response_model=Page[TestimonialAdminOut])
async def list_testimonials(
    session: SessionDep,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
) -> Page[TestimonialAdminOut]:
    return await content_admin.list_testimonials(session, q, page, page_size)


@router.post("/testimonials", response_model=TestimonialAdminOut, status_code=201)
async def create_testimonial(body: TestimonialIn, session: SessionDep) -> TestimonialAdminOut:
    return await content_admin.create_testimonial(session, body)


@router.post("/testimonials/reorder", status_code=204)
async def reorder_testimonials(body: ReorderIn, session: SessionDep) -> None:
    await content_admin.reorder(session, Testimonial, body.ids, "testimonials")


@router.get("/testimonials/{item_id}", response_model=TestimonialAdminOut)
async def get_testimonial(item_id: uuid.UUID, session: SessionDep) -> TestimonialAdminOut:
    return await content_admin.get_testimonial(session, item_id)


@router.patch("/testimonials/{item_id}", response_model=TestimonialAdminOut)
async def update_testimonial(
    item_id: uuid.UUID, body: TestimonialPatch, session: SessionDep
) -> TestimonialAdminOut:
    return await content_admin.update_testimonial(session, item_id, body)


@router.delete("/testimonials/{item_id}", status_code=204)
async def delete_testimonial(item_id: uuid.UUID, session: SessionDep) -> None:
    await content_admin.remove_row(session, Testimonial, item_id, "testimonials")


@router.get("/faqs", response_model=Page[FaqAdminOut])
async def list_faqs(
    session: SessionDep,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
) -> Page[FaqAdminOut]:
    return await content_admin.list_faqs(session, q, page, page_size)


@router.post("/faqs", response_model=FaqAdminOut, status_code=201)
async def create_faq(body: FaqIn, session: SessionDep) -> FaqAdminOut:
    return await content_admin.create_faq(session, body)


@router.post("/faqs/reorder", status_code=204)
async def reorder_faqs(body: ReorderIn, session: SessionDep) -> None:
    await content_admin.reorder(session, Faq, body.ids, "faqs")


@router.get("/faqs/{item_id}", response_model=FaqAdminOut)
async def get_faq(item_id: uuid.UUID, session: SessionDep) -> FaqAdminOut:
    return await content_admin.get_faq(session, item_id)


@router.patch("/faqs/{item_id}", response_model=FaqAdminOut)
async def update_faq(item_id: uuid.UUID, body: FaqPatch, session: SessionDep) -> FaqAdminOut:
    return await content_admin.update_faq(session, item_id, body)


@router.delete("/faqs/{item_id}", status_code=204)
async def delete_faq(item_id: uuid.UUID, session: SessionDep) -> None:
    await content_admin.remove_row(session, Faq, item_id, "faqs")


@router.get("/links", response_model=Page[LinkAdminOut])
async def list_links(
    session: SessionDep,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
) -> Page[LinkAdminOut]:
    return await content_admin.list_links(session, q, page, page_size)


@router.post("/links", response_model=LinkAdminOut, status_code=201)
async def create_link(body: LinkIn, session: SessionDep) -> LinkAdminOut:
    return await content_admin.create_link(session, body)


@router.post("/links/reorder", status_code=204)
async def reorder_links(body: ReorderIn, session: SessionDep) -> None:
    await content_admin.reorder(session, BioLink, body.ids, "links")


@router.get("/links/{item_id}", response_model=LinkAdminOut)
async def get_link(item_id: uuid.UUID, session: SessionDep) -> LinkAdminOut:
    return await content_admin.get_link(session, item_id)


@router.patch("/links/{item_id}", response_model=LinkAdminOut)
async def update_link(item_id: uuid.UUID, body: LinkPatch, session: SessionDep) -> LinkAdminOut:
    return await content_admin.update_link(session, item_id, body)


@router.delete("/links/{item_id}", status_code=204)
async def delete_link(item_id: uuid.UUID, session: SessionDep) -> None:
    await content_admin.remove_row(session, BioLink, item_id, "links")


@router.get("/settings", response_model=SiteSettingsSchema)
async def read_settings(session: SessionDep) -> SiteSettingsSchema:
    return await admin_settings.read_settings(session)


@router.put("/settings", response_model=SiteSettingsSchema)
async def write_settings(
    body: SiteSettingsSchema,
    session: SessionDep,
    user: UserDep,
) -> SiteSettingsSchema:
    return await admin_settings.write_settings(session, user, body)


@router.get("/media", response_model=Page[MediaAdminOut])
async def list_media(
    session: SessionDep,
    kind: MediaKind | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=40, ge=1, le=100),
) -> Page[MediaAdminOut]:
    return await admin_media.list_media(session, kind, page, page_size)


@router.post("/media", response_model=MediaAdminOut, status_code=201)
async def upload_media(
    session: SessionDep,
    file: Annotated[UploadFile, File()],
    alt_text: Annotated[str | None, Form()] = None,
) -> MediaAdminOut:
    return await admin_media.upload_media(session, file, alt_text)


@router.get("/media/{media_id}", response_model=MediaAdminOut)
async def get_media(media_id: uuid.UUID, session: SessionDep) -> MediaAdminOut:
    return await admin_media.get_media(session, media_id)


@router.patch("/media/{media_id}", response_model=MediaAdminOut)
async def set_alt(media_id: uuid.UUID, body: MediaAltIn, session: SessionDep) -> MediaAdminOut:
    return await admin_media.set_alt(session, media_id, body.alt_text)


@router.get("/leads/export.csv")
async def export_leads(
    session: SessionDep,
    status: LeadStatus | None = None,
    service: str | None = None,
    utm_source: str | None = None,
    start: date | None = None,
    end: date | None = None,
    q: str | None = None,
) -> Response:
    return await admin_leads.export_csv(
        session,
        status=status,
        service=service,
        utm_source=utm_source,
        start=start,
        end=end,
        q=q,
    )


@router.get("/leads", response_model=Page[LeadAdminOut])
async def list_leads(
    session: SessionDep,
    status: LeadStatus | None = None,
    service: str | None = None,
    utm_source: str | None = None,
    start: date | None = None,
    end: date | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100),
) -> Page[LeadAdminOut]:
    return await admin_leads.list_leads(
        session,
        status=status,
        service=service,
        utm_source=utm_source,
        start=start,
        end=end,
        q=q,
        page=page,
        page_size=page_size,
    )


@router.get("/leads/{lead_id}", response_model=LeadDetailOut)
async def get_lead(lead_id: uuid.UUID, session: SessionDep) -> LeadDetailOut:
    return await admin_leads.get_lead(session, lead_id)


@router.patch("/leads/{lead_id}", response_model=LeadDetailOut)
async def patch_lead(
    lead_id: uuid.UUID,
    body: LeadStatusIn,
    session: SessionDep,
    user: UserDep,
) -> LeadDetailOut:
    return await admin_leads.set_status(session, user, lead_id, body.status)


@router.post("/leads/{lead_id}/notes", response_model=LeadDetailOut)
async def note_lead(
    lead_id: uuid.UUID,
    body: LeadNoteIn,
    session: SessionDep,
    user: UserDep,
) -> LeadDetailOut:
    return await admin_leads.add_note(session, user, lead_id, body.note)


@router.get("/leads/{lead_id}/demo")
async def lead_demo(lead_id: uuid.UUID, session: SessionDep) -> FileResponse:
    path, mime = await admin_leads.demo_file(
        session,
        LocalStorage(Path(get_settings().media_root)),
        lead_id,
    )
    return FileResponse(path, media_type=mime, filename="maqueta")


@router.delete("/leads/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: uuid.UUID,
    session: SessionDep,
    confirm: bool = False,
) -> None:
    await admin_leads.delete_lead(session, lead_id, confirm)


@router.get("/stats/overview", response_model=StatsOut)
async def stats(session: SessionDep) -> StatsOut:
    return await admin_stats.overview(session)


@router.post("/preview-token", response_model=PreviewTokenOut)
async def preview_token(session: SessionDep, user: UserDep) -> PreviewTokenOut:
    return await auth.issue_preview(session, user)


@router.get("/users", response_model=list[UserAdminOut], dependencies=[Depends(require_superadmin)])
async def list_users(session: SessionDep) -> list[UserAdminOut]:
    return await admin_users.list_users(session)


@router.post(
    "/users",
    response_model=UserAdminOut,
    status_code=201,
    dependencies=[Depends(require_superadmin)],
)
async def create_user(body: UserCreateIn, session: SessionDep) -> UserAdminOut:
    return await admin_users.create_user(session, body)


@router.patch(
    "/users/{user_id}",
    response_model=UserAdminOut,
    dependencies=[Depends(require_superadmin)],
)
async def update_user(
    user_id: uuid.UUID,
    body: UserPatchIn,
    session: SessionDep,
    user: UserDep,
) -> UserAdminOut:
    return await admin_users.update_user(session, user, user_id, body)


@router.post(
    "/users/{user_id}/password",
    status_code=204,
    dependencies=[Depends(require_superadmin)],
)
async def user_password(user_id: uuid.UUID, body: UserPasswordIn, session: SessionDep) -> None:
    await admin_users.reset_password(session, user_id, body.new_password)
