from abc import abstractmethod
from typing import Any, Protocol

from products_app.domain.entitites.product import ProductEntity


class ProductReader(Protocol):
    @abstractmethod
    async def get_by_id(self, product_id: str) -> ProductEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        limit: int,
        offset: int,
        filters: dict[str, Any],
    ) -> list[ProductEntity]:
        raise NotImplementedError


class ProductSaver(Protocol):
    @abstractmethod
    async def save(self, product: ProductEntity) -> None:
        raise NotImplementedError


class ProductUpdater(Protocol):
    @abstractmethod
    async def update(self, product: ProductEntity) -> None:
        raise NotImplementedError


class ProductDeleter(Protocol):
    @abstractmethod
    async def delete(self, product_id: str) -> None:
        raise NotImplementedError


class ProductGatewayProtocol(
    ProductReader,
    ProductSaver,
    ProductUpdater,
    ProductDeleter,
    Protocol,
): ...
