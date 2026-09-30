from sqlalchemy import BigInteger, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import (
    MEDIA_KIND,
    MEDIA_STATUS,
    MEDIA_VISIBILITY,
    MediaKind,
    MediaStatus,
    MediaVisibility,
)
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class MediaAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "media_assets"

    kind: Mapped[MediaKind] = mapped_column(MEDIA_KIND, nullable=False)
    visibility: Mapped[MediaVisibility] = mapped_column(MEDIA_VISIBILITY, nullable=False)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MediaStatus] = mapped_column(MEDIA_STATUS, nullable=False)
    variants: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, server_default="{}")
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    duration_s: Mapped[float | None] = mapped_column(Numeric(10, 3))
    lufs_integrated: Mapped[float | None] = mapped_column(Numeric(6, 2))
    peaks_key: Mapped[str | None] = mapped_column(Text)
    lqip: Mapped[str | None] = mapped_column(Text)
    alt_text: Mapped[str | None] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(Text, nullable=False, index=True)
