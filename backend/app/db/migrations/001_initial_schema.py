"""Initial schema — users, road_segments, incidents, vehicles, shipments, alerts

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-29
"""

from alembic import op
import sqlalchemy as sa
import geoalchemy2

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("role", sa.Enum("admin", "operator", "field_officer", name="userrole"), nullable=False, server_default="operator"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # road_segments
    op.create_table(
        "road_segments",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255)),
        sa.Column("highway_type", sa.String(50)),
        sa.Column("status", sa.Enum("open", "risky", "blocked", "unknown", name="roadstatus"), nullable=False, server_default="unknown"),
        sa.Column("length_km", sa.Float),
        sa.Column("elevation_avg_m", sa.Float),
        sa.Column("slope_pct", sa.Float),
        sa.Column("risk_score", sa.Float, server_default="0.0"),
        sa.Column("disruption_prob", sa.Float, server_default="0.0"),
        sa.Column("is_pilot_corridor", sa.Boolean, server_default="false"),
        sa.Column("geometry", geoalchemy2.Geometry("LINESTRING", srid=4326), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.execute("CREATE INDEX ix_road_segments_geom ON road_segments USING GIST (geometry)")

    # incidents
    op.create_table(
        "incidents",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("road_segment_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("road_segments.id")),
        sa.Column("reported_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("incident_type", sa.Enum("landslide", "flood", "road_damage", "bridge_damage", "fallen_tree", "other", name="incidenttype"), nullable=False),
        sa.Column("severity", sa.Enum("low", "medium", "high", "critical", name="incidentseverity"), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("photo_url", sa.String(512)),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("location", geoalchemy2.Geometry("POINT", srid=4326), nullable=False),
        sa.Column("reported_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime),
    )
    op.execute("CREATE INDEX ix_incidents_location ON incidents USING GIST (location)")

    # vehicles
    op.create_table(
        "vehicles",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("registration", sa.String(50), nullable=False, unique=True),
        sa.Column("vehicle_type", sa.String(50)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("last_lat", sa.Float),
        sa.Column("last_lng", sa.Float),
        sa.Column("last_seen", sa.DateTime),
        sa.Column("current_road_segment_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("road_segments.id")),
    )

    # shipments
    op.create_table(
        "shipments",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vehicle_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("vehicles.id")),
        sa.Column("description", sa.String(255)),
        sa.Column("cargo_type", sa.String(100)),
        sa.Column("priority", sa.Enum("normal", "high", "critical", name="shipmentpriority"), nullable=False, server_default="normal"),
        sa.Column("status", sa.Enum("pending", "in_transit", "delayed", "delivered", "at_risk", name="shipmentstatus"), nullable=False, server_default="pending"),
        sa.Column("origin_location", geoalchemy2.Geometry("POINT", srid=4326)),
        sa.Column("destination_location", geoalchemy2.Geometry("POINT", srid=4326)),
        sa.Column("origin_name", sa.String(255)),
        sa.Column("destination_name", sa.String(255)),
        sa.Column("expected_delivery", sa.DateTime),
        sa.Column("estimated_delay_hours", sa.Float, server_default="0.0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("alert_type", sa.Enum("road_blocked", "high_risk_corridor", "predicted_disruption", "delivery_delay", "emergency", name="alerttype"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text),
        sa.Column("severity", sa.Enum("low", "medium", "high", "critical", name="alertseverity")),
        sa.Column("is_resolved", sa.Boolean, server_default="false"),
        sa.Column("road_segment_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("road_segments.id")),
        sa.Column("shipment_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("shipments.id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("shipments")
    op.drop_table("vehicles")
    op.drop_table("incidents")
    op.drop_table("road_segments")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS alerttype")
    op.execute("DROP TYPE IF EXISTS shipmentstatus")
    op.execute("DROP TYPE IF EXISTS shipmentpriority")
    op.execute("DROP TYPE IF EXISTS incidentseverity")
    op.execute("DROP TYPE IF EXISTS incidenttype")
    op.execute("DROP TYPE IF EXISTS roadstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
