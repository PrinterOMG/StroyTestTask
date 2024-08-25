from typing import Any

from products_app.application.dto.product import NewProductDTO, UpdateProductDTO
from products_app.application.interfaces.category import CategoryReader
from products_app.application.interfaces.common import (
    DateTimeNowGenerator,
    UUIDGenerator,
)
from products_app.application.interfaces.product import (
    ProductDeleter,
    ProductGatewayProtocol,
    ProductReader,
    ProductSaver,
)
from products_app.application.interfaces.unit_of_work import UnitOfWork
from products_app.domain.entitites.product import ProductEntity
from products_app.domain.exceptions.category import CategoryNotFoundError
from products_app.domain.exceptions.product import ProductNotFoundError


class GetAllProductsInteractor:
    def __init__(
        self,
        product_gateway: ProductReader,
    ):
        self._product_gateway = product_gateway

    async def __call__(
        self,
        limit: int,
        offset: int,
        filters: dict[str, Any] | None,
    ) -> list[ProductEntity]:
        return await self._product_gateway.get_all(
            limit=limit,
            offset=offset,
            filters=filters,
        )


class GetProductByIdInteractor:
    def __init__(
        self,
        product_gateway: ProductReader,
    ):
        self._product_gateway = product_gateway

    async def __call__(self, product_id: str) -> ProductEntity:
        product = await self._product_gateway.get_by_id(
            product_id=product_id,
        )
        if product is None:
            raise ProductNotFoundError(identifier=product_id)

        return product


class CreateProductInteractor:
    def __init__(
        self,
        product_gateway: ProductSaver,
        category_gateway: CategoryReader,
        uow: UnitOfWork,
        uuid_generator: UUIDGenerator,
        datetime_now_generator: DateTimeNowGenerator,
    ):
        self._product_gateway = product_gateway
        self._category_gateway = category_gateway
        self._uow = uow
        self._uuid_generator = uuid_generator
        self._datetime_now_generator = datetime_now_generator

    async def __call__(self, product: NewProductDTO) -> str:
        if await self._category_gateway.get_by_id(product.category_id) is None:
            raise CategoryNotFoundError(identifier=product.category_id)

        new_product = ProductEntity(
            id=self._uuid_generator(),
            created_at=self._datetime_now_generator(),
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            unit=product.unit,
            unit_size=product.unit_size,
            category_id=product.category_id,
            attributes=product.attributes,
        )

        await self._product_gateway.save(product=new_product)
        await self._uow.commit()

        return new_product.id


class UpdateProductInteractor:
    def __init__(
        self,
        product_gateway: ProductGatewayProtocol,
        category_gateway: CategoryReader,
        uow: UnitOfWork,
    ):
        self._product_gateway = product_gateway
        self._category_gateway = category_gateway
        self._uow = uow

    async def __call__(self, product_update: UpdateProductDTO) -> None:
        if await self._category_gateway.get_by_id(product_update.category_id) is None:
            raise CategoryNotFoundError(identifier=product_update.category_id)

        product = await self._product_gateway.get_by_id(product_update.id)
        if product is None:
            raise ProductNotFoundError(identifier=product_update.id)

        product.name = product_update.name
        product.description = product_update.description
        product.price = product_update.price
        product.stock = product_update.stock
        product.unit = product_update.unit
        product.unit_size = product_update.unit_size
        product.category_id = product_update.category_id
        product.attributes = product_update.attributes

        await self._product_gateway.update(product=product)
        await self._uow.commit()


class DeleteProductInteractor:
    def __init__(
        self,
        product_gateway: ProductDeleter,
        uow: UnitOfWork,
    ):
        self._product_gateway = product_gateway
        self._uow = uow

    async def __call__(self, product_id: str) -> None:
        await self._product_gateway.delete(product_id=product_id)
        await self._uow.commit()
