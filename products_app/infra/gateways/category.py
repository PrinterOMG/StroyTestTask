from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, MissingGreenlet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from products_app.application.interfaces.category import CategoryGatewayProtocol
from products_app.domain.entitites.category import (
    CategoryEntity,
    ExtendedCategoryEntity,
)
from products_app.domain.exceptions.category import CategoryNotFoundError
from products_app.infra.database.models import CategoryModel


class CategoryGateway(CategoryGatewayProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def to_entity(category: CategoryModel | None) -> CategoryEntity | None:
        if category is None:
            return None

        return CategoryEntity(
            id=str(category.id),
            created_at=category.created_at,
            name=category.name,
            parent_category_id=category.parent_category_id,
        )

    @staticmethod
    def to_extended_entity(
        category: CategoryModel | None,
    ) -> ExtendedCategoryEntity | None:
        if category is None:
            return None

        try:
            sub_categories = [
                CategoryGateway.to_extended_entity(sub_category)
                for sub_category in category.sub_categories
            ]
        except MissingGreenlet:
            sub_categories = None

        return ExtendedCategoryEntity(
            id=str(category.id),
            created_at=category.created_at,
            name=category.name,
            parent_category_id=category.parent_category_id,
            sub_categories=sub_categories,
        )

    async def get_by_id(self, category_id: str) -> CategoryEntity | None:
        return self.to_entity(await self._session.get(CategoryModel, category_id))

    async def get_all_root(self, depth: int) -> list[ExtendedCategoryEntity]:
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.parent_category_id.is_(None))
            .order_by(CategoryModel.name)
        )
        if depth > 0:
            depth = None if depth == 1 else depth
            stmt = stmt.options(
                selectinload(CategoryModel.sub_categories, recursion_depth=depth),
            )

        categories = await self._session.scalars(stmt)

        return [CategoryGateway.to_extended_entity(category) for category in categories]

    async def get_all(self, limit: int, offset: int) -> list[CategoryEntity]:
        stmt = (
            select(CategoryModel)
            .limit(limit)
            .offset(offset)
            .order_by(CategoryModel.name)
        )

        categories = await self._session.scalars(stmt)

        return [CategoryGateway.to_entity(category) for category in categories]

    async def save(self, category: CategoryEntity) -> None:
        stmt = insert(CategoryModel).values(
            id=category.id,
            created_at=category.created_at,
            name=category.name,
            parent_category_id=category.parent_category_id,
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError as error:
            raise CategoryNotFoundError(
                identifier=category.parent_category_id,
            ) from error

    async def update(self, category: CategoryEntity) -> None:
        stmt = (
            update(CategoryModel)
            .where(CategoryModel.id == category.id)
            .values(
                name=category.name,
                parent_category_id=category.parent_category_id,
            )
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError as error:
            raise CategoryNotFoundError(
                identifier=category.parent_category_id,
            ) from error

    async def delete(self, category_id: str) -> None:
        await self._session.execute(
            delete(CategoryModel).where(CategoryModel.id == category_id),
        )
