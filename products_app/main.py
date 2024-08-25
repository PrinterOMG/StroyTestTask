from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from products_app.config import AppConfig, get_app_config
from products_app.controllers.http.routers.main import router
from products_app.ioc.main import providers


app_config = get_app_config('.env')
container = make_async_container(
    *providers,
    context={
        AppConfig: app_config,
    },
)


def create_fastapi_app(lifespan=None):
    app = FastAPI(lifespan=lifespan)

    setup_dishka(container=container, app=app)

    app.include_router(router)

    return app
