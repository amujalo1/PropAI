"""Change Management routes — ITIL Change Management (user-scoped)

Scoping rules:
  - Regular users see/edit only changes they created (requested_by_id = their user id)
  - Admins see all changes and are the only ones who can approve/reject
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.models.change import Change, ChangeCI, ChangeStatus
from app.models.ci import CI
from app.models.user import UserRole
from app.schemas.change import (
    ChangeCreate, ChangeUpdate, ChangeResponse,
    ChangeCIAdd, ChangeCIResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/changes", tags=["changes"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_admin(current_user: dict) -> bool:
    return current_user.get("role") == UserRole.ADMIN.value


def _get_change_or_404(change_id: str, db: Session) -> Change:
    change = (
        db.query(Change)
        .filter(Change.id == change_id, Change.record_type == "change")
        .first()
    )
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")
    return change


def _assert_owner_or_admin(change: Change, current_user: dict):
    if _is_admin(current_user):
        return
    if str(change.requested_by_id) != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="You do not have permission to access this change")


def _assert_admin(current_user: dict):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can perform this action")


def _transition(change: Change, new_status: ChangeStatus, db: Session) -> Change:
    change.status = new_status
    db.commit()
    db.refresh(change)
    return change


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.post("", response_model=ChangeResponse, status_code=status.HTTP_201_CREATED)
async def create_change(
    data: ChangeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new Change — automatically assigned to the current user."""
    if data.property_id:
        from app.models.property import Property
        if not db.query(Property).filter(Property.id == data.property_id).first():
            raise HTTPException(status_code=404, detail="Property not found")

    change = Change(
        record_type="change",
        title=data.title,
        description=data.description,
        change_type=data.change_type,
        priority=data.priority,
        risk=data.risk,
        justification=data.justification,
        implementation_plan=data.implementation_plan,
        backout_plan=data.backout_plan,
        test_plan=data.test_plan,
        scheduled_start=data.scheduled_start,
        scheduled_end=data.scheduled_end,
        property_id=data.property_id,
        requested_by_id=current_user["sub"],
        assigned_to_id=data.assigned_to_id,
        status=ChangeStatus.DRAFT,
    )
    db.add(change)
    db.commit()
    db.refresh(change)
    return change


@router.get("")
async def list_changes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    property_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List changes — users see their own, admins see all."""
    query = db.query(Change).filter(Change.record_type == "change")

    if not _is_admin(current_user):
        query = query.filter(Change.requested_by_id == current_user["sub"])

    if status:
        query = query.filter(Change.status == status)
    if change_type:
        query = query.filter(Change.change_type == change_type)
    if priority:
        query = query.filter(Change.priority == priority)
    if property_id:
        query = query.filter(Change.property_id == property_id)

    total = query.count()
    changes = query.order_by(Change.created_at.desc()).limit(limit).offset(offset).all()

    return {
        "data": [ChangeResponse.model_validate(c) for c in changes],
        "pagination": {"total": total, "limit": limit, "offset": offset},
    }


@router.get("/{change_id}", response_model=ChangeResponse)
async def get_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a change by ID — owner or admin only."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)
    return change


@router.put("/{change_id}", response_model=ChangeResponse)
async def update_change(
    change_id: str,
    data: ChangeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a change — owner or admin only, only in editable statuses."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)

    if change.status not in (ChangeStatus.DRAFT, ChangeStatus.SUBMITTED, ChangeStatus.REJECTED):
        raise HTTPException(status_code=409, detail=f"Cannot edit a change in status '{change.status}'")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(change, field, value)

    db.commit()
    db.refresh(change)
    return change


@router.delete("/{change_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a DRAFT change — owner or admin only."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)

    if change.status != ChangeStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Only DRAFT changes can be deleted")

    db.delete(change)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# Lifecycle transitions
# ---------------------------------------------------------------------------

@router.post("/{change_id}/submit", response_model=ChangeResponse)
async def submit_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Submit a DRAFT change for approval — owner only."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)
    if change.status != ChangeStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Only DRAFT changes can be submitted")
    return _transition(change, ChangeStatus.SUBMITTED, db)


@router.post("/{change_id}/approve", response_model=ChangeResponse)
async def approve_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Approve a SUBMITTED change — admin only."""
    _assert_admin(current_user)
    change = _get_change_or_404(change_id, db)
    if change.status != ChangeStatus.SUBMITTED:
        raise HTTPException(status_code=409, detail="Only SUBMITTED changes can be approved")
    change.approved_by_id = current_user["sub"]
    return _transition(change, ChangeStatus.APPROVED, db)


@router.post("/{change_id}/reject", response_model=ChangeResponse)
async def reject_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reject a SUBMITTED change — admin only."""
    _assert_admin(current_user)
    change = _get_change_or_404(change_id, db)
    if change.status != ChangeStatus.SUBMITTED:
        raise HTTPException(status_code=409, detail="Only SUBMITTED changes can be rejected")
    return _transition(change, ChangeStatus.REJECTED, db)


@router.post("/{change_id}/start", response_model=ChangeResponse)
async def start_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark an APPROVED change as IN_PROGRESS — owner or admin."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)
    if change.status != ChangeStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Only APPROVED changes can be started")
    change.actual_start = datetime.utcnow()
    return _transition(change, ChangeStatus.IN_PROGRESS, db)


@router.post("/{change_id}/complete", response_model=ChangeResponse)
async def complete_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark an IN_PROGRESS change as COMPLETED — owner or admin."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)
    if change.status != ChangeStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Only IN_PROGRESS changes can be completed")
    change.actual_end = datetime.utcnow()
    return _transition(change, ChangeStatus.COMPLETED, db)


@router.post("/{change_id}/fail", response_model=ChangeResponse)
async def fail_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark an IN_PROGRESS change as FAILED — owner or admin."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)
    if change.status != ChangeStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Only IN_PROGRESS changes can be failed")
    change.actual_end = datetime.utcnow()
    return _transition(change, ChangeStatus.FAILED, db)


@router.post("/{change_id}/close", response_model=ChangeResponse)
async def close_change(
    change_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Close a COMPLETED or FAILED change — admin only."""
    _assert_admin(current_user)
    change = _get_change_or_404(change_id, db)
    if change.status not in (ChangeStatus.COMPLETED, ChangeStatus.FAILED):
        raise HTTPException(status_code=409, detail="Only COMPLETED or FAILED changes can be closed")
    return _transition(change, ChangeStatus.CLOSED, db)


# ---------------------------------------------------------------------------
# Affected CIs (SACM integration)
# ---------------------------------------------------------------------------

@router.post("/{change_id}/cis", response_model=ChangeCIResponse, status_code=status.HTTP_201_CREATED)
async def add_affected_ci(
    change_id: str,
    data: ChangeCIAdd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Associate a CI with this change — owner or admin."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)

    ci = db.query(CI).filter(CI.id == data.ci_id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="CI not found")

    existing = (
        db.query(ChangeCI)
        .filter(ChangeCI.change_id == change.id, ChangeCI.ci_id == data.ci_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="CI already associated with this change")

    assoc = ChangeCI(change_id=change.id, ci_id=data.ci_id, impact_description=data.impact_description)
    db.add(assoc)
    db.commit()
    db.refresh(assoc)
    return assoc


@router.delete("/{change_id}/cis/{ci_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_affected_ci(
    change_id: str,
    ci_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove a CI association — owner or admin."""
    change = _get_change_or_404(change_id, db)
    _assert_owner_or_admin(change, current_user)

    assoc = (
        db.query(ChangeCI)
        .filter(ChangeCI.change_id == change.id, ChangeCI.ci_id == ci_id)
        .first()
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="CI association not found")

    db.delete(assoc)
    db.commit()
    return None
