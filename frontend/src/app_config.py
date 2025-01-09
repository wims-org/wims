import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    BACKEND_URI = os.environ.get("BACKEND_URL") or "http://localhost:8000"


class DevelopmentConfig(Config):
    BACKEND_URI = os.environ.get("BACKEND_URL") or "http://localhost:5005"
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
