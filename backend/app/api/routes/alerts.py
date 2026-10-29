"""Alerts API — generate and retrieve system alerts."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Alert
from app.schemas.schemas import AlertOut

router = APIRouter()


@router.get("/", response_model=List[AlertOut])
def list_alerts(unresolved_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Alert)
    if unresolved_only:
        q = q.filter(Alert.is_resolved == False)
    return q.order_by(Alert.created_at.desc()).all()


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: UUID, db: Session = Depends(get_db)):
    from datetime import datetime, timezone
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    a.is_resolved = True
    a.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(a)
    return a
