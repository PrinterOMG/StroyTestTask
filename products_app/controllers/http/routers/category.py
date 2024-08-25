from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Query

from products_app.application.dto.category import NewCategoryDTO, UpdateCategoryDTO
from products_app.application.interactors.category import (
    CreateCategoryInteractor,
    DeleteCategoryInteractor,
    GetAllCategoriesInteractor,
    GetRootCategoriesInteractor,
    GetCategoryByIdInteractor,
    UpdateCategoryInteractor,
)
from products_app.controllers.schemas.category import (
    CategoryCreate,
    CategoryCreateResponse,
    CategoryRead,
    CategoryUpdate,
    ExtendedCategoryRead,
)
from products_app.controllers.schemas.common import ErrorDetail
from products_app.domain.exceptions.category import CategoryNotFoundError


router = APIRouter(route_class=DishkaRoute)


@router.get(
    '/root',
    response_model=list[ExtendedCategoryRead],
)
async def get_root_categories(
    depth: Annotated[int, Query(ge=0)] = 2,
    *,
    interactor: FromDishka[GetRootCategoriesInteractor],
):
    """
    Возвращает список корневых категорий *(у которых нет родительской категории)* с указанным уровнем вложенности.

    Сортировка по названию категории.

    Параметр `depth` определяет уровень вложенности:
    - Если `depth=0`, то возвращает только корневые категории.
    - Если `depth=1`, то вложенные категории будут получены только для корненвых категорий.
    - И так далее.

    Примечание про `sub_categories` в ответе:
    - Если `sub_categories = null`, то вложенные категории были обрезаны.
    - Если `sub_categories = []`, то вложенные категории отсутствуют.
    """
    return await interactor(depth=depth)


@router.get(
    '/',
    response_model=list[CategoryRead],
)
async def get_all_categories(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0, le=200)] = 200,
    *,
    interactor: FromDishka[GetAllCategoriesInteractor],
):
    """
    Возвращает список всех категорий с пагинацией без вложенных категорий.

    Сортировка по названию категории.
    """
    return await interactor(offset=offset, limit=limit)


@router.get(
    '/{category_id}',
    response_model=CategoryRead,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Category not found',
            'model': ErrorDetail,
        },
    },
)
async def get_by_id(
    category_id: str,
    *,
    interactor: FromDishka[GetCategoryByIdInteractor],
):
    """
    Возвращает категорию по ID без вложенных категорий.
    """
    try:
        return await interactor(category_id=category_id)
    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryCreateResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Parent category not found',
            'model': ErrorDetail,
        },
    },
)
async def create_category(
    category: CategoryCreate,
    *,
    interactor: FromDishka[CreateCategoryInteractor],
):
    """
    Создает новую категорию.
    """
    try:
        category_id = await interactor(
            new_category=NewCategoryDTO(
                name=category.name,
                parent_category_id=category.parent_category_id,
            ),
        )
    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return CategoryCreateResponse(id=category_id)


@router.put(
    '/{category_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Category not found',
            'model': ErrorDetail,
        },
    },
)
async def update_category(
    category_id: UUID,
    category: CategoryUpdate,
    *,
    interactor: FromDishka[UpdateCategoryInteractor],
):
    """
    Обновляет категорию по ID, если она существует.
    """
    try:
        await interactor(
            category_update=UpdateCategoryDTO(
                id=str(category_id),
                name=category.name,
                parent_category_id=str(category.parent_category_id)
                if category.parent_category_id
                else None,
            ),
        )
    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    '/{category_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: UUID,
    *,
    interactor: FromDishka[DeleteCategoryInteractor],
):
    """
    Удаляет категорию по ID, если она существует.

    Если категории под таким ID нет, то ничего не произойдёт.

    Если категория содержит вложенные категории, то они не будут удалены, `category_parent_id` у них станет `Null`.
    """
    await interactor(category_id=str(category_id))
