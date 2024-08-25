import datetime as dt
from typing import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from uuid import uuid4

from dishka import AnyOf, Provider, Scope, from_context, provide

from products_app.application.interfaces.common import (
    DateTimeNowGenerator,
    UUIDGenerator,
)
from products_app.application.interfaces.unit_of_work import UnitOfWork
from products_app.config import AppConfig
from products_app.infra.database.database import new_engine, new_session_maker
from products_app.ioc.gateways import GatewaysProvider
from products_app.ioc.interactors import InteractorsProvider


class AppProvider(Provider):
    app_config = from_context(provides=AppConfig, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_uuid_generator(self) -> UUIDGenerator:
        return lambda: str(uuid4())

    @provide(scope=Scope.APP)
    def get_datetime_now_generator(self) -> DateTimeNowGenerator:
        return dt.datetime.utcnow

    @provide(scope=Scope.APP)
    def get_async_engine(self, config: AppConfig) -> AsyncEngine:
        return new_engine(database_uri=config.postgres.database_uri)

    @provide(scope=Scope.APP)
    def get_async_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(engine=engine)

    @provide(scope=Scope.REQUEST)
    async def get_async_session(
        self,
        async_session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AnyOf[AsyncSession, UnitOfWork]]:
        async with async_session_maker() as session:
            yield session


providers = (
    AppProvider(),
    GatewaysProvider(),
    InteractorsProvider(),
)
