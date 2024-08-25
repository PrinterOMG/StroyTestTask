from dishka import AnyOf, Provider, Scope, provide

from products_app.application.interfaces.category import (
    CategoryDeleter,
    CategoryGatewayProtocol,
    CategoryReader,
    CategorySaver,
    CategoryUpdater,
)
from products_app.application.interfaces.product import (
    ProductDeleter,
    ProductGatewayProtocol,
    ProductReader,
    ProductSaver,
    ProductUpdater,
)
from products_app.infra.gateways.category import CategoryGateway
from products_app.infra.gateways.product import ProductGateway


class GatewaysProvider(Provider):
    scope = Scope.REQUEST

    category_gateway = provide(
        CategoryGateway,
        provides=AnyOf[
            CategoryReader,
            CategorySaver,
            CategoryDeleter,
            CategoryUpdater,
            CategoryGatewayProtocol,
        ],
    )

    product_gateway = provide(
        ProductGateway,
        provides=AnyOf[
            ProductReader,
            ProductSaver,
            ProductDeleter,
            ProductUpdater,
            ProductGatewayProtocol,
        ],
    )
