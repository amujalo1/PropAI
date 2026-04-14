"""CI (Configuration Item) model for CMDB hierarchy"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
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


class CI(Base):
    """Configuration Item model for hierarchical CMDB structure"""
    __tablename__ = "ci_hierarchy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ci_id = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(SQLEnum(CIType), nullable=False)
    region = Column(String(50), nullable=False)
    sequence = Column(Integer, nullable=False)
    hierarchy_level = Column(Integer, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("ci_hierarchy.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CI(ci_id={self.ci_id}, type={self.type}, level={self.hierarchy_level})>"
