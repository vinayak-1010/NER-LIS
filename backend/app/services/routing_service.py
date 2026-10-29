"""
Routing Service — builds a graph from PostGIS road segments and computes
risk-aware routes using Dijkstra / A*.

Edge cost function (Week 6 target):
  cost = distance_km * (1 + risk_weight * risk_score + disruption_weight * disruption_prob)

Mode presets:
  fastest   → risk_weight=0.0, disruption_weight=0.0
  safest    → risk_weight=2.0, disruption_weight=2.0
  balanced  → risk_weight=1.0, disruption_weight=1.0
  emergency → safest, but blocked segments skipped entirely
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.models import RoadSegment, RoadStatus
from app.schemas.schemas import RouteMode, RouteResponse, RouteSegmentOut


MODE_WEIGHTS = {
    RouteMode.FASTEST:   {"risk": 0.0, "disruption": 0.0},
    RouteMode.SAFEST:    {"risk": 2.0, "disruption": 2.0},
    RouteMode.BALANCED:  {"risk": 1.0, "disruption": 1.0},
    RouteMode.EMERGENCY: {"risk": 2.0, "disruption": 2.0},
}


def _edge_cost(seg: RoadSegment, risk_w: float, disruption_w: float) -> float:
    length = seg.length_km or 1.0
    penalty = 1.0 + risk_w * (seg.risk_score or 0.0) + disruption_w * (seg.disruption_prob or 0.0)
    return length * penalty


def compute_route(
    db: Session,
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    mode: RouteMode = RouteMode.BALANCED,
) -> Optional[RouteResponse]:
    """
    Build a NetworkX graph from road_segments and find the shortest path.
    NOTE: This is the Week-2 stub. The full spatial snap-to-graph implementation
    (using PostGIS ST_ClosestPoint) will be added in Week 6.
    """
    import networkx as nx
    from geoalchemy2.shape import to_shape

    weights = MODE_WEIGHTS[mode]
    risk_w = weights["risk"]
    disruption_w = weights["disruption"]

    segments = db.query(RoadSegment).all()
    if not segments:
        return None

    G = nx.Graph()

    for seg in segments:
        # Skip blocked roads in emergency mode
        if mode == RouteMode.EMERGENCY and seg.status == RoadStatus.BLOCKED:
            continue

        if seg.geometry is None:
            continue

        shape = to_shape(seg.geometry)
        coords = list(shape.coords)
        if len(coords) < 2:
            continue

        start_node = (round(coords[0][1], 5), round(coords[0][0], 5))
        end_node   = (round(coords[-1][1], 5), round(coords[-1][0], 5))
        cost = _edge_cost(seg, risk_w, disruption_w)

        G.add_edge(start_node, end_node, weight=cost, segment=seg)

    if G.number_of_nodes() == 0:
        return None

    # Snap origin/destination to nearest graph node
    import math

    def nearest_node(lat: float, lng: float):
        return min(G.nodes, key=lambda n: math.hypot(n[0] - lat, n[1] - lng))

    src = nearest_node(origin_lat, origin_lng)
    dst = nearest_node(destination_lat, destination_lng)

    try:
        path_nodes = nx.shortest_path(G, source=src, target=dst, weight="weight")
    except nx.NetworkXNoPath:
        return None

    path_segments: list[RoadSegment] = []
    total_distance = 0.0
    total_risk = 0.0

    for i in range(len(path_nodes) - 1):
        edge_data = G.get_edge_data(path_nodes[i], path_nodes[i + 1])
        if edge_data:
            seg = edge_data["segment"]
            path_segments.append(seg)
            total_distance += seg.length_km or 0.0
            total_risk += seg.risk_score or 0.0

    avg_risk = total_risk / len(path_segments) if path_segments else 0.0
    est_time = (total_distance / 40.0) * 60  # assume 40 km/h avg speed → minutes

    return RouteResponse(
        mode=mode,
        total_distance_km=round(total_distance, 2),
        estimated_time_min=round(est_time, 1),
        overall_risk_score=round(avg_risk, 4),
        segments=[
            RouteSegmentOut(
                road_segment_id=s.id,
                name=s.name,
                status=s.status,
                risk_score=s.risk_score or 0.0,
                length_km=s.length_km,
            )
            for s in path_segments
        ],
    )
