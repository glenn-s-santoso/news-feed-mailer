from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables or .env file."""

    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    news_api_key: str = Field(..., env="NEWS_API_KEY")

    email_from: str = Field(..., env="EMAIL_FROM")
    email_to: str = Field(..., env="EMAIL_TO")  # Comma-separated list

    gmail_service_account_file: str | None = Field(
        None, env="GMAIL_SERVICE_ACCOUNT_FILE"
    )

    brevo_api_key: str | None = Field(None, env="BREVO_API_KEY")
    brevo_email_provider: str | None = Field(None, env="BREVO_EMAIL_PROVIDER")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Load .env file if present
load_dotenv(dotenv_path=os.getenv("ENV_FILE", ".env"))


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
