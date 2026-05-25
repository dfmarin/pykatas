import os
from dataclasses import dataclass


class BaseConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    KATA_DIR = os.getenv("KATA_DIR", "katas")
    SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "kata-sandbox:latest")
    SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "30"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://kata:kata@localhost/kata_dev"
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg://kata:kata@localhost/kata_test"
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
