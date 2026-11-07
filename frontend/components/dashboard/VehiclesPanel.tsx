'use client';

import type { Vehicle } from '@/lib/api';

interface VehiclesPanelProps {
  vehicles: Vehicle[];
}

export default function VehiclesPanel({ vehicles }: VehiclesPanelProps) {
  return (
    <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <span>🚛</span> Tracked Vehicles
        </h2>
      </div>

      <div className="divide-y divide-gray-50 max-h-64 overflow-y-auto">
        {vehicles.length === 0 ? (
          <div className="px-4 py-6 text-center text-gray-400 text-sm">No vehicles tracked</div>
        ) : (
          vehicles.map((v) => (
            <div key={v.id} className="px-4 py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-gray-800">{v.registration}</p>
                <p className="text-xs text-gray-500 capitalize">{v.vehicle_type ?? 'Unknown type'}</p>
              </div>
              <div className="text-right">
                {v.last_lat && v.last_lng ? (
                  <p className="text-xs text-gray-500">
                    {v.last_lat.toFixed(4)}, {v.last_lng.toFixed(4)}
                  </p>
                ) : (
                  <p className="text-xs text-gray-400">No position</p>
                )}
                {v.last_seen && (
                  <p className="text-xs text-gray-400">
                    {new Date(v.last_seen).toLocaleTimeString()}
                  </p>
                )}
              </div>
              <span className={`ml-3 w-2 h-2 rounded-full ${v.is_active ? 'bg-green-400' : 'bg-gray-300'}`} />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
