from dishka import Provider, Scope, provide_all

from products_app.application.interactors.category import (
    CreateCategoryInteractor,
    DeleteCategoryInteractor,
    GetAllCategoriesInteractor,
    GetRootCategoriesInteractor,
    GetCategoryByIdInteractor,
    UpdateCategoryInteractor,
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
    )
