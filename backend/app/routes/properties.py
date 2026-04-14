"""Property routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.property import Property, PropertyStatus
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse

router = APIRouter(prefix="/properties", tags=["properties"])


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
):
    """Create a new property"""
    new_property = Property(
        name=property_data.name,
        type=property_data.type,
        location=property_data.location,
        price=property_data.price,
        description=property_data.description,
        status=property_data.status or PropertyStatus.DRAFT,
    )
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


@router.get("", response_model=dict)
async def list_properties(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str = Query(None),
    db: Session = Depends(get_db),
):
    """List properties with pagination and filtering"""
    query = db.query(Property)

    if status:
        query = query.filter(Property.status == status)

    total = query.count()
    properties = query.order_by(Property.created_at.desc()).limit(limit).offset(offset).all()

    return {
        "data": properties,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    db: Session = Depends(get_db),
):
    """Get property by ID"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return property_obj


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
):
    """Update property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    # Update fields
    update_data = property_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property_obj, field, value)

    db.commit()
    db.refresh(property_obj)
    return property_obj


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: str,
    db: Session = Depends(get_db),
):
    """Delete property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    db.delete(property_obj)
    db.commit()
    return None
