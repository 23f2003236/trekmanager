"""
Application configuration module.

Defines base configuration and environment-specific overrides.
Values are read from environment variables where appropriate so the app
can be deployed to production without code changes.
"""
import os

# Absolute path of the project root directory.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by every environment."""

    # Secret key used to sign sessions and CSRF tokens.
    SECRET_KEY = os.environ.get("SECRET_KEY", "trek-secret-key-change-in-production-2026")

    # SQLite database stored inside an ``instance`` folder next to the project.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "trekmanager.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directory where uploaded / seeded trek images are served from.
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "images")

    # Session / remember cookie hardening.
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Configuration used during local development."""

    DEBUG = True


class ProductionConfig(Config):
    """Configuration used in production deployments."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


# Convenience mapping so ``create_app`` can select a config by name.
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
