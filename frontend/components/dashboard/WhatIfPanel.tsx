'use client';

import { useState } from 'react';
import type { RoadSegment } from '@/lib/api';

interface WhatIfPanelProps {
  roadSegments: RoadSegment[];
  onSimulate: (blockedIds: string[]) => void;
  onReset: () => void;
}

export default function WhatIfPanel({ roadSegments, onSimulate, onReset }: WhatIfPanelProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [active, setActive] = useState(false);

  const toggleSegment = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleSimulate = () => {
    setActive(true);
    onSimulate(Array.from(selected));
  };

  const handleReset = () => {
    setActive(false);
    setSelected(new Set());
    onReset();
  };

  return (
    <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <span>🧪</span> What-If Simulation
        </h2>
      </div>

      <div className="p-4 space-y-3">
        <p className="text-xs text-gray-500">
          Select road segments to simulate closure and see impact on routes and shipments.
        </p>

        <div className="space-y-1 max-h-40 overflow-y-auto">
          {roadSegments.map((seg) => (
            <label
              key={seg.id}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-xs transition-colors ${
                selected.has(seg.id)
                  ? 'bg-red-50 border border-red-200'
                  : 'hover:bg-gray-50 border border-transparent'
              }`}
            >
              <input
                type="checkbox"
                checked={selected.has(seg.id)}
                onChange={() => toggleSegment(seg.id)}
                className="rounded border-gray-300"
              />
              <span className={`w-2 h-2 rounded-full shrink-0 ${
                seg.status === 'open' ? 'bg-green-400' :
                seg.status === 'risky' ? 'bg-orange-400' :
                seg.status === 'blocked' ? 'bg-red-500' : 'bg-gray-400'
              }`} />
              <span className="flex-1 truncate">{seg.name ?? 'Unnamed'}</span>
            </label>
          ))}
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleSimulate}
            disabled={selected.size === 0}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium text-xs py-2 rounded-lg transition-colors disabled:opacity-40"
          >
            🚫 Simulate Closure ({selected.size})
          </button>
          {active && (
            <button
              onClick={handleReset}
              className="px-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium text-xs py-2 rounded-lg transition-colors"
            >
              Reset
            </button>
          )}
        </div>

        {active && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-xs text-red-700">
            ⚠️ Simulating closure of {selected.size} segment{selected.size > 1 ? 's' : ''}.
            Routing engine will exclude these from path calculation.
          </div>
        )}
      </div>
    </div>
  );
}
