from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class UtmIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    source: str | None = None
    medium: str | None = None
    campaign: str | None = None
    content: str | None = None
    term: str | None = None


class LeadIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    email: str | None = None
    phone: str | None = None
    service_slug: str | None = None
    message: str = Field(min_length=1, max_length=5000)
    demo_url: str | None = None
    demo_upload_token: str | None = None
    tentative_date: date | None = None
    consent: bool
    source_page: str = Field(min_length=1, max_length=300)
    referrer: str | None = None
    utm: UtmIn | None = None
    website: str = ""
    turnstile_token: str | None = None


class LeadCreated(BaseModel):
    ok: bool = True


class UploadAccepted(BaseModel):
    upload_token: str
