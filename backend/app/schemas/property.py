"""Property schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class PropertyCreate(BaseModel):
    """Property creation request schema"""
    name: str = Field(..., min_length=1)
    type: str
    location: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    status: Optional[str] = "DRAFT"


class PropertyUpdate(BaseModel):
    """Property update request schema"""
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PropertyResponse(BaseModel):
    """Property response schema"""
    id: UUID
    name: str
    type: str
    location: str
    status: str
    price: float
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
