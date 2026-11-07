'use client';

import type { Alert } from '@/lib/api';
import { resolveAlert } from '@/lib/api';
import { useState } from 'react';

interface AlertsPanelProps {
  alerts: Alert[];
  onRefresh: () => void;
}

const severityStyles: Record<string, string> = {
  critical: 'border-red-500 bg-red-50',
  high:     'border-orange-400 bg-orange-50',
  medium:   'border-yellow-400 bg-yellow-50',
  low:      'border-green-400 bg-green-50',
};

const severityBadge: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  high:     'bg-orange-100 text-orange-700',
  medium:   'bg-yellow-100 text-yellow-700',
  low:      'bg-green-100 text-green-700',
};

export default function AlertsPanel({ alerts, onRefresh }: AlertsPanelProps) {
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const handleResolve = async (id: string) => {
    setResolvingId(id);
    try {
      await resolveAlert(id);
      onRefresh();
    } catch (e) {
      console.error('Failed to resolve alert:', e);
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-red-500">🔔</span> Active Alerts
        </h2>
        {alerts.length > 0 && (
          <span className="bg-red-100 text-red-700 text-xs font-bold px-2 py-0.5 rounded-full">
            {alerts.length}
          </span>
        )}
      </div>

      <div className="divide-y divide-gray-50 max-h-80 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="px-4 py-6 text-center text-gray-400 text-sm">
            ✅ No active alerts
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`px-4 py-3 border-l-4 ${severityStyles[alert.severity] ?? 'border-gray-300 bg-white'}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 text-sm truncate">{alert.title}</p>
                  {alert.message && (
                    <p className="text-gray-500 text-xs mt-0.5 line-clamp-2">{alert.message}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${severityBadge[alert.severity]}`}>
                      {alert.severity}
                    </span>
                    <span className="text-gray-400 text-xs">
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleResolve(alert.id)}
                  disabled={resolvingId === alert.id}
                  className="text-xs text-gray-400 hover:text-gray-600 shrink-0 mt-0.5 disabled:opacity-50"
                >
                  {resolvingId === alert.id ? '...' : '✕'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
