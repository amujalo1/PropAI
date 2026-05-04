"""Pytest configuration and fixtures"""
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.db import get_db
from app.main import app

# Use a dedicated test schema on the real PostgreSQL instance.
# SQLite cannot host these models because they use postgresql.UUID.
TEST_SCHEMA = "propai_test_api"
DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://propai:propai@postgres:5432/propai",
)

# Base engine used only to create/drop the schema
_base_engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Engine that targets the test schema for all DDL and queries
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": f"-csearch_path={TEST_SCHEMA}"},
)


def pytest_configure(config):
    """Create the test schema once before the entire test session."""
    with _base_engine.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        conn.execute(text(f"CREATE SCHEMA {TEST_SCHEMA}"))
    Base.metadata.create_all(bind=engine)


def pytest_unconfigure(config):
    """Drop the test schema after the entire test session."""
    engine.dispose()
    with _base_engine.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
    _base_engine.dispose()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Provide a clean DB session; truncate all tables before each test."""
    session = TestingSessionLocal()
    try:
        for tbl in ("change_ci", "incidents", "changes", "ci_hierarchy", "properties", "users"):
            session.execute(text(f"TRUNCATE TABLE {TEST_SCHEMA}.{tbl} RESTART IDENTITY CASCADE"))
        session.commit()
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """Create a TestClient that uses the test DB session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass  # session lifecycle managed by the db fixture

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
