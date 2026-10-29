"""
scripts/seed.py — Seeds the database with pilot corridor data.

Pilot Corridor: Guwahati → Shillong (NH6 / NH40 via Jorabat)
Run: python scripts/seed.py
"""

import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

# Allow importing from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import SessionLocal
from app.models.models import (
    RoadSegment, RoadStatus, Incident, IncidentType, IncidentSeverity,
    Vehicle, Shipment, ShipmentPriority, ShipmentStatus, Alert, AlertType, User, UserRole
)
from geoalchemy2.elements import WKTElement
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Pilot corridor road segments (simplified Guwahati–Shillong corridor)
# Each segment is a LineString in WGS84
# ---------------------------------------------------------------------------
ROAD_SEGMENTS = [
    {
        "name": "Guwahati City Stretch",
        "highway_type": "primary",
        "status": RoadStatus.OPEN,
        "length_km": 8.5,
        "elevation_avg_m": 55,
        "slope_pct": 1.2,
        "risk_score": 0.05,
        "disruption_prob": 0.04,
        "is_pilot_corridor": True,
        # WKT: LINESTRING(lng lat, lng lat, ...)
        "geom": "LINESTRING(91.7362 26.1445, 91.7500 26.1380, 91.7750 26.1290, 91.7990 26.1200)",
    },
    {
        "name": "Jorabat Junction",
        "highway_type": "primary",
        "status": RoadStatus.RISKY,
        "length_km": 5.2,
        "elevation_avg_m": 120,
        "slope_pct": 8.5,
        "risk_score": 0.45,
        "disruption_prob": 0.38,
        "is_pilot_corridor": True,
        "geom": "LINESTRING(91.7990 26.1200, 91.8200 26.0950, 91.8400 26.0700)",
    },
    {
        "name": "Barapani Ghat Section",
        "highway_type": "primary",
        "status": RoadStatus.RISKY,
        "length_km": 12.3,
        "elevation_avg_m": 650,
        "slope_pct": 18.7,
        "risk_score": 0.68,
        "disruption_prob": 0.62,
        "is_pilot_corridor": True,
        "geom": "LINESTRING(91.8400 26.0700, 91.8620 26.0400, 91.8890 26.0100, 91.9050 25.9800)",
    },
    {
        "name": "Nongpoh Town Stretch",
        "highway_type": "primary",
        "status": RoadStatus.OPEN,
        "length_km": 6.8,
        "elevation_avg_m": 800,
        "slope_pct": 5.5,
        "risk_score": 0.20,
        "disruption_prob": 0.15,
        "is_pilot_corridor": True,
        "geom": "LINESTRING(91.9050 25.9800, 91.9200 25.9600, 91.9380 25.9350)",
    },
    {
        "name": "Umiam Lake Approach",
        "highway_type": "primary",
        "status": RoadStatus.OPEN,
        "length_km": 9.1,
        "elevation_avg_m": 950,
        "slope_pct": 4.0,
        "risk_score": 0.15,
        "disruption_prob": 0.12,
        "is_pilot_corridor": True,
        "geom": "LINESTRING(91.9380 25.9350, 91.9500 25.9100, 91.9620 25.8900)",
    },
    {
        "name": "Shillong Bypass — Blocked Section",
        "highway_type": "secondary",
        "status": RoadStatus.BLOCKED,
        "length_km": 3.4,
        "elevation_avg_m": 1400,
        "slope_pct": 22.0,
        "risk_score": 0.92,
        "disruption_prob": 0.90,
        "is_pilot_corridor": True,
        "geom": "LINESTRING(91.9620 25.8900, 91.9700 25.8750, 91.9780 25.8620)",
    },
    {
        "name": "Shillong City — Laitumkhrah",
        "highway_type": "primary",
        "status": RoadStatus.OPEN,
        "length_km": 4.2,
        "elevation_avg_m": 1496,
        "slope_pct": 3.0,
        "risk_score": 0.08,
        "disruption_prob": 0.06,
        "is_pilot_corridor": True,
        "geom": "LINESTRING(91.9780 25.8620, 91.9820 25.8500, 91.9880 25.5780)",
    },
]

VEHICLES = [
    {"registration": "AS01A1001", "vehicle_type": "truck", "last_lat": 26.1445, "last_lng": 91.7362},
    {"registration": "AS01A1002", "vehicle_type": "van",   "last_lat": 26.0700, "last_lng": 91.8400},
    {"registration": "ML01B2001", "vehicle_type": "truck", "last_lat": 25.9800, "last_lng": 91.9050},
]


def run():
    db = SessionLocal()
    try:
        print("🌱 Seeding NER-LIS pilot corridor data...")

        # Admin user
        if not db.query(User).filter_by(email="admin@nerlis.dev").first():
            db.add(User(
                id=uuid.uuid4(),
                email="admin@nerlis.dev",
                hashed_password=pwd_context.hash("admin1234"),
                full_name="NER-LIS Admin",
                role=UserRole.ADMIN,
            ))
            print("  ✅ Admin user created (admin@nerlis.dev / admin1234)")

        # Road segments
        segs = {}
        for data in ROAD_SEGMENTS:
            existing = db.query(RoadSegment).filter_by(name=data["name"]).first()
            if existing:
                segs[data["name"]] = existing
                continue
            seg = RoadSegment(
                id=uuid.uuid4(),
                name=data["name"],
                highway_type=data["highway_type"],
                status=data["status"],
                length_km=data["length_km"],
                elevation_avg_m=data["elevation_avg_m"],
                slope_pct=data["slope_pct"],
                risk_score=data["risk_score"],
                disruption_prob=data["disruption_prob"],
                is_pilot_corridor=data["is_pilot_corridor"],
                geometry=WKTElement(data["geom"], srid=4326),
            )
            db.add(seg)
            segs[data["name"]] = seg
        print(f"  ✅ {len(ROAD_SEGMENTS)} road segments seeded")

        # Incidents
        if db.query(Incident).count() == 0:
            blocked_seg = segs.get("Shillong Bypass — Blocked Section")
            barapani_seg = segs.get("Barapani Ghat Section")
            db.flush()

            db.add(Incident(
                id=uuid.uuid4(),
                incident_type=IncidentType.LANDSLIDE,
                severity=IncidentSeverity.CRITICAL,
                description="Major landslide blocking NH6. Debris spanning full carriageway.",
                road_segment_id=blocked_seg.id if blocked_seg else None,
                location=WKTElement("POINT(91.9700 25.8750)", srid=4326),
                is_verified=True,
            ))
            db.add(Incident(
                id=uuid.uuid4(),
                incident_type=IncidentType.ROAD_DAMAGE,
                severity=IncidentSeverity.HIGH,
                description="Heavy monsoon rain has eroded shoulder. Single-lane passable with caution.",
                road_segment_id=barapani_seg.id if barapani_seg else None,
                location=WKTElement("POINT(91.8890 26.0100)", srid=4326),
                is_verified=False,
            ))
            print("  ✅ 2 sample incidents seeded")

        # Vehicles
        vehicles = {}
        for vdata in VEHICLES:
            existing = db.query(Vehicle).filter_by(registration=vdata["registration"]).first()
            if existing:
                vehicles[vdata["registration"]] = existing
                continue
            v = Vehicle(
                id=uuid.uuid4(),
                registration=vdata["registration"],
                vehicle_type=vdata["vehicle_type"],
                last_lat=vdata["last_lat"],
                last_lng=vdata["last_lng"],
                last_seen=datetime.now(timezone.utc),
            )
            db.add(v)
            vehicles[vdata["registration"]] = v
        print(f"  ✅ {len(VEHICLES)} vehicles seeded")

        # Shipments
        db.flush()
        if db.query(Shipment).count() == 0:
            v1 = vehicles.get("AS01A1001")
            v2 = vehicles.get("ML01B2001")
            db.add(Shipment(
                id=uuid.uuid4(),
                vehicle_id=v1.id if v1 else None,
                cargo_type="medicines",
                priority=ShipmentPriority.CRITICAL,
                status=ShipmentStatus.AT_RISK,
                origin_location=WKTElement("POINT(91.7362 26.1445)", srid=4326),
                destination_location=WKTElement("POINT(91.9880 25.5780)", srid=4326),
                origin_name="Guwahati Medical Store",
                destination_name="Shillong Civil Hospital",
                expected_delivery=datetime.now(timezone.utc) + timedelta(hours=6),
                estimated_delay_hours=3.5,
            ))
            db.add(Shipment(
                id=uuid.uuid4(),
                vehicle_id=v2.id if v2 else None,
                cargo_type="food supplies",
                priority=ShipmentPriority.HIGH,
                status=ShipmentStatus.IN_TRANSIT,
                origin_location=WKTElement("POINT(91.7362 26.1445)", srid=4326),
                destination_location=WKTElement("POINT(91.9380 25.9350)", srid=4326),
                origin_name="Guwahati Distribution Centre",
                destination_name="Nongpoh Relief Camp",
                expected_delivery=datetime.now(timezone.utc) + timedelta(hours=4),
                estimated_delay_hours=0.0,
            ))
            print("  ✅ 2 sample shipments seeded")

        # Alerts
        if db.query(Alert).count() == 0:
            db.add(Alert(
                id=uuid.uuid4(),
                alert_type=AlertType.ROAD_BLOCKED,
                title="NH6 Shillong Bypass BLOCKED",
                message="Landslide has completely blocked the Shillong Bypass. Critical medicine shipment at risk. Re-routing required.",
                severity=IncidentSeverity.CRITICAL,
                is_resolved=False,
            ))
            print("  ✅ 1 sample alert seeded")

        db.commit()
        print("\n✅ Seed complete. Database ready for NER-LIS pilot.")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
