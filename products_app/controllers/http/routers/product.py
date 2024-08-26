from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, HTTPException, Query, status

from products_app.application.dto.product import NewProductDTO, UpdateProductDTO
from products_app.application.interactors.product import (
    CreateProductInteractor,
    DeleteProductInteractor,
    GetAllProductsInteractor,
    GetProductByIdInteractor,
    UpdateProductInteractor,
)
from products_app.controllers.schemas.common import ErrorDetail
from products_app.controllers.schemas.product import (
    ProductCreate,
    ProductCreateResponse,
    ProductRead,
    ProductUpdate,
)
from products_app.domain.exceptions.category import CategoryNotFoundError
from products_app.domain.exceptions.product import (
    ProductFilterParamError,
    ProductNotFoundError,
)


router = APIRouter(route_class=DishkaRoute)


@router.get(
    '/{product_id}',
    response_model=ProductRead,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Product not found',
            'model': ErrorDetail,
        },
    },
)
async def get_product_by_id(
    product_id: UUID,
    *,
    interactor: FromDishka[GetProductByIdInteractor],
):
    """
    Возвращает информацию о товаре по его ID.
    """
    try:
        return await interactor(product_id=str(product_id))
    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    '/search',
    response_model=list[ProductRead],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Bad filter params',
            'model': ErrorDetail,
        },
    },
)
async def get_all_products(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0, le=200)] = 200,
    filters: Annotated[dict[str, Any] | None, Body()] = None,
    *,
    interactor: FromDishka[GetAllProductsInteractor],
):
    """
    Возвращает список товаров с пагинацией.

    Также есть возможность фильтрации.
    Фильтрация происходит сначала по полям товара, затем по атрибутам из поля `attributes`.
    Фильтры передаются в теле запроса.
    Формат: `{key}__{operator}`

    Доступные операторы:
    - `eq` - равно
    - `gt` - строго больше
    - `lt` - строго меньше

    `gt` и `lt` можно использовать только с числовыми значениями.

    Пример:
    ```
    {
        "price_gt": 100,
        "price_lt": 500
    }
    ```
    Вернёт товары, у которых цена между 100 и 500.

    Товары сортируются по названию.
    """
    try:
        return await interactor(offset=offset, limit=limit, filters=filters)
    except ProductFilterParamError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bad filter params',
        ) from error


@router.post(
    '/',
    response_model=ProductCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Category not found',
            'model': ErrorDetail,
        },
    },
)
async def create_product(
    product: ProductCreate,
    *,
    interactor: FromDishka[CreateProductInteractor],
):
    """
    Создает новый товар.
    """
    try:
        product_id = await interactor(
            product=NewProductDTO(
                name=product.name,
                description=product.description,
                price=Decimal(product.price),
                category_id=str(product.category_id),
                stock=Decimal(product.stock),
                unit=product.unit,
                unit_size=Decimal(product.unit_size),
                attributes=product.attributes,
            ),
        )
    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return ProductCreateResponse(id=product_id)


@router.put(
    '/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Product or category not found. Check details',
            'model': ErrorDetail,
        },
    },
)
async def update_product(
    product_id: UUID,
    product: ProductUpdate,
    *,
    interactor: FromDishka[UpdateProductInteractor],
):
    """
    Обновляет информацию о товаре.
    """
    try:
        return await interactor(
            product_update=UpdateProductDTO(
                id=str(product_id),
                name=product.name,
                description=product.description,
                price=Decimal(product.price),
                category_id=str(product.category_id) if product.category_id else None,
                stock=Decimal(product.stock),
                unit=product.unit,
                unit_size=Decimal(product.unit_size),
                attributes=product.attributes,
            ),
        )
    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    '/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: UUID,
    *,
    interactor: FromDishka[DeleteProductInteractor],
):
    """
    Удаляет товар по его ID.

    Если товар не существует, то ничего не происходит.
    """
    await interactor(product_id=str(product_id))
