'use client';

import dynamic from 'next/dynamic';
import { useCallback, useEffect, useState } from 'react';
import {
  getAlerts, getIncidentsGeoJSON, getRoadSegments, getRoadsGeoJSON,
  getShipments, getVehicles, getVehiclesGeoJSON,
  type Alert, type RoadSegment, type RouteResponse, type Shipment, type Vehicle,
} from '@/lib/api';
import Navbar from '@/components/ui/Navbar';
import StatCard from '@/components/ui/StatCard';
import AlertsPanel from '@/components/dashboard/AlertsPanel';
import ShipmentsPanel from '@/components/dashboard/ShipmentsPanel';
import VehiclesPanel from '@/components/dashboard/VehiclesPanel';
import RoutingPanel from '@/components/dashboard/RoutingPanel';
import DisruptionPanel from '@/components/dashboard/DisruptionPanel';
import WhatIfPanel from '@/components/dashboard/WhatIfPanel';
import MapLegend from '@/components/map/MapLegend';

// Leaflet map — client-side only
const Map = dynamic(() => import('@/components/map/Map'), { ssr: false });

const POLL_INTERVAL_MS = 15_000;

export default function DashboardPage() {
  // ── Data state ─────────────────────────────────────────────────────────
  const [roadsGeoJSON, setRoadsGeoJSON] = useState<GeoJSON.FeatureCollection | null>(null);
  const [incidentsGeoJSON, setIncidentsGeoJSON] = useState<GeoJSON.FeatureCollection | null>(null);
  const [vehiclesGeoJSON, setVehiclesGeoJSON] = useState<GeoJSON.FeatureCollection | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [roadSegments, setRoadSegments] = useState<RoadSegment[]>([]);
  const [activeRoute, setActiveRoute] = useState<RouteResponse | null>(null);

  // ── Layer toggles ──────────────────────────────────────────────────────
  const [showRoads, setShowRoads] = useState(true);
  const [showIncidents, setShowIncidents] = useState(true);
  const [showVehicles, setShowVehicles] = useState(true);

  // ── Sidebar tab ────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<'overview' | 'routing' | 'ai' | 'whatif'>('overview');

  // ── Loading / error ────────────────────────────────────────────────────
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ── Fetch data ─────────────────────────────────────────────────────────
  const fetchData = useCallback(async () => {
    try {
      const results = await Promise.allSettled([
        getRoadsGeoJSON(),
        getIncidentsGeoJSON(),
        getVehiclesGeoJSON(),
        getAlerts(),
        getShipments(),
        getVehicles(),
        getRoadSegments(),
      ]);

      if (results[0].status === 'fulfilled') setRoadsGeoJSON(results[0].value);
      if (results[1].status === 'fulfilled') setIncidentsGeoJSON(results[1].value);
      if (results[2].status === 'fulfilled') setVehiclesGeoJSON(results[2].value);
      if (results[3].status === 'fulfilled') setAlerts(results[3].value);
      if (results[4].status === 'fulfilled') setShipments(results[4].value);
      if (results[5].status === 'fulfilled') setVehicles(results[5].value);
      if (results[6].status === 'fulfilled') setRoadSegments(results[6].value);

      setError(null);
    } catch {
      setError('Failed to connect to NER-LIS API. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [fetchData]);

  // ── Derived stats ──────────────────────────────────────────────────────
  const blockedCount = roadsGeoJSON?.features.filter(f => f.properties?.status === 'blocked').length ?? 0;
  const riskyCount = roadsGeoJSON?.features.filter(f => f.properties?.status === 'risky').length ?? 0;
  const criticalShipments = shipments.filter(s => s.priority === 'critical').length;
  const atRiskShipments = shipments.filter(s => s.status === 'at_risk').length;

  const tabs = [
    { id: 'overview' as const, label: 'Overview', icon: '📊' },
    { id: 'routing'  as const, label: 'Routing',  icon: '🔀' },
    { id: 'ai'       as const, label: 'AI',       icon: '🤖' },
    { id: 'whatif'   as const, label: 'What-If',  icon: '🧪' },
  ];

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans">
      <Navbar alertCount={alerts.length} />

      {/* Error banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 text-red-700 text-sm px-6 py-2 flex items-center gap-2">
          <span>⚠️</span> {error}
        </div>
      )}

      {/* Stat bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 px-4 py-3 shrink-0">
        <StatCard icon="🚫" label="Blocked Roads" value={blockedCount} color="bg-red-50" />
        <StatCard icon="⚠️" label="Risky Segments" value={riskyCount} color="bg-orange-50" />
        <StatCard icon="🚨" label="Critical Shipments" value={criticalShipments} color="bg-purple-50" />
        <StatCard icon="🔴" label="At-Risk Deliveries" value={atRiskShipments} color="bg-yellow-50" />
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden gap-3 px-4 pb-4">
        {/* Left sidebar */}
        <div className="w-80 shrink-0 flex flex-col gap-2 overflow-y-auto">
          {/* Tab bar */}
          <div className="flex bg-white rounded-lg shadow border border-gray-100 overflow-hidden">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-2 text-xs font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:bg-gray-50'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {activeTab === 'overview' && (
            <>
              <AlertsPanel alerts={alerts} onRefresh={fetchData} />
              <ShipmentsPanel shipments={shipments} />
              <VehiclesPanel vehicles={vehicles} />
            </>
          )}
          {activeTab === 'routing' && (
            <RoutingPanel onRouteCalculated={setActiveRoute} />
          )}
          {activeTab === 'ai' && (
            <DisruptionPanel />
          )}
          {activeTab === 'whatif' && (
            <WhatIfPanel
              roadSegments={roadSegments}
              onSimulate={(ids) => console.log('Simulate closure:', ids)}
              onReset={() => console.log('Reset simulation')}
            />
          )}
        </div>

        {/* Map area */}
        <div className="flex-1 relative rounded-xl overflow-hidden shadow border border-gray-200">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
              <div className="text-center">
                <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                <p className="text-gray-500 text-sm">Loading NER-LIS data...</p>
              </div>
            </div>
          ) : (
            <Map
              roadsGeoJSON={roadsGeoJSON}
              incidentsGeoJSON={incidentsGeoJSON}
              vehiclesGeoJSON={vehiclesGeoJSON}
              activeRoute={activeRoute}
              showRoads={showRoads}
              showIncidents={showIncidents}
              showVehicles={showVehicles}
            />
          )}
          <MapLegend
            showRoads={showRoads}
            showIncidents={showIncidents}
            showVehicles={showVehicles}
            onToggleRoads={() => setShowRoads(v => !v)}
            onToggleIncidents={() => setShowIncidents(v => !v)}
            onToggleVehicles={() => setShowVehicles(v => !v)}
          />
        </div>
      </div>
    </div>
  );
}
