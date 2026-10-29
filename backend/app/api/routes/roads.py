"""Roads API — road segment CRUD and GeoJSON export."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import RoadSegment
from app.schemas.schemas import RoadSegmentOut, RoadSegmentUpdate

router = APIRouter()


@router.get("/", response_model=List[RoadSegmentOut])
def list_road_segments(
    pilot_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all road segments. Optionally filter to pilot corridor only."""
    q = db.query(RoadSegment)
    if pilot_only:
        q = q.filter(RoadSegment.is_pilot_corridor == True)
    return q.all()


@router.get("/geojson")
def road_segments_geojson(
    pilot_only: bool = True,
    db: Session = Depends(get_db),
):
    """Return road segments as a GeoJSON FeatureCollection for map rendering."""
    from geoalchemy2.shape import to_shape
    from shapely.geometry import mapping

    q = db.query(RoadSegment)
    if pilot_only:
        q = q.filter(RoadSegment.is_pilot_corridor == True)
    segments = q.all()

    features = []
    for seg in segments:
        if seg.geometry is None:
            continue
        geom = to_shape(seg.geometry)
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "id": str(seg.id),
                "name": seg.name,
                "status": seg.status.value if seg.status else "unknown",
                "risk_score": seg.risk_score,
                "disruption_prob": seg.disruption_prob,
                "highway_type": seg.highway_type,
                "length_km": seg.length_km,
            },
        })

    return {"type": "FeatureCollection", "features": features}


@router.get("/{segment_id}", response_model=RoadSegmentOut)
def get_road_segment(segment_id: UUID, db: Session = Depends(get_db)):
    seg = db.query(RoadSegment).filter(RoadSegment.id == segment_id).first()
    if not seg:
        raise HTTPException(status_code=404, detail="Road segment not found")
    return seg


@router.patch("/{segment_id}", response_model=RoadSegmentOut)
def update_road_segment(
    segment_id: UUID,
    payload: RoadSegmentUpdate,
    db: Session = Depends(get_db),
):
    seg = db.query(RoadSegment).filter(RoadSegment.id == segment_id).first()
    if not seg:
        raise HTTPException(status_code=404, detail="Road segment not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(seg, field, value)
    db.commit()
    db.refresh(seg)
    return seg
