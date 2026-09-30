from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.routers.health import router as health_router

configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    application = FastAPI(title="Cherry Studios API", version="0.1.0", lifespan=lifespan)
    register_exception_handlers(application)
    application.include_router(health_router)
    return application


app = create_app()
