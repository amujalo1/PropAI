"""Test data routes for development"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, UserRole
from app.models.property import Property, PropertyStatus, PropertyType
from app.models.incident import Incident, IncidentPriority, IncidentStatus
from app.utils.password import hash_password

router = APIRouter(prefix="/test", tags=["test"])


@router.post("/seed")
async def seed_test_data(db: Session = Depends(get_db)):
    """Seed test data for development"""
    # Create test user
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
    properties = [
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
    db.add_all(properties)
    db.commit()

    # Create test incidents
    incidents = [
        Incident(
            title="Roof Leak",
            description="Water leaking from roof during rain",
            property_id=properties[0].id,
            priority=IncidentPriority.P2,
            status=IncidentStatus.OPEN,
        ),
        Incident(
            title="Broken Window",
            description="Window in office needs replacement",
            property_id=properties[1].id,
            priority=IncidentPriority.P3,
            status=IncidentStatus.OPEN,
        ),
    ]
    db.add_all(incidents)
    db.commit()

    return {
        "message": "Test data seeded successfully",
        "user": {"email": test_user.email, "password": "testpass123"},
        "properties": len(properties),
        "incidents": len(incidents),
    }


@router.delete("/clean")
async def clean_test_data(db: Session = Depends(get_db)):
    """Clean all test data"""
    db.query(Incident).delete()
    db.query(Property).delete()
    db.query(User).delete()
    db.commit()
    return {"message": "Test data cleaned"}
