import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

EXPECTED_TABLES = {
    "users",
    "site_settings",
    "media_assets",
    "services",
    "team_members",
    "portfolio_items",
    "portfolio_item_services",
    "portfolio_item_credits",
    "testimonials",
    "faqs",
    "bio_links",
    "bio_link_clicks",
    "leads",
    "lead_events",
    "play_events",
    "jobs",
}


def _config() -> Config:
    return Config("alembic.ini")


@pytest.fixture(scope="module", autouse=True)
def _migrated() -> None:
    command.upgrade(_config(), "head")


def test_upgrade_head_and_model_match() -> None:
    config = _config()
    command.upgrade(config, "head")
    command.check(config)


async def test_phase1_tables_exist(session: AsyncSession) -> None:
    result = await session.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"),
    )
    names = {row[0] for row in result}
    assert names >= EXPECTED_TABLES
