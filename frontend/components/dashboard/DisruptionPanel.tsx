'use client';

import { useState } from 'react';
import { predictDisruption, type DisruptionResponse } from '@/lib/api';

export default function DisruptionPanel() {
  const [form, setForm] = useState({
    rainfall_mm: 120,
    elevation_m: 800,
    slope_pct: 18,
    historical_incident_count: 4,
    traffic_volume: 50,
    month: new Date().getMonth() + 1,
  });
  const [result, setResult] = useState<DisruptionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const res = await predictDisruption(form);
      setResult(res);
    } catch (e) {
      console.error('Prediction failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const riskColors: Record<string, string> = {
    low: 'bg-green-100 text-green-700',
    medium: 'bg-yellow-100 text-yellow-700',
    high: 'bg-orange-100 text-orange-700',
    critical: 'bg-red-100 text-red-700',
  };

  return (
    <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <span>🤖</span> AI Disruption Prediction
        </h2>
      </div>

      <div className="p-4 space-y-3">
        <div className="grid grid-cols-2 gap-2">
          {[
            { key: 'rainfall_mm', label: 'Rainfall (mm)', step: 10 },
            { key: 'elevation_m', label: 'Elevation (m)', step: 50 },
            { key: 'slope_pct', label: 'Slope (%)', step: 1 },
            { key: 'historical_incident_count', label: 'Past Incidents', step: 1 },
            { key: 'traffic_volume', label: 'Traffic Vol.', step: 10 },
            { key: 'month', label: 'Month (1-12)', step: 1 },
          ].map(({ key, label, step }) => (
            <div key={key}>
              <label className="text-[10px] text-gray-400 font-medium uppercase">{label}</label>
              <input
                type="number"
                step={step}
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })}
                className="w-full text-sm border border-gray-200 rounded px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>
          ))}
        </div>

        <button
          onClick={handlePredict}
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium text-sm py-2.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Predicting...' : 'Predict Disruption'}
        </button>

        {result && (
          <div className="bg-gray-50 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${riskColors[result.risk_level] ?? 'bg-gray-100'}`}>
                {result.risk_level.toUpperCase()} RISK
              </span>
              <span className="text-xs text-gray-400">
                Conf: {(result.confidence * 100).toFixed(0)}%
              </span>
            </div>

            <div className="text-center">
              <p className="text-3xl font-bold text-gray-800">
                {(result.disruption_probability * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-400">Disruption Probability</p>
            </div>

            {/* Risk bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  result.disruption_probability > 0.75 ? 'bg-red-500' :
                  result.disruption_probability > 0.5 ? 'bg-orange-500' :
                  result.disruption_probability > 0.25 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${result.disruption_probability * 100}%` }}
              />
            </div>

            {result.top_factors.length > 0 && (
              <div>
                <p className="text-[10px] text-gray-400 font-medium uppercase mb-1">Top Factors</p>
                <div className="flex flex-wrap gap-1">
                  {result.top_factors.map((f) => (
                    <span key={f} className="text-[10px] bg-gray-200 text-gray-600 px-2 py-0.5 rounded capitalize">
                      {f.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
