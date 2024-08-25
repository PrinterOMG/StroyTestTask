from products_app.domain.exceptions.base import EntityError


class CategoryError(EntityError): ...


class CategoryNotFoundError(CategoryError): ...
