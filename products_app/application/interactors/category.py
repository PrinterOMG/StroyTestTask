from products_app.application.dto.category import UpdateCategoryDTO, NewCategoryDTO
from products_app.application.interfaces.category import (
    CategoryGatewayProtocol,
    CategoryReader,
    CategorySaver,
)
from products_app.application.interfaces.common import (
    DateTimeNowGenerator,
    UUIDGenerator,
)
from products_app.application.interfaces.unit_of_work import UnitOfWork
from products_app.domain.entitites.category import (
    CategoryEntity,
    ExtendedCategoryEntity,
)
from products_app.domain.exceptions.category import CategoryNotFoundError


class GetRootCategoriesInteractor:
    def __init__(
        self,
        category_gateway: CategoryReader,
    ):
        self._category_gateway = category_gateway

    async def __call__(self, depth: int) -> list[ExtendedCategoryEntity]:
        return await self._category_gateway.get_all_root(depth=depth)


class GetAllCategoriesInteractor:
    def __init__(
        self,
        category_gateway: CategoryReader,
    ):
        self._category_gateway = category_gateway

    async def __call__(self, limit: int, offset: int) -> list[CategoryEntity]:
        return await self._category_gateway.get_all(limit=limit, offset=offset)


class GetCategoryByIdInteractor:
    def __init__(
        self,
        category_gateway: CategoryReader,
    ):
        self._category_gateway = category_gateway

    async def __call__(self, category_id: str) -> CategoryEntity:
        category = await self._category_gateway.get_by_id(category_id=category_id)
        if category is None:
            raise CategoryNotFoundError

        return category


class CreateCategoryInteractor:
    def __init__(
        self,
        category_gateway: CategorySaver,
        uuid_generator: UUIDGenerator,
        datetime_now_generator: DateTimeNowGenerator,
        uow: UnitOfWork,
    ):
        self._category_gateway = category_gateway
        self._uuid_generator = uuid_generator
        self._datetime_now_generator = datetime_now_generator
        self._uow = uow

    async def __call__(self, new_category: NewCategoryDTO) -> str:
        category_entity = CategoryEntity(
            id=self._uuid_generator(),
            created_at=self._datetime_now_generator(),
            name=new_category.name,
            parent_category_id=new_category.parent_category_id,
        )

        await self._category_gateway.save(category_entity)
        await self._uow.commit()

        return category_entity.id


class UpdateCategoryInteractor:
    def __init__(
        self,
        category_gateway: CategoryGatewayProtocol,
        uow: UnitOfWork,
    ):
        self._category_gateway = category_gateway
        self._uow = uow

    async def __call__(self, category_update: UpdateCategoryDTO) -> None:
        category = await self._category_gateway.get_by_id(
            category_id=category_update.id,
        )
        if category is None:
            raise CategoryNotFoundError

        category.name = category_update.name
        category.parent_category_id = category_update.parent_category_id

        await self._category_gateway.update(category)
        await self._uow.commit()


class DeleteCategoryInteractor:
    def __init__(
        self,
        category_gateway: CategoryGatewayProtocol,
        uow: UnitOfWork,
    ):
        self._category_gateway = category_gateway
        self._uow = uow

    async def __call__(self, category_id: str) -> None:
        if await self._category_gateway.get_by_id(category_id=category_id) is None:
            raise CategoryNotFoundError

        await self._category_gateway.delete(category_id=category_id)
        await self._uow.commit()
