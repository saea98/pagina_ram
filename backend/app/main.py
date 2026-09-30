from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.core.http_cache import PublicCacheMiddleware
from app.core.logging import configure_logging
from app.core.ratelimit import register_rate_limit
from app.routers.admin_api import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.leads import router as leads_router
from app.routers.public import router as public_router

configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Cherry Studios API",
        version="0.1.0",
        lifespan=lifespan,
        openapi_url="/api/v1/openapi.json",
    )
    register_exception_handlers(application)
    register_rate_limit(application)
    application.add_middleware(PublicCacheMiddleware)
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(public_router)
    application.include_router(leads_router)
    application.include_router(admin_router)
    return application


app = create_app()
