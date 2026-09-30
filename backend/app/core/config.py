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
    media_root: str = "/srv/media"
    max_upload_mb_admin: int = 200
    max_upload_mb_lead: int = 30
    template_root: str = ""
    seed_admin_email: str = ""
    seed_admin_password: str = ""
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "Cherry Studios <no-reply@cherrystudios.com.mx>"
    turnstile_secret_key: str = ""
    internal_revalidate_token: str = ""
    web_internal_url: str = "http://web:3010"
    public_site_url: str = "https://localhost"


@lru_cache
def get_settings() -> Settings:
    # Required fields come from the environment, which mypy cannot see.
    return Settings()  # type: ignore[call-arg]
