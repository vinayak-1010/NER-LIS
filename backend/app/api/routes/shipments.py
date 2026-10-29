"""Shipments API — create and track priority shipments."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Shipment, ShipmentStatus
from app.schemas.schemas import ShipmentCreate, ShipmentOut

router = APIRouter()


@router.get("/", response_model=List[ShipmentOut])
def list_shipments(
    status: ShipmentStatus = None,
    priority_only: bool = False,
    db: Session = Depends(get_db),
):
    from app.models.models import ShipmentPriority
    q = db.query(Shipment)
    if status:
        q = q.filter(Shipment.status == status)
    if priority_only:
        q = q.filter(Shipment.priority.in_([ShipmentPriority.HIGH, ShipmentPriority.CRITICAL]))
    return q.order_by(Shipment.created_at.desc()).all()


@router.post("/", response_model=ShipmentOut, status_code=201)
def create_shipment(payload: ShipmentCreate, db: Session = Depends(get_db)):
    from geoalchemy2.elements import WKTElement

    shipment = Shipment(
        vehicle_id=payload.vehicle_id,
        description=payload.description,
        cargo_type=payload.cargo_type,
        priority=payload.priority,
        origin_location=WKTElement(f"POINT({payload.origin_lng} {payload.origin_lat})", srid=4326),
        destination_location=WKTElement(f"POINT({payload.destination_lng} {payload.destination_lat})", srid=4326),
        origin_name=payload.origin_name,
        destination_name=payload.destination_name,
        expected_delivery=payload.expected_delivery,
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.get("/{shipment_id}", response_model=ShipmentOut)
def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)):
    s = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return s


@router.patch("/{shipment_id}/status", response_model=ShipmentOut)
def update_shipment_status(
    shipment_id: UUID,
    new_status: ShipmentStatus,
    db: Session = Depends(get_db),
):
    s = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")
    s.status = new_status
    db.commit()
    db.refresh(s)
    return s
