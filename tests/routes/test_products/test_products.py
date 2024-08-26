from typing import Any
from uuid import uuid4

import pytest
from dishka import AsyncContainer
from httpx import AsyncClient

from products_app.application.interfaces.product import ProductGatewayProtocol
from products_app.application.interfaces.unit_of_work import UnitOfWork
from products_app.domain.entitites.category import CategoryEntity
from products_app.domain.entitites.product import ProductEntity


async def test_get_product_by_id(
    ac: AsyncClient,
    prepared_product: ProductEntity,
) -> None:
    response = await ac.get(f'/products/{prepared_product.id}')
    assert response.status_code == 200
    assert response.json() == {
        'id': prepared_product.id,
        'name': prepared_product.name,
        'description': prepared_product.description,
        'price': prepared_product.price,
        'stock': prepared_product.stock,
        'unit': prepared_product.unit,
        'unit_size': prepared_product.unit_size,
        'category_id': prepared_product.category_id,
        'attributes': prepared_product.attributes,
        'created_at': prepared_product.created_at.isoformat(),
    }


async def test_get_product_by_id_not_found(
    ac: AsyncClient,
) -> None:
    response = await ac.get(f'/products/{uuid4()}')
    assert response.status_code == 404


async def test_delete_product(
    ac: AsyncClient,
    prepared_product: ProductEntity,
):
    response = await ac.delete(f'/products/{prepared_product.id}')
    assert response.status_code == 204

    response = await ac.get(f'/products/{prepared_product.id}')
    assert response.status_code == 404


async def test_delete_product_not_found(
    ac: AsyncClient,
):
    response = await ac.delete(f'/products/{uuid4()}')
    assert response.status_code == 204


async def test_create_product(
    ac: AsyncClient,
    container: AsyncContainer,
    prepared_category: CategoryEntity,
):
    response = await ac.post(
        '/products/',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': prepared_category.id,
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 201

    async with container() as nested_container:
        product_gateway = await nested_container.get(ProductGatewayProtocol)
        uow = await nested_container.get(UnitOfWork)
        product = await product_gateway.get_by_id(str(response.json()['id']))
        assert product is not None

        await product_gateway.delete(product.id)
        await uow.commit()


async def test_create_product_not_found(
    ac: AsyncClient,
):
    response = await ac.post(
        '/products/',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'name',
    ['', '   ', '        aa            ', 'aa', 'a' * 101],
)
async def test_create_product_bad_name(
    ac: AsyncClient,
    name: str,
):
    response = await ac.post(
        '/products/',
        json={
            'name': name,
            'description': 'test description',
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    'description',
    ['', '   ', '        aa            ', 'a' * 9, 'a' * 1001],
    ids=['empty', 'only spaces', 'with spaces', '9 chars', '1001 chars'],
)
async def test_create_product_bad_description(
    ac: AsyncClient,
    description: str,
):
    response = await ac.post(
        '/products/',
        json={
            'name': 'test product',
            'description': description,
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    'price',
    [-1, 0, 0.001, 'abc'],
)
async def test_create_product_bad_price(
    ac: AsyncClient,
    price: float,
):
    response = await ac.post(
        '/products/',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': price,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    'stock',
    [-1, 'abc'],
)
async def test_create_product_bad_stock(
    ac: AsyncClient,
    stock: float,
):
    response = await ac.post(
        '/products/',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': 50.0,
            'stock': stock,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    'unit_size',
    [-1, 0, 0.001, 'abc'],
)
async def test_create_product_bad_unit(
    ac: AsyncClient,
    unit_size: float,
):
    response = await ac.post(
        '/products/',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': unit_size,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


async def test_update_product(
    ac: AsyncClient,
    prepared_product: ProductEntity,
    prepared_category: CategoryEntity,
):
    response = await ac.put(
        f'/products/{prepared_product.id}',
        json={
            'name': 'test product upd',
            'description': 'test description upd',
            'price': 100.0,
            'stock': 100.0,
            'unit': 'pc',
            'unit_size': 2.0,
            'category_id': prepared_category.id,
            'attributes': {'test': 20},
        },
    )
    assert response.status_code == 204

    response = await ac.get(f'/products/{prepared_product.id}')
    assert response.status_code == 200
    json_response = response.json()
    json_response.pop('created_at')
    assert json_response == {
        'id': str(prepared_product.id),
        'name': 'test product upd',
        'description': 'test description upd',
        'price': 100.0,
        'stock': 100.0,
        'unit': 'pc',
        'unit_size': 2.0,
        'category_id': prepared_category.id,
        'attributes': {'test': 20},
    }


async def test_update_bad_product(
    ac: AsyncClient,
):
    response = await ac.put(
        f'/products/{uuid4()}',
        json={
            'name': 'test name upd',
            'description': 'test description upd',
            'price': 100.0,
            'stock': 100.0,
            'unit': 'pc',
            'unit_size': 2.0,
            'category_id': None,
            'attributes': {'test': 20},
        },
    )
    assert response.status_code == 404, response.text


@pytest.mark.parametrize(
    'name',
    ['', '   ', '        aa            ', 'aa', 'a' * 101],
)
async def test_update_product_bad_name(
    ac: AsyncClient,
    prepared_product: ProductEntity,
    name: str,
):
    response = await ac.put(
        f'/products/{prepared_product.id}',
        json={
            'name': name,
            'description': 'test description',
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    'description',
    ['', '   ', '        aa            ', 'a' * 9, 'a' * 1001],
    ids=['empty', 'only spaces', 'with spaces', '9 chars', '1001 chars'],
)
async def test_update_product_bad_description(
    ac: AsyncClient,
    prepared_product: ProductEntity,
    description: str,
):
    response = await ac.put(
        f'/products/{prepared_product.id}',
        json={
            'name': 'test product',
            'description': description,
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    'price',
    [-1, 0, 0.001, 'abc'],
)
async def test_update_product_bad_price(
    ac: AsyncClient,
    prepared_product: ProductEntity,
    price: float,
):
    response = await ac.put(
        f'/products/{prepared_product.id}',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': price,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    'stock',
    [-1, 'abc'],
)
async def test_update_product_bad_stock(
    ac: AsyncClient,
    prepared_product: ProductEntity,
    stock: float,
):
    response = await ac.put(
        f'/products/{prepared_product.id}',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': 50.0,
            'stock': stock,
            'unit': 'kg',
            'unit_size': 1.0,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    'unit_size',
    [-1, 0, 0.001, 'abc'],
)
async def test_update_product_bad_unit(
    ac: AsyncClient,
    prepared_product: ProductEntity,
    unit_size: float,
):
    response = await ac.put(
        f'/products/{prepared_product.id}',
        json={
            'name': 'test product',
            'description': 'test description',
            'price': 50.0,
            'stock': 10.0,
            'unit': 'kg',
            'unit_size': unit_size,
            'category_id': str(uuid4()),
            'attributes': {'test': 10},
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    'filters',
    [
        {'name': 'test product'},
        {'name_1': 'test product'},
        {'name__gt': 'test product'},
        {'price__le': 50.0},
    ],
)
async def test_search_bad_filters(
    ac: AsyncClient,
    prepared_products: tuple[ProductEntity, ProductEntity],
    filters: dict[str, Any],
):
    response = await ac.post('/products/search', json=filters)

    assert response.status_code == 400


@pytest.mark.parametrize(
    'filters',
    [
        {'price__gt': 40, 'price__lt': '100'},
        {'price__eq': 50.0},
        {'stock__gt': 5, 'stock__lt': 50},
        {'test__eq': 10},
        {'test__lt': '20'},
        {'test__lt': 20, 'unit__eq': 'kg'},
    ],
)
async def test_search_products_success(
    ac: AsyncClient,
    prepared_products: tuple[ProductEntity, ProductEntity],
    filters: dict[str, Any],
):
    response = await ac.post('/products/search', json=filters)

    assert response.status_code == 200
    json_response = response.json()

    assert len(json_response) == 1
    assert json_response[0]['id'] == prepared_products[0].id
