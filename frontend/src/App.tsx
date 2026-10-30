import React, { useState, useEffect, useRef } from 'react';
import { TopBar } from './components/layout/TopBar';
import { SidebarNavigation, NavTab } from './components/layout/SidebarNavigation';
import { DiscoverView } from './views/DiscoverView';
import { PlanJourneyView } from './views/PlanJourneyView';
import { LiveTransitView } from './views/LiveTransitView';
import { SavedRoutesView } from './views/SavedRoutesView';
import { SettingsView } from './views/SettingsView';
import { RaahiAssistant } from './components/assistant/RaahiAssistant';

import {
  planJourney,
  getTransitDelays,
  getSavedRoutes,
  deleteSavedRoute
} from './services/api';
import {
  RouteItinerary,
  GeoLocation,
  SavedRoute,
  TransitIncident,
  CityRealtimeContext,
  TravelPreferences,
  TimeMode,
  AppLanguage
} from './types/transit';

export const App: React.FC = () => {
  // Navigation & UI States
  const [activeTab, setActiveTab] = useState<NavTab>('discover');
  const [selectedCity, setSelectedCity] = useState<string>('Delhi NCR');
  const [language, setLanguage] = useState<AppLanguage>('en');
  const [isAssistantOpen, setIsAssistantOpen] = useState<boolean>(false);

  // Settings
  const [accessibleOnly, setAccessibleOnly] = useState<boolean>(false);
  const [reducedMotion, setReducedMotion] = useState<boolean>(false);

  // Journey Search State
  const [origin, setOrigin] = useState<string>('Rajiv Chowk (Connaught Place)');
  const [destination, setDestination] = useState<string>('Cyber City (Gurugram)');

  const handleCityChange = (newCity: string) => {
    setSelectedCity(newCity);
    let newOrigin = origin;
    let newDest = destination;
    if (newCity.toLowerCase().includes('mathura')) {
      newOrigin = 'Mathura Junction Railway Station (MTJ)';
      newDest = 'Shri Bankey Bihari Ji Mandir (Vrindavan)';
    } else if (newCity.includes('Delhi')) {
      newOrigin = 'Rajiv Chowk (Connaught Place)';
      newDest = 'Cyber City (Gurugram)';
    } else if (newCity.includes('Mumbai')) {
      newOrigin = 'Chhatrapati Shivaji Maharaj Terminus (CSMT)';
      newDest = 'Bandra Kurla Complex (BKC)';
    } else if (newCity.includes('Bengaluru')) {
      newOrigin = 'Majestic (KSR Bengaluru)';
      newDest = 'Whitefield (Kadugodi)';
    }
    setOrigin(newOrigin);
    setDestination(newDest);
    handleExecuteSearch(newOrigin, newDest, newCity);
  };
  const [preferences, setPreferences] = useState<TravelPreferences>({
    fastest: true,
    cheapest: false,
    less_crowded: false,
    fewer_transfers: false,
    less_walking: false,
    accessible: false,
    prefer_ebus: false,
    allow_auto: true,
    allow_taxi: true,
    pink_pass: false
  });

  // Routing Results
  const [routes, setRoutes] = useState<RouteItinerary[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<RouteItinerary | null>(null);
  const [originLocation, setOriginLocation] = useState<GeoLocation | null>(null);
  const [destLocation, setDestLocation] = useState<GeoLocation | null>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  // Incidents & Saved Routes Data
  const [incidents, setIncidents] = useState<TransitIncident[]>([]);
  const [realtimeContext, setRealtimeContext] = useState<CityRealtimeContext | null>(null);
  const [savedRoutes, setSavedRoutes] = useState<SavedRoute[]>([]);

  // Initial Data Fetch
  const refreshIncidents = async () => {
    try {
      const data = await getTransitDelays(selectedCity);
      setIncidents(data.active_disruptions || []);
      if (data.realtime_context) {
        setRealtimeContext(data.realtime_context);
      }
    } catch (err) {
      console.warn('Failed to load delays:', err);
    }
  };

  const refreshSavedRoutes = async () => {
    try {
      const list = await getSavedRoutes(selectedCity);
      setSavedRoutes(list);
    } catch (err) {
      console.warn('Failed to load saved routes:', err);
    }
  };

  useEffect(() => {
    refreshIncidents();
    refreshSavedRoutes();

    // Trigger initial search for realistic first view
    handleExecuteSearch();
  }, [selectedCity]);

  // WebSocket for Live Telemetry Updates
  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      const wsUrl = 'ws://127.0.0.1:8000/ws/telemetry';
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'SIMULATION_UPDATE') {
            refreshIncidents();
            // If user has routes computed, refresh route ranking seamlessly!
            handleExecuteSearch(undefined, undefined, undefined, undefined, undefined, undefined, true);
          }
        } catch (e) {
          // ignore
        }
      };
    } catch (err) {
      console.warn('WebSocket connection not available:', err);
    }

    return () => {
      if (ws) ws.close();
    };
  }, [origin, destination, selectedCity, preferences]);

  // Execute Route Planning
  const handleExecuteSearch = async (
    customOrigin?: string,
    customDestination?: string,
    customCity?: string,
    departureTime?: string,
    arrivalTime?: string,
    timeMode?: TimeMode,
    silent: boolean = false
  ) => {
    const o = customOrigin || origin;
    const d = customDestination || destination;
    const c = customCity || selectedCity;
    if (!o || !d) return;
    if (!silent) {
      setIsSearching(true);
      setActiveTab('plan'); // Immediately shift to 'plan' tab when tapping Search Journeys!
    }
    try {
      const res = await planJourney(
        o,
        d,
        c,
        departureTime,
        arrivalTime,
        timeMode,
        preferences
      );
      setRoutes(res.routes);
      setOriginLocation(res.origin);
      setDestLocation(res.destination);
      if (res.routes.length > 0) {
        setSelectedRoute(res.routes[0]);
      }
    } catch (err) {
      console.error('Journey planning error:', err);
    } finally {
      if (!silent) setIsSearching(false);
    }
  };

  // Stable references for background telemetry updates without triggering effect re-subscriptions
  const handleExecuteSearchRef = useRef(handleExecuteSearch);
  handleExecuteSearchRef.current = handleExecuteSearch;

  const refreshIncidentsRef = useRef(refreshIncidents);
  refreshIncidentsRef.current = refreshIncidents;

  useEffect(() => {
    refreshIncidents();
    refreshSavedRoutes();

    // Trigger initial search for realistic first view
    handleExecuteSearch();
  }, [selectedCity]);

  // WebSocket for Live Telemetry Updates (persistent single connection)
  useEffect(() => {
    let ws: WebSocket | null = null;
    let isMounted = true;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      if (!isMounted) return;
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        let wsUrl: string;
        if (apiUrl && (apiUrl.startsWith('http://') || apiUrl.startsWith('https://'))) {
          wsUrl = apiUrl.replace(/^http/, 'ws') + '/ws/telemetry';
        } else {
          const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
          wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;
        }

        ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data);
            if (payload.type === 'SIMULATION_UPDATE') {
              refreshIncidentsRef.current();
              // If user has routes computed, refresh route ranking seamlessly!
              handleExecuteSearchRef.current(undefined, undefined, undefined, undefined, undefined, undefined, true);
            }
          } catch {
            // ignore
          }
        };

        ws.onclose = () => {
          if (isMounted) {
            reconnectTimeout = setTimeout(connect, 4000);
          }
        };

        ws.onerror = () => {
          // Handled gracefully without logging uncaught errors
        };
      } catch (err) {
        console.warn('WebSocket connection not available:', err);
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        // Detach handlers first so callbacks don't fire during unmount
        ws.onopen = null;
        ws.onmessage = null;
        ws.onerror = null;
        ws.onclose = null;

        if (ws.readyState === WebSocket.CONNECTING) {
          // If still connecting, wait until open before calling close to prevent browser
          // "WebSocket is closed before the connection is established" error
          ws.onopen = () => {
            try {
              ws?.close();
            } catch {
              // ignore
            }
          };
        } else if (ws.readyState === WebSocket.OPEN) {
          try {
            ws.close();
          } catch {
            // ignore
          }
        }
      }
    };
  }, []);

  // Replan a Saved Commute
  const handleReplanSaved = (saved: SavedRoute) => {
    setOrigin(saved.origin);
    setDestination(saved.destination);
    setSelectedCity(saved.city);
    handleExecuteSearch(saved.origin, saved.destination, saved.city);
  };

  // Delete a Saved Commute
  const handleDeleteSaved = async (id: string) => {
    try {
      await deleteSavedRoute(id);
      refreshSavedRoutes();
    } catch (err) {
      console.error('Delete saved route failed:', err);
    }
  };

  // Plan alternative when disruption occurs
  const handlePlanAlternative = (lineName: string) => {
    // Switch preference to avoid crowd or fastest bypass
    setPreferences(prev => ({ ...prev, fastest: false, less_crowded: true }));
    handleExecuteSearch();
    setActiveTab('plan');
  };

  return (
    <div className="min-h-screen bg-[#F7F5EF] flex flex-col text-[#292D29]">
      {/* Top Bar */}
      <TopBar
        selectedCity={selectedCity}
        onCityChange={handleCityChange}
        language={language}
        onLanguageChange={(lang) => setLanguage(lang)}
        disruptionsCount={incidents.length}
        onOpenAssistant={() => setIsAssistantOpen(true)}
        onOpenNotifications={() => setActiveTab('live')}
      />

      {/* Main Container with Sidebar + Content */}
      <div className="flex-1 flex w-full">
        <SidebarNavigation
          activeTab={activeTab}
          onTabChange={(tab) => {
            if (tab === 'assistant') {
              setIsAssistantOpen(true);
            } else {
              setActiveTab(tab);
            }
          }}
          disruptionsCount={incidents.length}
          savedRoutesCount={savedRoutes.length}
        />

        {/* Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 pb-20 lg:pb-8 overflow-y-auto">
          {activeTab === 'discover' && (
            <DiscoverView
              origin={origin}
              destination={destination}
              city={selectedCity}
              preferences={preferences}
              savedRoutes={savedRoutes}
              incidents={incidents}
              onOriginChange={setOrigin}
              onDestinationChange={setDestination}
              onPreferencesChange={(p) => setPreferences(p)}
              onSearch={(depTime, arrTime, mode) => handleExecuteSearch(undefined, undefined, undefined, depTime, arrTime, mode)}
              onReplanSaved={handleReplanSaved}
              onNavigateToPlan={() => setActiveTab('plan')}
              onNavigateToLive={() => setActiveTab('live')}
              isLoading={isSearching}
            />
          )}

          {activeTab === 'plan' && (
            <PlanJourneyView
              originLocation={originLocation}
              destLocation={destLocation}
              routes={routes}
              selectedRoute={selectedRoute}
              city={selectedCity}
              onSelectRoute={setSelectedRoute}
              onBackToSearch={() => setActiveTab('discover')}
              onRouteSaved={refreshSavedRoutes}
              isLoading={isSearching}
            />
          )}

          {activeTab === 'live' && (
            <LiveTransitView
              incidents={incidents}
              city={selectedCity}
              realtimeContext={realtimeContext}
              onRefreshIncidents={refreshIncidents}
              onPlanAlternative={handlePlanAlternative}
            />
          )}

          {activeTab === 'saved' && (
            <SavedRoutesView
              savedRoutes={savedRoutes}
              city={selectedCity}
              onReplan={handleReplanSaved}
              onDelete={handleDeleteSaved}
              onRefresh={refreshSavedRoutes}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsView
              selectedCity={selectedCity}
              onCityChange={handleCityChange}
              language={language}
              onLanguageChange={setLanguage}
              accessibleOnly={accessibleOnly}
              onAccessibleChange={setAccessibleOnly}
              reducedMotion={reducedMotion}
              onReducedMotionChange={setReducedMotion}
            />
          )}
        </main>
      </div>

      {/* Floating / Slide-over Raahi AI Assistant */}
      <RaahiAssistant
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        onSelectRoute={(r) => {
          setSelectedRoute(r);
          setActiveTab('plan');
        }}
        onNavigateToPlan={() => setActiveTab('plan')}
        onNavigateToSaved={() => setActiveTab('saved')}
        onNavigateToLive={() => setActiveTab('live')}
        contextOrigin={origin}
        contextDestination={destination}
        city={selectedCity}
        language={language}
      />
    </div>
  );
};

export default App;
