"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.routes import auth, properties, incidents, changes, ai, ci, health, test, users


def _run_migrations():
    """Run Alembic migrations on startup instead of raw create_all."""
    try:
        from alembic.config import Config
        from alembic import command
        import os

        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            os.environ.get("DATABASE_URL", settings.database_url),
        )
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        # Log the error but don't crash the app — tables may already exist
        import logging
        logging.getLogger(__name__).warning(f"Alembic migration warning: {e}")
        # Fallback: ensure tables exist via SQLAlchemy
        from app.db import init_db
        init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run Alembic migrations before the app starts serving requests."""
    _run_migrations()
    yield


# Create FastAPI app with Swagger JWT support
app = FastAPI(
    lifespan=lifespan,
    title="PropAI",
    description="Real Estate Management Platform MVP",
    version="0.1.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(changes.router)
app.include_router(incidents.router)
app.include_router(ai.router)
app.include_router(ci.router)
app.include_router(test.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Welcome to PropAI", "version": "0.1.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.backend_host, port=settings.backend_port)
