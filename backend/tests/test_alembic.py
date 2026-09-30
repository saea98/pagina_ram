from alembic import command
from alembic.config import Config


def test_upgrade_head() -> None:
    config = Config("alembic.ini")
    command.upgrade(config, "head")
