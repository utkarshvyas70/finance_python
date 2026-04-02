from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.database import Base, engine
from app.models import User, Transaction  # noqa: F401
from app.utils.exceptions import global_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="A clean, layered finance tracking backend built with FastAPI.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

    # Custom OpenAPI schema — fixes Swagger Authorize box to show HTTPBearer
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=settings.APP_NAME,
            version=settings.APP_VERSION,
            description="A clean, layered finance tracking backend built with FastAPI.",
            routes=app.routes,
        )
        schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        for path in schema["paths"].values():
            for method in path.values():
                method["security"] = [{"BearerAuth": []}]
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi

    _register_routers(app)
    return app


def _register_routers(app: FastAPI) -> None:
    from app.routes import health, auth, users, transactions, analytics
    app.include_router(health.router,       prefix="/api/v1",              tags=["Health"])
    app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["Auth"])
    app.include_router(users.router,        prefix="/api/v1/users",        tags=["Users"])
    app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
    app.include_router(analytics.router,    prefix="/api/v1/analytics",    tags=["Analytics"])


app = create_app()