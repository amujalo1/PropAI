"""Property schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.property import PropertyType, PropertyStatus


class PropertyCreate(BaseModel):
    """Property creation request schema"""
    name: str = Field(..., min_length=1)
    type: PropertyType
    location: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    status: Optional[PropertyStatus] = PropertyStatus.DRAFT


class PropertyUpdate(BaseModel):
    """Property update request schema"""
    name: Optional[str] = None
    type: Optional[PropertyType] = None
    location: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    status: Optional[PropertyStatus] = None


class PropertyResponse(BaseModel):
    """Property response schema"""
    id: UUID
    name: str
    type: PropertyType
    location: str
    status: PropertyStatus
    price: float
    description: Optional[str]
    owner_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
