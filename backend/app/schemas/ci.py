"""CI schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class CICreate(BaseModel):
    """CI creation request schema"""
    type: str
    region: str = Field(..., min_length=1)
    parent_id: Optional[UUID] = None


class CIResponse(BaseModel):
    """CI response schema"""
    id: UUID
    ci_id: str
    type: str
    region: str
    sequence: int
    hierarchy_level: int
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
