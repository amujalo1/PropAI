"""CMDB CI routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.models.ci import CI, CIType
from app.schemas.ci import CICreate, CIResponse

router = APIRouter(prefix="/ci", tags=["ci"])


def generate_ci_id(ci_type: str, region: str, sequence: int) -> str:
    """Generate CI ID in format PROP-[TYPE]-[REGION]-[SEQUENCE]"""
    type_abbr = ci_type[:4].upper()
    return f"PROP-{type_abbr}-{region.upper()}-{sequence:06d}"


@router.post("", response_model=CIResponse, status_code=status.HTTP_201_CREATED)
async def create_ci(
    ci_data: CICreate,
    db: Session = Depends(get_db),
):
    """Create a new CI"""
    # Validate parent if provided
    if ci_data.parent_id:
        parent = db.query(CI).filter(CI.id == ci_data.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent CI not found",
            )

    # Get next sequence number
    last_ci = db.query(CI).filter(
        CI.type == ci_data.type,
        CI.region == ci_data.region,
    ).order_by(CI.sequence.desc()).first()
    
    sequence = (last_ci.sequence + 1) if last_ci else 1
    ci_id = generate_ci_id(ci_data.type, ci_data.region, sequence)

    # Determine hierarchy level
    hierarchy_level = 1
    if ci_data.parent_id:
        parent = db.query(CI).filter(CI.id == ci_data.parent_id).first()
        hierarchy_level = parent.hierarchy_level + 1

    new_ci = CI(
        ci_id=ci_id,
        type=ci_data.type,
        region=ci_data.region,
        sequence=sequence,
        hierarchy_level=hierarchy_level,
        parent_id=ci_data.parent_id,
    )
    db.add(new_ci)
    db.commit()
    db.refresh(new_ci)
    return new_ci


@router.get("/{ci_id}", response_model=CIResponse)
async def get_ci(
    ci_id: str,
    db: Session = Depends(get_db),
):
    """Get CI by ID"""
    ci = db.query(CI).filter(CI.ci_id == ci_id).first()
    if not ci:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CI not found",
        )
    return ci


@router.get("/hierarchy/{ci_id}", response_model=list)
async def get_ci_hierarchy(
    ci_id: str,
    db: Session = Depends(get_db),
):
    """Get full hierarchy path for a CI"""
    ci = db.query(CI).filter(CI.ci_id == ci_id).first()
    if not ci:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CI not found",
        )

    hierarchy = []
    current = ci
    while current:
        hierarchy.insert(0, {
            "id": str(current.id),
            "ci_id": current.ci_id,
            "type": current.type,
            "level": current.hierarchy_level,
        })
        if current.parent_id:
            current = db.query(CI).filter(CI.id == current.parent_id).first()
        else:
            current = None

    return hierarchy


@router.get("/level/{level}", response_model=list)
async def get_ci_by_level(
    level: int,
    db: Session = Depends(get_db),
):
    """Get all CIs at a specific hierarchy level"""
    cis = db.query(CI).filter(CI.hierarchy_level == level).all()
    return cis
