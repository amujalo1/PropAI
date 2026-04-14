"""AI routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from app.db import get_db
from app.models.property import Property
import random


router = APIRouter(prefix="/ai", tags=["ai"])


class ValuationRequest(BaseModel):
    """Valuation request schema"""
    property_id: UUID


class ValuationResponse(BaseModel):
    """Valuation response schema"""
    estimated_value: float
    currency: str
    note: str


@router.post("/valuation", response_model=ValuationResponse)
async def get_valuation(
    request: ValuationRequest,
    db: Session = Depends(get_db),
):
    """Get property valuation (mock implementation)"""
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == request.property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    # Generate mock valuation
    base_value = float(property_obj.price)
    variance = random.uniform(0.8, 1.2)
    estimated_value = base_value * variance

    return ValuationResponse(
        estimated_value=round(estimated_value, 2),
        currency="EUR",
        note="This is a mock AI valuation for MVP demonstration purposes only",
    )
