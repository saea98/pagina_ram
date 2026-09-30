from app.core.config import get_settings
from app.core.db import SessionMaker
from app.models.content import BioLink, PortfolioItem, Service, TeamMember
from app.models.enums import MediaStatus
from app.models.media import MediaAsset
from app.models.users import SiteSettings, User
from app.seed.run import run_seed
from sqlalchemy import func, select


async def test_seed_is_idempotent(monkeypatch) -> None:
    monkeypatch.setenv("SEED_ADMIN_EMAIL", "seed@cherrystudios.test")
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", "seed-local-password")
    monkeypatch.setenv("TEMPLATE_ROOT", "/seed-source")
    get_settings.cache_clear()

    await run_seed()
    first = await _counts()
    await run_seed()
    second = await _counts()

    assert first == second
    assert first["services"] == 8
    assert first["team"] == 2
    assert first["portfolio"] == 3
    assert first["links"] == 5
    assert first["users"] >= 1
    assert first["settings"] == 1

    async with SessionMaker() as session:
        settings = await session.get(SiteSettings, 1)
        neto = await session.scalar(
            select(PortfolioItem).where(PortfolioItem.slug == "neto-tec-live-session")
        )
        audio = await session.get(MediaAsset, neto.audio_after_media_id) if neto else None

    assert settings is not None
    data = settings.data
    features = data["features"]
    assert isinstance(features, dict)
    assert features["whatsapp_float"] is False
    assert features["testimonials"] is False
    assert features["ab_player"] is False
    legal = data["legal"]
    assert isinstance(legal, dict)
    assert legal["privacy_updated_at"] == "2026-08-04"
    assert "Cherry Studios" in str(legal["privacy_html"])
    assert neto is not None
    assert audio is not None
    assert audio.status is MediaStatus.READY
    assert audio.lufs_integrated is not None
    assert audio.peaks_key is not None


async def _counts() -> dict[str, int]:
    async with SessionMaker() as session:
        services = await session.scalar(select(func.count()).select_from(Service))
        team = await session.scalar(select(func.count()).select_from(TeamMember))
        portfolio = await session.scalar(select(func.count()).select_from(PortfolioItem))
        links = await session.scalar(select(func.count()).select_from(BioLink))
        users = await session.scalar(select(func.count()).select_from(User))
        settings = await session.scalar(select(func.count()).select_from(SiteSettings))
    return {
        "services": int(services or 0),
        "team": int(team or 0),
        "portfolio": int(portfolio or 0),
        "links": int(links or 0),
        "users": int(users or 0),
        "settings": int(settings or 0),
    }
