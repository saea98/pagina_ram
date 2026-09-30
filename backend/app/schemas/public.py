from datetime import datetime
from typing import Literal

from app.schemas.site import (
    BrandSettings,
    ContactSettings,
    FeatureSettings,
    HeroSettings,
    LegalSettings,
    PortfolioSettings,
    SectionHeading,
    SeoSettings,
    ServicesSettings,
    SocialSettings,
    StudioSettings,
)
from pydantic import BaseModel, ConfigDict, Field


class ContactPublic(ContactSettings):
    notify_emails: list[str] = Field(default_factory=list, exclude=True)


class ImageOut(BaseModel):
    alt: str | None
    width: int | None
    height: int | None
    lqip: str | None
    webp: dict[str, str]
    avif: dict[str, str]


class SitePublic(BaseModel):
    model_config = ConfigDict(extra="ignore")

    brand: BrandSettings
    hero: HeroSettings
    studio: StudioSettings
    team: SectionHeading
    services: ServicesSettings
    portfolio: PortfolioSettings
    contact: ContactPublic
    social: SocialSettings
    seo: SeoSettings
    legal: LegalSettings
    features: FeatureSettings
    media: dict[str, ImageOut] = Field(default_factory=dict)


class AudioOut(BaseModel):
    duration_s: float | None
    lufs: float | None
    m4a_url: str | None
    mp3_url: str | None
    peaks_url: str | None


class ServiceCardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    number_label: str
    title: str
    short_description: str
    icon: str
    price_from_mxn: int | None
    sort_order: int
    updated_at: datetime


class FaqOut(BaseModel):
    question: str
    answer: str
    service_slug: str | None


class PortfolioCardOut(BaseModel):
    slug: str
    title: str
    artist_name: str
    year: int | None
    genre: str | None
    kind: str
    external_url: str | None
    external_id: str | None
    youtube_start_s: int | None
    is_featured: bool
    is_ab_featured: bool
    play_count: int
    cover: ImageOut | None
    audio: AudioOut | None = None
    audio_before: AudioOut | None = None
    service_slugs: list[str]
    updated_at: datetime


class ServiceDetailOut(ServiceCardOut):
    long_description: str
    faqs: list[FaqOut]
    portfolio: list[PortfolioCardOut]


class TeamCardOut(BaseModel):
    slug: str
    full_name: str
    nickname: str
    role_label: str
    bio_short: str
    photo: ImageOut | None
    socials: dict[str, object]
    updated_at: datetime


class CreditOut(BaseModel):
    portfolio_slug: str
    portfolio_title: str
    role_label: str


class TeamDetailOut(TeamCardOut):
    bio_long: str
    credits: list[CreditOut]


class PortfolioDetailOut(PortfolioCardOut):
    credits_text: str
    description: str | None


class TestimonialOut(BaseModel):
    quote: str
    author_name: str
    author_role: str
    project_label: str
    photo: ImageOut | None
    portfolio_slug: str | None


class BioLinkOut(BaseModel):
    id: str
    label: str
    url: str
    icon: str
    highlight: bool
    is_internal: bool


class PrivacyOut(BaseModel):
    html: str
    updated_at: str


class HomeOut(BaseModel):
    site: SitePublic
    services: list[ServiceCardOut]
    team: list[TeamCardOut]
    portfolio: list[PortfolioCardOut]
    ab_comparisons: list[PortfolioCardOut]
    testimonials: list[TestimonialOut]


class PlayEventIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    event: Literal["play", "ab_toggle", "complete"]
