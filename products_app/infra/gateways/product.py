from decimal import Decimal
from typing import Any

from sqlalchemy import DECIMAL, Select, delete, insert, inspect, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from products_app.application.interfaces.product import ProductGatewayProtocol
from products_app.domain.entitites.product import ProductEntity
from products_app.domain.exceptions.product import ProductFilterParamError
from products_app.infra.database.models import ProductModel


class ProductGateway(ProductGatewayProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def to_entity(product: ProductModel | None) -> ProductEntity | None:
        if product is None:
            return None

        return ProductEntity(
            id=str(product.id),
            created_at=product.created_at,
            name=product.name,
            description=product.description,
            price=Decimal(product.price),
            stock=Decimal(product.stock),
            unit=product.unit,
            unit_size=Decimal(product.unit_size),
            category_id=str(product.category_id),
            attributes=product.attributes,
        )

    @staticmethod
    def _has_column(model, column_name: str) -> bool:
        """Проверяет, существует ли столбец с заданным именем в модели SQLAlchemy"""
        mapper = inspect(model)
        return column_name in mapper.columns

    @staticmethod
    def _apply_filters(stmt: Select, filters: dict[str, Any]) -> Select:
        for key, value in filters.items():
            try:
                path, operator = key.split('__', 1)

                if ProductGateway._has_column(ProductModel, path):
                    left = getattr(ProductModel, path)
                else:
                    left = ProductModel.attributes[path].astext
                    if operator in ('gt', 'lt'):
                        left = left.cast(DECIMAL)

                if operator == 'eq':
                    stmt = stmt.where(left == str(value))
                elif operator == 'gt':
                    stmt = stmt.where(left > float(value))
                elif operator == 'lt':
                    stmt = stmt.where(left < float(value))
                else:
                    raise ProductFilterParamError(f'Invalid operator: {operator}')
            except ValueError as error:
                raise ProductFilterParamError(
                    f"Bad filter param: '{key}' or value: '{value}'",
                ) from error

        return stmt

    async def get_all(
        self,
        limit: int,
        offset: int,
        filters: dict[str, Any] | None,
    ) -> list[ProductEntity]:
        stmt = select(ProductModel)
        if filters is not None:
            stmt = self._apply_filters(stmt, filters)
        stmt = stmt.limit(limit).offset(offset).order_by(ProductModel.name)

        try:
            products = await self._session.scalars(stmt)
        except DBAPIError as error:
            if 'InvalidParameterValueError' in str(error):
                raise ProductFilterParamError from error

            raise

        return [self.to_entity(product) for product in products]

    async def get_by_id(self, product_id: str) -> ProductEntity | None:
        product = await self._session.get(ProductModel, product_id)
        return self.to_entity(product)

    async def save(self, product: ProductEntity) -> None:
        stmt = insert(ProductModel).values(
            id=product.id,
            created_at=product.created_at,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            unit=product.unit,
            unit_size=product.unit_size,
            category_id=product.category_id,
            attributes=product.attributes,
        )

        await self._session.execute(stmt)

    async def update(self, product: ProductEntity) -> None:
        stmt = (
            update(ProductModel)
            .where(ProductModel.id == product.id)
            .values(
                name=product.name,
                description=product.description,
                price=product.price,
                stock=product.stock,
                unit=product.unit,
                unit_size=product.unit_size,
                category_id=product.category_id,
                attributes=product.attributes,
            )
        )

        await self._session.execute(stmt)

    async def delete(self, product_id: str) -> None:
        await self._session.execute(
            delete(ProductModel).where(ProductModel.id == product_id),
        )
