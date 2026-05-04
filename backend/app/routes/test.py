"""Test data routes for development"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, UserRole
from app.models.property import Property, PropertyStatus, PropertyType
from app.models.incident import Incident, IncidentImpact, IncidentUrgency, IncidentCategory
from app.models.change import Change, ChangeCI, ChangeType, ChangeStatus, ChangePriority, ChangeRisk
from app.models.ci import CI, CIType, CIStatus
from app.utils.password import hash_password

router = APIRouter(prefix="/test", tags=["test"])


@router.post("/seed")
async def seed_test_data(db: Session = Depends(get_db)):
    """Seed test data for development"""
    import traceback
    try:
        return await _seed(db)
    except Exception as e:
        tb = traceback.format_exc()
        return {"error": str(e), "traceback": tb}


async def _seed(db: Session):
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
    admin_user = User(
        email="admin@propai.ba",
        password_hash=hash_password("admin12345"),
        name="Configuration Manager",
        role=UserRole.ADMIN,
    )
    steward_user = User(
        email="steward@propai.ba",
        password_hash=hash_password("steward12345"),
        name="Data Steward",
        role=UserRole.DATA_STEWARD,
    )
    db.add_all([test_user, admin_user, steward_user])
    db.commit()
    db.refresh(test_user)
    db.refresh(admin_user)
    db.refresh(steward_user)

    # Create test properties
    props = [
        Property(
            name="Modern Apartment Vijećnica",
            type=PropertyType.RESIDENTIAL,
            location="Sarajevo - Stari Grad",
            status=PropertyStatus.ACTIVE,
            price=250000.0,
            description="Beautiful modern apartment in the city center, 68m², 2nd floor",
        ),
        Property(
            name="Office Space Marijin Dvor",
            type=PropertyType.COMMERCIAL,
            location="Sarajevo - Centar",
            status=PropertyStatus.ACTIVE,
            price=500000.0,
            description="Prime office space with great views, 120m²",
        ),
        Property(
            name="Land Plot Ilidža",
            type=PropertyType.LAND,
            location="Sarajevo - Ilidža",
            status=PropertyStatus.DRAFT,
            price=100000.0,
            description="Large land plot for development, 1500m²",
        ),
        Property(
            name="Family House Banja Luka",
            type=PropertyType.RESIDENTIAL,
            location="Banja Luka - Centar",
            status=PropertyStatus.ACTIVE,
            price=320000.0,
            description="Family house with garden, 180m², 3 bedrooms",
        ),
        Property(
            name="Retail Space Mostar",
            type=PropertyType.COMMERCIAL,
            location="Mostar - Stari Most",
            status=PropertyStatus.RESERVED,
            price=180000.0,
            description="Retail unit in pedestrian zone, 65m²",
        ),
    ]
    db.add_all(props)
    db.commit()
    for p in props:
        db.refresh(p)

    # ----------------------------------------------------------------------
    # SACM — seed CMDB hierarchy: Location → Complex → Building → Property → Component
    # ----------------------------------------------------------------------
    location_sa = CI(
        ci_id="PROP-LOCA-SA-000001",
        name="Sarajevo - Novo Sarajevo",
        type=CIType.LOCATION,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=1,
        hierarchy_level=1,
        description="Geografska zona — Sarajevo, Novo Sarajevo (poštanski 71000)",
        owner_id=admin_user.id,
    )
    location_bl = CI(
        ci_id="PROP-LOCA-BL-000001",
        name="Banja Luka - Centar",
        type=CIType.LOCATION,
        status=CIStatus.ACTIVE,
        region="BL",
        sequence=1,
        hierarchy_level=1,
        description="Geografska zona — Banja Luka centar",
        owner_id=admin_user.id,
    )
    location_mo = CI(
        ci_id="PROP-LOCA-MO-000001",
        name="Mostar - Stari Most",
        type=CIType.LOCATION,
        status=CIStatus.ACTIVE,
        region="MO",
        sequence=1,
        hierarchy_level=1,
        description="Geografska zona — Mostar, Stari Most",
        owner_id=admin_user.id,
    )
    db.add_all([location_sa, location_bl, location_mo])
    db.commit()
    for c in (location_sa, location_bl, location_mo):
        db.refresh(c)

    complex_sa = CI(
        ci_id="PROP-COMP-SA-000001",
        name="Stambeni kompleks 'Vijećnica'",
        type=CIType.COMPLEX,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=1,
        hierarchy_level=2,
        description="Stambeni kompleks s 3 lamele",
        parent_id=location_sa.id,
        owner_id=steward_user.id,
    )
    db.add(complex_sa)
    db.commit()
    db.refresh(complex_sa)

    building_sa = CI(
        ci_id="PROP-BUIL-SA-000001",
        name="Lamela A, ul. Obala bb",
        type=CIType.BUILDING,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=1,
        hierarchy_level=3,
        description="Stambena zgrada — 8 spratova, godište 2018, AB konstrukcija",
        parent_id=complex_sa.id,
        owner_id=steward_user.id,
    )
    building_bl = CI(
        ci_id="PROP-BUIL-BL-000001",
        name="Porodična kuća, ul. Kralja Petra",
        type=CIType.BUILDING,
        status=CIStatus.ACTIVE,
        region="BL",
        sequence=1,
        hierarchy_level=2,
        description="Porodična kuća, godište 2010, P+1, gas grijanje",
        parent_id=location_bl.id,
        owner_id=steward_user.id,
    )
    db.add_all([building_sa, building_bl])
    db.commit()
    for c in (building_sa, building_bl):
        db.refresh(c)

    # Property-level CIs (linked to Property records)
    prop_ci_apartment = CI(
        ci_id="PROP-PROP-SA-000001",
        name="Stan 3A, 68m², 2. sprat",
        type=CIType.PROPERTY,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=1,
        hierarchy_level=4,
        description="Trosoban stan, 68m², energetski razred B",
        parent_id=building_sa.id,
        property_id=props[0].id,
        owner_id=steward_user.id,
    )
    prop_ci_office = CI(
        ci_id="PROP-PROP-SA-000002",
        name="Office Space Marijin Dvor",
        type=CIType.PROPERTY,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=2,
        hierarchy_level=2,
        description="Poslovni prostor, 120m², prizemlje",
        parent_id=location_sa.id,
        property_id=props[1].id,
        owner_id=steward_user.id,
    )
    prop_ci_house = CI(
        ci_id="PROP-PROP-BL-000001",
        name="Family House Banja Luka",
        type=CIType.PROPERTY,
        status=CIStatus.ACTIVE,
        region="BL",
        sequence=1,
        hierarchy_level=3,
        description="Porodična kuća, 180m², 3 spavaće sobe",
        parent_id=building_bl.id,
        property_id=props[3].id,
        owner_id=steward_user.id,
    )
    prop_ci_retail = CI(
        ci_id="PROP-PROP-MO-000001",
        name="Retail Space Mostar",
        type=CIType.PROPERTY,
        status=CIStatus.ACTIVE,
        region="MO",
        sequence=1,
        hierarchy_level=2,
        description="Retail jedinica, 65m², pješačka zona",
        parent_id=location_mo.id,
        property_id=props[4].id,
        owner_id=steward_user.id,
    )
    db.add_all([prop_ci_apartment, prop_ci_office, prop_ci_house, prop_ci_retail])
    db.commit()
    for c in (prop_ci_apartment, prop_ci_office, prop_ci_house, prop_ci_retail):
        db.refresh(c)

    # Component-level CIs (infrastructure inside buildings/properties)
    comp_lift = CI(
        ci_id="PROP-COMP-SA-000002",
        name="Lift Lamela A",
        type=CIType.COMPONENT,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=2,
        hierarchy_level=4,
        description="Putnički lift, kapacitet 8 osoba, instaliran 2018",
        parent_id=building_sa.id,
        version="OTIS-2018",
        serial_number="OT-SA-2018-001",
        location_detail="Lamela A — centralni hodnik",
    )
    comp_heating = CI(
        ci_id="PROP-COMP-SA-000003",
        name="Centralno grijanje Lamela A",
        type=CIType.COMPONENT,
        status=CIStatus.MAINTENANCE,
        region="SA",
        sequence=3,
        hierarchy_level=4,
        description="Plinski kotao Vaillant, godište 2019",
        parent_id=building_sa.id,
        version="Vaillant-2019",
        serial_number="VL-SA-2019-A",
        location_detail="Lamela A — podrum",
    )
    comp_garage = CI(
        ci_id="PROP-COMP-SA-000004",
        name="Podzemna garaža",
        type=CIType.COMPONENT,
        status=CIStatus.ACTIVE,
        region="SA",
        sequence=4,
        hierarchy_level=3,
        description="Podzemna garaža kompleksa, 24 mjesta",
        parent_id=complex_sa.id,
        location_detail="Ispod kompleksa Vijećnica",
    )
    db.add_all([comp_lift, comp_heating, comp_garage])
    db.commit()
    for c in (comp_lift, comp_heating, comp_garage):
        db.refresh(c)

    # ----------------------------------------------------------------------
    # Change Management — sample changes
    # ----------------------------------------------------------------------
    changes = [
        Change(
            record_type="change",
            title="Replace lift control board — Lamela A",
            description="Scheduled replacement of OTIS lift control board after end-of-life notice",
            change_type=ChangeType.NORMAL,
            status=ChangeStatus.APPROVED,
            priority=ChangePriority.P3,
            risk=ChangeRisk.MEDIUM,
            justification="Vendor end-of-support for current control board",
            implementation_plan="Schedule overnight maintenance window, swap board, validate operation",
            backout_plan="Reinstall original board if validation fails",
            property_id=props[0].id,
            requested_by_id=steward_user.id,
            assigned_to_id=admin_user.id,
        ),
        Change(
            record_type="change",
            title="Update zoning classification — Ilidža plot",
            description="Update legal status after municipal rezoning decision",
            change_type=ChangeType.STANDARD,
            status=ChangeStatus.SUBMITTED,
            priority=ChangePriority.P4,
            risk=ChangeRisk.LOW,
            justification="Municipal decision changed zoning from agricultural to residential",
            property_id=props[2].id,
            requested_by_id=steward_user.id,
        ),
    ]
    db.add_all(changes)
    db.commit()
    for c in changes:
        db.refresh(c)

    # Link changes to affected CIs (SACM ↔ Change integration)
    db.add_all([
        ChangeCI(
            change_id=changes[0].id,
            ci_id=comp_lift.id,
            impact_description="Lift will be unavailable during 4-hour maintenance window",
        ),
        ChangeCI(
            change_id=changes[0].id,
            ci_id=building_sa.id,
            impact_description="Building residents informed of temporary lift outage",
        ),
    ])
    db.commit()

    # ----------------------------------------------------------------------
    # Incident Management — sample incidents
    # ----------------------------------------------------------------------
    incidents = [
        Incident(
            record_type="incident",
            title="Roof Leak — Vijećnica Lamela A",
            description="Water leaking from roof during heavy rain, affecting 3rd floor units",
            change_type=ChangeType.EMERGENCY,
            property_id=props[0].id,
            priority=ChangePriority.P2,
            risk=ChangeRisk.HIGH,
            status=ChangeStatus.IN_PROGRESS,
            requested_by_id=test_user.id,
            assigned_to_id=admin_user.id,
            impact=IncidentImpact.MODERATE,
            urgency=IncidentUrgency.HIGH,
            category=IncidentCategory.FACILITY,
            incident_number="INC-000001",
        ),
        Incident(
            record_type="incident",
            title="Broken Window — Office Marijin Dvor",
            description="Office window in unit 2B needs replacement after storm damage",
            change_type=ChangeType.EMERGENCY,
            property_id=props[1].id,
            priority=ChangePriority.P3,
            risk=ChangeRisk.MEDIUM,
            status=ChangeStatus.SUBMITTED,
            requested_by_id=test_user.id,
            impact=IncidentImpact.MINOR,
            urgency=IncidentUrgency.MEDIUM,
            category=IncidentCategory.FACILITY,
            incident_number="INC-000002",
        ),
        Incident(
            record_type="incident",
            title="AI Valuation engine returning stale prices",
            description="AVM model returning prices > 30 days old for Sarajevo region",
            change_type=ChangeType.EMERGENCY,
            priority=ChangePriority.P1,
            risk=ChangeRisk.CRITICAL,
            status=ChangeStatus.IN_PROGRESS,
            requested_by_id=admin_user.id,
            assigned_to_id=admin_user.id,
            impact=IncidentImpact.EXTENSIVE,
            urgency=IncidentUrgency.CRITICAL,
            category=IncidentCategory.SOFTWARE,
            incident_number="INC-000003",
        ),
        Incident(
            record_type="incident",
            title="CMDB sync with cadastre API failing",
            description="Nightly sync job with katastar API failing with HTTP 503 since 02:00",
            change_type=ChangeType.EMERGENCY,
            priority=ChangePriority.P2,
            risk=ChangeRisk.HIGH,
            status=ChangeStatus.SUBMITTED,
            requested_by_id=admin_user.id,
            impact=IncidentImpact.SIGNIFICANT,
            urgency=IncidentUrgency.HIGH,
            category=IncidentCategory.NETWORK,
            incident_number="INC-000004",
        ),
        Incident(
            record_type="incident",
            title="Heating outage — Lamela A",
            description="Central heating system offline, residents reporting cold units",
            change_type=ChangeType.EMERGENCY,
            property_id=props[0].id,
            priority=ChangePriority.P2,
            risk=ChangeRisk.HIGH,
            status=ChangeStatus.COMPLETED,
            requested_by_id=steward_user.id,
            assigned_to_id=admin_user.id,
            impact=IncidentImpact.SIGNIFICANT,
            urgency=IncidentUrgency.HIGH,
            category=IncidentCategory.FACILITY,
            incident_number="INC-000005",
            resolution="Replaced faulty pressure sensor on Vaillant boiler",
            root_cause="Sensor failed due to limescale build-up; preventive descaling scheduled",
        ),
    ]
    db.add_all(incidents)
    db.commit()
    for inc in incidents:
        db.refresh(inc)

    # Link incidents to affected CIs
    db.add_all([
        ChangeCI(
            change_id=incidents[0].id,
            ci_id=building_sa.id,
            impact_description="Roof of Lamela A — water ingress",
        ),
        ChangeCI(
            change_id=incidents[4].id,
            ci_id=comp_heating.id,
            impact_description="Central heating boiler — pressure sensor failure",
        ),
    ])
    db.commit()

    return {
        "message": "Test data seeded successfully",
        "user": {"email": test_user.email, "password": "testpass123"},
        "admin": {"email": admin_user.email, "password": "admin12345"},
        "steward": {"email": steward_user.email, "password": "steward12345"},
        "properties": len(props),
        "cis": 13,
        "changes": len(changes),
        "incidents": len(incidents),
    }


@router.delete("/clean")
async def clean_test_data(db: Session = Depends(get_db)):
    """Clean all test data"""
    db.query(ChangeCI).delete()
    db.query(Incident).delete()
    db.query(Change).delete()
    db.query(CI).delete()
    db.query(Property).delete()
    db.query(User).delete()
    db.commit()
    return {"message": "Test data cleaned"}
