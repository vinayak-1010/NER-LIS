"""ML API — disruption prediction inference endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import DisruptionPredictRequest, DisruptionPredictResponse
from app.services.ml_service import predict_disruption

router = APIRouter()


@router.post("/predict-disruption", response_model=DisruptionPredictResponse)
def disruption_prediction(
    payload: DisruptionPredictRequest,
    db: Session = Depends(get_db),
):
    """
    Predict the probability of road disruption for a given segment and conditions.
    Returns probability (0–1), confidence, risk level, and top contributing factors.
    """
    return predict_disruption(payload, db)
