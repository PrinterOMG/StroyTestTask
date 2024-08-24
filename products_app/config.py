from dataclasses import dataclass
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        frozen=True,
        extra='ignore',
    )


class CommonConfig(BaseAppConfig):
    pass


class PostgresConfig(BaseAppConfig):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = 'postgres'
    POSTGRES_PORT: int = 5432

    @computed_field  # type: ignore[misc]
    @property
    def database_uri(self) -> str:
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )


@dataclass(slots=True)
class AppConfig:
    postgres: PostgresConfig
    common: CommonConfig


@lru_cache
def get_app_config(env_file: str | None = None) -> AppConfig:
    return AppConfig(
        postgres=PostgresConfig(_env_file=env_file),
        common=CommonConfig(_env_file=env_file),
    )
