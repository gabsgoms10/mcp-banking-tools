import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Production configuration settings for FastMCP Banking Tools Server."""

    postgres_host: str = "postgres-service.guardrails.svc.cluster.local"
    postgres_port: int = 5432
    postgres_db: str = "guardrails_db"
    postgres_user: str = "guardrails_user"
    postgres_password: str = ""

    server_host: str = "0.0.0.0"
    server_port: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
