'use client';

import { ROAD_STATUS_COLORS } from '@/lib/constants';

interface MapLegendProps {
  showRoads: boolean;
  showIncidents: boolean;
  showVehicles: boolean;
  onToggleRoads: () => void;
  onToggleIncidents: () => void;
  onToggleVehicles: () => void;
}

const statusLabels = [
  { key: 'open',    label: 'Open' },
  { key: 'risky',   label: 'Risky' },
  { key: 'blocked', label: 'Blocked' },
  { key: 'unknown', label: 'Unknown' },
];

export default function MapLegend({
  showRoads,
  showIncidents,
  showVehicles,
  onToggleRoads,
  onToggleIncidents,
  onToggleVehicles,
}: MapLegendProps) {
  return (
    <div className="absolute bottom-6 left-4 z-[1000] bg-white rounded-xl shadow-lg p-4 w-52 text-sm">
      <p className="font-bold text-gray-700 mb-3 text-xs uppercase tracking-wide">Map Layers</p>

      {/* Toggle buttons */}
      <div className="flex flex-col gap-1 mb-3">
        <button
          onClick={onToggleRoads}
          className={`flex items-center gap-2 px-2 py-1 rounded-md text-xs font-medium transition-colors ${
            showRoads ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-400'
          }`}
        >
          <span>━━</span> Road Network
        </button>
        <button
          onClick={onToggleIncidents}
          className={`flex items-center gap-2 px-2 py-1 rounded-md text-xs font-medium transition-colors ${
            showIncidents ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-400'
          }`}
        >
          <span>●</span> Incidents
        </button>
        <button
          onClick={onToggleVehicles}
          className={`flex items-center gap-2 px-2 py-1 rounded-md text-xs font-medium transition-colors ${
            showVehicles ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-400'
          }`}
        >
          <span>🚛</span> Vehicles
        </button>
      </div>

      {/* Road status legend */}
      {showRoads && (
        <>
          <p className="text-gray-500 text-xs mb-1 font-semibold uppercase tracking-wide">Road Status</p>
          <div className="flex flex-col gap-1">
            {statusLabels.map(({ key, label }) => (
              <div key={key} className="flex items-center gap-2">
                <span
                  className="inline-block w-5 h-2 rounded-full"
                  style={{ backgroundColor: ROAD_STATUS_COLORS[key] }}
                />
                <span className="text-gray-600 text-xs">{label}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
