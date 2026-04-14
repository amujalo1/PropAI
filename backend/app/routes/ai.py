"""AI routes - mock implementations"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from app.db import get_db
from app.models.property import Property
import random

router = APIRouter(prefix="/ai", tags=["ai"])


class ValuationRequest(BaseModel):
    property_id: UUID


class ValuationResponse(BaseModel):
    estimated_value: float
    currency: str
    confidence: float
    note: str
    factors: dict


class MarketAnalysisRequest(BaseModel):
    location: str
    property_type: str


class MarketAnalysisResponse(BaseModel):
    location: str
    property_type: str
    avg_price_per_sqm: float
    market_trend: str
    demand_level: str
    price_change_6m: float
    note: str


class RiskAssessmentRequest(BaseModel):
    property_id: UUID


class RiskAssessmentResponse(BaseModel):
    risk_level: str
    risk_score: int
    factors: list
    recommendations: list
    note: str


class PricePredictionRequest(BaseModel):
    property_id: UUID
    months_ahead: int = 6


class PricePredictionResponse(BaseModel):
    current_value: float
    predicted_value: float
    change_percent: float
    currency: str
    months_ahead: int
    trend: str
    note: str


class SimilarPropertiesRequest(BaseModel):
    property_id: UUID
    limit: int = 5


@router.post("/valuation", response_model=ValuationResponse)
async def get_valuation(
    request: ValuationRequest,
    db: Session = Depends(get_db),
):
    """Get AI property valuation (mock)"""
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    base = float(prop.price)
    variance = random.uniform(0.88, 1.12)
    estimated = round(base * variance, 2)
    confidence = round(random.uniform(0.72, 0.95), 2)

    return ValuationResponse(
        estimated_value=estimated,
        currency="EUR",
        confidence=confidence,
        note="Mock AI valuation. Real model coming in Sprint 2.",
        factors={
            "location_score": round(random.uniform(6.0, 9.5), 1),
            "market_demand": random.choice(["High", "Medium", "Low"]),
            "property_condition": random.choice(["Excellent", "Good", "Fair"]),
            "comparable_sales": f"{random.randint(3, 12)} recent sales in area",
        }
    )


@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(request: MarketAnalysisRequest):
    """Get market analysis for a location (mock)"""
    trends = ["Bullish", "Bearish", "Stable", "Volatile"]
    demands = ["Very High", "High", "Medium", "Low"]

    return MarketAnalysisResponse(
        location=request.location,
        property_type=request.property_type,
        avg_price_per_sqm=round(random.uniform(1200, 4500), 2),
        market_trend=random.choice(trends),
        demand_level=random.choice(demands),
        price_change_6m=round(random.uniform(-8.5, 15.2), 2),
        note="Mock market analysis. Real data integration coming in Sprint 2.",
    )


@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db),
):
    """Get risk assessment for a property (mock)"""
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    risk_score = random.randint(15, 85)
    risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 60 else "High"

    all_factors = [
        "Market volatility in area",
        "High vacancy rate nearby",
        "Infrastructure development planned",
        "Flood zone proximity",
        "Strong rental demand",
        "New commercial hub nearby",
        "Aging building structure",
        "Recent price appreciation",
    ]

    all_recs = [
        "Consider property insurance upgrade",
        "Monitor local market trends monthly",
        "Evaluate renovation ROI",
        "Diversify portfolio in this area",
        "Good time to list for sale",
        "Hold for 12+ months for appreciation",
    ]

    return RiskAssessmentResponse(
        risk_level=risk_level,
        risk_score=risk_score,
        factors=random.sample(all_factors, 3),
        recommendations=random.sample(all_recs, 2),
        note="Mock risk assessment. Real model coming in Sprint 2.",
    )


@router.post("/price-prediction", response_model=PricePredictionResponse)
async def get_price_prediction(
    request: PricePredictionRequest,
    db: Session = Depends(get_db),
):
    """Get price prediction for a property (mock)"""
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    current = float(prop.price)
    change = random.uniform(-5.0, 18.0)
    predicted = round(current * (1 + change / 100), 2)
    trend = "Upward" if change > 2 else "Downward" if change < -2 else "Stable"

    return PricePredictionResponse(
        current_value=current,
        predicted_value=predicted,
        change_percent=round(change, 2),
        currency="EUR",
        months_ahead=request.months_ahead,
        trend=trend,
        note="Mock price prediction. Real ML model coming in Sprint 2.",
    )


@router.get("/insights/summary")
async def get_ai_insights(db: Session = Depends(get_db)):
    """Get overall AI insights summary (mock)"""
    total = db.query(Property).count()

    return {
        "total_properties_analyzed": total,
        "market_sentiment": random.choice(["Positive", "Neutral", "Cautious"]),
        "avg_portfolio_value_change": round(random.uniform(-3.0, 12.0), 2),
        "top_performing_type": random.choice(["residential", "commercial", "land"]),
        "ai_recommendations": [
            "3 properties are undervalued based on market data",
            "Consider listing 2 properties - market conditions favorable",
            "High demand detected in downtown area",
        ],
        "note": "Mock AI insights. Real analytics coming in Sprint 2.",
    }
