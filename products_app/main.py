from fastapi import FastAPI


def create_fastapi_app(lifespan=None):
    app = FastAPI(lifespan=lifespan)

    return app
