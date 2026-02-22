from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    class ConfigKeys:
        FRONTEND_HOST = "frontend.host"
        DATABASE_HOST = "database.host"
        DATABASE_PORT = "database.port"
        DATABASE_NAME = "database.name"
        DATABASE_USER = "database.user"
        DATABASE_PASSWORD = "database.password"
        CAMERA_URL = "camera.url"
        LOGGING_LEVEL = "logging.level"
        SENTRY_FRONTEND_DSN = "sentry.frontend.dsn"
        SENTRY_BACKEND_DSN = "sentry.backend.dsn"
        FEATURES_OPENAI_API_KEY = "features.openai.api_key"

    frontend_host: str = "localhost"
    database_host: str = "127.0.0.1"
    database_port: int = 3306
    database_name: str = "wims"
    database_user: str = "root"
    database_password: str = "example"
    logging_level: str = "INFO"
    sentry_frontend_dsn: str = "https://08b94672614847df87cac87c393f4a66@glitch.fleaz.me/5"
    sentry_backend_dsn: str = "https://9f6b292159894c6983b61313779ad123@glitch.fleaz.me/4"
    features_openai_api_key: str = ""


def get_settings() -> Settings:
    """
    Reads the configuration settings from environment variables and returns a Settings object.
    :return: Settings object containing the configuration settings.
    """
    return Settings()
