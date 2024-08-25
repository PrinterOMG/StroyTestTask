from abc import abstractmethod
from typing import Protocol

from products_app.domain.entitites.category import (
    CategoryEntity,
    ExtendedCategoryEntity,
)


class CategoryReader(Protocol):
    @abstractmethod
    async def get_by_id(self, category_id: str) -> CategoryEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all_root(self, depth: int) -> list[ExtendedCategoryEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> list[CategoryEntity]:
        raise NotImplementedError


class CategorySaver(Protocol):
    @abstractmethod
    async def save(self, category: CategoryEntity) -> None:
        raise NotImplementedError


class CategoryUpdater(Protocol):
    @abstractmethod
    async def update(self, category: CategoryEntity) -> None:
        raise NotImplementedError


class CategoryDeleter(Protocol):
    @abstractmethod
    async def delete(self, category_id: str) -> None:
        raise NotImplementedError


class CategoryGatewayProtocol(
    CategoryReader,
    CategorySaver,
    CategoryUpdater,
    CategoryDeleter,
    Protocol,
): ...
