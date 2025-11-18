import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_PATH = BASE_DIR / "instance" / "app.db"


class Config:
    """Base configuration shared across environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-smartprintpro-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
