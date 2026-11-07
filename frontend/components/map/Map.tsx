'use client';

import { useEffect, useRef, useState } from 'react';
import type { Alert, Incident, RoadSegment, RouteResponse, Vehicle } from '@/lib/api';
import { ROAD_STATUS_COLORS, INCIDENT_SEVERITY_COLORS, PILOT_CORRIDOR_CENTER, PILOT_CORRIDOR_ZOOM } from '@/lib/constants';

// Leaflet is loaded client-side only (no SSR)
let L: typeof import('leaflet');

interface MapProps {
  roadsGeoJSON: GeoJSON.FeatureCollection | null;
  incidentsGeoJSON: GeoJSON.FeatureCollection | null;
  vehiclesGeoJSON: GeoJSON.FeatureCollection | null;
  activeRoute: RouteResponse | null;
  showRoads: boolean;
  showIncidents: boolean;
  showVehicles: boolean;
  onSegmentClick?: (segment: RoadSegment) => void;
}

export default function Map({
  roadsGeoJSON,
  incidentsGeoJSON,
  vehiclesGeoJSON,
  activeRoute,
  showRoads,
  showIncidents,
  showVehicles,
  onSegmentClick,
}: MapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import('leaflet').Map | null>(null);
  const roadsLayerRef = useRef<import('leaflet').GeoJSON | null>(null);
  const incidentsLayerRef = useRef<import('leaflet').GeoJSON | null>(null);
  const vehiclesLayerRef = useRef<import('leaflet').GeoJSON | null>(null);
  const routeLayerRef = useRef<import('leaflet').Polyline | null>(null);

  // ── Init map ──────────────────────────────────────────────────────────────
  useEffect(() => {
    if (mapRef.current || !mapContainerRef.current) return;

    (async () => {
      L = (await import('leaflet')).default;
      await import('leaflet/dist/leaflet.css');

      const map = L.map(mapContainerRef.current!, {
        center: PILOT_CORRIDOR_CENTER,
        zoom: PILOT_CORRIDOR_ZOOM,
        zoomControl: true,
      });

      // OpenStreetMap base tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;
    })();

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  // ── Roads layer ───────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !L) return;
    roadsLayerRef.current?.remove();
    roadsLayerRef.current = null;

    if (!roadsGeoJSON || !showRoads) return;

    roadsLayerRef.current = L.geoJSON(roadsGeoJSON, {
      style: (feature) => {
        const status = feature?.properties?.status ?? 'unknown';
        return {
          color: ROAD_STATUS_COLORS[status] ?? ROAD_STATUS_COLORS.unknown,
          weight: 5,
          opacity: 0.9,
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindPopup(`
          <div class="text-sm">
            <p class="font-bold text-gray-800">${p.name ?? 'Unnamed Segment'}</p>
            <p>Status: <span class="font-semibold capitalize">${p.status}</span></p>
            <p>Risk Score: <span class="font-semibold">${(p.risk_score * 100).toFixed(1)}%</span></p>
            <p>Disruption Prob: <span class="font-semibold">${(p.disruption_prob * 100).toFixed(1)}%</span></p>
            <p>Length: ${p.length_km ? p.length_km.toFixed(1) + ' km' : 'N/A'}</p>
          </div>
        `);
        layer.on('click', () => {
          if (onSegmentClick) onSegmentClick(p as RoadSegment);
        });
      },
    }).addTo(mapRef.current);
  }, [roadsGeoJSON, showRoads]);

  // ── Incidents layer ───────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !L) return;
    incidentsLayerRef.current?.remove();
    incidentsLayerRef.current = null;

    if (!incidentsGeoJSON || !showIncidents) return;

    incidentsLayerRef.current = L.geoJSON(incidentsGeoJSON, {
      pointToLayer: (feature, latlng) => {
        const severity = feature.properties?.severity ?? 'low';
        return L.circleMarker(latlng, {
          radius: 10,
          fillColor: INCIDENT_SEVERITY_COLORS[severity],
          color: '#1e293b',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.85,
        });
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindPopup(`
          <div class="text-sm">
            <p class="font-bold capitalize">${p.type?.replace('_', ' ')} — ${p.severity}</p>
            <p>${p.description ?? 'No description'}</p>
            <p class="text-gray-500 text-xs mt-1">Verified: ${p.is_verified ? '✅ Yes' : '⏳ Pending'}</p>
          </div>
        `);
      },
    }).addTo(mapRef.current);
  }, [incidentsGeoJSON, showIncidents]);

  // ── Vehicles layer ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !L) return;
    vehiclesLayerRef.current?.remove();
    vehiclesLayerRef.current = null;

    if (!vehiclesGeoJSON || !showVehicles) return;

    const truckIcon = L.divIcon({
      className: '',
      html: '<div style="font-size:22px;line-height:1">🚛</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    vehiclesLayerRef.current = L.geoJSON(vehiclesGeoJSON, {
      pointToLayer: (_, latlng) => L.marker(latlng, { icon: truckIcon }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindPopup(`
          <div class="text-sm">
            <p class="font-bold">${p.registration}</p>
            <p>Type: ${p.vehicle_type ?? 'Unknown'}</p>
            <p class="text-gray-500 text-xs">Last seen: ${p.last_seen ? new Date(p.last_seen).toLocaleTimeString() : 'N/A'}</p>
          </div>
        `);
      },
    }).addTo(mapRef.current);
  }, [vehiclesGeoJSON, showVehicles]);

  // ── Active route overlay ──────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !L) return;
    routeLayerRef.current?.remove();
    routeLayerRef.current = null;
    if (!activeRoute) return;

    // Draw route using segment risk scores as colour gradient
    // Simple implementation: one polyline per segment based on road data
    // Full spatial geometry comes in Week 6 — for now draw as a dashed overlay
    const routeColors: Record<string, string> = {
      fastest: '#3b82f6',
      safest: '#22c55e',
      balanced: '#a855f7',
      emergency: '#ef4444',
    };

    // Placeholder: highlight the map area with a mode indicator
    const modeColor = routeColors[activeRoute.mode] ?? '#3b82f6';
    routeLayerRef.current = L.polyline(
      [[PILOT_CORRIDOR_CENTER[0] + 0.5, PILOT_CORRIDOR_CENTER[1] - 0.3],
       [PILOT_CORRIDOR_CENTER[0] - 0.5, PILOT_CORRIDOR_CENTER[1] + 0.3]],
      { color: modeColor, weight: 4, dashArray: '8 4', opacity: 0.8 }
    ).addTo(mapRef.current);
  }, [activeRoute]);

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-full rounded-lg"
      style={{ minHeight: '500px' }}
    />
  );
}
