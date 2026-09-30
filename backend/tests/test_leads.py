import asyncio
import time
from pathlib import Path

import httpx
import pytest
from app.core.db import SessionMaker
from app.core.storage import LocalStorage
from app.models.jobs import Job
from app.models.leads import Lead
from app.workers.loop import run_once
from httpx import AsyncClient
from sqlalchemy import func, select
from tests.test_media_pipeline import _wav_5s
from tests.test_public import _ensure_seed_env

_LEAD = {
    "name": "Ana López",
    "email": "ana@mail.com",
    "phone": "+525512345678",
    "service_slug": "mezcla",
    "message": "Tengo 3 canciones.",
    "source_page": "/servicios/mezcla",
    "consent": True,
    "website": "",
    "utm": {"source": "instagram", "medium": "bio", "campaign": "lanzamiento"},
}


@pytest.fixture(scope="module", autouse=True)
async def _seeded() -> None:
    _ensure_seed_env()
    from app.core.config import get_settings
    from app.seed.run import run_seed

    get_settings.cache_clear()
    await run_seed()


async def test_lead_validation(client: AsyncClient) -> None:
    missing = await client.post(
        "/api/v1/public/leads",
        json={**_LEAD, "email": None, "phone": None},
        headers={"X-Forwarded-For": "203.0.113.10"},
    )
    refused = await client.post(
        "/api/v1/public/leads",
        json={**_LEAD, "consent": False},
        headers={"X-Forwarded-For": "203.0.113.11"},
    )
    assert missing.status_code == 422
    assert "email" in missing.json()["error"]["fields"]
    assert refused.status_code == 422
    assert "consent" in refused.json()["error"]["fields"]


async def test_honeypot_does_not_store(client: AsyncClient) -> None:
    before = await _lead_count()
    response = await client.post(
        "/api/v1/public/leads",
        json={**_LEAD, "website": "https://spam.test", "email": "bot@spam.test"},
        headers={"X-Forwarded-For": "203.0.113.12"},
    )
    assert response.status_code == 201
    assert await _lead_count() == before


async def test_rate_limit(client: AsyncClient) -> None:
    headers = {"X-Forwarded-For": "203.0.113.13"}
    codes = []
    for _ in range(6):
        response = await client.post(
            "/api/v1/public/leads",
            json={**_LEAD, "website": "filled"},
            headers=headers,
        )
        codes.append(response.status_code)
    assert codes[:5] == [201, 201, 201, 201, 201]
    assert codes[5] == 429


async def test_upload_and_notification_email(client: AsyncClient) -> None:
    uploaded = await client.post(
        "/api/v1/public/leads/uploads",
        files={"file": ("toma.wav", _wav_5s(), "audio/wav")},
    )
    assert uploaded.status_code == 200
    token = uploaded.json()["upload_token"]
    created = await client.post(
        "/api/v1/public/leads",
        json={**_LEAD, "demo_upload_token": token, "email": "ana.demo@mail.com"},
        headers={"X-Forwarded-For": "203.0.113.14"},
    )
    assert created.status_code == 201
    async with SessionMaker() as session:
        lead = await session.scalar(select(Lead).where(Lead.email == "ana.demo@mail.com"))
        queued = await session.scalar(
            select(func.count())
            .select_from(Job)
            .where(Job.type == "send_email", Job.status == "queued")
        )
    assert lead is not None
    assert lead.demo_media_id is not None
    assert lead.consent_text_version == "2026-08-04"
    assert lead.utm_source == "instagram"
    assert int(queued or 0) >= 1
    await _drain_mail("Recibimos tu mensaje — Cherry Studios")
    await _drain_mail("Nuevo contacto — Cherry Studios")


async def test_turnstile_required_when_configured(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TURNSTILE_SECRET_KEY", "secret")
    missing = await client.post(
        "/api/v1/public/leads",
        json=_LEAD,
        headers={"X-Forwarded-For": "203.0.113.15"},
    )
    assert missing.status_code == 422

    class _Response:
        status_code = 200

        def json(self) -> dict[str, bool]:
            return {"success": True}

    class _Client:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> "_Client":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, *args: object, **kwargs: object) -> _Response:
            return _Response()

    monkeypatch.setattr("app.services.leads.httpx.AsyncClient", _Client)
    accepted = await client.post(
        "/api/v1/public/leads",
        json={**_LEAD, "turnstile_token": "ok", "email": "ana.turnstile@mail.com"},
        headers={"X-Forwarded-For": "203.0.113.16"},
    )
    assert accepted.status_code == 201


async def _lead_count() -> int:
    async with SessionMaker() as session:
        count = await session.scalar(select(func.count()).select_from(Lead))
    return int(count or 0)


async def _drain_mail(subject: str) -> None:
    storage = LocalStorage(Path("/srv/media"))
    deadline = time.monotonic() + 20
    async with httpx.AsyncClient() as client:
        while time.monotonic() < deadline:
            await run_once(storage)
            response = await client.get("http://mailpit:8025/api/v1/messages")
            messages = response.json().get("messages", [])
            if any(subject == item.get("Subject") for item in messages):
                return
            await asyncio.sleep(0.2)
    raise AssertionError(subject)
