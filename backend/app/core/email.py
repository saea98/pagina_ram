from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import get_settings

_TEMPLATES = Path(__file__).resolve().parents[2] / "templates" / "email"
_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATES),
    autoescape=select_autoescape(["html"]),
)


async def deliver(payload: dict[str, object]) -> None:
    template = str(payload["template"])
    recipients = [str(item) for item in payload["to"]] if isinstance(payload["to"], list) else []
    if not recipients:
        return
    raw_context = payload["context"] if isinstance(payload["context"], dict) else {}
    context = {str(key): "" if value is None else str(value) for key, value in raw_context.items()}
    reply_to = payload.get("reply_to")
    subject = str(payload["subject"])
    message = EmailMessage()
    settings = get_settings()
    message["From"] = settings.smtp_from
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    if isinstance(reply_to, str) and reply_to:
        message["Reply-To"] = reply_to
    message.set_content(_ENV.get_template(f"{template}.txt").render(**context))
    message.add_alternative(
        _ENV.get_template(f"{template}.html").render(**context),
        subtype="html",
    )
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        start_tls=bool(settings.smtp_user),
    )
