import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as maplibregl from 'maplibre-gl';
import { config } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url';

if (typeof window !== 'undefined') {
  config.WORKER_URL = maplibreWorkerUrl;
}

import { RouteItinerary, GeoLocation, LiveVehicle } from '../../types/transit';
import { fetchLiveVehicles } from '../../services/api';
import { CheckCircle2, Crosshair, Navigation } from 'lucide-react';
import { useLocation } from '../../context/LocationContext';

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
  onSelectRoute,
  className = '',
  city
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [isMapReady, setIsMapReady] = useState<boolean>(false);

  // Markers
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const vehicleMarkersRef = useRef<maplibregl.Marker[]>([]);
  const userLocationMarkerRef = useRef<maplibregl.Marker | null>(null);

  // User Geolocation from context
  const {
    latitude: userLat,
    longitude: userLon,
    accuracy: userAcc,
    detectedLocality,
    hasExplicitlyLocated,
    recenterCount,
    recenterMap
  } = useLocation();

  const initialCenteredRef = useRef<boolean>(false);
  const lastCenteredCountRef = useRef<number>(0);

  // Always keep latest props accessible to event callbacks without stale closures
  const propsRef = useRef({ selectedRoute, allRoutes, origin, destination, onSelectRoute, city });
  propsRef.current = { selectedRoute, allRoutes, origin, destination, onSelectRoute, city };

  // Open Transit Data Real-time GPS toggle
  const [showLiveGPS, setShowLiveGPS] = useState<boolean>(true);
  const [liveVehicles, setLiveVehicles] = useState<LiveVehicle[]>([]);
  const [lastTelemetryUpdate, setLastTelemetryUpdate] = useState<string>('');

  // Helper: Safely clear existing custom layers and sources
  const clearCustomLayers = useCallback((map: maplibregl.Map) => {
    try {
      const style = map.getStyle();
      if (!style) return;

      // 1. Remove custom layers first
      if (Array.isArray(style.layers)) {
        style.layers.forEach((l) => {
          if (
            l.id.startsWith('active-leg-') ||
            l.id.startsWith('alt-route-') ||
            l.id.startsWith('active-transit-') ||
            l.id.startsWith('active-walk-')
          ) {
            try {
              if (map.getLayer(l.id)) {
                map.removeLayer(l.id);
              }
            } catch {
              // ignore
            }
          }
        });
      }

      // 2. Remove custom sources after all custom layers have been removed
      if (style.sources) {
        Object.keys(style.sources).forEach((sId) => {
          if (
            sId.startsWith('active-leg-') ||
            sId.startsWith('alt-route-') ||
            sId.startsWith('active-transit-') ||
            sId.startsWith('active-walk-')
          ) {
            try {
              if (map.getSource(sId)) {
                map.removeSource(sId);
              }
            } catch {
              // ignore
            }
          }
        });
      }
    } catch (e) {
      console.warn('Error clearing custom map layers:', e);
    }
  }, []);

  // Update Route Polyline Layers, Markers, and Camera Bounds
  const updateMapLayers = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    const render = () => {
      if (!mapRef.current) return;

      try {
        map.resize();
      } catch {
        // ignore
      }

      // Clear previous route & stop markers (preserving user location marker)
      markersRef.current.forEach((m) => {
        try {
          m.remove();
        } catch {
          // ignore
        }
      });
      markersRef.current = [];

      // Clear previous route layers & sources
      clearCustomLayers(map);

      const activeRoute = selectedRoute || (allRoutes && allRoutes.length > 0 ? allRoutes[0] : null);
      const bounds = new maplibregl.LngLatBounds();
      let hasCoords = false;

      // 1. Draw subtle background paths for alternate routes
      if (allRoutes && allRoutes.length > 1) {
        allRoutes.forEach((altRoute, altIdx) => {
          if (activeRoute && altRoute.id === activeRoute.id) return;

          const altCoords: [number, number][] = [];
          (altRoute.legs || []).forEach((leg) => {
            const raw = leg.path_coords && leg.path_coords.length >= 2
              ? leg.path_coords
              : [leg.origin_coords, leg.destination_coords];

            (raw || []).forEach((pt) => {
              if (Array.isArray(pt) && pt.length >= 2 && !isNaN(pt[0]) && !isNaN(pt[1])) {
                altCoords.push([pt[0], pt[1]]);
              }
            });
          });

          if (altCoords.length >= 2) {
            const sourceId = `alt-route-source-${altIdx}`;
            const layerId = `alt-route-line-${altIdx}`;

            try {
              if (map.getLayer(layerId)) map.removeLayer(layerId);
              if (map.getSource(sourceId)) map.removeSource(sourceId);

              map.addSource(sourceId, {
                type: 'geojson',
                data: {
                  type: 'Feature',
                  properties: { routeId: altRoute.id },
                  geometry: {
                    type: 'LineString',
                    coordinates: altCoords
                  }
                }
              });

              map.addLayer({
                id: layerId,
                type: 'line',
                source: sourceId,
                layout: {
                  'line-join': 'round',
                  'line-cap': 'round'
                },
                paint: {
                  'line-color': '#7A847B',
                  'line-width': 3,
                  'line-dasharray': [2, 2],
                  'line-opacity': 0.45
                }
              });
            } catch (err) {
              console.warn(`Failed to add alternate route ${altIdx}:`, err);
            }
          }
        });
      }

      // 2. Draw Active / Selected Route with Outer Casing + Bold Colors
      if (activeRoute && activeRoute.legs && activeRoute.legs.length > 0) {
        activeRoute.legs.forEach((leg, legIdx) => {
          const rawCoords = leg.path_coords && leg.path_coords.length >= 2
            ? leg.path_coords
            : [leg.origin_coords, leg.destination_coords];

          const validCoords: [number, number][] = [];
          (rawCoords || []).forEach((pt) => {
            if (Array.isArray(pt) && pt.length >= 2 && !isNaN(pt[0]) && !isNaN(pt[1])) {
              const coord: [number, number] = [pt[0], pt[1]];
              validCoords.push(coord);
              bounds.extend(coord);
              hasCoords = true;
            }
          });

          if (validCoords.length >= 2) {
            const sourceId = `active-leg-source-${legIdx}`;
            const casingId = `active-leg-casing-${legIdx}`;
            const lineId = `active-leg-line-${legIdx}`;

            try {
              if (map.getLayer(casingId)) map.removeLayer(casingId);
              if (map.getLayer(lineId)) map.removeLayer(lineId);
              if (map.getSource(sourceId)) map.removeSource(sourceId);

              map.addSource(sourceId, {
                type: 'geojson',
                data: {
                  type: 'Feature',
                  properties: {},
                  geometry: {
                    type: 'LineString',
                    coordinates: validCoords
                  }
                }
              });

              if (leg.mode === 'walk') {
                // Walking segment: dashed dark slate path
                map.addLayer({
                  id: lineId,
                  type: 'line',
                  source: sourceId,
                  layout: {
                    'line-join': 'round',
                    'line-cap': 'round'
                  },
                  paint: {
                    'line-color': '#3D483F',
                    'line-width': 4.5,
                    'line-dasharray': [2, 2],
                    'line-opacity': 0.95
                  }
                });
              } else {
                const legColor = leg.line_color || (
                  leg.mode === 'auto' ? '#E68A00' :
                  leg.mode === 'erickshaw' ? '#00897B' :
                  leg.mode === 'ebus' ? '#00A86B' :
                  leg.mode === 'taxi' ? '#2F5D7C' :
                  leg.mode === 'bus' ? '#C8795A' : '#304B3C'
                );

                // Outer white casing for sharp contrast
                map.addLayer({
                  id: casingId,
                  type: 'line',
                  source: sourceId,
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

                // Vibrant core mode color line
                map.addLayer({
                  id: lineId,
                  type: 'line',
                  source: sourceId,
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
            } catch (err) {
              console.warn(`Failed to add leg ${legIdx} line:`, err);
            }
          }

          // Stop / Interchange Pins
          if (leg.mode !== 'walk' && Array.isArray(leg.origin_coords) && leg.origin_coords.length >= 2) {
            try {
              const el = document.createElement('div');
              el.className = 'w-4 h-4 rounded-full bg-[#E5A919] border-2 border-white shadow-md cursor-pointer transition-transform hover:scale-125';
              el.title = leg.origin_name;

              const popup = new maplibregl.Popup({ offset: 12 }).setHTML(`
                <div class="text-xs p-1">
                  <p class="font-bold text-[#304B3C]">${leg.line_name || 'Transit Line'}</p>
                  <p class="text-[#55554D] font-semibold">${leg.origin_name}</p>
                  <p class="text-[11px] text-[#292D29] mt-1">${leg.instructions || ''}</p>
                </div>
              `);

              const marker = new maplibregl.Marker({ element: el })
                .setLngLat(leg.origin_coords)
                .setPopup(popup)
                .addTo(map);

              markersRef.current.push(marker);
            } catch (err) {
              console.warn('Failed to add stop marker:', err);
            }
          }
        });
      }

      // 3. Resolve Origin (A) Coordinates
      let originPt: [number, number] | null = null;
      let originLabel = 'Origin';
      if (origin && typeof origin.lon === 'number' && typeof origin.lat === 'number') {
        originPt = [origin.lon, origin.lat];
        originLabel = origin.name;
      } else if (activeRoute && activeRoute.legs && activeRoute.legs.length > 0) {
        originPt = activeRoute.legs[0].origin_coords;
        originLabel = activeRoute.legs[0].origin_name;
      }

      if (originPt) {
        bounds.extend(originPt);
        hasCoords = true;

        const originEl = document.createElement('div');
        originEl.className = 'flex items-center justify-center w-8 h-8 rounded-full bg-[#2E5A3D] text-white font-extrabold text-xs shadow-lg border-2 border-white ring-2 ring-[#2E5A3D]/40 cursor-pointer';
        originEl.innerHTML = 'A';

        const originMarker = new maplibregl.Marker({ element: originEl })
          .setLngLat(originPt)
          .setPopup(new maplibregl.Popup({ offset: 16 }).setHTML(`
            <div class="text-xs">
              <span class="text-[10px] uppercase font-bold text-[#2E5A3D]">Origin</span>
              <h4 class="font-bold text-[#1F231F]">${originLabel}</h4>
            </div>
          `))
          .addTo(map);

        markersRef.current.push(originMarker);
      }

      // 4. Resolve Destination (B) Coordinates
      let destPt: [number, number] | null = null;
      let destLabel = 'Destination';
      if (destination && typeof destination.lon === 'number' && typeof destination.lat === 'number') {
        destPt = [destination.lon, destination.lat];
        destLabel = destination.name;
      } else if (activeRoute && activeRoute.legs && activeRoute.legs.length > 0) {
        const lastLeg = activeRoute.legs[activeRoute.legs.length - 1];
        destPt = lastLeg.destination_coords;
        destLabel = lastLeg.destination_name;
      }

      if (destPt) {
        bounds.extend(destPt);
        hasCoords = true;

        const destEl = document.createElement('div');
        destEl.className = 'flex items-center justify-center w-8 h-8 rounded-full bg-[#C8795A] text-white font-extrabold text-xs shadow-lg border-2 border-white ring-2 ring-[#C8795A]/40 cursor-pointer';
        destEl.innerHTML = 'B';

        const destMarker = new maplibregl.Marker({ element: destEl })
          .setLngLat(destPt)
          .setPopup(new maplibregl.Popup({ offset: 16 }).setHTML(`
            <div class="text-xs">
              <span class="text-[10px] uppercase font-bold text-[#C8795A]">Destination</span>
              <h4 class="font-bold text-[#1F231F]">${destLabel}</h4>
            </div>
          `))
          .addTo(map);

        markersRef.current.push(destMarker);
      }

      // 5. Auto-fit camera smoothly to show entire journey if route exists
      if (hasCoords && !bounds.isEmpty()) {
        try {
          map.fitBounds(bounds, {
            padding: { top: 70, bottom: 70, left: 70, right: 70 },
            maxZoom: 14.2,
            duration: 800
          });
        } catch (err) {
          console.warn('Map fitBounds error:', err);
        }
      }
    };

    // Render immediately if style is ready or map is loaded, and also attach idle listener to settle tiles
    if (map.isStyleLoaded() || map.loaded()) {
      render();
    } else {
      map.once('idle', render);
    }
  }, [clearCustomLayers, selectedRoute, allRoutes, origin, destination]);

  // 1. Initialize MapLibre
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const isMathura = (city && city.toLowerCase().includes('mathura')) || (origin && origin.city.toLowerCase().includes('mathura'));
    const isMumbai = (city && city.toLowerCase().includes('mumbai')) || (origin && origin.city.toLowerCase().includes('mumbai'));
    const isBengaluru = (city && (city.toLowerCase().includes('bengaluru') || city.toLowerCase().includes('bangalore'))) || (origin && origin.city.toLowerCase().includes('bengaluru'));

    // Only use user coordinates if user explicitly requested location
    const initialCenter: [number, number] = hasExplicitlyLocated && userLon && userLat
      ? [userLon, userLat]
      : origin
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
      zoom: userLon && userLat ? 14 : 12
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');

    map.on('load', () => {
      mapRef.current = map;
      setIsMapReady(true);
      updateMapLayers();
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      vehicleMarkersRef.current.forEach((m) => m.remove());
      vehicleMarkersRef.current = [];
      if (userLocationMarkerRef.current) {
        userLocationMarkerRef.current.remove();
        userLocationMarkerRef.current = null;
      }
      map.remove();
      mapRef.current = null;
      setIsMapReady(false);
    };
  }, []);

  // 2. Trigger route layer update whenever map is ready OR route/origin/destination props update
  useEffect(() => {
    if (isMapReady && mapRef.current) {
      updateMapLayers();
    }
  }, [isMapReady, selectedRoute, allRoutes, origin, destination, updateMapLayers]);

  // 3. User Geolocation Marker Integration (Blue dot with pulsing halo & accuracy)
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isMapReady || !hasExplicitlyLocated || userLat === null || userLon === null) return;

    const userCoord: [number, number] = [userLon, userLat];

    if (userLocationMarkerRef.current) {
      // Update existing marker position without creating duplicates
      userLocationMarkerRef.current.setLngLat(userCoord);
    } else {
      // Create modern pulsing blue dot marker
      const el = document.createElement('div');
      el.className = 'relative flex items-center justify-center cursor-pointer group';
      el.innerHTML = `
        <span class="absolute w-8 h-8 rounded-full bg-[#2563EB]/25 animate-ping"></span>
        <span class="absolute w-5 h-5 rounded-full bg-[#3B82F6]/30 animate-pulse"></span>
        <div class="relative w-4 h-4 rounded-full bg-[#2563EB] border-2 border-white shadow-md transition-transform duration-200 group-hover:scale-125"></div>
      `;

      const popup = new maplibregl.Popup({ offset: 14 }).setHTML(`
        <div class="text-xs p-1">
          <div class="flex items-center gap-1.5 font-bold text-[#2563EB] border-b border-[#E3E0D6] pb-1 mb-1">
            <span class="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse"></span>
            <span>Your Current Location</span>
          </div>
          <p class="font-bold text-[#1F231F]">${detectedLocality || 'Live GPS Position'}</p>
          ${userAcc ? `<p class="text-[10px] text-[#52544D] mt-0.5 font-medium">Accuracy: ±${Math.round(userAcc)}m</p>` : ''}
        </div>
      `);

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(userCoord)
        .setPopup(popup)
        .addTo(map);

      userLocationMarkerRef.current = marker;
    }

    // Auto-center on first detected location if user hasn't searched yet
    if (!initialCenteredRef.current && (!selectedRoute || selectedRoute.legs.length === 0)) {
      initialCenteredRef.current = true;
      map.flyTo({
        center: userCoord,
        zoom: 14.2,
        duration: 900
      });
    }
  }, [isMapReady, userLat, userLon, userAcc, detectedLocality, selectedRoute]);

  // 4. Handle Recenter Map Action
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isMapReady || !hasExplicitlyLocated || userLat === null || userLon === null) return;

    if (recenterCount > 0 && recenterCount !== lastCenteredCountRef.current) {
      lastCenteredCountRef.current = recenterCount;
      map.flyTo({
        center: [userLon, userLat],
        zoom: 14.5,
        duration: 800
      });
    }
  }, [recenterCount, isMapReady, userLat, userLon]);

  // 5. Poll Live OTD Delhi vehicles every 4 seconds when active
  useEffect(() => {
    if (!showLiveGPS) {
      vehicleMarkersRef.current.forEach((m) => m.remove());
      vehicleMarkersRef.current = [];
      return;
    }

    const loadVehicles = async () => {
      try {
        const targetCity = city || (origin && origin.city) || 'Delhi NCR';
        const data = await fetchLiveVehicles(targetCity);
        setLiveVehicles(data);
        setLastTelemetryUpdate(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
      } catch {
        // ignore
      }
    };

    loadVehicles();
    const interval = setInterval(loadVehicles, 4000);
    return () => clearInterval(interval);
  }, [showLiveGPS, city, origin]);

  // 6. Render / Update Live Vehicle GPS Markers on the Map
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isMapReady || !map.isStyleLoaded() || !showLiveGPS) return;

    // Clear old vehicle markers
    vehicleMarkersRef.current.forEach((m) => m.remove());
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
  }, [liveVehicles, showLiveGPS, isMapReady]);

  return (
    <div className={`relative w-full h-full rounded-2xl overflow-hidden border border-[#E3E0D6] shadow-sm bg-[#EEECE3] ${className}`}>
      <div ref={mapContainer} className="w-full h-full" />

      {/* Floating Action: Use My Current Location / Recenter Map */}
      <div className="absolute bottom-24 right-2.5 z-10 flex flex-col gap-2">
        <button
          type="button"
          onClick={recenterMap}
          title={userLat !== null ? "Center map on your current location" : "Detect your current location"}
          className="flex items-center justify-center w-8.5 h-8.5 rounded-xl bg-[#FFFEFA]/95 hover:bg-[#FFFEFA] text-[#2563EB] shadow-md border border-[#D8D4C7] transition-all cursor-pointer hover:scale-105 active:scale-95 backdrop-blur-xs"
        >
          <Crosshair size={18} className="stroke-[2.4]" />
        </button>
      </div>

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
        <span className="flex items-center gap-1 text-[#2563EB] font-bold">
          <span className="w-2.5 h-2.5 rounded-full bg-[#2563EB] inline-block border border-white shadow-xs" /> You
        </span>
        <span className="flex items-center gap-1 ml-1.5">
          <span className="w-3 h-1 bg-[#304B3C] rounded-full inline-block" /> Transit
        </span>
        <span className="flex items-center gap-1 ml-1.5">
          <span className="w-3 h-0.5 border-t border-dashed border-[#77776F] inline-block" /> Walk
        </span>
        <span className="flex items-center gap-1 ml-1.5 text-[#304B3C] font-medium">
          <span className="w-2 h-2 rounded-full bg-[#304B3C] inline-block animate-ping" /> Bus GPS
        </span>
      </div>
    </div>
  );
};
