"""Incident routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.incident import Incident, IncidentStatus
from app.schemas.incident import IncidentCreate, IncidentResponse

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
):
    """Create a new incident"""
    # Verify property exists
    from app.models.property import Property
    property_obj = db.query(Property).filter(Property.id == incident_data.property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    new_incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        property_id=incident_data.property_id,
        priority=incident_data.priority,
        status=IncidentStatus.OPEN,
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident


@router.get("", response_model=dict)
async def list_incidents(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    priority: str = Query(None),
    property_id: str = Query(None),
    db: Session = Depends(get_db),
):
    """List incidents with pagination and filtering"""
    query = db.query(Incident)

    if priority:
        query = query.filter(Incident.priority == priority)

    if property_id:
        query = query.filter(Incident.property_id == property_id)

    total = query.count()
    incidents = query.order_by(Incident.created_at.desc()).limit(limit).offset(offset).all()

    return {
        "data": incidents,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
):
    """Get incident by ID"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )
    return incident
