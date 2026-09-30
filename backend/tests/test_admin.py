import os
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.core.config import get_settings
from app.core.db import SessionMaker
from app.core.security import hash_password, hash_token
from app.models.auth import PasswordResetToken
from app.models.content import Service
from app.models.leads import Lead
from app.models.users import User
from app.seed.run import run_seed
from httpx import AsyncClient
from sqlalchemy import delete, select


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


def _csrf(client: AsyncClient) -> dict[str, str]:
    token = client.cookies.get("csrf_token")
    assert token
    return {"X-CSRF-Token": token}


async def _login(client: AsyncClient, email: str | None = None, password: str | None = None):
    settings = get_settings()
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email or settings.seed_admin_email,
            "password": password or settings.seed_admin_password,
        },
    )
    return response


async def test_login_me_and_csrf(client: AsyncClient) -> None:
    denied = await client.get("/api/v1/auth/me")
    assert denied.status_code == 401
    logged = await _login(client)
    assert logged.status_code == 200
    assert logged.json()["role"] == "superadmin"
    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 200
    blocked = await client.post(
        "/api/v1/admin/services",
        json={
            "slug": "no-csrf",
            "title": "No",
            "short_description": "x",
            "long_description": "x",
            "icon": "mezcla",
        },
    )
    assert blocked.status_code == 403


async def test_service_crud_preview_and_reorder(client: AsyncClient) -> None:
    await _login(client)
    headers = _csrf(client)
    slug = f"prueba-{uuid.uuid4().hex[:8]}"
    created = await client.post(
        "/api/v1/admin/services",
        headers=headers,
        json={
            "slug": slug,
            "title": "Prueba",
            "short_description": "Un servicio de prueba.",
            "long_description": "Detalle",
            "icon": "mezcla",
            "is_published": False,
        },
    )
    assert created.status_code == 201
    item_id = created.json()["id"]
    hidden = await client.get(f"/api/v1/public/services/{slug}")
    assert hidden.status_code == 404
    token = await client.post("/api/v1/admin/preview-token", headers=headers)
    assert token.status_code == 200
    preview = token.json()["token"]
    visible = await client.get(f"/api/v1/public/services/{slug}", params={"preview": preview})
    assert visible.status_code == 200
    listed = await client.get("/api/v1/admin/services", params={"q": slug})
    ids = [row["id"] for row in listed.json()["items"]]
    assert item_id in ids
    moved = await client.post(
        "/api/v1/admin/services/reorder",
        headers=headers,
        json={"ids": list(reversed(ids))},
    )
    assert moved.status_code == 204
    removed = await client.delete(f"/api/v1/admin/services/{item_id}", headers=headers)
    assert removed.status_code == 204
    async with SessionMaker() as session:
        await session.execute(delete(Service).where(Service.slug == slug))
        await session.commit()


async def test_lock_and_password_reset(client: AsyncClient) -> None:
    await _login(client)
    headers = _csrf(client)
    email = f"lock-{uuid.uuid4().hex[:8]}@cherrystudios.test"
    created = await client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": email,
            "full_name": "Prueba",
            "password": "clave-correcta",
            "role": "admin",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]
    for _ in range(5):
        failed = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "clave-incorrecta"},
        )
        assert failed.status_code == 401
    locked = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "clave-correcta"},
    )
    assert locked.status_code == 401
    assert "más tarde" in locked.json()["error"]["message"]
    forgot = await client.post("/api/v1/auth/password/forgot", json={"email": email})
    assert forgot.status_code == 204
    async with SessionMaker() as session:
        row = await session.scalar(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == uuid.UUID(user_id))
            .order_by(PasswordResetToken.created_at.desc())
        )
        assert row is not None
        token_hash = row.token_hash
    reset_token = f"token-de-prueba-{uuid.uuid4().hex}"
    missing = await client.post(
        "/api/v1/auth/password/reset",
        json={"token": "no-existe-token", "new_password": "clave-nueva-1"},
    )
    assert missing.status_code == 401
    async with SessionMaker() as session:
        user = await session.get(User, uuid.UUID(user_id))
        assert user is not None
        user.locked_until = None
        user.password_hash = hash_password("clave-temporal")
        await session.execute(
            delete(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        )
        fresh = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(reset_token),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        session.add(fresh)
        await session.commit()
    reset = await client.post(
        "/api/v1/auth/password/reset",
        json={"token": reset_token, "new_password": "clave-nueva-1"},
    )
    assert reset.status_code == 204
    again = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "clave-nueva-1"},
    )
    assert again.status_code == 200
    await _login(client)
    headers = _csrf(client)
    removed = await client.patch(
        f"/api/v1/admin/users/{user_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert removed.status_code == 200


async def test_lead_inbox(client: AsyncClient) -> None:
    await _login(client)
    headers = _csrf(client)
    lead_id = uuid.uuid4()
    async with SessionMaker() as session:
        session.add(
            Lead(
                id=lead_id,
                name="Ana Prueba",
                email="ana-prueba@example.com",
                message="Quiero mezclar un EP",
                consent_at=datetime.now(UTC),
                consent_text_version="2026-08-04",
                source_page="/",
                utm_source="instagram",
                ip_hash="test",
            )
        )
        await session.commit()
    listed = await client.get(
        "/api/v1/admin/leads",
        params={"q": "Ana Prueba", "utm_source": "instagram"},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1
    changed = await client.patch(
        f"/api/v1/admin/leads/{lead_id}",
        headers=headers,
        json={"status": "contacted"},
    )
    assert changed.status_code == 200
    assert changed.json()["events"][0]["to_status"] == "contacted"
    noted = await client.post(
        f"/api/v1/admin/leads/{lead_id}/notes",
        headers=headers,
        json={"note": "Llamar mañana"},
    )
    assert noted.status_code == 200
    blocked = await client.delete(f"/api/v1/admin/leads/{lead_id}", headers=headers)
    assert blocked.status_code == 400
    gone = await client.delete(
        f"/api/v1/admin/leads/{lead_id}",
        headers=headers,
        params={"confirm": "true"},
    )
    assert gone.status_code == 204
