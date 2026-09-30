import os

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.core.db import SessionMaker
from app.core.errors import NotFound
from app.main import app


class _Probe(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str


def _mount_probes(application: FastAPI) -> None:
    @application.post("/api/_validation-probe")
    async def validation_probe(body: _Probe) -> dict[str, str]:
        return {"name": body.name}

    @application.get("/api/_missing")
    async def missing() -> None:
        raise NotFound("No encontramos ese recurso.")

    @application.get("/api/_boom")
    async def boom() -> None:
        raise RuntimeError("secret stack")


_mount_probes(app)


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http


@pytest.fixture
async def session() -> AsyncSession:
    async with SessionMaker() as db:
        transaction = await db.begin()
        yield db
        await transaction.rollback()
