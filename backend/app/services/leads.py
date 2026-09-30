import os
import re
from datetime import UTC, datetime
from pathlib import Path

import httpx
import structlog
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.ratelimit import client_ip_hash
from app.core.storage import LocalStorage
from app.core.uploads import issue_upload_token, read_upload_token
from app.models.enums import JobType, LeadStatus, MediaVisibility
from app.models.jobs import Job
from app.models.leads import Lead
from app.models.media import MediaAsset
from app.models.users import SiteSettings
from app.repositories.public import get_service
from app.schemas.leads import LeadIn
from app.services.media import ingest_upload
from fastapi import Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger()
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE = re.compile(r"^\+[1-9]\d{7,14}$")
_TURNSTILE = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


class LeadValidation(AppError):
    code = "validation_error"
    status_code = 422


async def accept_demo(session: AsyncSession, upload: UploadFile) -> str:
    settings = get_settings()
    storage = LocalStorage(Path(settings.media_root))
    filename = upload.filename or "maqueta"
    asset = await ingest_upload(
        session,
        storage,
        upload.file,
        filename=filename,
        visibility=MediaVisibility.PRIVATE,
        max_bytes=settings.max_upload_mb_lead * 1024 * 1024,
        process=False,
    )
    return issue_upload_token(asset.id)


async def create_lead(session: AsyncSession, request: Request, body: LeadIn) -> None:
    if body.website.strip():
        log.info("spam_honeypot")
        return
    _validate(body)
    await _verify_turnstile(body.turnstile_token, request)
    settings_row = await session.get(SiteSettings, 1)
    if settings_row is None:
        raise LeadValidation("El sitio todavía no puede recibir mensajes.")
    data = settings_row.data
    legal = data.get("legal")
    contact = data.get("contact")
    version = legal.get("privacy_updated_at") if isinstance(legal, dict) else None
    if not isinstance(version, str) or not version:
        raise LeadValidation("El aviso de privacidad no está disponible.")
    service_id = None
    service_title = "Aún no estoy seguro"
    if body.service_slug:
        service = await get_service(session, body.service_slug)
        if service is None:
            raise LeadValidation(
                "Ese servicio no existe.",
                fields={"service_slug": "Elige un servicio de la lista."},
            )
        service_id = service.id
        service_title = service.title
    demo_id = None
    if body.demo_upload_token:
        media_id = read_upload_token(body.demo_upload_token)
        asset = await session.get(MediaAsset, media_id)
        if asset is None or asset.visibility is not MediaVisibility.PRIVATE:
            raise LeadValidation(
                "La maqueta expiró o no es válida.",
                fields={"demo_upload_token": "Súbela de nuevo."},
            )
        demo_id = asset.id
    utm = body.utm
    lead = Lead(
        name=body.name,
        email=body.email,
        phone_e164=body.phone,
        service_id=service_id,
        message=body.message,
        demo_url=body.demo_url,
        demo_media_id=demo_id,
        tentative_date=body.tentative_date,
        consent_at=datetime.now(UTC),
        consent_text_version=version,
        status=LeadStatus.NEW,
        source_page=body.source_page,
        referrer=body.referrer,
        utm_source=utm.source if utm else None,
        utm_medium=utm.medium if utm else None,
        utm_campaign=utm.campaign if utm else None,
        utm_content=utm.content if utm else None,
        utm_term=utm.term if utm else None,
        ip_hash=client_ip_hash(request),
    )
    session.add(lead)
    await session.flush()
    context = {
        "name": body.name,
        "email": body.email or "—",
        "phone": body.phone or "—",
        "service": service_title,
        "message": body.message,
        "source_page": body.source_page,
    }
    notify = contact.get("notify_emails") if isinstance(contact, dict) else None
    recipients = (
        [item for item in notify if isinstance(item, str)] if isinstance(notify, list) else []
    )
    if recipients:
        session.add(
            _email_job(
                template="lead_notification",
                subject="Nuevo contacto — Cherry Studios",
                recipients=recipients,
                reply_to=body.email,
                context=context,
            )
        )
    if body.email:
        session.add(
            _email_job(
                template="lead_ack",
                subject="Recibimos tu mensaje — Cherry Studios",
                recipients=[body.email],
                reply_to=None,
                context=context,
            )
        )
    await session.commit()


def _validate(body: LeadIn) -> None:
    fields: dict[str, str] = {}
    if not body.consent:
        fields["consent"] = "Necesitamos tu consentimiento para contactarte."
    if not body.email and not body.phone:
        fields["email"] = "Escribe un correo o un teléfono."
    if body.email and _EMAIL.fullmatch(body.email) is None:
        fields["email"] = "El correo no es válido."
    if body.phone and _PHONE.fullmatch(body.phone) is None:
        fields["phone"] = "Usa el teléfono con clave de país, por ejemplo +525512345678."
    if fields:
        raise LeadValidation("Revisa los datos enviados.", fields=fields)


async def _verify_turnstile(token: str | None, request: Request) -> None:
    secret = os.environ.get("TURNSTILE_SECRET_KEY", "") or get_settings().turnstile_secret_key
    if not secret:
        return
    if not token:
        raise LeadValidation(
            "Confirma que no eres un robot.",
            fields={"turnstile_token": "Falta la verificación."},
        )
    forwarded = request.headers.get("x-forwarded-for", "")
    remote = forwarded.split(",", 1)[0].strip() if forwarded else None
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.post(
            _TURNSTILE,
            data={"secret": secret, "response": token, "remoteip": remote or ""},
        )
    payload = response.json()
    if response.status_code != 200 or not payload.get("success"):
        raise LeadValidation(
            "No pudimos verificar que no eres un robot.",
            fields={"turnstile_token": "Inténtalo de nuevo."},
        )


def _email_job(
    *,
    template: str,
    subject: str,
    recipients: list[str],
    reply_to: str | None,
    context: dict[str, str],
) -> Job:
    return Job(
        type=JobType.SEND_EMAIL,
        payload={
            "template": template,
            "subject": subject,
            "to": recipients,
            "reply_to": reply_to,
            "context": context,
        },
        run_after=datetime.now(UTC),
    )
