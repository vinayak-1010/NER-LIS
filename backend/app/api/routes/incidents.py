"""Incidents API — report, list, and verify road incidents."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Incident
from app.schemas.schemas import IncidentCreate, IncidentOut

router = APIRouter()


@router.get("/", response_model=List[IncidentOut])
def list_incidents(
    unresolved_only: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Incident)
    if unresolved_only:
        q = q.filter(Incident.resolved_at == None)
    return q.order_by(Incident.reported_at.desc()).all()


@router.post("/report", response_model=IncidentOut, status_code=201)
def report_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
):
    """Submit a new incident report (from field app or dashboard)."""
    from geoalchemy2.elements import WKTElement

    point_wkt = f"POINT({payload.longitude} {payload.latitude})"
    incident = Incident(
        incident_type=payload.incident_type,
        severity=payload.severity,
        description=payload.description,
        road_segment_id=payload.road_segment_id,
        location=WKTElement(point_wkt, srid=4326),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/{incident_id}/verify", response_model=IncidentOut)
def verify_incident(incident_id: UUID, db: Session = Depends(get_db)):
    """Mark an incident as verified by a field officer or operator."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.is_verified = True
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/geojson")
def incidents_geojson(db: Session = Depends(get_db)):
    """GeoJSON FeatureCollection of all active incidents for map overlay."""
    from geoalchemy2.shape import to_shape
    from shapely.geometry import mapping

    incidents = db.query(Incident).filter(Incident.resolved_at == None).all()
    features = []
    for inc in incidents:
        if inc.location is None:
            continue
        geom = to_shape(inc.location)
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "id": str(inc.id),
                "type": inc.incident_type.value,
                "severity": inc.severity.value,
                "description": inc.description,
                "is_verified": inc.is_verified,
                "reported_at": inc.reported_at.isoformat() if inc.reported_at else None,
            },
        })
    return {"type": "FeatureCollection", "features": features}
