import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "BITJUDGE"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "bitjudge"
    postgres_host: str = "db"
    postgres_port: int = 5432
    database_url: str | None = None
    db_pool_size: int = 50
    db_max_overflow: int = 100
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    redis_url: str | None = "redis://redis:6379/0"
    redis_max_connections: int = 200
    judge0_url: str = "http://judge0:2358"
    judge0_api_key: str | None = None
    enable_codeforces_scheduler: bool = True

    allowed_email_domain: str = "juetguna.in"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    page_size_default: int = 20
    page_size_max: int = 100
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def is_running_on_vercel() -> bool:
    return bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
