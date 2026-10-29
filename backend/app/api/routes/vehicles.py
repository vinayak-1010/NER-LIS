"""Vehicles API — tracking and GPS position updates."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Vehicle
from app.schemas.schemas import VehicleOut, VehiclePositionUpdate

router = APIRouter()


@router.get("/", response_model=List[VehicleOut])
def list_vehicles(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Vehicle)
    if active_only:
        q = q.filter(Vehicle.is_active == True)
    return q.all()


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: UUID, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return v


@router.post("/{vehicle_id}/position", response_model=VehicleOut)
def update_vehicle_position(
    vehicle_id: UUID,
    payload: VehiclePositionUpdate,
    db: Session = Depends(get_db),
):
    """Receive GPS position update from vehicle tracker or GPS sim script."""
    from datetime import datetime, timezone

    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    v.last_lat = payload.latitude
    v.last_lng = payload.longitude
    v.last_seen = datetime.now(timezone.utc)
    if payload.road_segment_id:
        v.current_road_segment_id = payload.road_segment_id

    db.commit()
    db.refresh(v)
    return v


@router.get("/positions/geojson")
def vehicles_geojson(db: Session = Depends(get_db)):
    """Live vehicle positions as GeoJSON FeatureCollection."""
    vehicles = db.query(Vehicle).filter(
        Vehicle.is_active == True,
        Vehicle.last_lat.isnot(None),
    ).all()

    features = []
    for v in vehicles:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [v.last_lng, v.last_lat]},
            "properties": {
                "id": str(v.id),
                "registration": v.registration,
                "vehicle_type": v.vehicle_type,
                "last_seen": v.last_seen.isoformat() if v.last_seen else None,
            },
        })
    return {"type": "FeatureCollection", "features": features}
