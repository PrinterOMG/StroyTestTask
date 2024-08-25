from uuid import uuid4

import pytest
from dishka import AsyncContainer
from httpx import AsyncClient

from products_app.application.interfaces.category import CategoryGatewayProtocol
from products_app.domain.entitites.category import (
    CategoryEntity,
)


def category_to_json_dict(category: CategoryEntity) -> dict:
    return {
        'id': category.id,
        'name': category.name,
        'created_at': category.created_at.isoformat(),
        'parent_category_id': category.parent_category_id,
    }


async def test_get_category_by_id_success(
    ac: AsyncClient,
    prepared_category: CategoryEntity,
):
    response = await ac.get(f'/categories/{prepared_category.id}')

    assert response.status_code == 200, f'Wrong status code: {response.status_code}'

    assert response.json() == category_to_json_dict(prepared_category)


async def test_get_category_by_id_not_found(ac: AsyncClient):
    response = await ac.get(f'/categories/{uuid4()}')

    assert response.status_code == 404, f'Wrong status code: {response.status_code}'


async def test_get_all_categories_success(
    ac: AsyncClient,
    prepared_categories: list[CategoryEntity],
):
    response = await ac.get('/categories/')

    assert response.status_code == 200, f'Wrong status code: {response.status_code}'

    assert response.json() == [
        category_to_json_dict(category) for category in prepared_categories
    ]


@pytest.mark.parametrize(
    ('offset',),
    (
        ('abc',),
        (-10,),
        (10.5,),
    ),
)
async def test_get_all_categories_bad_offset(ac: AsyncClient, offset: int):
    response = await ac.get(f'/categories/?offset={offset}')

    assert response.status_code == 422


@pytest.mark.parametrize(
    ('limit',),
    (
        ('abc',),
        (-10,),
        (0,),
        (10.5,),
        (201,),
    ),
)
async def test_get_all_categories_bad_limit(ac: AsyncClient, limit: int):
    response = await ac.get(f'/categories/?limit={limit}')

    assert response.status_code == 422


async def test_get_root_categories_depth_0(
    ac: AsyncClient,
    nested_categories: tuple[CategoryEntity, CategoryEntity],
):
    response = await ac.get('/categories/root?depth=0')

    assert response.status_code == 200, f'Wrong status code: {response.status_code}'

    root_category, sub_category = nested_categories
    assert response.json() == [
        {
            'id': root_category.id,
            'name': root_category.name,
            'created_at': root_category.created_at.isoformat(),
            'parent_category_id': root_category.parent_category_id,
            'sub_categories': None,
        },
    ]


async def test_get_root_categories_depth_1(
    ac: AsyncClient,
    nested_categories: tuple[CategoryEntity, CategoryEntity],
):
    response = await ac.get('/categories/root?depth=2')

    assert response.status_code == 200, f'Wrong status code: {response.status_code}'

    root_category, sub_category = nested_categories
    assert response.json() == [
        {
            'id': root_category.id,
            'name': root_category.name,
            'created_at': root_category.created_at.isoformat(),
            'parent_category_id': root_category.parent_category_id,
            'sub_categories': [
                {
                    'id': sub_category.id,
                    'name': sub_category.name,
                    'created_at': sub_category.created_at.isoformat(),
                    'parent_category_id': sub_category.parent_category_id,
                    'sub_categories': [],
                },
            ],
        },
    ]


@pytest.mark.parametrize(
    ('depth',),
    (
        ('abc',),
        (-10,),
        (10.5,),
    ),
)
async def test_get_root_categories_bad_depth(ac: AsyncClient, depth):
    response = await ac.get(f'/categories/root?depth={depth}')

    assert response.status_code == 422


async def test_create_category_success(ac: AsyncClient, container: AsyncContainer):
    response = await ac.post(
        '/categories/',
        json={
            'name': 'Test category',
            'parent_category_id': None,
        },
    )

    assert response.status_code == 201, f'Wrong status code: {response.status_code}'

    category_json = response.json()

    async with container() as nested_container:
        category_gateway: CategoryGatewayProtocol = await nested_container.get(
            CategoryGatewayProtocol,
        )

        db_category = await category_gateway.get_by_id(category_json['id'])

        assert db_category, 'Category not found in DB'
        assert category_json == {'id': db_category.id}


async def test_create_category_bad_parent_id(ac: AsyncClient):
    response = await ac.post(
        '/categories/',
        json={
            'name': 'Test category',
            'parent_category_id': str(uuid4()),
        },
    )

    assert response.status_code == 404, f'Wrong status code: {response.status_code}'


async def test_update_category_success(
    ac: AsyncClient,
    container: AsyncContainer,
    prepared_category: CategoryEntity,
):
    response = await ac.put(
        f'/categories/{prepared_category.id}',
        json={
            'name': 'Test category update',
            'parent_category_id': None,
        },
    )

    assert response.status_code == 204, f'Wrong status code: {response.status_code}'

    async with container() as nested_container:
        category_gateway: CategoryGatewayProtocol = await nested_container.get(
            CategoryGatewayProtocol,
        )

        db_category = await category_gateway.get_by_id(prepared_category.id)

        assert db_category, 'Category not found in DB'
        assert db_category.name == 'Test category update'
        assert db_category.parent_category_id is None


async def test_update_bad_category_id(ac: AsyncClient):
    response = await ac.put(
        f'/categories/{uuid4()}',
        json={
            'name': 'Test category update',
            'parent_category_id': None,
        },
    )

    assert response.status_code == 404, f'Wrong status code: {response.status_code}'


async def test_update_category_bad_parent_id(
    ac: AsyncClient,
    prepared_category: CategoryEntity,
):
    response = await ac.put(
        f'/categories/{prepared_category.id}',
        json={
            'name': 'Test category update',
            'parent_category_id': str(uuid4()),
        },
    )

    assert response.status_code == 404, f'Wrong status code: {response.status_code}'


async def test_delete_category_success(
    ac: AsyncClient,
    container: AsyncContainer,
    prepared_category: CategoryEntity,
):
    response = await ac.delete(f'/categories/{prepared_category.id}')

    assert response.status_code == 204, f'Wrong status code: {response.status_code}'

    async with container() as nested_container:
        category_gateway: CategoryGatewayProtocol = await nested_container.get(
            CategoryGatewayProtocol,
        )

        db_category = await category_gateway.get_by_id(prepared_category.id)

        assert db_category is None


async def test_delete_bad_category_id(ac: AsyncClient):
    response = await ac.delete(f'/categories/{uuid4()}')

    assert response.status_code == 204, f'Wrong status code: {response.status_code}'


async def test_delete_parent_category(
    ac: AsyncClient,
    container: AsyncContainer,
    nested_categories: tuple[CategoryEntity, CategoryEntity],
):
    parent_category, sub_category = nested_categories

    response = await ac.delete(f'/categories/{parent_category.id}')

    assert response.status_code == 204, f'Wrong status code: {response.status_code}'

    async with container() as nested_container:
        category_gateway: CategoryGatewayProtocol = await nested_container.get(
            CategoryGatewayProtocol,
        )

        db_parent_category = await category_gateway.get_by_id(parent_category.id)
        db_sub_category = await category_gateway.get_by_id(sub_category.id)

        assert db_parent_category is None, 'Parent category not deleted'
        assert db_sub_category, 'Sub category deleted'
        assert (
            db_sub_category.parent_category_id is None
        ), 'Sub category parent id is not None'
