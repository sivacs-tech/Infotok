import os


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./infoscroll.db",
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    CORS_ORIGINS = _split_csv(os.getenv("CORS_ORIGINS", "*"))
    MEDIA_ROOT = os.getenv("MEDIA_ROOT", "uploads")
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")


settings = Settings()
