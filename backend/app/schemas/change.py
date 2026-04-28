"""Change schemas — ITIL Change Management request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ---------------------------------------------------------------------------
# Change CI association schemas
# ---------------------------------------------------------------------------

class ChangeCIAdd(BaseModel):
    """Add a CI to a change's affected items"""
    ci_id: UUID
    impact_description: Optional[str] = None


class ChangeCIResponse(BaseModel):
    """CI association response"""
    id: UUID
    change_id: UUID
    ci_id: UUID
    impact_description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Change schemas
# ---------------------------------------------------------------------------

class ChangeCreate(BaseModel):
    """Change creation request"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    change_type: str = Field(default="NORMAL")
    priority: str = Field(default="P3")
    risk: str = Field(default="MEDIUM")
    justification: Optional[str] = None
    implementation_plan: Optional[str] = None
    backout_plan: Optional[str] = None
    test_plan: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    property_id: Optional[UUID] = None
    requested_by_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None


class ChangeUpdate(BaseModel):
    """Change update request — all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    change_type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    risk: Optional[str] = None
    justification: Optional[str] = None
    implementation_plan: Optional[str] = None
    backout_plan: Optional[str] = None
    test_plan: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    property_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    approved_by_id: Optional[UUID] = None


class ChangeResponse(BaseModel):
    """Change response schema"""
    id: UUID
    record_type: str
    title: str
    description: str
    change_type: str
    status: str
    priority: str
    risk: str
    justification: Optional[str]
    implementation_plan: Optional[str]
    backout_plan: Optional[str]
    test_plan: Optional[str]
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    property_id: Optional[UUID]
    requested_by_id: Optional[UUID]
    assigned_to_id: Optional[UUID]
    approved_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    affected_cis: List[ChangeCIResponse] = []

    class Config:
        from_attributes = True
