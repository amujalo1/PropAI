"""CMDB / SACM CI routes — ITIL Service Asset & Configuration Management

Endpoints:
  POST   /ci                          Create a new CI
  GET    /ci                          List CIs (paginated, filterable)
  GET    /ci/{ci_id}                  Get CI by ci_id string
  GET    /ci/uuid/{id}                Get CI by UUID
  PUT    /ci/uuid/{id}                Update CI
  DELETE /ci/uuid/{id}                Delete CI
  GET    /ci/hierarchy/{ci_id}        Get full ancestor path
  GET    /ci/tree/{ci_id}             Get subtree rooted at CI
  GET    /ci/level/{level}            Get all CIs at a hierarchy level
  GET    /ci/property/{property_id}   Get CIs linked to a property
  GET    /ci/uuid/{id}/changes        Get changes affecting this CI
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db import get_db
from app.models.ci import CI, CIType, CIStatus
from app.schemas.ci import CICreate, CIUpdate, CIResponse, CIHierarchyNode

router = APIRouter(prefix="/ci", tags=["ci"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_ci_id(ci_type: str, region: str, sequence: int) -> str:
    """Generate CI ID: PROP-[TYPE4]-[REGION]-[SEQ6]"""
    type_abbr = ci_type[:4].upper()
    return f"PROP-{type_abbr}-{region.upper()}-{sequence:06d}"


def _get_ci_by_uuid_or_404(ci_uuid: str, db: Session) -> CI:
    ci = db.query(CI).filter(CI.id == ci_uuid).first()
    if not ci:
        raise HTTPException(status_code=404, detail="CI not found")
    return ci


def _build_subtree(ci: CI, db: Session) -> dict:
    """Recursively build a subtree dict for a CI."""
    children = db.query(CI).filter(CI.parent_id == ci.id).all()
    return {
        "id": str(ci.id),
        "ci_id": ci.ci_id,
        "name": ci.name,
        "type": ci.type,
        "status": ci.status,
        "level": ci.hierarchy_level,
        "children": [_build_subtree(c, db) for c in children],
    }


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.post("", response_model=CIResponse, status_code=status.HTTP_201_CREATED)
async def create_ci(
    data: CICreate,
    db: Session = Depends(get_db),
):
    """Create a new Configuration Item."""
    # Validate parent
    hierarchy_level = 1
    if data.parent_id:
        parent = db.query(CI).filter(CI.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent CI not found")
        hierarchy_level = parent.hierarchy_level + 1

    # Validate property link
    if data.property_id:
        from app.models.property import Property
        if not db.query(Property).filter(Property.id == data.property_id).first():
            raise HTTPException(status_code=404, detail="Property not found")

    # Auto-increment sequence per type+region
    last = (
        db.query(CI)
        .filter(CI.type == data.type, CI.region == data.region)
        .order_by(CI.sequence.desc())
        .first()
    )
    sequence = (last.sequence + 1) if last else 1
    ci_id = _generate_ci_id(data.type, data.region, sequence)

    ci = CI(
        ci_id=ci_id,
        name=data.name,
        type=data.type,
        status=data.status,
        region=data.region,
        sequence=sequence,
        hierarchy_level=hierarchy_level,
        description=data.description,
        parent_id=data.parent_id,
        property_id=data.property_id,
        owner_id=data.owner_id,
        version=data.version,
        serial_number=data.serial_number,
        location_detail=data.location_detail,
    )
    db.add(ci)
    db.commit()
    db.refresh(ci)
    return ci


@router.get("")
async def list_cis(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ci_type: Optional[str] = Query(None, alias="type"),
    ci_status: Optional[str] = Query(None, alias="status"),
    region: Optional[str] = Query(None),
    level: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List CIs with pagination and filtering."""
    query = db.query(CI)

    if ci_type:
        query = query.filter(CI.type == ci_type)
    if ci_status:
        query = query.filter(CI.status == ci_status)
    if region:
        query = query.filter(CI.region == region)
    if level is not None:
        query = query.filter(CI.hierarchy_level == level)

    total = query.count()
    cis = query.order_by(CI.hierarchy_level, CI.sequence).limit(limit).offset(offset).all()

    return {
        "data": [CIResponse.model_validate(c) for c in cis],
        "pagination": {"total": total, "limit": limit, "offset": offset},
    }


@router.get("/uuid/{ci_uuid}", response_model=CIResponse)
async def get_ci_by_uuid(ci_uuid: str, db: Session = Depends(get_db)):
    """Get CI by UUID."""
    return _get_ci_by_uuid_or_404(ci_uuid, db)


@router.put("/uuid/{ci_uuid}", response_model=CIResponse)
async def update_ci(
    ci_uuid: str,
    data: CIUpdate,
    db: Session = Depends(get_db),
):
    """Update a CI's attributes."""
    ci = _get_ci_by_uuid_or_404(ci_uuid, db)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ci, field, value)

    db.commit()
    db.refresh(ci)
    return ci


@router.delete("/uuid/{ci_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ci(ci_uuid: str, db: Session = Depends(get_db)):
    """Delete a CI (must have no children)."""
    ci = _get_ci_by_uuid_or_404(ci_uuid, db)

    children_count = db.query(CI).filter(CI.parent_id == ci.id).count()
    if children_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete CI with {children_count} child CI(s). Remove children first.",
        )

    db.delete(ci)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# Hierarchy queries
# ---------------------------------------------------------------------------

@router.get("/{ci_id}", response_model=CIResponse)
async def get_ci(ci_id: str, db: Session = Depends(get_db)):
    """Get CI by ci_id string (e.g. PROP-LOCA-EU-000001)."""
    ci = db.query(CI).filter(CI.ci_id == ci_id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="CI not found")
    return ci


@router.get("/hierarchy/{ci_id}")
async def get_ci_hierarchy(ci_id: str, db: Session = Depends(get_db)):
    """Get the full ancestor path (root → CI) for a given ci_id."""
    ci = db.query(CI).filter(CI.ci_id == ci_id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="CI not found")

    path = []
    current = ci
    while current:
        path.insert(0, {
            "id": str(current.id),
            "ci_id": current.ci_id,
            "name": current.name,
            "type": current.type,
            "status": current.status,
            "level": current.hierarchy_level,
        })
        current = db.query(CI).filter(CI.id == current.parent_id).first() if current.parent_id else None

    return path


@router.get("/tree/{ci_id}")
async def get_ci_tree(ci_id: str, db: Session = Depends(get_db)):
    """Get the full subtree rooted at the given ci_id."""
    ci = db.query(CI).filter(CI.ci_id == ci_id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="CI not found")
    return _build_subtree(ci, db)


@router.get("/level/{level}")
async def get_ci_by_level(level: int, db: Session = Depends(get_db)):
    """Get all CIs at a specific hierarchy level."""
    cis = db.query(CI).filter(CI.hierarchy_level == level).all()
    return [CIResponse.model_validate(c) for c in cis]


@router.get("/property/{property_id}")
async def get_cis_by_property(property_id: str, db: Session = Depends(get_db)):
    """Get all CIs linked to a specific property."""
    cis = db.query(CI).filter(CI.property_id == property_id).all()
    return [CIResponse.model_validate(c) for c in cis]


@router.get("/uuid/{ci_uuid}/changes")
async def get_ci_changes(ci_uuid: str, db: Session = Depends(get_db)):
    """Get all Changes (and Incidents) that affect this CI."""
    ci = _get_ci_by_uuid_or_404(ci_uuid, db)

    from app.models.change import Change, ChangeCI
    from app.schemas.change import ChangeResponse

    results = (
        db.query(Change)
        .join(ChangeCI, ChangeCI.change_id == Change.id)
        .filter(ChangeCI.ci_id == ci.id)
        .order_by(Change.created_at.desc())
        .all()
    )
    return [ChangeResponse.model_validate(c) for c in results]
