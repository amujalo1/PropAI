"""AI routes — deterministic mock implementations.

These routes simulate AI/ML outputs but are deterministic: the same input
produces the same output across calls. That keeps the demo stable while
the real models are not yet trained.

Determinism strategy:
  - Per-property responses seed random.Random with the property UUID, so
    repeated calls for the same property return identical values.
  - Aggregate responses (insights summary, market analysis) compute real
    aggregates from the database (averages, counts, sums) and only seed
    auxiliary fields (sentiment label, trend label) by the input itself.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
import random

from app.db import get_db
from app.models.property import Property, PropertyType, PropertyStatus

router = APIRouter(prefix="/ai", tags=["ai"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

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
    sample_size: int
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rng_for_property(prop: Property) -> random.Random:
    """Deterministic RNG seeded by the property UUID."""
    return random.Random(int(prop.id.int))


def _rng_for_string(s: str) -> random.Random:
    """Deterministic RNG seeded by an arbitrary string."""
    return random.Random(hash(s) & 0xFFFFFFFF)


def _location_score(prop: Property, rng: random.Random) -> float:
    """Stable location score 6.0–9.5 based on the property."""
    return round(6.0 + rng.random() * 3.5, 1)


# ---------------------------------------------------------------------------
# Valuation — deterministic per property
# ---------------------------------------------------------------------------

@router.post("/valuation", response_model=ValuationResponse)
async def get_valuation(
    request: ValuationRequest,
    db: Session = Depends(get_db),
):
    """AI property valuation — deterministic per property_id.

    Estimate is base price adjusted by a per-property variance (±5%)
    derived from the property UUID, so the same property always returns
    the same estimate.
    """
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    rng = _rng_for_property(prop)

    # Type multiplier — commercial typically priced higher per asset
    type_multiplier = {
        PropertyType.RESIDENTIAL: 1.00,
        PropertyType.COMMERCIAL: 1.05,
        PropertyType.LAND: 0.92,
    }.get(prop.type, 1.0)

    base = float(prop.price)
    # Tight ±5% variance for stability
    variance = 0.95 + rng.random() * 0.10
    estimated = round(base * type_multiplier * variance, 2)

    # Confidence rises with active listings, falls for DRAFT/ARCHIVED
    status_confidence = {
        PropertyStatus.ACTIVE: 0.92,
        PropertyStatus.RESERVED: 0.88,
        PropertyStatus.SOLD: 0.85,
        PropertyStatus.RENTED: 0.85,
        PropertyStatus.PENDING_REVIEW: 0.80,
        PropertyStatus.DRAFT: 0.72,
        PropertyStatus.SUSPENDED: 0.70,
        PropertyStatus.ARCHIVED: 0.65,
    }.get(prop.status, 0.80)
    confidence = round(status_confidence + (rng.random() - 0.5) * 0.04, 2)

    # Comparable sales — count of same-type, same-location properties
    comparables = (
        db.query(Property)
        .filter(Property.type == prop.type, Property.location == prop.location, Property.id != prop.id)
        .count()
    )

    demand_pool = ["High", "Medium", "Low"]
    condition_pool = ["Excellent", "Good", "Fair"]

    return ValuationResponse(
        estimated_value=estimated,
        currency="EUR",
        confidence=confidence,
        note="Mock AI valuation (deterministic). Real model coming in Sprint 2.",
        factors={
            "location_score": _location_score(prop, rng),
            "market_demand": rng.choice(demand_pool),
            "property_condition": rng.choice(condition_pool),
            "comparable_sales": f"{comparables} comparable properties in area",
            "type_multiplier": type_multiplier,
        }
    )


# ---------------------------------------------------------------------------
# Market analysis — real aggregates from the database
# ---------------------------------------------------------------------------

@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    request: MarketAnalysisRequest,
    db: Session = Depends(get_db),
):
    """Market analysis — average price computed from real properties in the location."""
    # Try the requested location/type first
    matching = (
        db.query(Property)
        .filter(Property.location.ilike(f"%{request.location}%"))
        .filter(Property.type == request.property_type)
        .all()
    )

    # Fallback to type-only if no match for the specific location
    if not matching:
        matching = db.query(Property).filter(Property.type == request.property_type).all()

    if matching:
        prices = [float(p.price) for p in matching]
        avg_price = sum(prices) / len(prices)
    else:
        avg_price = 0.0

    # avg_price_per_sqm is a derived figure — we don't store sqm yet, so we
    # estimate from a typical sqm for the type. This is stable per type.
    typical_sqm = {
        "residential": 75,
        "commercial": 120,
        "land": 800,
    }.get(request.property_type, 75)
    avg_price_per_sqm = round(avg_price / typical_sqm, 2) if typical_sqm else 0.0

    # Trend & demand — deterministic on (location, type)
    rng = _rng_for_string(f"{request.location}|{request.property_type}")
    trends = ["Bullish", "Stable", "Bearish", "Volatile"]
    demands = ["Very High", "High", "Medium", "Low"]
    trend = trends[rng.randint(0, len(trends) - 1)]
    demand = demands[rng.randint(0, len(demands) - 1)]
    price_change_6m = round(-8.0 + rng.random() * 23.0, 2)

    return MarketAnalysisResponse(
        location=request.location,
        property_type=request.property_type,
        avg_price_per_sqm=avg_price_per_sqm,
        market_trend=trend,
        demand_level=demand,
        price_change_6m=price_change_6m,
        sample_size=len(matching),
        note=(
            f"Computed from {len(matching)} {request.property_type} properties in '{request.location}'. "
            "Trend/demand labels are mock; full model in Sprint 2."
        ),
    )


# ---------------------------------------------------------------------------
# Risk assessment — deterministic per property
# ---------------------------------------------------------------------------

@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db),
):
    """Risk assessment — deterministic per property_id."""
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    rng = _rng_for_property(prop)

    # Base risk by type & status
    base_score = {
        PropertyType.RESIDENTIAL: 30,
        PropertyType.COMMERCIAL: 45,
        PropertyType.LAND: 55,
    }.get(prop.type, 40)

    status_modifier = {
        PropertyStatus.ACTIVE: 0,
        PropertyStatus.RESERVED: -5,
        PropertyStatus.SOLD: -10,
        PropertyStatus.RENTED: -8,
        PropertyStatus.DRAFT: 10,
        PropertyStatus.PENDING_REVIEW: 5,
        PropertyStatus.SUSPENDED: 20,
        PropertyStatus.ARCHIVED: 15,
    }.get(prop.status, 0)

    risk_score = max(5, min(95, base_score + status_modifier + rng.randint(-8, 8)))
    risk_level = "Low" if risk_score < 35 else "Medium" if risk_score < 65 else "High"

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
        factors=rng.sample(all_factors, 3),
        recommendations=rng.sample(all_recs, 2),
        note="Mock risk assessment (deterministic). Real model coming in Sprint 2.",
    )


# ---------------------------------------------------------------------------
# Price prediction — deterministic per (property_id, months_ahead)
# ---------------------------------------------------------------------------

@router.post("/price-prediction", response_model=PricePredictionResponse)
async def get_price_prediction(
    request: PricePredictionRequest,
    db: Session = Depends(get_db),
):
    """Price prediction — deterministic per property_id + months_ahead."""
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    # Seed by both property id and horizon so different horizons differ but
    # same horizon is stable.
    rng = random.Random(int(prop.id.int) ^ request.months_ahead)

    current = float(prop.price)
    # Annualised drift around +4%, scaled to horizon
    annual_drift = -2.0 + rng.random() * 12.0           # -2% .. +10% annual
    horizon_change = annual_drift * (request.months_ahead / 12.0)
    predicted = round(current * (1 + horizon_change / 100), 2)
    trend = "Upward" if horizon_change > 1.5 else "Downward" if horizon_change < -1.5 else "Stable"

    return PricePredictionResponse(
        current_value=current,
        predicted_value=predicted,
        change_percent=round(horizon_change, 2),
        currency="EUR",
        months_ahead=request.months_ahead,
        trend=trend,
        note="Mock price prediction (deterministic). Real ML model coming in Sprint 2.",
    )


# ---------------------------------------------------------------------------
# Portfolio summary — real aggregates
# ---------------------------------------------------------------------------

@router.get("/insights/summary")
async def get_ai_insights(db: Session = Depends(get_db)):
    """Portfolio summary — computed from real data, not random.

    Stable across refreshes: any randomised label is seeded by the
    aggregate state of the portfolio.
    """
    total = db.query(Property).count()
    active = db.query(Property).filter(Property.status == PropertyStatus.ACTIVE).count()

    avg_price = db.query(func.avg(Property.price)).scalar() or 0
    total_value = db.query(func.sum(Property.price)).scalar() or 0

    by_type = (
        db.query(Property.type, func.count(Property.id), func.avg(Property.price))
        .group_by(Property.type)
        .all()
    )
    type_breakdown = {
        str(t.value if hasattr(t, 'value') else t): {
            "count": count,
            "avg_price": round(float(avg or 0), 2),
        }
        for t, count, avg in by_type
    }

    # Pick the type with the highest count as "top performing"
    top_type = max(type_breakdown.items(), key=lambda kv: kv[1]["count"])[0] if type_breakdown else None

    # Stable sentiment seeded by portfolio shape
    rng = _rng_for_string(f"{total}|{active}|{round(float(avg_price), 2)}")
    sentiment = rng.choice(["Positive", "Neutral", "Cautious"])
    avg_change = round(-3.0 + rng.random() * 15.0, 2)

    # Recommendations based on real counts
    recommendations = []
    drafts = db.query(Property).filter(Property.status == PropertyStatus.DRAFT).count()
    if drafts > 0:
        recommendations.append(f"{drafts} property(ies) in DRAFT — finalise to publish")
    if active > 0:
        recommendations.append(f"{active} active listing(s) — monitor market trend")
    if total > 0 and avg_price:
        recommendations.append(f"Portfolio average price: €{round(float(avg_price), 2):,.2f}")
    if not recommendations:
        recommendations.append("No properties yet — seed test data via POST /test/seed")

    return {
        "total_properties_analyzed": total,
        "active_listings": active,
        "portfolio_total_value": round(float(total_value), 2),
        "portfolio_avg_price": round(float(avg_price), 2),
        "type_breakdown": type_breakdown,
        "top_performing_type": top_type,
        "market_sentiment": sentiment,
        "avg_portfolio_value_change": avg_change,
        "ai_recommendations": recommendations,
        "note": "Aggregates are real; sentiment label is mock but stable per portfolio state.",
    }
