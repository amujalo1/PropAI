"""Incident schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class IncidentCreate(BaseModel):
    """Incident creation request schema"""
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    property_id: UUID
    priority: str


class IncidentResponse(BaseModel):
    """Incident response schema"""
    id: UUID
    title: str
    description: str
    property_id: UUID
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
