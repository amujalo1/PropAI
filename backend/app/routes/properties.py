"""Property routes — user-scoped with admin override"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db import get_db
from app.models.property import Property, PropertyStatus
from app.models.user import UserRole
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/properties", tags=["properties"])


def _is_admin(current_user: dict) -> bool:
    return current_user.get("role") == UserRole.ADMIN.value


def _get_property_or_404(property_id: str, db: Session) -> Property:
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return prop


def _assert_owner_or_admin(prop: Property, current_user: dict):
    """Raise 403 if the caller is not the owner and not an admin."""
    if _is_admin(current_user):
        return
    if str(prop.owner_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this property",
        )


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new property owned by the current user."""
    new_property = Property(
        name=property_data.name,
        type=property_data.type,
        location=property_data.location,
        price=property_data.price,
        description=property_data.description,
        status=property_data.status or PropertyStatus.DRAFT,
        owner_id=current_user["sub"],
    )
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


@router.get("")
async def list_properties(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List properties.
    - Regular users see only their own properties.
    - Admins see all properties.
    """
    query = db.query(Property)

    if not _is_admin(current_user):
        query = query.filter(Property.owner_id == current_user["sub"])

    if status:
        query = query.filter(Property.status == status)

    total = query.count()
    properties = query.order_by(Property.created_at.desc()).limit(limit).offset(offset).all()

    return {
        "data": [PropertyResponse.model_validate(p) for p in properties],
        "pagination": {"total": total, "limit": limit, "offset": offset},
    }


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a property by ID — owner or admin only."""
    prop = _get_property_or_404(property_id, db)
    _assert_owner_or_admin(prop, current_user)
    return prop


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a property — owner or admin only."""
    prop = _get_property_or_404(property_id, db)
    _assert_owner_or_admin(prop, current_user)

    for field, value in property_data.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)

    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a property — owner or admin only."""
    prop = _get_property_or_404(property_id, db)
    _assert_owner_or_admin(prop, current_user)

    db.delete(prop)
    db.commit()
    return None
