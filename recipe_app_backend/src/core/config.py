"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql://appuser:apppassword@localhost:5000/myapp"

    # Auth
    JWT_SECRET: str = "change-me"  # Must be overridden in .env
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ALLOWED_HEADERS: str = "Content-Type,Authorization,X-Requested-With"
    ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,PATCH,OPTIONS"

    # App metadata
    APP_NAME: str = "Recipe Hub API"
    APP_VERSION: str = "0.1.0"


settings = Settings()
