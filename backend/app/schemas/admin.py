from datetime import datetime
from uuid import UUID

from app.models.enums import LeadStatus, MediaKind, MediaStatus, PortfolioKind, UserRole
from pydantic import BaseModel, ConfigDict, Field


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int


class ReorderIn(BaseModel):
    ids: list[UUID] = Field(min_length=1)


class ServiceIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str = Field(min_length=1, max_length=80)
    number_label: str = ""
    title: str = Field(min_length=1, max_length=160)
    short_description: str = Field(min_length=1, max_length=180)
    long_description: str = Field(min_length=1)
    icon: str = Field(min_length=1, max_length=40)
    price_from_mxn: int | None = None
    image_media_id: UUID | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    is_published: bool = False


class ServicePatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str | None = None
    number_label: str | None = None
    title: str | None = None
    short_description: str | None = Field(default=None, max_length=180)
    long_description: str | None = None
    icon: str | None = None
    price_from_mxn: int | None = None
    image_media_id: UUID | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    is_published: bool | None = None


class ServiceAdminOut(ServiceIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sort_order: int
    updated_at: datetime


class TeamIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str = Field(min_length=1, max_length=80)
    full_name: str = Field(min_length=1)
    nickname: str = Field(min_length=1)
    role_label: str = Field(min_length=1)
    bio_short: str = Field(min_length=1)
    bio_long: str = ""
    photo_media_id: UUID | None = None
    socials: dict[str, str] = Field(default_factory=dict)
    is_published: bool = False


class TeamPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str | None = None
    full_name: str | None = None
    nickname: str | None = None
    role_label: str | None = None
    bio_short: str | None = None
    bio_long: str | None = None
    photo_media_id: UUID | None = None
    socials: dict[str, str] | None = None
    is_published: bool | None = None


class TeamAdminOut(TeamIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sort_order: int
    updated_at: datetime


class CreditIn(BaseModel):
    team_member_id: UUID
    role_label: str = ""


class PortfolioIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1)
    artist_name: str = Field(min_length=1)
    year: int | None = None
    genre: str | None = None
    kind: PortfolioKind
    external_url: str | None = None
    external_id: str | None = None
    youtube_start_s: int | None = None
    cover_media_id: UUID | None = None
    audio_after_media_id: UUID | None = None
    audio_before_media_id: UUID | None = None
    credits_text: str = ""
    description: str | None = None
    is_featured: bool = False
    is_ab_featured: bool = False
    is_published: bool = False
    service_ids: list[UUID] = Field(default_factory=list)
    credits: list[CreditIn] = Field(default_factory=list)


class PortfolioPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str | None = None
    title: str | None = None
    artist_name: str | None = None
    year: int | None = None
    genre: str | None = None
    kind: PortfolioKind | None = None
    external_url: str | None = None
    external_id: str | None = None
    youtube_start_s: int | None = None
    cover_media_id: UUID | None = None
    audio_after_media_id: UUID | None = None
    audio_before_media_id: UUID | None = None
    credits_text: str | None = None
    description: str | None = None
    is_featured: bool | None = None
    is_ab_featured: bool | None = None
    is_published: bool | None = None
    service_ids: list[UUID] | None = None
    credits: list[CreditIn] | None = None


class PortfolioAdminOut(PortfolioIn):
    id: UUID
    sort_order: int
    play_count: int
    updated_at: datetime


class TestimonialIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    quote: str = Field(min_length=1)
    author_name: str = Field(min_length=1)
    author_role: str = ""
    project_label: str = ""
    photo_media_id: UUID | None = None
    portfolio_item_id: UUID | None = None
    is_published: bool = False


class TestimonialPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    quote: str | None = None
    author_name: str | None = None
    author_role: str | None = None
    project_label: str | None = None
    photo_media_id: UUID | None = None
    portfolio_item_id: UUID | None = None
    is_published: bool | None = None


class TestimonialAdminOut(TestimonialIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sort_order: int
    updated_at: datetime


class FaqIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    service_id: UUID | None = None
    is_published: bool = False


class FaqPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str | None = None
    answer: str | None = None
    service_id: UUID | None = None
    is_published: bool | None = None


class FaqAdminOut(FaqIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sort_order: int
    updated_at: datetime


class LinkIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    label: str = Field(min_length=1)
    url: str = Field(min_length=1)
    icon: str = ""
    is_internal: bool = False
    utm_overrides: dict[str, str] = Field(default_factory=dict)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    highlight: bool = False
    is_published: bool = False


class LinkPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    label: str | None = None
    url: str | None = None
    icon: str | None = None
    is_internal: bool | None = None
    utm_overrides: dict[str, str] | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    highlight: bool | None = None
    is_published: bool | None = None


class LinkAdminOut(LinkIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sort_order: int
    updated_at: datetime


class MediaAdminOut(BaseModel):
    id: UUID
    kind: MediaKind
    status: MediaStatus
    original_filename: str
    mime_type: str
    alt_text: str | None
    width: int | None
    height: int | None
    duration_s: float | None
    lufs_integrated: float | None
    preview_url: str | None
    created_at: datetime


class MediaAltIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    alt_text: str = Field(min_length=1, max_length=300)


class InspectIn(BaseModel):
    url: str = Field(min_length=8)


class InspectOut(BaseModel):
    kind: PortfolioKind | None = None
    external_id: str | None = None
    youtube_start_s: int | None = None
    title: str | None = None
    artist_name: str | None = None


class LeadNoteIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    note: str = Field(min_length=1, max_length=4000)


class LeadStatusIn(BaseModel):
    status: LeadStatus


class LeadEventOut(BaseModel):
    id: UUID
    type: str
    from_status: str | None
    to_status: str | None
    note: str | None
    created_at: datetime


class LeadAdminOut(BaseModel):
    id: UUID
    name: str
    email: str | None
    phone_e164: str | None
    service_id: UUID | None
    service_title: str | None
    message: str
    demo_url: str | None
    has_demo: bool
    tentative_date: str | None
    status: LeadStatus
    source_page: str
    referrer: str | None
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    utm_content: str | None
    utm_term: str | None
    created_at: datetime


class LeadDetailOut(LeadAdminOut):
    events: list[LeadEventOut]


class UserCreateIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=200)
    full_name: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=8, max_length=200)
    role: UserRole = UserRole.ADMIN


class UserPatchIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserPasswordIn(BaseModel):
    new_password: str = Field(min_length=8, max_length=200)


class UserAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    last_login_at: datetime | None


class CountPoint(BaseModel):
    label: str
    count: int


class PiecePlays(BaseModel):
    title: str
    plays: int


class StatsOut(BaseModel):
    new_leads_7d: int
    close_rate: float | None
    top_source_month: str | None
    link_clicks_7d: int
    leads_by_status: list[CountPoint]
    leads_by_source: list[CountPoint]
    leads_by_week: list[CountPoint]
    top_pieces: list[PiecePlays]
