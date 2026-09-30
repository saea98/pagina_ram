from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "production"] = "development"
    database_url: str
    secret_key: str
    ip_hash_salt: str = ""
    tz: str = "America/Mexico_City"


@lru_cache
def get_settings() -> Settings:
    # Required fields come from the environment, which mypy cannot see.
    return Settings()  # type: ignore[call-arg]
