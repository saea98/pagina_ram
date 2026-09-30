import os

import pytest
from app.core.config import get_settings
from app.core.db import SessionMaker
from app.models.content import BioLinkClick
from app.seed.run import run_seed
from httpx import AsyncClient
from sqlalchemy import func, select


def _ensure_seed_env() -> None:
    os.environ["SEED_ADMIN_EMAIL"] = os.environ.get("SEED_ADMIN_EMAIL") or "seed@cherrystudios.test"
    os.environ["SEED_ADMIN_PASSWORD"] = (
        os.environ.get("SEED_ADMIN_PASSWORD") or "seed-local-password"
    )
    os.environ["TEMPLATE_ROOT"] = os.environ.get("TEMPLATE_ROOT") or "/seed-source"


@pytest.fixture(scope="module", autouse=True)
async def _seeded() -> None:
    _ensure_seed_env()
    get_settings.cache_clear()
    await run_seed()


async def test_site_hides_notify_emails_and_sets_cache(client: AsyncClient) -> None:
    response = await client.get("/api/v1/public/site")
    assert response.status_code == 200
    body = response.json()
    assert "notify_emails" not in body["contact"]
    assert body["contact"]["email"] == "contacto@cherrystudios.com.mx"
    assert body["features"]["whatsapp_float"] is False
    assert response.headers["cache-control"] == "public, max-age=60, stale-while-revalidate=300"
    etag = response.headers["etag"]
    cached = await client.get("/api/v1/public/site", headers={"If-None-Match": etag})
    assert cached.status_code == 304


async def test_home_and_catalog_endpoints(client: AsyncClient) -> None:
    home = await client.get("/api/v1/public/home")
    services = await client.get("/api/v1/public/services")
    mezcla = await client.get("/api/v1/public/services/mezcla")
    missing = await client.get("/api/v1/public/services/no-existe")
    team = await client.get("/api/v1/public/team")
    chemita = await client.get("/api/v1/public/team/alejandro-vega")
    portfolio = await client.get("/api/v1/public/portfolio", params={"featured": "true"})
    filtered = await client.get("/api/v1/public/portfolio", params={"service": "mezcla"})
    neto = await client.get("/api/v1/public/portfolio/neto-tec-live-session")
    testimonials = await client.get("/api/v1/public/testimonials")
    faqs = await client.get("/api/v1/public/faqs")
    privacy = await client.get("/api/v1/public/legal/privacy")

    assert home.status_code == 200
    assert len(home.json()["services"]) == 8
    assert home.json()["ab_comparisons"] == []
    assert services.status_code == 200
    assert services.json()[0]["slug"] == "composicion"
    assert mezcla.status_code == 200
    assert "estéreo" in mezcla.json()["short_description"]
    assert missing.status_code == 404
    assert team.status_code == 200
    assert team.json()[0]["photo"]["webp"]
    assert chemita.status_code == 200
    assert chemita.json()["nickname"] == "Chemita"
    assert portfolio.status_code == 200
    assert len(portfolio.json()) == 3
    assert filtered.status_code == 200
    assert filtered.json() == []
    assert neto.status_code == 200
    detail = neto.json()
    assert detail["audio"]["lufs"] is not None
    assert detail["audio"]["peaks_url"].endswith(".peaks.json")
    assert detail["youtube_start_s"] == 137
    assert testimonials.json() == []
    assert faqs.json() == []
    assert privacy.status_code == 200
    assert privacy.json()["updated_at"] == "2026-08-04"
    assert "Cherry Studios" in privacy.json()["html"]


async def test_play_event_and_rate_limit(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created = await client.post(
        "/api/v1/public/portfolio/palenque/events",
        json={"event": "play"},
    )
    assert created.status_code == 204
    monkeypatch.setenv("PLAY_EVENTS_PER_MINUTE", "2")
    headers = {"X-Forwarded-For": "203.0.113.44"}
    first = await client.post(
        "/api/v1/public/portfolio/palenque/events",
        json={"event": "complete"},
        headers=headers,
    )
    second = await client.post(
        "/api/v1/public/portfolio/palenque/events",
        json={"event": "complete"},
        headers=headers,
    )
    third = await client.post(
        "/api/v1/public/portfolio/palenque/events",
        json={"event": "complete"},
        headers=headers,
    )
    assert first.status_code == 204
    assert second.status_code == 204
    assert third.status_code == 429


async def test_link_redirect_records_click(client: AsyncClient) -> None:
    listed = await client.get("/api/v1/public/links")
    assert listed.status_code == 200
    labels = [item["label"] for item in listed.json()]
    assert labels == ["Contacto", "Instagram", "Portafolio"]
    portfolio = next(item for item in listed.json() if item["label"] == "Portafolio")
    redirect = await client.get(
        f"/api/v1/public/links/{portfolio['id']}/go",
        follow_redirects=False,
    )
    assert redirect.status_code == 302
    assert "utm_source=instagram" in redirect.headers["location"]
    assert redirect.headers["cache-control"] == "no-store"
    async with SessionMaker() as session:
        clicks = await session.scalar(
            select(func.count())
            .select_from(BioLinkClick)
            .where(BioLinkClick.bio_link_id == portfolio["id"])
        )
    assert int(clicks or 0) >= 1


async def test_openapi_lists_public_routes(client: AsyncClient) -> None:
    response = await client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/public/site" in paths
    assert "/api/v1/public/leads" in paths
