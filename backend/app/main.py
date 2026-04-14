"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.config.settings import settings
from app.db import init_db
from app.routes import auth, properties, incidents, ai, ci, health, test, users

# Initialize database
init_db()

# Create FastAPI app with Swagger JWT support
app = FastAPI(
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
