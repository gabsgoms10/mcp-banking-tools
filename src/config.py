import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Production configuration settings for FastMCP Banking Tools Server.
    Strict Security Policy: Mandatory environment variables — Zero hardcoded fallbacks.
    """

    postgres_host: str = Field(default_factory=lambda: os.environ["POSTGRES_HOST"])
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default_factory=lambda: os.environ["POSTGRES_DB"])
    postgres_user: str = Field(default_factory=lambda: os.environ["POSTGRES_USER"])
    postgres_password: str = Field(default_factory=lambda: os.environ["POSTGRES_PASSWORD"])

    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=8001)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
