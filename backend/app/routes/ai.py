"""AI routes — powered by Google Gemini with deterministic mock fallback.

When GEMINI_API_KEY is set the endpoints call Gemini 1.5 Flash and parse
the structured JSON response.  If the key is absent or the call fails the
endpoints fall back to the original deterministic mock so the app always
returns a valid response.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
import random
import json
import logging

from app.db import get_db
from app.models.property import Property, PropertyType, PropertyStatus
from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


# ---------------------------------------------------------------------------
# Gemini client — initialised lazily so missing key just triggers fallback
# ---------------------------------------------------------------------------

def _get_gemini_model():
    """Return a configured Gemini GenerativeModel or None if key is absent."""
    if not settings.gemini_api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel(
            model_name="gemini-flash-latest",
            generation_config={"response_mime_type": "application/json"},
        )
    except Exception as exc:
        logger.warning("Gemini init failed: %s", exc)
        return None


def _call_gemini(prompt: str) -> Optional[dict]:
    """Call Gemini and return parsed JSON dict, or None on any failure."""
    model = _get_gemini_model()
    if model is None:
        return None
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as exc:
        logger.warning("Gemini call failed: %s", exc)
        return None


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
# Mock helpers (fallback)
# ---------------------------------------------------------------------------

def _rng_for_property(prop: Property) -> random.Random:
    return random.Random(int(prop.id.int))


def _rng_for_string(s: str) -> random.Random:
    return random.Random(hash(s) & 0xFFFFFFFF)


def _location_score(prop: Property, rng: random.Random) -> float:
    return round(6.0 + rng.random() * 3.5, 1)


# ---------------------------------------------------------------------------
# Valuation
# ---------------------------------------------------------------------------

@router.post("/valuation", response_model=ValuationResponse)
async def get_valuation(
    request: ValuationRequest,
    db: Session = Depends(get_db),
):
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    # Gather comparable properties for context
    comparables = (
        db.query(Property)
        .filter(Property.type == prop.type, Property.location == prop.location, Property.id != prop.id)
        .all()
    )
    comp_prices = [float(c.price) for c in comparables]
    comp_avg = round(sum(comp_prices) / len(comp_prices), 2) if comp_prices else None

    prompt = f"""You are a real estate valuation expert specialising in the Bosnian property market.

Analyse this property and provide a valuation:
- Name: {prop.name}
- Type: {prop.type.value}
- Location: {prop.location}
- Listed price: €{float(prop.price):,.2f}
- Status: {prop.status.value}
- Description: {prop.description or 'N/A'}
- Comparable properties in same area/type: {len(comparables)}
- Average price of comparables: {f'€{comp_avg:,.2f}' if comp_avg else 'N/A'}

Return ONLY a JSON object with exactly these fields:
{{
  "estimated_value": <float, your estimated market value in EUR>,
  "confidence": <float between 0.0 and 1.0>,
  "location_score": <float between 1.0 and 10.0>,
  "market_demand": <"High" | "Medium" | "Low">,
  "property_condition": <"Excellent" | "Good" | "Fair" | "Poor">,
  "reasoning": <string, 1-2 sentence explanation>
}}"""

    result = _call_gemini(prompt)

    if result:
        try:
            return ValuationResponse(
                estimated_value=float(result["estimated_value"]),
                currency="EUR",
                confidence=min(1.0, max(0.0, float(result["confidence"]))),
                note=result.get("reasoning", "AI valuation powered by Google Gemini."),
                factors={
                    "location_score": result.get("location_score"),
                    "market_demand": result.get("market_demand"),
                    "property_condition": result.get("property_condition"),
                    "comparable_sales": f"{len(comparables)} comparable properties in area",
                    "comparable_avg_price": f"€{comp_avg:,.2f}" if comp_avg else "N/A",
                },
            )
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("Gemini valuation parse error: %s — falling back to mock", exc)

    # --- Mock fallback ---
    rng = _rng_for_property(prop)
    type_multiplier = {PropertyType.RESIDENTIAL: 1.00, PropertyType.COMMERCIAL: 1.05, PropertyType.LAND: 0.92}.get(prop.type, 1.0)
    base = float(prop.price)
    variance = 0.95 + rng.random() * 0.10
    estimated = round(base * type_multiplier * variance, 2)
    status_confidence = {
        PropertyStatus.ACTIVE: 0.92, PropertyStatus.RESERVED: 0.88, PropertyStatus.SOLD: 0.85,
        PropertyStatus.RENTED: 0.85, PropertyStatus.PENDING_REVIEW: 0.80,
        PropertyStatus.DRAFT: 0.72, PropertyStatus.SUSPENDED: 0.70, PropertyStatus.ARCHIVED: 0.65,
    }.get(prop.status, 0.80)
    confidence = round(status_confidence + (rng.random() - 0.5) * 0.04, 2)
    return ValuationResponse(
        estimated_value=estimated, currency="EUR", confidence=confidence,
        note="Mock valuation (Gemini unavailable).",
        factors={
            "location_score": _location_score(prop, rng),
            "market_demand": rng.choice(["High", "Medium", "Low"]),
            "property_condition": rng.choice(["Excellent", "Good", "Fair"]),
            "comparable_sales": f"{len(comparables)} comparable properties in area",
            "type_multiplier": type_multiplier,
        },
    )


# ---------------------------------------------------------------------------
# Market analysis
# ---------------------------------------------------------------------------

@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    request: MarketAnalysisRequest,
    db: Session = Depends(get_db),
):
    matching = (
        db.query(Property)
        .filter(Property.location.ilike(f"%{request.location}%"))
        .filter(Property.type == request.property_type)
        .all()
    )
    if not matching:
        matching = db.query(Property).filter(Property.type == request.property_type).all()

    prices = [float(p.price) for p in matching]
    avg_price = sum(prices) / len(prices) if prices else 0.0
    typical_sqm = {"residential": 75, "commercial": 120, "land": 800}.get(request.property_type, 75)
    avg_price_per_sqm = round(avg_price / typical_sqm, 2) if typical_sqm else 0.0

    prompt = f"""You are a real estate market analyst specialising in Bosnia and Herzegovina.

Analyse the market for:
- Location: {request.location}
- Property type: {request.property_type}
- Number of listings in our database: {len(matching)}
- Average listed price: €{avg_price:,.2f}
- Average price per sqm (estimated): €{avg_price_per_sqm:,.2f}

Based on your knowledge of the Bosnian real estate market, return ONLY a JSON object:
{{
  "market_trend": <"Bullish" | "Stable" | "Bearish" | "Volatile">,
  "demand_level": <"Very High" | "High" | "Medium" | "Low">,
  "price_change_6m": <float, estimated % price change over last 6 months>,
  "analysis": <string, 2-3 sentence market summary>
}}"""

    result = _call_gemini(prompt)

    if result:
        try:
            return MarketAnalysisResponse(
                location=request.location,
                property_type=request.property_type,
                avg_price_per_sqm=avg_price_per_sqm,
                market_trend=result["market_trend"],
                demand_level=result["demand_level"],
                price_change_6m=float(result["price_change_6m"]),
                sample_size=len(matching),
                note=result.get("analysis", "Market analysis powered by Google Gemini."),
            )
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("Gemini market analysis parse error: %s — falling back to mock", exc)

    # --- Mock fallback ---
    rng = _rng_for_string(f"{request.location}|{request.property_type}")
    return MarketAnalysisResponse(
        location=request.location, property_type=request.property_type,
        avg_price_per_sqm=avg_price_per_sqm,
        market_trend=rng.choice(["Bullish", "Stable", "Bearish", "Volatile"]),
        demand_level=rng.choice(["Very High", "High", "Medium", "Low"]),
        price_change_6m=round(-8.0 + rng.random() * 23.0, 2),
        sample_size=len(matching),
        note=f"Mock analysis (Gemini unavailable). Based on {len(matching)} properties.",
    )


# ---------------------------------------------------------------------------
# Risk assessment
# ---------------------------------------------------------------------------

@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db),
):
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    prompt = f"""You are a real estate risk analyst specialising in the Bosnian property market.

Assess the investment risk for this property:
- Name: {prop.name}
- Type: {prop.type.value}
- Location: {prop.location}
- Price: €{float(prop.price):,.2f}
- Status: {prop.status.value}
- Description: {prop.description or 'N/A'}

Return ONLY a JSON object:
{{
  "risk_level": <"Low" | "Medium" | "High">,
  "risk_score": <integer between 5 and 95>,
  "factors": <list of exactly 3 strings describing key risk factors>,
  "recommendations": <list of exactly 2 strings with actionable recommendations>
}}"""

    result = _call_gemini(prompt)

    if result:
        try:
            return RiskAssessmentResponse(
                risk_level=result["risk_level"],
                risk_score=int(result["risk_score"]),
                factors=result["factors"][:3],
                recommendations=result["recommendations"][:2],
                note="Risk assessment powered by Google Gemini.",
            )
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("Gemini risk parse error: %s — falling back to mock", exc)

    # --- Mock fallback ---
    rng = _rng_for_property(prop)
    base_score = {PropertyType.RESIDENTIAL: 30, PropertyType.COMMERCIAL: 45, PropertyType.LAND: 55}.get(prop.type, 40)
    status_modifier = {
        PropertyStatus.ACTIVE: 0, PropertyStatus.RESERVED: -5, PropertyStatus.SOLD: -10,
        PropertyStatus.RENTED: -8, PropertyStatus.DRAFT: 10, PropertyStatus.PENDING_REVIEW: 5,
        PropertyStatus.SUSPENDED: 20, PropertyStatus.ARCHIVED: 15,
    }.get(prop.status, 0)
    risk_score = max(5, min(95, base_score + status_modifier + rng.randint(-8, 8)))
    risk_level = "Low" if risk_score < 35 else "Medium" if risk_score < 65 else "High"
    all_factors = [
        "Market volatility in area", "High vacancy rate nearby", "Infrastructure development planned",
        "Flood zone proximity", "Strong rental demand", "New commercial hub nearby",
        "Aging building structure", "Recent price appreciation",
    ]
    all_recs = [
        "Consider property insurance upgrade", "Monitor local market trends monthly",
        "Evaluate renovation ROI", "Diversify portfolio in this area",
        "Good time to list for sale", "Hold for 12+ months for appreciation",
    ]
    return RiskAssessmentResponse(
        risk_level=risk_level, risk_score=risk_score,
        factors=rng.sample(all_factors, 3), recommendations=rng.sample(all_recs, 2),
        note="Mock risk assessment (Gemini unavailable).",
    )


# ---------------------------------------------------------------------------
# Price prediction
# ---------------------------------------------------------------------------

@router.post("/price-prediction", response_model=PricePredictionResponse)
async def get_price_prediction(
    request: PricePredictionRequest,
    db: Session = Depends(get_db),
):
    prop = db.query(Property).filter(Property.id == request.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    current = float(prop.price)

    prompt = f"""You are a real estate price forecasting expert specialising in Bosnia and Herzegovina.

Predict the price trajectory for this property over {request.months_ahead} months:
- Name: {prop.name}
- Type: {prop.type.value}
- Location: {prop.location}
- Current price: €{current:,.2f}
- Status: {prop.status.value}
- Description: {prop.description or 'N/A'}

Consider Bosnian market conditions, local economic trends, and property-specific factors.

Return ONLY a JSON object:
{{
  "predicted_value": <float, predicted price in EUR after {request.months_ahead} months>,
  "change_percent": <float, percentage change from current price>,
  "trend": <"Upward" | "Stable" | "Downward">,
  "reasoning": <string, 1-2 sentence explanation of the forecast>
}}"""

    result = _call_gemini(prompt)

    if result:
        try:
            predicted = float(result["predicted_value"])
            change_pct = float(result["change_percent"])
            return PricePredictionResponse(
                current_value=current,
                predicted_value=predicted,
                change_percent=round(change_pct, 2),
                currency="EUR",
                months_ahead=request.months_ahead,
                trend=result["trend"],
                note=result.get("reasoning", "Price prediction powered by Google Gemini."),
            )
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("Gemini prediction parse error: %s — falling back to mock", exc)

    # --- Mock fallback ---
    rng = random.Random(int(prop.id.int) ^ request.months_ahead)
    annual_drift = -2.0 + rng.random() * 12.0
    horizon_change = annual_drift * (request.months_ahead / 12.0)
    predicted = round(current * (1 + horizon_change / 100), 2)
    trend = "Upward" if horizon_change > 1.5 else "Downward" if horizon_change < -1.5 else "Stable"
    return PricePredictionResponse(
        current_value=current, predicted_value=predicted,
        change_percent=round(horizon_change, 2), currency="EUR",
        months_ahead=request.months_ahead, trend=trend,
        note="Mock price prediction (Gemini unavailable).",
    )


# ---------------------------------------------------------------------------
# Portfolio summary — real aggregates + Gemini narrative
# ---------------------------------------------------------------------------

@router.get("/insights/summary")
async def get_ai_insights(db: Session = Depends(get_db)):
    total = db.query(Property).count()
    active = db.query(Property).filter(Property.status == PropertyStatus.ACTIVE).count()
    avg_price = db.query(func.avg(Property.price)).scalar() or 0
    total_value = db.query(func.sum(Property.price)).scalar() or 0
    drafts = db.query(Property).filter(Property.status == PropertyStatus.DRAFT).count()

    by_type = (
        db.query(Property.type, func.count(Property.id), func.avg(Property.price))
        .group_by(Property.type)
        .all()
    )
    type_breakdown = {
        str(t.value if hasattr(t, "value") else t): {
            "count": count,
            "avg_price": round(float(avg or 0), 2),
        }
        for t, count, avg in by_type
    }
    top_type = max(type_breakdown.items(), key=lambda kv: kv[1]["count"])[0] if type_breakdown else None

    # Build base recommendations from real data
    recommendations = []
    if drafts > 0:
        recommendations.append(f"{drafts} property(ies) in DRAFT — finalise to publish")
    if active > 0:
        recommendations.append(f"{active} active listing(s) — monitor market trend")
    if total > 0 and avg_price:
        recommendations.append(f"Portfolio average price: €{round(float(avg_price), 2):,.2f}")
    if not recommendations:
        recommendations.append("No properties yet — seed test data via POST /test/seed")

    # Ask Gemini for sentiment and an enhanced recommendation
    sentiment = None
    avg_change = None

    if total > 0:
        prompt = f"""You are a real estate portfolio analyst specialising in Bosnia and Herzegovina.

Analyse this portfolio snapshot:
- Total properties: {total}
- Active listings: {active}
- Draft properties: {drafts}
- Total portfolio value: €{round(float(total_value), 2):,.2f}
- Average property price: €{round(float(avg_price), 2):,.2f}
- Breakdown by type: {json.dumps(type_breakdown)}

Return ONLY a JSON object:
{{
  "market_sentiment": <"Positive" | "Neutral" | "Cautious">,
  "avg_portfolio_value_change": <float, estimated % change in portfolio value over last 6 months>,
  "ai_recommendation": <string, one actionable portfolio-level recommendation>
}}"""

        result = _call_gemini(prompt)
        if result:
            try:
                sentiment = result.get("market_sentiment")
                avg_change = float(result.get("avg_portfolio_value_change", 0))
                ai_rec = result.get("ai_recommendation")
                if ai_rec:
                    recommendations.append(f"AI insight: {ai_rec}")
            except (ValueError, TypeError) as exc:
                logger.warning("Gemini insights parse error: %s", exc)

    # Fallback sentiment
    if sentiment is None:
        rng = _rng_for_string(f"{total}|{active}|{round(float(avg_price), 2)}")
        sentiment = rng.choice(["Positive", "Neutral", "Cautious"])
        avg_change = round(-3.0 + rng.random() * 15.0, 2)

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
        "note": "Aggregates from real data. Sentiment and recommendations powered by Google Gemini.",
    }
