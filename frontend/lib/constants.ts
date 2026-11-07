/**
 * Road status colour mapping for map layers and UI badges.
 */
export const ROAD_STATUS_COLORS: Record<string, string> = {
  open: '#22c55e',      // green-500
  risky: '#f97316',     // orange-500
  blocked: '#ef4444',   // red-500
  unknown: '#94a3b8',   // slate-400
};

export const INCIDENT_SEVERITY_COLORS: Record<string, string> = {
  low: '#86efac',       // green-300
  medium: '#fde68a',    // amber-200
  high: '#fb923c',      // orange-400
  critical: '#dc2626',  // red-600
};

export const SHIPMENT_STATUS_COLORS: Record<string, string> = {
  pending: '#94a3b8',
  in_transit: '#3b82f6',
  delayed: '#f97316',
  delivered: '#22c55e',
  at_risk: '#ef4444',
};

/** Pilot corridor centre (Guwahati–Shillong midpoint) */
export const PILOT_CORRIDOR_CENTER: [number, number] = [26.0, 91.85];
export const PILOT_CORRIDOR_ZOOM = 9;
