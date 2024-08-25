from datetime import datetime
from uuid import uuid4

import pytest
from dishka import AsyncContainer

from products_app.application.interfaces.category import CategoryGatewayProtocol
from products_app.application.interfaces.unit_of_work import UnitOfWork
from products_app.domain.entitites.category import (
    CategoryEntity,
)


@pytest.fixture(scope='function')
async def prepared_category(
    container: AsyncContainer,
) -> CategoryEntity:
    async with container() as nested_container:
        category_gateway = await nested_container.get(CategoryGatewayProtocol)
        uow = await nested_container.get(UnitOfWork)

        category = CategoryEntity(
            id=str(uuid4()),
            name='test category',
            created_at=datetime.utcnow(),
            parent_category_id=None,
        )
        await category_gateway.save(category)
        await uow.commit()

        yield category

        await category_gateway.delete(category.id)
        await uow.commit()


@pytest.fixture(scope='function')
async def prepared_categories(
    container: AsyncContainer,
) -> list[CategoryEntity]:
    async with container() as nested_container:
        category_gateway = await nested_container.get(CategoryGatewayProtocol)
        uow = await nested_container.get(UnitOfWork)

        categories = [
            CategoryEntity(
                id=str(uuid4()),
                name=f'test category {i}',
                created_at=datetime.utcnow(),
                parent_category_id=None,
            )
            for i in range(10)
        ]
        for category in categories:
            await category_gateway.save(category)
        await uow.commit()

        yield categories

        for category in categories:
            await category_gateway.delete(category.id)
        await uow.commit()


@pytest.fixture(scope='function')
async def nested_categories(
    container: AsyncContainer,
) -> tuple[CategoryEntity, CategoryEntity]:
    async with container() as nested_container:
        category_gateway = await nested_container.get(CategoryGatewayProtocol)
        uow = await nested_container.get(UnitOfWork)

        root_category = CategoryEntity(
            name='root category',
            id=str(uuid4()),
            created_at=datetime.utcnow(),
            parent_category_id=None,
        )
        sub_category = CategoryEntity(
            name='sub category',
            id=str(uuid4()),
            created_at=datetime.utcnow(),
            parent_category_id=root_category.id,
        )
        await category_gateway.save(root_category)
        await category_gateway.save(sub_category)
        await uow.commit()

        yield root_category, sub_category

        await category_gateway.delete(root_category.id)
        await category_gateway.delete(sub_category.id)
        await uow.commit()
