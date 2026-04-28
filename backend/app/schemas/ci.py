"""CI schemas — ITIL SACM request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CICreate(BaseModel):
    """CI creation request"""
    type: str
    region: str = Field(..., min_length=1)
    name: Optional[str] = None
    description: Optional[str] = None
    status: str = Field(default="ACTIVE")
    parent_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    version: Optional[str] = None
    serial_number: Optional[str] = None
    location_detail: Optional[str] = None


class CIUpdate(BaseModel):
    """CI update request — all fields optional"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None
    serial_number: Optional[str] = None
    location_detail: Optional[str] = None
    owner_id: Optional[UUID] = None
    property_id: Optional[UUID] = None


class CIResponse(BaseModel):
    """CI response schema"""
    id: UUID
    ci_id: str
    name: Optional[str]
    type: str
    status: str
    region: str
    sequence: int
    hierarchy_level: int
    description: Optional[str]
    owner_id: Optional[UUID]
    version: Optional[str]
    serial_number: Optional[str]
    location_detail: Optional[str]
    parent_id: Optional[UUID]
    property_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CIHierarchyNode(BaseModel):
    """Lightweight node for hierarchy tree responses"""
    id: str
    ci_id: str
    name: Optional[str]
    type: str
    status: str
    level: int
    children: List["CIHierarchyNode"] = []

    class Config:
        from_attributes = True


CIHierarchyNode.model_rebuild()
