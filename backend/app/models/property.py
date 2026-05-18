"""Property model"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from .base import Base


class PropertyType(str, Enum):
    """Property type enumeration"""
    RESIDENTIAL = "RESIDENTIAL"
    COMMERCIAL = "COMMERCIAL"
    LAND = "LAND"


class PropertyStatus(str, Enum):
    """Property lifecycle status enumeration"""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    ACTIVE = "ACTIVE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    RENTED = "RENTED"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class Property(Base):
    """Property model for real estate assets"""
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    type = Column(SQLEnum(PropertyType), nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(SQLEnum(PropertyStatus), nullable=False, default=PropertyStatus.DRAFT)
    price = Column(Numeric(15, 2), nullable=False)
    description = Column(String(1000), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id])

    def __repr__(self):
        return f"<Property(id={self.id}, name={self.name}, status={self.status})>"
