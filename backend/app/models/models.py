"""
SQLAlchemy ORM models for all NER-LIS core entities.
All spatial columns use GeoAlchemy2 Geometry types (SRID 4326 = WGS84).
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, Enum, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class RoadStatus(str, PyEnum):
    OPEN = "open"
    RISKY = "risky"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class IncidentType(str, PyEnum):
    LANDSLIDE = "landslide"
    FLOOD = "flood"
    ROAD_DAMAGE = "road_damage"
    BRIDGE_DAMAGE = "bridge_damage"
    FALLEN_TREE = "fallen_tree"
    OTHER = "other"


class IncidentSeverity(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ShipmentPriority(str, PyEnum):
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ShipmentStatus(str, PyEnum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    DELIVERED = "delivered"
    AT_RISK = "at_risk"


class RouteMode(str, PyEnum):
    FASTEST = "fastest"
    SAFEST = "safest"
    BALANCED = "balanced"
    EMERGENCY = "emergency"


class AlertType(str, PyEnum):
    ROAD_BLOCKED = "road_blocked"
    HIGH_RISK_CORRIDOR = "high_risk_corridor"
    PREDICTED_DISRUPTION = "predicted_disruption"
    DELIVERY_DELAY = "delivery_delay"
    EMERGENCY = "emergency"


class UserRole(str, PyEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    FIELD_OFFICER = "field_officer"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.OPERATOR, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    incidents = relationship("Incident", back_populates="reported_by_user")


class RoadSegment(Base):
    """
    A single road segment in the pilot corridor network.
    geometry: LineString in WGS84 (SRID=4326)
    """
    __tablename__ = "road_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    highway_type = Column(String(50))           # primary, secondary, track…
    status = Column(Enum(RoadStatus), default=RoadStatus.UNKNOWN, nullable=False)
    length_km = Column(Float)
    elevation_avg_m = Column(Float)
    slope_pct = Column(Float)
    risk_score = Column(Float, default=0.0)     # 0.0 – 1.0
    disruption_prob = Column(Float, default=0.0)# ML-predicted probability
    is_pilot_corridor = Column(Boolean, default=False)

    geometry = Column(Geometry("LINESTRING", srid=4326), nullable=False)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    incidents = relationship("Incident", back_populates="road_segment")


class Incident(Base):
    """A reported or detected incident on a road segment."""
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_segment_id = Column(UUID(as_uuid=True), ForeignKey("road_segments.id"), nullable=True)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    incident_type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Enum(IncidentSeverity), nullable=False)
    description = Column(Text)
    photo_url = Column(String(512))
    is_verified = Column(Boolean, default=False)

    location = Column(Geometry("POINT", srid=4326), nullable=False)
    reported_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    road_segment = relationship("RoadSegment", back_populates="incidents")
    reported_by_user = relationship("User", back_populates="incidents")


class Vehicle(Base):
    """A tracked vehicle operating in the NER corridor."""
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(String(50))           # truck, van, motorcycle…
    is_active = Column(Boolean, default=True)

    last_lat = Column(Float)
    last_lng = Column(Float)
    last_seen = Column(DateTime)
    current_road_segment_id = Column(UUID(as_uuid=True), ForeignKey("road_segments.id"), nullable=True)

    shipments = relationship("Shipment", back_populates="vehicle")


class Shipment(Base):
    """A delivery assignment with priority and status tracking."""
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)

    description = Column(String(255))
    cargo_type = Column(String(100))            # medicines, food, fuel…
    priority = Column(Enum(ShipmentPriority), default=ShipmentPriority.NORMAL, nullable=False)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PENDING, nullable=False)

    origin_location = Column(Geometry("POINT", srid=4326))
    destination_location = Column(Geometry("POINT", srid=4326))
    origin_name = Column(String(255))
    destination_name = Column(String(255))

    expected_delivery = Column(DateTime)
    estimated_delay_hours = Column(Float, default=0.0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    vehicle = relationship("Vehicle", back_populates="shipments")
    alerts = relationship("Alert", back_populates="shipment")


class Alert(Base):
    """System-generated alert for a road event or shipment risk."""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    is_resolved = Column(Boolean, default=False)

    road_segment_id = Column(UUID(as_uuid=True), ForeignKey("road_segments.id"), nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    shipment = relationship("Shipment", back_populates="alerts")
