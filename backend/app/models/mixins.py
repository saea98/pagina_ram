import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from uuid_utils import uuid7


def new_uuid() -> uuid.UUID:
    generated = uuid7()
    return uuid.UUID(bytes=generated.bytes)


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OrderedMixin:
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class PublishableMixin:
    is_published: Mapped[bool] = mapped_column(nullable=False, server_default="false")
