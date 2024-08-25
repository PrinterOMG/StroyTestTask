from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from products_app.config import AppConfig, get_app_config
from products_app.infra.database.models.base import BaseModel
from products_app.ioc.main import providers
from products_app.main import create_fastapi_app


pytest_plugins = ['tests.docker_services']


@pytest.fixture
async def db_engine(container) -> AsyncEngine:
    return await container.get(AsyncEngine)


@pytest.fixture
async def async_session_factory(container) -> async_sessionmaker[AsyncSession]:
    return await container.get(async_sessionmaker[AsyncSession])


@pytest.fixture(scope='session')
def config() -> AppConfig:
    return get_app_config(env_file='tests/.env.test')


@pytest.fixture
async def container(config) -> AsyncContainer:
    container = make_async_container(
        *providers,
        context={
            AppConfig: config,
        },
    )

    yield container

    await container.close()


@pytest.fixture(autouse=True)
async def prepare_database(postgres_service, db_engine):
    async with db_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield

    async with db_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture
def app(container) -> FastAPI:
    app = create_fastapi_app()
    setup_dishka(container=container, app=app)
    return app


@pytest.fixture
async def ac(app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
