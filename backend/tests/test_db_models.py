"""Database model tests — Task 2.3 (Properties 54–58).

Validates Requirements 14.1–14.5: tables exist and required fields are
persisted for User, Property, Incident, and CI models.

These tests run against a dedicated test schema on the real PostgreSQL
database (the one in docker-compose). SQLite cannot host these models
because they use the PostgreSQL UUID column type.

Run with:
  docker exec propai-backend python -m pytest tests/test_db_models.py -v
"""
import os
import uuid
import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.user import User, UserRole
from app.models.property import Property, PropertyType, PropertyStatus
from app.models.change import Change, ChangeStatus, ChangePriority, ChangeType, ChangeRisk
from app.models.incident import Incident, IncidentImpact, IncidentUrgency, IncidentCategory
from app.models.ci import CI, CIType, CIStatus


# ---------------------------------------------------------------------------
# Test database — a separate schema on the real PostgreSQL instance.
# Schema is created and dropped per test session.
# ---------------------------------------------------------------------------

TEST_SCHEMA = "propai_test"
DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://propai:propai@postgres:5432/propai",
)


@pytest.fixture(scope="module")
def engine():
    eng = create_engine(DATABASE_URL, pool_pre_ping=True)
    with eng.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        conn.execute(text(f"CREATE SCHEMA {TEST_SCHEMA}"))
        conn.execute(text(f"SET search_path TO {TEST_SCHEMA}"))

    eng_test = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"options": f"-csearch_path={TEST_SCHEMA}"},
    )
    Base.metadata.create_all(bind=eng_test)

    yield eng_test

    eng_test.dispose()
    with eng.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
    eng.dispose()


@pytest.fixture(scope="function")
def db(engine):
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        # Clean tables before each test so tests are isolated
        for tbl in ("change_ci", "incidents", "changes", "ci_hierarchy", "properties", "users"):
            session.execute(text(f"TRUNCATE TABLE {TEST_SCHEMA}.{tbl} RESTART IDENTITY CASCADE"))
        session.commit()
        yield session
    finally:
        session.rollback()
        session.close()


# ---------------------------------------------------------------------------
# Property 54 — Database tables exist (Req 14.1)
# ---------------------------------------------------------------------------

def test_property_54_database_tables_exist(engine):
    """All required ITIL/SACM tables are created on startup."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names(schema=TEST_SCHEMA))

    required = {"users", "properties", "incidents", "ci_hierarchy", "changes", "change_ci"}
    missing = required - tables
    assert not missing, f"Missing tables: {missing}"


# ---------------------------------------------------------------------------
# Property 55 — User fields stored (Req 14.2)
# ---------------------------------------------------------------------------

def test_property_55_user_fields_stored(db):
    """User row persists email, hashed password, name, role, created_at, updated_at."""
    user = User(
        email="dbtest@example.com",
        password_hash="hashed_pw_value",
        name="DB Test User",
        role=UserRole.AGENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.email == "dbtest@example.com"
    assert user.password_hash == "hashed_pw_value"
    assert user.name == "DB Test User"
    assert user.role == UserRole.AGENT
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

    # Round-trip: re-query and verify persistence
    fetched = db.query(User).filter(User.email == "dbtest@example.com").first()
    assert fetched is not None
    assert fetched.id == user.id


# ---------------------------------------------------------------------------
# Property 56 — Property fields stored (Req 14.3)
# ---------------------------------------------------------------------------

def test_property_56_property_fields_stored(db):
    """Property row persists name, type, location, status, price, description, created_at, updated_at."""
    prop = Property(
        name="Test Apartment",
        type=PropertyType.RESIDENTIAL,
        location="Sarajevo - Centar",
        status=PropertyStatus.ACTIVE,
        price=199999.99,
        description="Two-bedroom flat",
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)

    assert prop.id is not None
    assert prop.name == "Test Apartment"
    assert prop.type == PropertyType.RESIDENTIAL
    assert prop.location == "Sarajevo - Centar"
    assert prop.status == PropertyStatus.ACTIVE
    assert float(prop.price) == 199999.99
    assert prop.description == "Two-bedroom flat"
    assert isinstance(prop.created_at, datetime)
    assert isinstance(prop.updated_at, datetime)


# ---------------------------------------------------------------------------
# Property 57 — Incident fields stored (Req 14.4)
# ---------------------------------------------------------------------------

def test_property_57_incident_fields_stored(db):
    """Incident row persists title, description, property_id, priority, status, created_at, updated_at.

    Incident inherits from Change (joined-table inheritance), so title,
    description, priority, status, created_at, updated_at live on the parent
    `changes` table while incident-specific fields live on `incidents`.
    """
    prop = Property(
        name="Incident Property",
        type=PropertyType.COMMERCIAL,
        location="Mostar",
        status=PropertyStatus.ACTIVE,
        price=300000.0,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)

    incident = Incident(
        record_type="incident",
        title="Test Incident",
        description="Roof leak in unit 2A",
        property_id=prop.id,
        change_type=ChangeType.EMERGENCY,
        priority=ChangePriority.P2,
        risk=ChangeRisk.HIGH,
        status=ChangeStatus.SUBMITTED,
        impact=IncidentImpact.MODERATE,
        urgency=IncidentUrgency.HIGH,
        category=IncidentCategory.FACILITY,
        incident_number="INC-TEST-01",
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Required fields (Req 14.4)
    assert incident.id is not None
    assert incident.title == "Test Incident"
    assert incident.description == "Roof leak in unit 2A"
    assert incident.property_id == prop.id
    assert incident.priority == ChangePriority.P2
    assert incident.status == ChangeStatus.SUBMITTED
    assert isinstance(incident.created_at, datetime)
    assert isinstance(incident.updated_at, datetime)

    # Incident-specific fields persisted
    assert incident.incident_number == "INC-TEST-01"
    assert incident.impact == IncidentImpact.MODERATE
    assert incident.urgency == IncidentUrgency.HIGH
    assert incident.category == IncidentCategory.FACILITY

    # Round-trip via the parent Change query — proves joined-table inheritance
    parent = db.query(Change).filter(Change.id == incident.id).first()
    assert parent is not None
    assert parent.record_type == "incident"


# ---------------------------------------------------------------------------
# Property 58 — CI fields stored (Req 14.5)
# ---------------------------------------------------------------------------

def test_property_58_ci_fields_stored(db):
    """CI row persists ci_id, type, region, sequence, hierarchy_level, parent_id, created_at, updated_at."""
    parent = CI(
        ci_id="PROP-LOCA-SA-000099",
        name="Test Location",
        type=CIType.LOCATION,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=99,
        hierarchy_level=1,
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = CI(
        ci_id="PROP-BUIL-SA-000099",
        name="Test Building",
        type=CIType.BUILDING,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=99,
        hierarchy_level=2,
        parent_id=parent.id,
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Required fields (Req 14.5)
    assert child.ci_id == "PROP-BUIL-SA-000099"
    assert child.type == CIType.BUILDING
    assert child.region == "SA"
    assert child.sequence == 99
    assert child.hierarchy_level == 2
    assert child.parent_id == parent.id
    assert isinstance(child.created_at, datetime)
    assert isinstance(child.updated_at, datetime)

    # Parent/child relationship round-trips through the ORM
    fetched_parent = db.query(CI).filter(CI.id == parent.id).first()
    fetched_children = db.query(CI).filter(CI.parent_id == parent.id).all()
    assert fetched_parent is not None
    assert len(fetched_children) == 1
    assert fetched_children[0].ci_id == "PROP-BUIL-SA-000099"
