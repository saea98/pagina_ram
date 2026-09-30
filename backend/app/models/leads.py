import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import LEAD_EVENT_TYPE, LEAD_STATUS, LeadEventType, LeadStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Lead(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint("email IS NOT NULL OR phone_e164 IS NOT NULL", name="email_or_phone"),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str | None] = mapped_column(CITEXT)
    phone_e164: Mapped[str | None] = mapped_column(Text)
    service_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("services.id"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    demo_url: Mapped[str | None] = mapped_column(Text)
    demo_media_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    tentative_date: Mapped[date | None] = mapped_column(Date)
    consent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consent_text_version: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[LeadStatus] = mapped_column(LEAD_STATUS, nullable=False, server_default="new")
    source_page: Mapped[str] = mapped_column(Text, nullable=False)
    referrer: Mapped[str | None] = mapped_column(Text)
    utm_source: Mapped[str | None] = mapped_column(Text)
    utm_medium: Mapped[str | None] = mapped_column(Text)
    utm_campaign: Mapped[str | None] = mapped_column(Text)
    utm_content: Mapped[str | None] = mapped_column(Text)
    utm_term: Mapped[str | None] = mapped_column(Text)
    quote_payload: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    ip_hash: Mapped[str] = mapped_column(Text, nullable=False)


class LeadEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lead_events"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    type: Mapped[LeadEventType] = mapped_column(LEAD_EVENT_TYPE, nullable=False)
    from_status: Mapped[LeadStatus | None] = mapped_column(LEAD_STATUS)
    to_status: Mapped[LeadStatus | None] = mapped_column(LEAD_STATUS)
    note: Mapped[str | None] = mapped_column(Text)
