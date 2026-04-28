"""Incident Management routes — ITIL Incident Management

Incidents are a specialised subtype of Change (joined-table inheritance).
Every Incident IS a Change; not every Change is an Incident.

ITIL Incident lifecycle (mapped to ChangeStatus):
  DRAFT → SUBMITTED (open) → IN_PROGRESS → COMPLETED (resolved) → CLOSED

Endpoints:
  POST   /incidents                   Create a new incident
  GET    /incidents                   List incidents (paginated, filterable)
  GET    /incidents/{id}              Get incident by ID
  PUT    /incidents/{id}              Update incident
  POST   /incidents/{id}/assign       Assign to agent
  POST   /incidents/{id}/start        Mark as IN_PROGRESS
  POST   /incidents/{id}/resolve      Mark as COMPLETED (resolved)
  POST   /incidents/{id}/close        Close incident
  POST   /incidents/{id}/cis          Add affected CI
  DELETE /incidents/{id}/cis/{ci_id}  Remove affected CI
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.models.incident import Incident
from app.models.change import ChangeCI, ChangeStatus
from app.models.ci import CI
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.schemas.change import ChangeCIAdd, ChangeCIResponse

router = APIRouter(prefix="/incidents", tags=["incidents"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_INCIDENT_COUNTER_KEY = "incident_seq"


def _next_incident_number(db: Session) -> str:
    """Generate the next INC-XXXXXX number."""
    count = db.query(Incident).count()
    return f"INC-{(count + 1):06d}"


def _get_incident_or_404(incident_id: str, db: Session) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


def _transition(incident: Incident, new_status: ChangeStatus, db: Session) -> Incident:
    incident.status = new_status
    db.commit()
    db.refresh(incident)
    return incident


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
):
    """Create a new Incident (which is also a Change)."""
    if data.property_id:
        from app.models.property import Property
        if not db.query(Property).filter(Property.id == data.property_id).first():
            raise HTTPException(status_code=404, detail="Property not found")

    incident = Incident(
        record_type="incident",
        title=data.title,
        description=data.description,
        # Incidents are always EMERGENCY change type (unplanned)
        change_type="EMERGENCY",
        priority=data.priority,
        risk=data.risk,
        justification=data.justification,
        implementation_plan=data.implementation_plan,
        backout_plan=data.backout_plan,
        property_id=data.property_id,
        requested_by_id=data.requested_by_id,
        assigned_to_id=data.assigned_to_id,
        status=ChangeStatus.SUBMITTED,   # Incidents start as SUBMITTED (open)
        # Incident-specific
        impact=data.impact,
        urgency=data.urgency,
        category=data.category,
    )
    incident.incident_number = _next_incident_number(db)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("")
async def list_incidents(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    property_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List Incidents with pagination and filtering."""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if priority:
        query = query.filter(Incident.priority == priority)
    if category:
        query = query.filter(Incident.category == category)
    if property_id:
        query = query.filter(Incident.property_id == property_id)

    total = query.count()
    incidents = query.order_by(Incident.created_at.desc()).limit(limit).offset(offset).all()

    return {
        "data": [IncidentResponse.model_validate(i) for i in incidents],
        "pagination": {"total": total, "limit": limit, "offset": offset},
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get an Incident by ID."""
    return _get_incident_or_404(incident_id, db)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
):
    """Update an Incident."""
    incident = _get_incident_or_404(incident_id, db)

    if incident.status == ChangeStatus.CLOSED:
        raise HTTPException(status_code=409, detail="Cannot edit a closed incident")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    return incident


# ---------------------------------------------------------------------------
# Lifecycle transitions
# ---------------------------------------------------------------------------

@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: str,
    assigned_to_id: str = Query(..., description="UUID of the user to assign"),
    db: Session = Depends(get_db),
):
    """Assign an incident to an agent."""
    incident = _get_incident_or_404(incident_id, db)
    incident.assigned_to_id = assigned_to_id
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/{incident_id}/start", response_model=IncidentResponse)
async def start_incident(incident_id: str, db: Session = Depends(get_db)):
    """Mark incident as IN_PROGRESS (investigation started)."""
    incident = _get_incident_or_404(incident_id, db)
    if incident.status != ChangeStatus.SUBMITTED:
        raise HTTPException(status_code=409, detail="Only SUBMITTED incidents can be started")
    incident.actual_start = datetime.utcnow()
    return _transition(incident, ChangeStatus.IN_PROGRESS, db)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: str,
    resolution: str = Query(..., description="Resolution description"),
    db: Session = Depends(get_db),
):
    """Resolve an IN_PROGRESS incident."""
    incident = _get_incident_or_404(incident_id, db)
    if incident.status != ChangeStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Only IN_PROGRESS incidents can be resolved")
    incident.resolution = resolution
    incident.resolved_at = datetime.utcnow()
    incident.actual_end = datetime.utcnow()
    return _transition(incident, ChangeStatus.COMPLETED, db)


@router.post("/{incident_id}/close", response_model=IncidentResponse)
async def close_incident(incident_id: str, db: Session = Depends(get_db)):
    """Close a COMPLETED incident."""
    incident = _get_incident_or_404(incident_id, db)
    if incident.status != ChangeStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Only COMPLETED (resolved) incidents can be closed")
    return _transition(incident, ChangeStatus.CLOSED, db)


# ---------------------------------------------------------------------------
# Affected CIs (SACM integration)
# ---------------------------------------------------------------------------

@router.post("/{incident_id}/cis", response_model=ChangeCIResponse, status_code=status.HTTP_201_CREATED)
async def add_affected_ci(
    incident_id: str,
    data: ChangeCIAdd,
    db: Session = Depends(get_db),
):
    """Associate a CI with this incident (SACM impact tracking)."""
    incident = _get_incident_or_404(incident_id, db)

    ci = db.query(CI).filter(CI.id == data.ci_id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="CI not found")

    existing = (
        db.query(ChangeCI)
        .filter(ChangeCI.change_id == incident.id, ChangeCI.ci_id == data.ci_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="CI already associated with this incident")

    assoc = ChangeCI(
        change_id=incident.id,
        ci_id=data.ci_id,
        impact_description=data.impact_description,
    )
    db.add(assoc)
    db.commit()
    db.refresh(assoc)
    return assoc


@router.delete("/{incident_id}/cis/{ci_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_affected_ci(
    incident_id: str,
    ci_id: str,
    db: Session = Depends(get_db),
):
    """Remove a CI association from this incident."""
    incident = _get_incident_or_404(incident_id, db)

    assoc = (
        db.query(ChangeCI)
        .filter(ChangeCI.change_id == incident.id, ChangeCI.ci_id == ci_id)
        .first()
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="CI association not found")

    db.delete(assoc)
    db.commit()
    return None
