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
    
    # M-Pesa Configuration (Sandbox)
    MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")  # sandbox or production
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "UnDvUCktXcQDyRScx0uAnJlA7rboMWhSnAxvhSOYQiX8QU0t")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "eP7nwvhM3OwL0nVhRlOCsGnRawPi32BkENmT33NygDpdYdq5sy1WyAshdCnidCkb")
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://mydomain.com/mpesa/callback")
    
    # Session security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
    
    # Flask-Login settings
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 2592000  # 30 days
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
