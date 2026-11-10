from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.users import router as users_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
# Ensure all models are registered on Base.metadata
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that initializes database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Task Manager API",
    description=(
        "A production-ready Task Manager REST API built with FastAPI, "
        "SQLAlchemy 2.0 ORM, SQLite, Pydantic v2, and JWT authentication."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration and token issuance.",
        },
        {
            "name": "Users",
            "description": "User profile operations.",
        },
        {
            "name": "Tasks",
            "description": "Task creation, retrieval, filtering, updating, and deletion.",
        },
        {
            "name": "Health",
            "description": "Application health monitoring.",
        },
    ],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check whether the API service is alive and healthy.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {"application/json": {"example": {"status": "ok"}}},
        }
    },
)
def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {"status": "ok"}
