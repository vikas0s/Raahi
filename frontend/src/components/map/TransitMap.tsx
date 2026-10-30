import React, { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import { config } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url';

if (typeof window !== 'undefined') {
  config.WORKER_URL = maplibreWorkerUrl;
}
import { RouteItinerary, GeoLocation, LiveVehicle } from '../../types/transit';
import { fetchLiveVehicles } from '../../services/api';
import { Radio, Bus, Navigation2, CheckCircle2 } from 'lucide-react';

interface Props {
  selectedRoute: RouteItinerary | null;
  allRoutes?: RouteItinerary[];
  origin?: GeoLocation | null;
  destination?: GeoLocation | null;
  onSelectRoute?: (route: RouteItinerary) => void;
  className?: string;
  city?: string;
}

export const TransitMap: React.FC<Props> = ({
  selectedRoute,
  allRoutes = [],
  origin,
  destination,
  className = '',
  city
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const vehicleMarkersRef = useRef<maplibregl.Marker[]>([]);

  // Open Transit Data Delhi Real-time GPS toggle
  const [showLiveGPS, setShowLiveGPS] = useState<boolean>(true);
  const [liveVehicles, setLiveVehicles] = useState<LiveVehicle[]>([]);
  const [lastTelemetryUpdate, setLastTelemetryUpdate] = useState<string>('');

  // 1. Initialize MapLibre
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const isMathura = (city && city.toLowerCase().includes('mathura')) || (origin && origin.city.toLowerCase().includes('mathura'));
    const isMumbai = (city && city.toLowerCase().includes('mumbai')) || (origin && origin.city.toLowerCase().includes('mumbai'));
    const isBengaluru = (city && (city.toLowerCase().includes('bengaluru') || city.toLowerCase().includes('bangalore'))) || (origin && origin.city.toLowerCase().includes('bengaluru'));

    const initialCenter: [number, number] = origin
      ? [origin.lon, origin.lat]
      : isMathura
      ? [77.6737, 27.4855]
      : isMumbai
      ? [72.8400, 19.0400]
      : isBengaluru
      ? [77.5946, 12.9716]
      : [77.2197, 28.6328];

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm-tiles': {
            type: 'raster',
            tiles: [
              'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors'
          }
        },
        layers: [
          {
            id: 'osm-layer',
            type: 'raster',
            source: 'osm-tiles',
            minzoom: 0,
            maxzoom: 19,
            paint: {
              'raster-saturation': -0.35,
              'raster-contrast': -0.05
            }
          }
        ]
      },
      center: initialCenter,
      zoom: 12
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');

    map.on('load', () => {
      mapRef.current = map;
      updateMapLayers();
    });

    return () => {
      markersRef.current.forEach(m => m.remove());
      markersRef.current = [];
      vehicleMarkersRef.current.forEach(m => m.remove());
      vehicleMarkersRef.current = [];
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // 2. Poll Live OTD Delhi vehicles every 3.5 seconds when active
  useEffect(() => {
    if (!showLiveGPS) {
      vehicleMarkersRef.current.forEach(m => m.remove());
      vehicleMarkersRef.current = [];
      return;
    }

    const loadVehicles = async () => {
      try {
        const targetCity = city || (origin && origin.city) || 'Delhi NCR';
        const data = await fetchLiveVehicles(targetCity);
        setLiveVehicles(data);
        setLastTelemetryUpdate(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
      } catch (e) {
        // ignore
      }
    };

    loadVehicles();
    const interval = setInterval(loadVehicles, 3500);
    return () => clearInterval(interval);
  }, [showLiveGPS, city, origin]);

  // 3. Render / Update Live Vehicle GPS Markers on the Map
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded() || !showLiveGPS) return;

    // Clear old vehicle markers
    vehicleMarkersRef.current.forEach(m => m.remove());
    vehicleMarkersRef.current = [];

    liveVehicles.forEach((veh) => {
      const el = document.createElement('div');
      el.className = 'group relative cursor-pointer';

      // Custom pulsing beacon with transit bus styling
      el.innerHTML = `
        <div class="relative flex items-center justify-center">
          <span class="absolute w-7 h-7 rounded-full bg-[#304B3C]/20 animate-ping"></span>
          <div class="relative flex items-center justify-center w-6 h-6 rounded-full bg-[#304B3C] text-white shadow-md border-2 border-white transition-transform duration-300 hover:scale-125">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/>
              <circle cx="7" cy="17" r="2"/>
              <circle cx="17" cy="17" r="2"/>
            </svg>
          </div>
          <span class="absolute -top-4 bg-[#F7F5EF] text-[#292D29] text-[9px] font-bold px-1.5 py-0.2 rounded border border-[#E3E0D6] shadow-xs whitespace-nowrap pointer-events-none">
            ${veh.route_short_name.split(' ')[0]}
          </span>
        </div>
      `;

      const popup = new maplibregl.Popup({ offset: 16 }).setHTML(`
        <div class="text-xs p-1">
          <div class="flex items-center justify-between gap-2 border-b border-[#E3E0D6] pb-1.5 mb-1.5">
            <span class="font-bold text-[#304B3C]">${veh.route_short_name}</span>
            <span class="text-[9px] font-mono bg-[#5B8A6E]/15 text-[#304B3C] px-1.5 py-0.5 rounded font-bold">LIVE GPS</span>
          </div>
          <p class="text-[11px] text-[#292D29]"><strong>Vehicle ID:</strong> ${veh.id}</p>
          <p class="text-[11px] text-[#77776F]"><strong>Agency:</strong> ${veh.agency}</p>
          <p class="text-[11px] text-[#77776F]"><strong>Speed:</strong> ${veh.speed_kmh} km/h • Bearing: ${veh.bearing}°</p>
          <p class="text-[10px] text-[#5B8A6E] mt-1.5 font-medium flex items-center gap-1">
            ✓ ${veh.data_source}
          </p>
        </div>
      `);

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([veh.lon, veh.lat])
        .setPopup(popup)
        .addTo(map);

      vehicleMarkersRef.current.push(marker);
    });
  }, [liveVehicles, showLiveGPS]);

  // 4. Update route layers & stop pins
  const updateMapLayers = () => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    const layerIds = ['active-transit-line', 'active-walk-line'];
    const sourceIds = ['active-transit-source', 'active-walk-source'];

    layerIds.forEach(id => {
      if (map.getLayer(id)) map.removeLayer(id);
    });
    sourceIds.forEach(id => {
      if (map.getSource(id)) map.removeSource(id);
    });

    for (let i = 0; i < 30; i++) {
      if (map.getLayer(`active-leg-line-${i}`)) map.removeLayer(`active-leg-line-${i}`);
      if (map.getLayer(`active-leg-casing-${i}`)) map.removeLayer(`active-leg-casing-${i}`);
      if (map.getSource(`active-leg-source-${i}`)) map.removeSource(`active-leg-source-${i}`);
    }

    for (let r = 0; r < 10; r++) {
      if (map.getLayer(`alt-route-line-${r}`)) map.removeLayer(`alt-route-line-${r}`);
      if (map.getSource(`alt-route-source-${r}`)) map.removeSource(`alt-route-source-${r}`);
    }

    const bounds = new maplibregl.LngLatBounds();
    let hasCoords = false;

    const activeRoute = selectedRoute || (allRoutes && allRoutes.length > 0 ? allRoutes[0] : null);

    // 1. Draw subtle background paths for alternate routes
    if (allRoutes && allRoutes.length > 1) {
      allRoutes.forEach((altRoute, altIdx) => {
        if (activeRoute && altRoute.id === activeRoute.id) return;
        const altCoords: [number, number][] = [];
        altRoute.legs.forEach(leg => {
          const coords = leg.path_coords && leg.path_coords.length > 0
            ? leg.path_coords
            : [leg.origin_coords, leg.destination_coords];
          coords.forEach(pt => altCoords.push(pt));
        });

        if (altCoords.length > 1) {
          map.addSource(`alt-route-source-${altIdx}`, {
            type: 'geojson',
            data: {
              type: 'Feature',
              properties: {},
              geometry: {
                type: 'LineString',
                coordinates: altCoords
              }
            }
          });

          map.addLayer({
            id: `alt-route-line-${altIdx}`,
            type: 'line',
            source: `alt-route-source-${altIdx}`,
            layout: {
              'line-join': 'round',
              'line-cap': 'round'
            },
            paint: {
              'line-color': '#8B949E',
              'line-width': 3,
              'line-dasharray': [2, 2],
              'line-opacity': 0.45
            }
          });
        }
      });
    }

    // 2. Draw Active/Selected Route with Outer Casing + Bold Colors
    if (activeRoute && activeRoute.legs.length > 0) {
      activeRoute.legs.forEach((leg, legIdx) => {
        const coords = leg.path_coords && leg.path_coords.length > 0
          ? leg.path_coords
          : [leg.origin_coords, leg.destination_coords];

        coords.forEach(pt => {
          bounds.extend(pt);
          hasCoords = true;
        });

        if (coords.length > 1) {
          map.addSource(`active-leg-source-${legIdx}`, {
            type: 'geojson',
            data: {
              type: 'Feature',
              properties: {},
              geometry: {
                type: 'LineString',
                coordinates: coords
              }
            }
          });

          if (leg.mode === 'walk') {
            // Distinct walking segment (dashed, dark charcoal)
            map.addLayer({
              id: `active-leg-line-${legIdx}`,
              type: 'line',
              source: `active-leg-source-${legIdx}`,
              layout: {
                'line-join': 'round',
                'line-cap': 'round'
              },
              paint: {
                'line-color': '#52544D',
                'line-width': 3.5,
                'line-dasharray': [1.8, 2],
                'line-opacity': 0.85
              }
            });
          } else {
            const legColor = leg.line_color || (
              leg.mode === 'auto' ? '#E68A00' :
              leg.mode === 'erickshaw' ? '#00897B' :
              leg.mode === 'ebus' ? '#00A86B' :
              leg.mode === 'taxi' ? '#3B5360' :
              leg.mode === 'bus' ? '#C8795A' : '#304B3C'
            );

            // High-contrast outer casing (Apple/Google Maps style)
            map.addLayer({
              id: `active-leg-casing-${legIdx}`,
              type: 'line',
              source: `active-leg-source-${legIdx}`,
              layout: {
                'line-join': 'round',
                'line-cap': 'round'
              },
              paint: {
                'line-color': '#FFFFFF',
                'line-width': 8,
                'line-opacity': 0.95
              }
            });

            // Vibrant mode color core line
            map.addLayer({
              id: `active-leg-line-${legIdx}`,
              type: 'line',
              source: `active-leg-source-${legIdx}`,
              layout: {
                'line-join': 'round',
                'line-cap': 'round'
              },
              paint: {
                'line-color': legColor,
                'line-width': 5.5,
                'line-opacity': 1.0
              }
            });
          }
        }
      });

      // Stop / Interchange Pins
      activeRoute.legs.forEach((leg) => {
        if (leg.mode !== 'walk') {
          const el = document.createElement('div');
          el.className = 'w-3.5 h-3.5 rounded-full bg-[#E5A919] border-2 border-white shadow-md cursor-pointer transition-transform hover:scale-125';
          el.title = leg.origin_name;

          const popup = new maplibregl.Popup({ offset: 12 }).setHTML(`
            <div class="text-xs p-1">
              <p class="font-bold text-[#304B3C]">${leg.line_name || 'Transit Line'}</p>
              <p class="text-[#77776F] font-semibold">${leg.origin_name}</p>
              <p class="text-[11px] text-[#292D29] mt-1">${leg.instructions}</p>
            </div>
          `);

          const marker = new maplibregl.Marker({ element: el })
            .setLngLat(leg.origin_coords)
            .setPopup(popup)
            .addTo(map);

          markersRef.current.push(marker);
        }
      });
    }

    // Origin Marker (A)
    if (origin) {
      bounds.extend([origin.lon, origin.lat]);
      hasCoords = true;

      const originEl = document.createElement('div');
      originEl.className = 'flex items-center justify-center w-8 h-8 rounded-full bg-[#2E5A3D] text-white font-extrabold text-xs shadow-lg border-2 border-white ring-2 ring-[#2E5A3D]/30';
      originEl.innerHTML = 'A';

      const originMarker = new maplibregl.Marker({ element: originEl })
        .setLngLat([origin.lon, origin.lat])
        .setPopup(new maplibregl.Popup({ offset: 16 }).setHTML(`
          <div class="text-xs">
            <span class="text-[10px] uppercase font-bold text-[#2E5A3D]">Origin</span>
            <h4 class="font-bold text-[#292D29]">${origin.name}</h4>
          </div>
        `))
        .addTo(map);

      markersRef.current.push(originMarker);
    }

    // Destination Marker (B)
    if (destination) {
      bounds.extend([destination.lon, destination.lat]);
      hasCoords = true;

      const destEl = document.createElement('div');
      destEl.className = 'flex items-center justify-center w-8 h-8 rounded-full bg-[#C8795A] text-white font-extrabold text-xs shadow-lg border-2 border-white ring-2 ring-[#C8795A]/30';
      destEl.innerHTML = 'B';

      const destMarker = new maplibregl.Marker({ element: destEl })
        .setLngLat([destination.lon, destination.lat])
        .setPopup(new maplibregl.Popup({ offset: 16 }).setHTML(`
          <div class="text-xs">
            <span class="text-[10px] uppercase font-bold text-[#C8795A]">Destination</span>
            <h4 class="font-bold text-[#292D29]">${destination.name}</h4>
          </div>
        `))
        .addTo(map);

      markersRef.current.push(destMarker);
    }

    if (hasCoords) {
      map.fitBounds(bounds, {
        padding: { top: 60, bottom: 60, left: 60, right: 60 },
        maxZoom: 14.5,
        duration: 900
      });
    }
  };

  useEffect(() => {
    updateMapLayers();
  }, [selectedRoute, allRoutes, origin, destination]);

  return (
    <div className={`relative w-full h-full rounded-2xl overflow-hidden border border-[#E3E0D6] shadow-sm bg-[#EEECE3] ${className}`}>
      <div ref={mapContainer} className="w-full h-full" />

      {/* Top Left: Open Transit Delhi Real-Time Telemetry Badge */}
      <div className="absolute top-3 left-3 z-10 flex flex-col gap-1.5">
        <button
          type="button"
          onClick={() => setShowLiveGPS(!showLiveGPS)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold shadow-xs border transition-all cursor-pointer backdrop-blur-md ${
            showLiveGPS
              ? 'bg-[#304B3C] text-white border-[#304B3C]'
              : 'bg-[#F7F5EF]/90 text-[#292D29] border-[#E3E0D6] hover:bg-white'
          }`}
        >
          <span className={`w-2 h-2 rounded-full ${showLiveGPS ? 'bg-[#5B8A6E] animate-pulse' : 'bg-[#77776F]'}`} />
          <span>Live Delhi Transit (OTD)</span>
          {showLiveGPS && (
            <span className="text-[10px] bg-white/20 px-1.5 py-0.2 rounded-full font-mono ml-0.5">
              {liveVehicles.length} buses
            </span>
          )}
        </button>

        {showLiveGPS && lastTelemetryUpdate && (
          <span className="text-[10px] text-[#304B3C] bg-[#F7F5EF]/90 backdrop-blur-xs px-2.5 py-0.5 rounded-lg border border-[#E3E0D6] shadow-xs inline-flex items-center gap-1 font-mono">
            <CheckCircle2 size={10} className="text-[#5B8A6E]" />
            OTD Key Active • {lastTelemetryUpdate}
          </span>
        )}
      </div>

      {/* Top Right: Legend Badge */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-2 bg-[#F7F5EF]/90 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-[#E3E0D6] text-xs text-[#292D29] shadow-sm">
        <span className="flex items-center gap-1">
          <span className="w-3 h-1 bg-[#304B3C] rounded-full inline-block" /> Transit
        </span>
        <span className="flex items-center gap-1 ml-2">
          <span className="w-3 h-0.5 border-t border-dashed border-[#77776F] inline-block" /> Walk
        </span>
        <span className="flex items-center gap-1 ml-2 text-[#304B3C] font-medium">
          <span className="w-2 h-2 rounded-full bg-[#304B3C] inline-block animate-ping" /> Bus GPS
        </span>
      </div>
    </div>
  );
};
