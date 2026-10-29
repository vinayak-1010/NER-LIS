"""
ML Service — wraps the trained disruption prediction model for inference.
Falls back to a rule-based heuristic when no model file is present.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.schemas import DisruptionPredictRequest, DisruptionPredictResponse


def _risk_level(prob: float) -> str:
    if prob < 0.25:
        return "low"
    elif prob < 0.50:
        return "medium"
    elif prob < 0.75:
        return "high"
    return "critical"


def _heuristic_predict(payload: DisruptionPredictRequest) -> tuple[float, float, list[str]]:
    """
    Rule-based fallback when trained model is unavailable.
    Returns (probability, confidence, top_factors).
    """
    score = 0.0
    factors = []

    if payload.rainfall_mm > 100:
        score += 0.35
        factors.append("high_rainfall")
    elif payload.rainfall_mm > 50:
        score += 0.15
        factors.append("moderate_rainfall")

    if payload.slope_pct > 30:
        score += 0.25
        factors.append("steep_slope")
    elif payload.slope_pct > 15:
        score += 0.10
        factors.append("moderate_slope")

    if payload.historical_incident_count > 5:
        score += 0.20
        factors.append("historical_incidents")
    elif payload.historical_incident_count > 2:
        score += 0.10
        factors.append("past_incidents")

    if payload.elevation_m > 1500:
        score += 0.10
        factors.append("high_elevation")

    # Monsoon season (June–September)
    if payload.month in (6, 7, 8, 9):
        score += 0.10
        factors.append("monsoon_season")

    prob = min(score, 1.0)
    confidence = 0.60  # fixed heuristic confidence
    return prob, confidence, factors[:3]


def predict_disruption(
    payload: DisruptionPredictRequest,
    db: Session,
) -> DisruptionPredictResponse:
    """
    Attempt to load the trained XGBoost model; fall back to heuristic.
    """
    import os
    import numpy as np

    model_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "disruption_model.pkl")

    try:
        import joblib
        model = joblib.load(model_path)
        features = np.array([[
            payload.rainfall_mm,
            payload.elevation_m,
            payload.slope_pct,
            payload.historical_incident_count,
            payload.traffic_volume,
            payload.month,
        ]])
        prob = float(model.predict_proba(features)[0][1])
        confidence = 0.85
        top_factors = ["rainfall_mm", "slope_pct", "historical_incident_count"]

    except (FileNotFoundError, Exception):
        prob, confidence, top_factors = _heuristic_predict(payload)

    return DisruptionPredictResponse(
        road_segment_id=payload.road_segment_id,
        disruption_probability=round(prob, 4),
        confidence=round(confidence, 4),
        risk_level=_risk_level(prob),
        top_factors=top_factors,
    )
