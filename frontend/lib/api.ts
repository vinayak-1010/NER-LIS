/**
 * NER-LIS API client — thin wrapper around fetch for all backend calls.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API ${res.status}: ${error}`);
  }
  return res.json();
}

// ── Roads ──────────────────────────────────────────────────────────────────
export const getRoadsGeoJSON = () =>
  apiFetch<GeoJSON.FeatureCollection>('/api/v1/roads/geojson?pilot_only=true');

export const getRoadSegments = () =>
  apiFetch<RoadSegment[]>('/api/v1/roads/');

// ── Incidents ──────────────────────────────────────────────────────────────
export const getIncidentsGeoJSON = () =>
  apiFetch<GeoJSON.FeatureCollection>('/api/v1/incidents/geojson');

export const getIncidents = () =>
  apiFetch<Incident[]>('/api/v1/incidents/?unresolved_only=true');

// ── Vehicles ───────────────────────────────────────────────────────────────
export const getVehiclesGeoJSON = () =>
  apiFetch<GeoJSON.FeatureCollection>('/api/v1/vehicles/positions/geojson');

export const getVehicles = () =>
  apiFetch<Vehicle[]>('/api/v1/vehicles/');

// ── Shipments ──────────────────────────────────────────────────────────────
export const getShipments = (priorityOnly = false) =>
  apiFetch<Shipment[]>(`/api/v1/shipments/?priority_only=${priorityOnly}`);

// ── Alerts ─────────────────────────────────────────────────────────────────
export const getAlerts = () =>
  apiFetch<Alert[]>('/api/v1/alerts/');

export const resolveAlert = (id: string) =>
  apiFetch<Alert>(`/api/v1/alerts/${id}/resolve`, { method: 'POST' });

// ── Routing ────────────────────────────────────────────────────────────────
export const calculateRoute = (payload: RouteRequest) =>
  apiFetch<RouteResponse>('/api/v1/routing/route', {
    method: 'POST',
    body: JSON.stringify(payload),
  });

// ── ML ─────────────────────────────────────────────────────────────────────
export const predictDisruption = (payload: DisruptionRequest) =>
  apiFetch<DisruptionResponse>('/api/v1/ml/predict-disruption', {
    method: 'POST',
    body: JSON.stringify(payload),
  });

// ── Types ──────────────────────────────────────────────────────────────────
export type RoadStatus = 'open' | 'risky' | 'blocked' | 'unknown';
export type IncidentSeverity = 'low' | 'medium' | 'high' | 'critical';
export type ShipmentPriority = 'normal' | 'high' | 'critical';
export type ShipmentStatus = 'pending' | 'in_transit' | 'delayed' | 'delivered' | 'at_risk';
export type RouteMode = 'fastest' | 'safest' | 'balanced' | 'emergency';

export interface RoadSegment {
  id: string;
  name: string | null;
  highway_type: string | null;
  status: RoadStatus;
  length_km: number | null;
  risk_score: number;
  disruption_prob: number;
  is_pilot_corridor: boolean;
}

export interface Incident {
  id: string;
  incident_type: string;
  severity: IncidentSeverity;
  description: string | null;
  is_verified: boolean;
  reported_at: string;
}

export interface Vehicle {
  id: string;
  registration: string;
  vehicle_type: string | null;
  is_active: boolean;
  last_lat: number | null;
  last_lng: number | null;
  last_seen: string | null;
}

export interface Shipment {
  id: string;
  cargo_type: string;
  priority: ShipmentPriority;
  status: ShipmentStatus;
  origin_name: string;
  destination_name: string;
  estimated_delay_hours: number;
  created_at: string;
}

export interface Alert {
  id: string;
  alert_type: string;
  title: string;
  message: string | null;
  severity: IncidentSeverity;
  is_resolved: boolean;
  created_at: string;
}

export interface RouteRequest {
  origin_lat: number;
  origin_lng: number;
  destination_lat: number;
  destination_lng: number;
  mode: RouteMode;
}

export interface RouteResponse {
  mode: RouteMode;
  total_distance_km: number;
  estimated_time_min: number;
  overall_risk_score: number;
  segments: RouteSegment[];
}

export interface RouteSegment {
  road_segment_id: string;
  name: string | null;
  status: RoadStatus;
  risk_score: number;
  length_km: number | null;
}

export interface DisruptionRequest {
  rainfall_mm: number;
  elevation_m: number;
  slope_pct: number;
  historical_incident_count: number;
  traffic_volume: number;
  month: number;
}

export interface DisruptionResponse {
  disruption_probability: number;
  confidence: number;
  risk_level: string;
  top_factors: string[];
}
