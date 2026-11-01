from typing import Literal
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

CONFIG_DIR = Path(__file__).resolve().parent
ENV_FILE = CONFIG_DIR / ".test_env"

class Settings(BaseSettings):
    DEBUG: bool = False
    PROJECT_NAME: str = "Analytics API"
    APP_ENV: Literal["prod", "dev", "test"] = "prod"

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "test_db"
    DB_PORT: int = 5432
    DB_HOST: str | None = None

    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def _db_host(self) -> str:
        if self.DB_HOST:
            return self.DB_HOST
        return "db" if self.APP_ENV == "prod" else "127.0.0.1"

    def _url(self, driver: str) -> str:
        return (
            f"postgresql+{driver}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self._db_host}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return self._url("asyncpg")

    @computed_field
    @property
    def DATABASE_URL_PD(self) -> str:
        return self._url("psycopg2")

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        host = "redis" if self.APP_ENV == "prod" else "127.0.0.1"
        return f"redis://{host}:6379"
    
    @computed_field
    @property
    def REDIS_HOST(self) -> str:
        host = "redis" if self.APP_ENV == "prod" else "127.0.0.1"
        return host

settings = Settings()