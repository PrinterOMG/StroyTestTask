from dishka import Provider, Scope, provide_all

from products_app.application.interactors.category import (
    CreateCategoryInteractor,
    DeleteCategoryInteractor,
    GetAllCategoriesInteractor,
    GetRootCategoriesInteractor,
    GetCategoryByIdInteractor,
    UpdateCategoryInteractor,
)
from products_app.application.interactors.product import (
    CreateProductInteractor,
    DeleteProductInteractor,
    GetAllProductsInteractor,
    GetProductByIdInteractor,
    UpdateProductInteractor,
)


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    interactors = provide_all(
        GetRootCategoriesInteractor,
        GetCategoryByIdInteractor,
        CreateCategoryInteractor,
        GetAllCategoriesInteractor,
        UpdateCategoryInteractor,
        DeleteCategoryInteractor,
        GetAllProductsInteractor,
        GetProductByIdInteractor,
        UpdateProductInteractor,
        DeleteProductInteractor,
        CreateProductInteractor,
    )
