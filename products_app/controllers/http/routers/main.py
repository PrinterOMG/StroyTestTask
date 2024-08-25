from fastapi import APIRouter

from products_app.controllers.http.routers import category, product
from products_app.openapi import OpenAPITags


router = APIRouter()

router.include_router(
    category.router,
    prefix='/categories',
    tags=[OpenAPITags.categories],
)

router.include_router(
    product.router,
    prefix='/products',
    tags=[OpenAPITags.products],
)
