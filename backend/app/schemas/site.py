from pydantic import BaseModel, ConfigDict, Field


class BrandSettings(BaseModel):
    name: str
    tagline: str
    logo_media_id: str | None = None
    logo_alt_media_id: str | None = None


class HeroSettings(BaseModel):
    quote: str
    title_html: str
    cta_primary_text: str
    cta_secondary_text: str
    image_media_id: str | None = None


class StudioSettings(BaseModel):
    eyebrow: str
    title: str
    body: str
    image_media_id: str | None = None
    image_caption: str


class SectionHeading(BaseModel):
    eyebrow: str
    title: str


class ServicesSettings(SectionHeading):
    lede: str
    hint: str


class PortfolioSettings(SectionHeading):
    note: str
    featured_limit: int = 4


class ContactSettings(BaseModel):
    eyebrow: str
    title: str
    email: str
    whatsapp_e164: str = ""
    whatsapp_default_msg: str = ""
    notify_emails: list[str] = Field(default_factory=list)
    consent_text: str


class SocialSettings(BaseModel):
    instagram: str = ""
    tiktok: str = ""
    youtube: str = ""
    spotify: str = ""
    facebook: str = ""
    x: str = ""
    threads: str = ""
    soundcloud: str = ""


class SeoSettings(BaseModel):
    default_title: str
    title_template: str
    default_description: str
    og_image_media_id: str | None = None


class LegalSettings(BaseModel):
    privacy_html: str
    privacy_updated_at: str


class FeatureSettings(BaseModel):
    ab_player: bool = False
    testimonials: bool = False
    turnstile: bool = False
    whatsapp_float: bool = False


class SiteSettingsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand: BrandSettings
    hero: HeroSettings
    studio: StudioSettings
    team: SectionHeading
    services: ServicesSettings
    portfolio: PortfolioSettings
    contact: ContactSettings
    social: SocialSettings
    seo: SeoSettings
    legal: LegalSettings
    features: FeatureSettings
