"""Change model — ITIL Change Management

Every Incident IS a Change (Incident extends Change via joined-table inheritance).
Not every Change is an Incident.

Change types (ITIL):
  - Standard:   Pre-approved, low-risk, routine
  - Normal:     Requires CAB review and approval
  - Emergency:  Urgent, expedited approval process

Change statuses (ITIL lifecycle):
  DRAFT → SUBMITTED → APPROVED / REJECTED → IN_PROGRESS → COMPLETED / FAILED → CLOSED
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from .base import Base


class ChangeType(str, Enum):
    """ITIL Change type enumeration"""
    STANDARD = "STANDARD"
    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"


class ChangeStatus(str, Enum):
    """ITIL Change lifecycle status"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CLOSED = "CLOSED"


class ChangePriority(str, Enum):
    """Change priority enumeration"""
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class ChangeRisk(str, Enum):
    """Change risk level"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Change(Base):
    """
    ITIL Change record.

    This is the parent entity. Incidents are a specialised subtype of Change
    (joined-table inheritance: ``changes`` + ``incidents`` tables).
    """
    __tablename__ = "changes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Discriminator column — 'change' for plain changes, 'incident' for incidents
    record_type = Column(String(20), nullable=False, default="change")

    # Core fields
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    change_type = Column(SQLEnum(ChangeType), nullable=False, default=ChangeType.NORMAL)
    status = Column(SQLEnum(ChangeStatus), nullable=False, default=ChangeStatus.DRAFT)
    priority = Column(SQLEnum(ChangePriority), nullable=False, default=ChangePriority.P3)
    risk = Column(SQLEnum(ChangeRisk), nullable=False, default=ChangeRisk.MEDIUM)

    # ITIL fields
    justification = Column(Text, nullable=True)          # Reason for the change
    implementation_plan = Column(Text, nullable=True)    # How it will be done
    backout_plan = Column(Text, nullable=True)           # Rollback plan
    test_plan = Column(Text, nullable=True)              # Verification steps

    # Scheduling
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)

    # Ownership
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Property link (optional — changes may affect a property)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    property = relationship("Property", foreign_keys=[property_id])

    # CI associations (affected configuration items)
    affected_cis = relationship(
        "ChangeCI",
        back_populates="change",
        cascade="all, delete-orphan",
    )

    __mapper_args__ = {
        "polymorphic_on": record_type,
        "polymorphic_identity": "change",
    }

    def __repr__(self):
        return (
            f"<Change(id={self.id}, title={self.title!r}, "
            f"type={self.change_type}, status={self.status})>"
        )


class ChangeCI(Base):
    """
    Association table: Change ↔ CI (affected configuration items).
    Part of SACM — tracks which CIs are impacted by a change.
    """
    __tablename__ = "change_ci"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    change_id = Column(UUID(as_uuid=True), ForeignKey("changes.id"), nullable=False)
    ci_id = Column(UUID(as_uuid=True), ForeignKey("ci_hierarchy.id"), nullable=False)
    impact_description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    change = relationship("Change", back_populates="affected_cis")
    ci = relationship("CI")

    def __repr__(self):
        return f"<ChangeCI(change_id={self.change_id}, ci_id={self.ci_id})>"
