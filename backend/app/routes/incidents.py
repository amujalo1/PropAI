"""Incident Management routes — ITIL Incident Management (user-scoped)

Scoping rules:
  - Regular users see/edit only incidents they reported (requested_by_id)
  - Admins see all incidents and can approve/close any of them
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.models.incident import Incident
from app.models.change import ChangeCI, ChangeStatus
from app.models.ci import CI
from app.models.user import UserRole
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.schemas.change import ChangeCIAdd, ChangeCIResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/incidents", tags=["incidents"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_admin(current_user: dict) -> bool:
    return current_user.get("role") == UserRole.ADMIN.value


def _get_incident_or_404(incident_id: str, db: Session) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


def _assert_owner_or_admin(incident: Incident, current_user: dict):
    if _is_admin(current_user):
        return
    if str(incident.requested_by_id) != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="You do not have permission to access this incident")


def _assert_admin(current_user: dict):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can perform this action")


def _next_incident_number(db: Session) -> str:
    count = db.query(Incident).count()
    return f"INC-{(count + 1):06d}"


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
    current_user: dict = Depends(get_current_user),
):
    """Report a new Incident — automatically assigned to the current user."""
    if data.property_id:
        from app.models.property import Property
        if not db.query(Property).filter(Property.id == data.property_id).first():
            raise HTTPException(status_code=404, detail="Property not found")

    incident = Incident(
        record_type="incident",
        title=data.title,
        description=data.description,
        change_type="EMERGENCY",
        priority=data.priority,
        risk=data.risk,
        justification=data.justification,
        implementation_plan=data.implementation_plan,
        backout_plan=data.backout_plan,
        property_id=data.property_id,
        requested_by_id=current_user["sub"],
        assigned_to_id=data.assigned_to_id,
        status=ChangeStatus.SUBMITTED,
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
    current_user: dict = Depends(get_current_user),
):
    """List incidents — users see their own, admins see all."""
    query = db.query(Incident)

    if not _is_admin(current_user):
        query = query.filter(Incident.requested_by_id == current_user["sub"])

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
async def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get an incident by ID — owner or admin only."""
    incident = _get_incident_or_404(incident_id, db)
    _assert_owner_or_admin(incident, current_user)
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update an incident — owner or admin only."""
    incident = _get_incident_or_404(incident_id, db)
    _assert_owner_or_admin(incident, current_user)

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
    current_user: dict = Depends(get_current_user),
):
    """Assign an incident to an agent — admin only."""
    _assert_admin(current_user)
    incident = _get_incident_or_404(incident_id, db)
    incident.assigned_to_id = assigned_to_id
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/{incident_id}/start", response_model=IncidentResponse)
async def start_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark incident as IN_PROGRESS — admin only."""
    _assert_admin(current_user)
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
    current_user: dict = Depends(get_current_user),
):
    """Resolve an incident — admin only."""
    _assert_admin(current_user)
    incident = _get_incident_or_404(incident_id, db)
    if incident.status != ChangeStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Only IN_PROGRESS incidents can be resolved")
    incident.resolution = resolution
    incident.resolved_at = datetime.utcnow()
    incident.actual_end = datetime.utcnow()
    return _transition(incident, ChangeStatus.COMPLETED, db)


@router.post("/{incident_id}/close", response_model=IncidentResponse)
async def close_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Close a resolved incident — admin only."""
    _assert_admin(current_user)
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
    current_user: dict = Depends(get_current_user),
):
    """Associate a CI with this incident — owner or admin."""
    incident = _get_incident_or_404(incident_id, db)
    _assert_owner_or_admin(incident, current_user)

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

    assoc = ChangeCI(change_id=incident.id, ci_id=data.ci_id, impact_description=data.impact_description)
    db.add(assoc)
    db.commit()
    db.refresh(assoc)
    return assoc


@router.delete("/{incident_id}/cis/{ci_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_affected_ci(
    incident_id: str,
    ci_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove a CI association — owner or admin."""
    incident = _get_incident_or_404(incident_id, db)
    _assert_owner_or_admin(incident, current_user)

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
