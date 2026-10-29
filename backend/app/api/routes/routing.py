"""
Routing API — risk-aware route calculation.
Delegates to the routing engine in routing/src.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import RouteRequest, RouteResponse
from app.services.routing_service import compute_route

router = APIRouter()


@router.post("/route", response_model=RouteResponse)
def calculate_route(payload: RouteRequest, db: Session = Depends(get_db)):
    """
    Compute a risk-aware route between two points.
    Modes: fastest | safest | balanced | emergency
    """
    result = compute_route(
        db=db,
        origin_lat=payload.origin_lat,
        origin_lng=payload.origin_lng,
        destination_lat=payload.destination_lat,
        destination_lng=payload.destination_lng,
        mode=payload.mode,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="No route found between the given points")
    return result
