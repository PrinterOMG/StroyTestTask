from products_app.domain.exceptions.base import EntityError


class CategoryError(EntityError): ...


class CategoryNotFoundError(CategoryError):
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__()

    def __str__(self):
        return f'Category<{self.identifier}> not found'
