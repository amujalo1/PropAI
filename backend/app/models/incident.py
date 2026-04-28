"""Incident model — ITIL Incident Management

Every Incident IS a Change (joined-table inheritance).
Incidents represent unplanned interruptions or reductions in quality of service.

ITIL Incident lifecycle:
  OPEN → IN_PROGRESS → RESOLVED → CLOSED
  (maps to the parent Change status field)

Incident-specific fields (stored in the ``incidents`` table):
  - incident_number: human-readable reference (INC-000001)
  - impact:          scope of the disruption
  - urgency:         how quickly it must be resolved
  - category:        classification (hardware, software, network, …)
  - resolution:      what was done to fix it
  - resolved_at:     when the incident was resolved
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from .base import Base
from .change import Change


class IncidentImpact(str, Enum):
    """Scope of the disruption"""
    EXTENSIVE = "EXTENSIVE"   # Whole organisation / many users
    SIGNIFICANT = "SIGNIFICANT"  # Department / service
    MODERATE = "MODERATE"    # Small group
    MINOR = "MINOR"          # Single user


class IncidentUrgency(str, Enum):
    """How quickly the incident must be resolved"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IncidentCategory(str, Enum):
    """Incident classification"""
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    NETWORK = "NETWORK"
    SECURITY = "SECURITY"
    FACILITY = "FACILITY"
    SERVICE_REQUEST = "SERVICE_REQUEST"
    OTHER = "OTHER"


class Incident(Change):
    """
    ITIL Incident record.

    Inherits all Change fields (title, description, status, priority, …).
    Adds incident-specific fields in the ``incidents`` table.

    The ``status`` field (from Change) drives the incident lifecycle:
      DRAFT → SUBMITTED (= OPEN) → IN_PROGRESS → COMPLETED (= RESOLVED) → CLOSED
    """
    __tablename__ = "incidents"

    # FK to parent Change record
    id = Column(UUID(as_uuid=True), ForeignKey("changes.id"), primary_key=True)

    # Human-readable reference number (auto-generated)
    incident_number = Column(String(20), unique=True, nullable=True, index=True)

    # Incident-specific classification
    impact = Column(SQLEnum(IncidentImpact), nullable=False, default=IncidentImpact.MODERATE)
    urgency = Column(SQLEnum(IncidentUrgency), nullable=False, default=IncidentUrgency.MEDIUM)
    category = Column(SQLEnum(IncidentCategory), nullable=False, default=IncidentCategory.OTHER)

    # Resolution details
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Root cause (filled in during post-incident review)
    root_cause = Column(Text, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "incident",
    }

    def __repr__(self):
        return (
            f"<Incident(id={self.id}, number={self.incident_number!r}, "
            f"title={self.title!r}, status={self.status})>"
        )
