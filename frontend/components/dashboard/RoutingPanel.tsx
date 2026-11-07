'use client';

import { useState } from 'react';
import { calculateRoute, type RouteMode, type RouteResponse } from '@/lib/api';

interface RoutingPanelProps {
  onRouteCalculated: (route: RouteResponse) => void;
}

const ROUTE_MODES: { value: RouteMode; label: string; icon: string; desc: string }[] = [
  { value: 'fastest',   label: 'Fastest',   icon: '⚡', desc: 'Shortest travel time' },
  { value: 'safest',    label: 'Safest',    icon: '🛡️', desc: 'Lowest risk score' },
  { value: 'balanced',  label: 'Balanced',  icon: '⚖️', desc: 'Risk × time trade-off' },
  { value: 'emergency', label: 'Emergency', icon: '🚨', desc: 'Skip blocked segments' },
];

const PRESETS = {
  guwahati_to_shillong: {
    label: 'Guwahati → Shillong',
    origin_lat: 26.1445, origin_lng: 91.7362,
    destination_lat: 25.5780, destination_lng: 91.9880,
  },
  guwahati_to_nongpoh: {
    label: 'Guwahati → Nongpoh',
    origin_lat: 26.1445, origin_lng: 91.7362,
    destination_lat: 25.9350, destination_lng: 91.9380,
  },
};

export default function RoutingPanel({ onRouteCalculated }: RoutingPanelProps) {
  const [mode, setMode] = useState<RouteMode>('balanced');
  const [preset, setPreset] = useState('guwahati_to_shillong');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RouteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    const p = PRESETS[preset as keyof typeof PRESETS];
    try {
      const route = await calculateRoute({
        origin_lat: p.origin_lat,
        origin_lng: p.origin_lng,
        destination_lat: p.destination_lat,
        destination_lng: p.destination_lng,
        mode,
      });
      setResult(route);
      onRouteCalculated(route);
    } catch (e: any) {
      setError(e.message ?? 'Route calculation failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const modeColors: Record<string, string> = {
    fastest: 'text-blue-600', safest: 'text-green-600',
    balanced: 'text-purple-600', emergency: 'text-red-600',
  };

  return (
    <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <span>🔀</span> Risk-Aware Routing
        </h2>
      </div>

      <div className="p-4 space-y-3">
        {/* Route preset */}
        <div>
          <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Corridor</label>
          <select
            value={preset}
            onChange={(e) => setPreset(e.target.value)}
            className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200"
          >
            {Object.entries(PRESETS).map(([key, val]) => (
              <option key={key} value={key}>{val.label}</option>
            ))}
          </select>
        </div>

        {/* Route mode */}
        <div>
          <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Mode</label>
          <div className="grid grid-cols-2 gap-2 mt-1">
            {ROUTE_MODES.map((m) => (
              <button
                key={m.value}
                onClick={() => setMode(m.value)}
                className={`text-left px-3 py-2 rounded-lg border text-xs transition-colors ${
                  mode === m.value
                    ? 'border-blue-400 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-600'
                }`}
              >
                <span className="text-sm">{m.icon}</span> {m.label}
                <p className="text-[10px] text-gray-400 mt-0.5">{m.desc}</p>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleCalculate}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Calculating...' : 'Calculate Route'}
        </button>

        {error && <p className="text-xs text-red-500">{error}</p>}

        {/* Result */}
        {result && (
          <div className="bg-gray-50 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className={`font-bold text-sm capitalize ${modeColors[result.mode]}`}>
                {result.mode} Route
              </span>
              <span className="text-xs text-gray-400">{result.segments.length} segments</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-white rounded px-2 py-1.5 shadow-sm">
                <p className="text-sm font-bold text-gray-800">{result.total_distance_km} km</p>
                <p className="text-[10px] text-gray-400">Distance</p>
              </div>
              <div className="bg-white rounded px-2 py-1.5 shadow-sm">
                <p className="text-sm font-bold text-gray-800">{result.estimated_time_min} min</p>
                <p className="text-[10px] text-gray-400">Est. Time</p>
              </div>
              <div className="bg-white rounded px-2 py-1.5 shadow-sm">
                <p className="text-sm font-bold text-gray-800">{(result.overall_risk_score * 100).toFixed(0)}%</p>
                <p className="text-[10px] text-gray-400">Risk</p>
              </div>
            </div>

            {/* Segment detail */}
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {result.segments.map((seg) => (
                <div key={seg.road_segment_id} className="flex items-center gap-2 text-xs">
                  <span className={`w-2 h-2 rounded-full shrink-0 ${
                    seg.status === 'open' ? 'bg-green-400' :
                    seg.status === 'risky' ? 'bg-orange-400' :
                    seg.status === 'blocked' ? 'bg-red-500' : 'bg-gray-400'
                  }`} />
                  <span className="flex-1 truncate text-gray-600">{seg.name ?? 'Unnamed'}</span>
                  <span className="text-gray-400 shrink-0">{seg.length_km?.toFixed(1)} km</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
