'use client';

import type { Shipment } from '@/lib/api';
import { SHIPMENT_STATUS_COLORS } from '@/lib/constants';

interface ShipmentsPanelProps {
  shipments: Shipment[];
}

const priorityBadge: Record<string, string> = {
  critical: 'bg-red-100 text-red-700 border border-red-200',
  high:     'bg-orange-100 text-orange-700 border border-orange-200',
  normal:   'bg-gray-100 text-gray-600',
};

const priorityIcon: Record<string, string> = {
  critical: '🚨',
  high:     '⚠️',
  normal:   '📦',
};

export default function ShipmentsPanel({ shipments }: ShipmentsPanelProps) {
  return (
    <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <span>📦</span> Active Shipments
        </h2>
      </div>

      <div className="divide-y divide-gray-50 max-h-80 overflow-y-auto">
        {shipments.length === 0 ? (
          <div className="px-4 py-6 text-center text-gray-400 text-sm">No active shipments</div>
        ) : (
          shipments.map((s) => (
            <div key={s.id} className="px-4 py-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-sm">{priorityIcon[s.priority]}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${priorityBadge[s.priority]}`}>
                      {s.priority.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500 capitalize">{s.cargo_type}</span>
                  </div>
                  <p className="text-sm text-gray-700 font-medium truncate">
                    {s.origin_name} → {s.destination_name}
                  </p>
                  {s.estimated_delay_hours > 0 && (
                    <p className="text-xs text-orange-600 mt-0.5">
                      ⏱ Delayed ~{s.estimated_delay_hours}h
                    </p>
                  )}
                </div>
                <div className="shrink-0 text-right">
                  <span
                    className="text-xs px-2 py-0.5 rounded-full text-white font-medium capitalize"
                    style={{ backgroundColor: SHIPMENT_STATUS_COLORS[s.status] ?? '#94a3b8' }}
                  >
                    {s.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
