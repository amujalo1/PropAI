"""CI (Configuration Item) model — ITIL SACM

Service Asset & Configuration Management (SACM) maintains the CMDB.
CIs represent any component that needs to be managed to deliver an IT service.

Hierarchy levels:
  1 = Location
  2 = Complex
  3 = Building
  4 = Property
  5 = Component

A CI can be linked to a Property (when type == Property) and can be
associated with Changes via the ChangeCI association table.
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from .base import Base


class CIType(str, Enum):
    """CI type enumeration for hierarchy levels"""
    LOCATION = "Location"
    COMPLEX = "Complex"
    BUILDING = "Building"
    PROPERTY = "Property"
    COMPONENT = "Component"


class CIStatus(str, Enum):
    """Operational status of the CI"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    RETIRED = "RETIRED"
    PLANNED = "PLANNED"


class CI(Base):
    """
    Configuration Item — node in the CMDB hierarchy.

    Supports self-referential parent/child relationships for the
    Location → Complex → Building → Property → Component hierarchy.
    """
    __tablename__ = "ci_hierarchy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ci_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)          # Human-readable name
    type = Column(SQLEnum(CIType), nullable=False)
    status = Column(SQLEnum(CIStatus), nullable=False, default=CIStatus.ACTIVE)
    region = Column(String(50), nullable=False)
    sequence = Column(Integer, nullable=False)
    hierarchy_level = Column(Integer, nullable=False)

    # SACM attributes
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    version = Column(String(50), nullable=True)        # Asset version / firmware
    serial_number = Column(String(100), nullable=True)
    location_detail = Column(String(255), nullable=True)  # Physical location detail

    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("ci_hierarchy.id"), nullable=True)

    # Optional link to a Property record (when CI type == Property)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    property = relationship("Property", foreign_keys=[property_id])
    children = relationship("CI", back_populates="parent", foreign_keys=[parent_id])
    parent = relationship("CI", back_populates="children", remote_side=[id], foreign_keys=[parent_id])

    def __repr__(self):
        return (
            f"<CI(ci_id={self.ci_id!r}, type={self.type}, "
            f"level={self.hierarchy_level}, status={self.status})>"
        )
