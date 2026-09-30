import csv
import io
import uuid
from datetime import UTC, date, datetime
from typing import cast

from app.core.errors import AppError, NotFound
from app.core.storage import LocalStorage
from app.models.content import Service
from app.models.enums import LeadEventType, LeadStatus
from app.models.leads import Lead, LeadEvent
from app.models.media import MediaAsset
from app.models.users import User
from app.schemas.admin import LeadAdminOut, LeadDetailOut, LeadEventOut, Page
from fastapi.responses import Response
from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class DeleteNotConfirmed(AppError):
    code = "bad_request"
    status_code = 400


def _pairs(rows: object) -> list[tuple[Lead, str | None]]:
    return cast(list[tuple[Lead, str | None]], rows)


def _out(lead: Lead, service_title: str | None) -> LeadAdminOut:
    return LeadAdminOut(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone_e164=lead.phone_e164,
        service_id=lead.service_id,
        service_title=service_title,
        message=lead.message,
        demo_url=lead.demo_url,
        has_demo=lead.demo_media_id is not None,
        tentative_date=None if lead.tentative_date is None else lead.tentative_date.isoformat(),
        status=lead.status,
        source_page=lead.source_page,
        referrer=lead.referrer,
        utm_source=lead.utm_source,
        utm_medium=lead.utm_medium,
        utm_campaign=lead.utm_campaign,
        utm_content=lead.utm_content,
        utm_term=lead.utm_term,
        created_at=lead.created_at,
    )


def _filtered(
    status: LeadStatus | None,
    service: str | None,
    utm_source: str | None,
    start: date | None,
    end: date | None,
    q: str | None,
) -> Select[tuple[Lead, str | None]]:
    query = (
        select(Lead, Service.title)
        .outerjoin(Service, Service.id == Lead.service_id)
        .where(Lead.deleted_at.is_(None))
    )
    if status is not None:
        query = query.where(Lead.status == status)
    if service:
        query = query.where(Service.slug == service)
    if utm_source:
        query = query.where(Lead.utm_source == utm_source)
    if start is not None:
        query = query.where(Lead.created_at >= datetime.combine(start, datetime.min.time(), UTC))
    if end is not None:
        query = query.where(Lead.created_at <= datetime.combine(end, datetime.max.time(), UTC))
    if q:
        term = f"%{q.strip()}%"
        query = query.where(
            or_(Lead.name.ilike(term), Lead.email.ilike(term), Lead.message.ilike(term))
        )
    return cast(Select[tuple[Lead, str | None]], query)


async def list_leads(
    session: AsyncSession,
    *,
    status: LeadStatus | None,
    service: str | None,
    utm_source: str | None,
    start: date | None,
    end: date | None,
    q: str | None,
    page: int,
    page_size: int,
) -> Page[LeadAdminOut]:
    query = _filtered(status, service, utm_source, start, end, q)
    rows = (await session.execute(query.order_by(Lead.created_at.desc()))).all()
    sliced = rows[(page - 1) * page_size : page * page_size]
    return Page(
        items=[_out(lead, title) for lead, title in _pairs(sliced)],
        total=len(rows),
        page=page,
        page_size=page_size,
    )


async def get_lead(session: AsyncSession, lead_id: uuid.UUID) -> LeadDetailOut:
    row = (
        await session.execute(
            select(Lead, Service.title)
            .outerjoin(Service, Service.id == Lead.service_id)
            .where(Lead.id == lead_id, Lead.deleted_at.is_(None))
        )
    ).one_or_none()
    if row is None:
        raise NotFound("No encontramos ese mensaje.")
    lead, title = row
    events = (
        await session.scalars(
            select(LeadEvent).where(LeadEvent.lead_id == lead.id).order_by(LeadEvent.created_at)
        )
    ).all()
    base = _out(lead, title)
    return LeadDetailOut(
        **base.model_dump(),
        events=[
            LeadEventOut(
                id=event.id,
                type=event.type.value,
                from_status=None if event.from_status is None else event.from_status.value,
                to_status=None if event.to_status is None else event.to_status.value,
                note=event.note,
                created_at=event.created_at,
            )
            for event in events
        ],
    )


async def set_status(
    session: AsyncSession,
    user: User,
    lead_id: uuid.UUID,
    status: LeadStatus,
) -> LeadDetailOut:
    lead = await session.get(Lead, lead_id)
    if lead is None or lead.deleted_at is not None:
        raise NotFound("No encontramos ese mensaje.")
    if lead.status is not status:
        session.add(
            LeadEvent(
                lead_id=lead.id,
                user_id=user.id,
                type=LeadEventType.STATUS_CHANGE,
                from_status=lead.status,
                to_status=status,
            )
        )
        lead.status = status
        await session.commit()
    return await get_lead(session, lead_id)


async def add_note(
    session: AsyncSession,
    user: User,
    lead_id: uuid.UUID,
    note: str,
) -> LeadDetailOut:
    lead = await session.get(Lead, lead_id)
    if lead is None or lead.deleted_at is not None:
        raise NotFound("No encontramos ese mensaje.")
    session.add(
        LeadEvent(
            lead_id=lead.id,
            user_id=user.id,
            type=LeadEventType.NOTE,
            note=note,
        )
    )
    await session.commit()
    return await get_lead(session, lead_id)


async def export_csv(
    session: AsyncSession,
    *,
    status: LeadStatus | None,
    service: str | None,
    utm_source: str | None,
    start: date | None,
    end: date | None,
    q: str | None,
) -> Response:
    rows = (await session.execute(_filtered(status, service, utm_source, start, end, q))).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["nombre", "correo", "telefono", "servicio", "estado", "fuente", "mensaje", "creado"]
    )
    for lead, title in _pairs(rows):
        writer.writerow(
            [
                lead.name,
                lead.email or "",
                lead.phone_e164 or "",
                title or "",
                lead.status.value,
                lead.utm_source or "",
                lead.message,
                lead.created_at.isoformat(),
            ]
        )
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


async def delete_lead(session: AsyncSession, lead_id: uuid.UUID, confirm: bool) -> None:
    if not confirm:
        raise DeleteNotConfirmed(
            "Confirma el borrado con confirm=true. Esto es irreversible (ARCO)."
        )
    lead = await session.get(Lead, lead_id)
    if lead is None:
        raise NotFound("No encontramos ese mensaje.")
    await session.delete(lead)
    await session.commit()


async def demo_file(
    session: AsyncSession,
    storage: LocalStorage,
    lead_id: uuid.UUID,
) -> tuple[str, str]:
    lead = await session.get(Lead, lead_id)
    if lead is None or lead.deleted_at is not None or lead.demo_media_id is None:
        raise NotFound("Este mensaje no tiene maqueta.")
    asset = await session.get(MediaAsset, lead.demo_media_id)
    if asset is None:
        raise NotFound("No encontramos la maqueta.")
    return str(storage.path(asset.storage_key)), asset.mime_type
