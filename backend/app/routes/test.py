"""Test data routes for development"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, UserRole
from app.models.property import Property, PropertyStatus, PropertyType
from app.models.incident import Incident, IncidentImpact, IncidentUrgency, IncidentCategory
from app.models.change import ChangeStatus, ChangePriority, ChangeRisk
from app.utils.password import hash_password

router = APIRouter(prefix="/test", tags=["test"])


@router.post("/seed")
async def seed_test_data(db: Session = Depends(get_db)):
    """Seed test data for development"""
    # Create test user
    existing = db.query(User).filter(User.email == "test@example.com").first()
    if existing:
        return {"message": "Test data already seeded", "user": {"email": "test@example.com", "password": "testpass123"}}

    test_user = User(
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        name="Test User",
        role=UserRole.AGENT,
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Create test properties
    props = [
        Property(
            name="Modern Apartment",
            type=PropertyType.RESIDENTIAL,
            location="Downtown",
            status=PropertyStatus.ACTIVE,
            price=250000.0,
            description="Beautiful modern apartment in the city center",
        ),
        Property(
            name="Office Space",
            type=PropertyType.COMMERCIAL,
            location="Business District",
            status=PropertyStatus.ACTIVE,
            price=500000.0,
            description="Prime office space with great views",
        ),
        Property(
            name="Land Plot",
            type=PropertyType.LAND,
            location="Suburbs",
            status=PropertyStatus.DRAFT,
            price=100000.0,
            description="Large land plot for development",
        ),
    ]
    db.add_all(props)
    db.commit()

    # Create test incidents (using new ITIL model)
    incidents = [
        Incident(
            record_type="incident",
            title="Roof Leak",
            description="Water leaking from roof during rain",
            change_type="EMERGENCY",
            property_id=props[0].id,
            priority=ChangePriority.P2,
            risk=ChangeRisk.HIGH,
            status=ChangeStatus.SUBMITTED,
            impact=IncidentImpact.MODERATE,
            urgency=IncidentUrgency.HIGH,
            category=IncidentCategory.FACILITY,
            incident_number="INC-000001",
        ),
        Incident(
            record_type="incident",
            title="Broken Window",
            description="Window in office needs replacement",
            change_type="EMERGENCY",
            property_id=props[1].id,
            priority=ChangePriority.P3,
            risk=ChangeRisk.MEDIUM,
            status=ChangeStatus.SUBMITTED,
            impact=IncidentImpact.MINOR,
            urgency=IncidentUrgency.MEDIUM,
            category=IncidentCategory.FACILITY,
            incident_number="INC-000002",
        ),
    ]
    db.add_all(incidents)
    db.commit()

    return {
        "message": "Test data seeded successfully",
        "user": {"email": test_user.email, "password": "testpass123"},
        "properties": len(props),
        "incidents": len(incidents),
    }


@router.delete("/clean")
async def clean_test_data(db: Session = Depends(get_db)):
    """Clean all test data"""
    from app.models.change import Change, ChangeCI
    db.query(ChangeCI).delete()
    db.query(Incident).delete()
    db.query(Change).delete()
    db.query(Property).delete()
    db.query(User).delete()
    db.commit()
    return {"message": "Test data cleaned"}
