"""Incident schemas — ITIL Incident Management request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.change import ChangeType, ChangeStatus, ChangePriority, ChangeRisk
from app.models.incident import IncidentImpact, IncidentUrgency, IncidentCategory
from .change import ChangeCIResponse


class IncidentCreate(BaseModel):
    """Incident creation request"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    priority: ChangePriority = ChangePriority.P3
    risk: ChangeRisk = ChangeRisk.MEDIUM
    justification: Optional[str] = None
    implementation_plan: Optional[str] = None
    backout_plan: Optional[str] = None
    property_id: Optional[UUID] = None
    requested_by_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    impact: IncidentImpact = IncidentImpact.MODERATE
    urgency: IncidentUrgency = IncidentUrgency.MEDIUM
    category: IncidentCategory = IncidentCategory.OTHER


class IncidentUpdate(BaseModel):
    """Incident update request — all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ChangeStatus] = None
    priority: Optional[ChangePriority] = None
    risk: Optional[ChangeRisk] = None
    justification: Optional[str] = None
    implementation_plan: Optional[str] = None
    backout_plan: Optional[str] = None
    property_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    approved_by_id: Optional[UUID] = None
    impact: Optional[IncidentImpact] = None
    urgency: Optional[IncidentUrgency] = None
    category: Optional[IncidentCategory] = None
    resolution: Optional[str] = None
    root_cause: Optional[str] = None


class IncidentResponse(BaseModel):
    """Incident response schema — includes all Change + Incident fields"""
    # Change fields
    id: UUID
    record_type: str
    title: str
    description: str
    change_type: ChangeType
    status: ChangeStatus
    priority: ChangePriority
    risk: ChangeRisk
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

    # Incident-specific fields
    incident_number: Optional[str]
    impact: IncidentImpact
    urgency: IncidentUrgency
    category: IncidentCategory
    resolution: Optional[str]
    resolved_at: Optional[datetime]
    root_cause: Optional[str]

    class Config:
        from_attributes = True
