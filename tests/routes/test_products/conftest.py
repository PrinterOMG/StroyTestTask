from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from dishka import AsyncContainer

from products_app.application.interfaces.category import CategoryGatewayProtocol
from products_app.application.interfaces.product import ProductGatewayProtocol
from products_app.application.interfaces.unit_of_work import UnitOfWork
from products_app.domain.entitites.category import CategoryEntity
from products_app.domain.entitites.product import ProductEntity


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
async def prepared_product(
    container: AsyncContainer,
) -> ProductEntity:
    async with container() as nested_container:
        product_gateway = await nested_container.get(ProductGatewayProtocol)
        uow = await nested_container.get(UnitOfWork)
        category = await nested_container.get(CategoryGatewayProtocol)

        category_entity = CategoryEntity(
            id=str(uuid4()),
            name='test category',
            created_at=datetime.utcnow(),
            parent_category_id=None,
        )

        product = ProductEntity(
            id=str(uuid4()),
            name='test product',
            description='test description',
            price=Decimal(50.0),
            stock=Decimal(10.0),
            unit='kg',
            unit_size=Decimal(1.0),
            category_id=category_entity.id,
            created_at=datetime.utcnow(),
            attributes={'test': 10},
        )

        await category.save(category_entity)
        await product_gateway.save(product)
        await uow.commit()

        yield product

        await product_gateway.delete(product.id)
        await category.delete(category_entity.id)
        await uow.commit()


@pytest.fixture(scope='function')
async def prepared_products(
    container: AsyncContainer,
) -> tuple[ProductEntity, ProductEntity]:
    async with container() as nested_container:
        product_gateway = await nested_container.get(ProductGatewayProtocol)
        uow = await nested_container.get(UnitOfWork)
        category = await nested_container.get(CategoryGatewayProtocol)

        category_entity = CategoryEntity(
            id=str(uuid4()),
            name='test category',
            created_at=datetime.utcnow(),
            parent_category_id=None,
        )

        product_1 = ProductEntity(
            id=str(uuid4()),
            name='test product',
            description='test description',
            price=Decimal(50.0),
            stock=Decimal(10.0),
            unit='kg',
            unit_size=Decimal(1.0),
            category_id=category_entity.id,
            created_at=datetime.utcnow(),
            attributes={'test': 10},
        )

        product_2 = ProductEntity(
            id=str(uuid4()),
            name='test product 2',
            description='test description 2',
            price=Decimal(100.0),
            stock=Decimal(0.0),
            unit='pc',
            unit_size=Decimal(1.0),
            category_id=category_entity.id,
            created_at=datetime.utcnow(),
            attributes={'test': 20},
        )

        await category.save(category_entity)
        await product_gateway.save(product_1)
        await product_gateway.save(product_2)
        await uow.commit()

        yield product_1, product_2

        await product_gateway.delete(product_1.id)
        await product_gateway.delete(product_2.id)
        await category.delete(category_entity.id)
        await uow.commit()
