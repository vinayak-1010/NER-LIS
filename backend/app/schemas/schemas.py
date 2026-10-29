"""
Pydantic schemas for request/response serialization.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.models import (
    AlertType, IncidentSeverity, IncidentType,
    RoadStatus, RouteMode, ShipmentPriority, ShipmentStatus, UserRole,
)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.OPERATOR


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Road Segments
# ---------------------------------------------------------------------------

class RoadSegmentOut(BaseModel):
    id: UUID
    name: Optional[str]
    highway_type: Optional[str]
    status: RoadStatus
    length_km: Optional[float]
    risk_score: float
    disruption_prob: float
    is_pilot_corridor: bool
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class RoadSegmentUpdate(BaseModel):
    status: Optional[RoadStatus] = None
    risk_score: Optional[float] = None
    disruption_prob: Optional[float] = None


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

class IncidentCreate(BaseModel):
    incident_type: IncidentType
    severity: IncidentSeverity
    description: Optional[str] = None
    latitude: float
    longitude: float
    road_segment_id: Optional[UUID] = None


class IncidentOut(BaseModel):
    id: UUID
    incident_type: IncidentType
    severity: IncidentSeverity
    description: Optional[str]
    photo_url: Optional[str]
    is_verified: bool
    reported_at: datetime
    resolved_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

class VehicleOut(BaseModel):
    id: UUID
    registration: str
    vehicle_type: Optional[str]
    is_active: bool
    last_lat: Optional[float]
    last_lng: Optional[float]
    last_seen: Optional[datetime]

    model_config = {"from_attributes": True}


class VehiclePositionUpdate(BaseModel):
    latitude: float
    longitude: float
    road_segment_id: Optional[UUID] = None


# ---------------------------------------------------------------------------
# Shipments
# ---------------------------------------------------------------------------

class ShipmentCreate(BaseModel):
    vehicle_id: Optional[UUID] = None
    description: Optional[str] = None
    cargo_type: str
    priority: ShipmentPriority = ShipmentPriority.NORMAL
    origin_lat: float
    origin_lng: float
    origin_name: str
    destination_lat: float
    destination_lng: float
    destination_name: str
    expected_delivery: Optional[datetime] = None


class ShipmentOut(BaseModel):
    id: UUID
    cargo_type: str
    priority: ShipmentPriority
    status: ShipmentStatus
    origin_name: str
    destination_name: str
    estimated_delay_hours: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

class RouteRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    mode: RouteMode = RouteMode.BALANCED


class RouteSegmentOut(BaseModel):
    road_segment_id: UUID
    name: Optional[str]
    status: RoadStatus
    risk_score: float
    length_km: Optional[float]


class RouteResponse(BaseModel):
    mode: RouteMode
    total_distance_km: float
    estimated_time_min: float
    overall_risk_score: float
    segments: List[RouteSegmentOut]
    geometry: Optional[dict] = None     # GeoJSON LineString


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

class AlertOut(BaseModel):
    id: UUID
    alert_type: AlertType
    title: str
    message: Optional[str]
    severity: IncidentSeverity
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ML
# ---------------------------------------------------------------------------

class DisruptionPredictRequest(BaseModel):
    road_segment_id: Optional[UUID] = None
    rainfall_mm: float = 0.0
    elevation_m: float = 0.0
    slope_pct: float = 0.0
    historical_incident_count: int = 0
    traffic_volume: float = 0.0
    month: int = 1


class DisruptionPredictResponse(BaseModel):
    road_segment_id: Optional[UUID]
    disruption_probability: float
    confidence: float
    risk_level: str          # low / medium / high / critical
    top_factors: List[str]
