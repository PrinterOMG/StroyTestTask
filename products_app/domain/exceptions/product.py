from products_app.domain.exceptions.base import EntityError


class ProductError(EntityError): ...


class ProductNotFoundError(ProductError):
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__()

    def __str__(self):
        return f'Product<{self.identifier}> not found'


class ProductFilterParamError(ProductError): ...
