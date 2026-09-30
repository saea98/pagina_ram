import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import PLAY_EVENT_TYPE, PORTFOLIO_KIND, PlayEventType, PortfolioKind
from app.models.mixins import (
    OrderedMixin,
    PublishableMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class Service(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    OrderedMixin,
    PublishableMixin,
    Base,
):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint(
            "char_length(short_description) <= 180",
            name="short_description_len",
        ),
    )

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    number_label: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str] = mapped_column(Text, nullable=False)
    long_description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(Text, nullable=False)
    price_from_mxn: Mapped[int | None] = mapped_column(Integer)
    image_media_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    seo_title: Mapped[str | None] = mapped_column(Text)
    seo_description: Mapped[str | None] = mapped_column(Text)


class TeamMember(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    OrderedMixin,
    PublishableMixin,
    Base,
):
    __tablename__ = "team_members"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    nickname: Mapped[str] = mapped_column(Text, nullable=False)
    role_label: Mapped[str] = mapped_column(Text, nullable=False)
    bio_short: Mapped[str] = mapped_column(Text, nullable=False)
    bio_long: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    photo_media_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    socials: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, server_default="{}")


class PortfolioItem(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    OrderedMixin,
    PublishableMixin,
    Base,
):
    __tablename__ = "portfolio_items"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    artist_name: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    genre: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[PortfolioKind] = mapped_column(PORTFOLIO_KIND, nullable=False)
    external_url: Mapped[str | None] = mapped_column(Text)
    external_id: Mapped[str | None] = mapped_column(Text)
    youtube_start_s: Mapped[int | None] = mapped_column(Integer)
    cover_media_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    audio_after_media_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    audio_before_media_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    credits_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    description: Mapped[str | None] = mapped_column(Text)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_ab_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    play_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class PortfolioItemService(TimestampMixin, Base):
    __tablename__ = "portfolio_item_services"

    portfolio_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("portfolio_items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    )


class PortfolioItemCredit(TimestampMixin, Base):
    __tablename__ = "portfolio_item_credits"

    portfolio_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("portfolio_items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    team_member_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team_members.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_label: Mapped[str] = mapped_column(Text, nullable=False, server_default="")


class Testimonial(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    OrderedMixin,
    PublishableMixin,
    Base,
):
    __tablename__ = "testimonials"

    quote: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(Text, nullable=False)
    author_role: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    project_label: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    photo_media_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    portfolio_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("portfolio_items.id"))


class Faq(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    OrderedMixin,
    PublishableMixin,
    Base,
):
    __tablename__ = "faqs"

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    service_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("services.id"))


class BioLink(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    OrderedMixin,
    PublishableMixin,
    Base,
):
    __tablename__ = "bio_links"

    label: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    utm_overrides: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    highlight: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")


class BioLinkClick(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bio_link_clicks"

    bio_link_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bio_links.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    referrer: Mapped[str | None] = mapped_column(Text)
    user_agent_family: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)


class PlayEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "play_events"
    __table_args__ = (
        UniqueConstraint("portfolio_item_id", "event", "occurred_on", name="uq_play_events_daily"),
    )

    portfolio_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("portfolio_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    event: Mapped[PlayEventType] = mapped_column(PLAY_EVENT_TYPE, nullable=False)
    occurred_on: Mapped[date] = mapped_column(Date, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
