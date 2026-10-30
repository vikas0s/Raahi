import {
  PlanResponse,
  TransitIncident,
  CityRealtimeContext,
  SavedRoute,
  TravelPreferences,
  TimeMode,
  RouteItinerary,
  GeoLocation,
  RailStation,
  TrainSchedule,
  LiveRunningStatus,
  StationBoardResponse,
  RailSearchResponse,
  ReverseGeocodeResult,
  AssistantChatResponse
} from '../types/transit';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function searchPlaces(query: string, city: string = 'Delhi NCR'): Promise<GeoLocation[]> {
  try {
    const res = await fetch(`${API_BASE}/places/search?q=${encodeURIComponent(query)}&city=${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error('Search failed');
    const data = await res.json();
    return data.results || [];
  } catch (err) {
    console.warn('API error in searchPlaces, returning local fallback:', err);
    // Local fallback for smooth offline/resilience
    if (city.toLowerCase().includes('mumbai')) {
      return [
        { name: 'Chhatrapati Shivaji Maharaj Terminus (CSMT)', lat: 18.9400, lon: 72.8353, category: 'railway_station', city },
        { name: 'Bandra Kurla Complex (BKC)', lat: 19.0657, lon: 72.8687, category: 'landmark', city },
        { name: 'Andheri Station', lat: 19.1197, lon: 72.8464, category: 'metro_station', city },
        { name: 'Ghatkopar Station', lat: 19.0863, lon: 72.9084, category: 'metro_station', city },
        { name: 'Churchgate Railway Station', lat: 18.9322, lon: 72.8264, category: 'railway_station', city },
        { name: 'Dadar Station (Central & Western interchange)', lat: 19.0178, lon: 72.8478, category: 'railway_station', city }
      ];
    } else if (city.toLowerCase().includes('mathura') || city.toLowerCase().includes('vrindavan')) {
      return [
        { name: 'Mathura Junction Railway Station (MTJ)', lat: 27.4855, lon: 77.6737, category: 'railway_station', city },
        { name: 'Shri Bankey Bihari Ji Mandir (Vrindavan)', lat: 27.5804, lon: 77.7006, category: 'landmark', city },
        { name: 'Shri Krishna Janmabhoomi (Janmasthan)', lat: 27.5050, lon: 77.6698, category: 'landmark', city },
        { name: 'Prem Mandir (Vrindavan)', lat: 27.5724, lon: 77.6710, category: 'landmark', city },
        { name: 'Chhata', lat: 27.7214, lon: 77.5042, category: 'railway_station', city }
      ];
    } else if (city.toLowerCase().includes('bengaluru') || city.toLowerCase().includes('bangalore')) {
      return [
        { name: 'Majestic (KSR Bengaluru)', lat: 12.9781, lon: 77.5695, category: 'railway_station', city },
        { name: 'Whitefield (Kadugodi)', lat: 12.9961, lon: 77.7601, category: 'metro_station', city },
        { name: 'Indiranagar 100ft Road', lat: 12.9784, lon: 77.6408, category: 'landmark', city },
        { name: 'Electronic City Phase 1', lat: 12.8452, lon: 77.6602, category: 'landmark', city }
      ];
    }
    return [
      { name: 'Rajiv Chowk (Connaught Place)', lat: 28.6328, lon: 77.2197, category: 'metro_station', city },
      { name: 'Cyber City (Gurugram)', lat: 28.4950, lon: 77.0895, category: 'landmark', city },
      { name: 'Lajpat Nagar 2 (Central Market)', lat: 28.5695, lon: 77.2420, category: 'market', city },
      { name: 'Janakpuri District Centre (D-Block)', lat: 28.6295, lon: 77.0780, category: 'market', city },
      { name: 'Rohini Sector 7 & 8 (M2K Cinema & Sai Mandir)', lat: 28.7080, lon: 77.1260, category: 'residential_block', city },
      { name: 'Dwarka Sector 14 (Vegas Mall & NLU)', lat: 28.6010, lon: 77.0260, category: 'market', city },
      { name: 'Laxmi Nagar (Vikas Marg)', lat: 28.6310, lon: 77.2780, category: 'market', city },
      { name: 'Shahpur Jat (Fashion Village)', lat: 28.5480, lon: 77.2185, category: 'village', city },
      { name: 'Sangam Vihar (Blocks A to L & Ratia Marg)', lat: 28.5020, lon: 77.2420, category: 'residential_block', city },
      { name: 'New Delhi Railway Station (NDLS)', lat: 28.6431, lon: 77.2223, category: 'railway_station', city }
    ];
  }
}

export async function planJourney(
  origin: string,
  destination: string,
  city: string = 'Delhi NCR',
  departureTime?: string,
  arrivalTime?: string,
  timeMode: TimeMode = 'now',
  preferences?: Partial<TravelPreferences>,
  originCoords?: [number, number],
  destinationCoords?: [number, number]
): Promise<PlanResponse> {
  const payload = {
    origin,
    destination,
    city,
    origin_coords: originCoords,
    destination_coords: destinationCoords,
    departure_time: departureTime,
    arrival_time: arrivalTime,
    time_mode: timeMode,
    preferences: {
      fastest: preferences?.fastest ?? true,
      cheapest: preferences?.cheapest ?? false,
      less_crowded: preferences?.less_crowded ?? false,
      fewer_transfers: preferences?.fewer_transfers ?? false,
      less_walking: preferences?.less_walking ?? false,
      accessible: preferences?.accessible ?? false,
      prefer_ebus: preferences?.prefer_ebus ?? false,
      allow_auto: preferences?.allow_auto ?? true,
      allow_taxi: preferences?.allow_taxi ?? true,
      pink_pass: preferences?.pink_pass ?? false,
      prefer_multimodal: preferences?.prefer_multimodal ?? false,
      prefer_rail: preferences?.prefer_rail ?? false
    }
  };

  const res = await fetch(`${API_BASE}/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`Journey plan request failed: ${res.status} ${errorBody}`);
  }

  return res.json();
}

export async function getTransitDelays(city: string = 'Delhi NCR'): Promise<{
  city?: string;
  active_disruptions: TransitIncident[];
  total_disruptions: number;
  realtime_context?: CityRealtimeContext;
  delays_summary: Record<string, number>;
}> {
  try {
    const res = await fetch(`${API_BASE}/delays?city=${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error('Failed to fetch delays');
    return res.json();
  } catch (err) {
    console.warn('Delays fetch failed:', err);
    return {
      active_disruptions: [],
      total_disruptions: 0,
      delays_summary: {}
    };
  }
}

export async function simulateDelay(
  scenario: string,
  city: string = 'Delhi NCR',
  targetLine?: string,
  delayMinutes?: number
) {
  const res = await fetch(`${API_BASE}/simulate/delay`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario,
      city,
      target_line: targetLine,
      delay_minutes: delayMinutes
    })
  });
  if (!res.ok) throw new Error('Simulation trigger failed');
  return res.json();
}

export async function chatWithAssistant(
  message: string,
  language: 'en' | 'hi' = 'en',
  contextOrigin?: string,
  contextDestination?: string,
  city: string = 'Delhi NCR',
  sessionId?: string
): Promise<AssistantChatResponse> {
  const res = await fetch(`${API_BASE}/api/assistant/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      language,
      context_origin: contextOrigin,
      context_destination: contextDestination,
      city,
      session_id: sessionId
    })
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || 'Chat request failed');
  }
  return res.json();
}

export async function resetAssistantSession(sessionId: string): Promise<void> {
  try {
    await fetch(`${API_BASE}/api/assistant/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
  } catch (err) {
    console.warn('Failed to reset assistant session:', err);
  }
}

export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const formData = new FormData();
  const ext = audioBlob.type.includes('wav') ? 'wav' : (audioBlob.type.includes('mp3') ? 'mp3' : 'wav');
  formData.append('file', audioBlob, `voice_query.${ext}`);
  const res = await fetch(`${API_BASE}/api/assistant/transcribe`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || 'Audio transcription failed');
  }
  const data = await res.json();
  return data.transcript || '';
}

export async function synthesizeSpeech(text: string, languageCode: string = 'hi-IN'): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE}/api/assistant/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language_code: languageCode, speaker: 'meera' })
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.audio_base64 || null;
  } catch {
    return null;
  }
}

export async function getSavedRoutes(city?: string): Promise<SavedRoute[]> {
  try {
    const url = city ? `${API_BASE}/saved-routes?city=${encodeURIComponent(city)}` : `${API_BASE}/saved-routes`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to get saved routes');
    return res.json();
  } catch (err) {
    console.warn('Saved routes API error:', err);
    return [];
  }
}

export async function createSavedRoute(
  name: string,
  origin: string,
  destination: string,
  city: string = 'Delhi NCR',
  preferredMode: string = 'fastest'
): Promise<SavedRoute> {
  const res = await fetch(`${API_BASE}/saved-routes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name,
      origin,
      destination,
      city,
      preferred_mode: preferredMode
    })
  });
  if (!res.ok) throw new Error('Failed to create saved route');
  return res.json();
}

export async function deleteSavedRoute(id: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/saved-routes/${id}`, {
    method: 'DELETE'
  });
  return res.ok;
}

export async function fetchLiveVehicles(city: string = 'Delhi NCR') {
  try {
    const res = await fetch(`${API_BASE}/transit/live-vehicles?city=${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error('Live vehicles fetch failed');
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch live transit vehicles:', err);
    return [];
  }
}

// ==============================================================================
// Raahi RailConnect — Indian Railways API Client
// ==============================================================================

export async function searchRailStations(query: string = '', city?: string): Promise<RailStation[]> {
  try {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (city) params.append('city', city);
    const res = await fetch(`${API_BASE}/api/rail/stations?${params.toString()}`);
    if (!res.ok) throw new Error('Station search failed');
    return await res.json();
  } catch (err) {
    console.warn('Rail station search failed:', err);
    return [];
  }
}

export async function getTrainsBetweenStations(
  fromStation: string,
  toStation: string,
  date?: string
): Promise<RailSearchResponse> {
  const params = new URLSearchParams({
    from_station: fromStation,
    to_station: toStation
  });
  if (date) params.append('date', date);
  const res = await fetch(`${API_BASE}/api/rail/trains?${params.toString()}`);
  if (!res.ok) throw new Error('Trains lookup failed');
  return await res.json();
}

export async function getTrainSchedule(trainNo: string): Promise<TrainSchedule> {
  const res = await fetch(`${API_BASE}/api/rail/schedule/${encodeURIComponent(trainNo)}`);
  if (!res.ok) throw new Error(`Train schedule fetch failed for ${trainNo}`);
  return await res.json();
}

export async function getLiveTrainStatus(trainNo: string, date?: string): Promise<LiveRunningStatus> {
  const url = date
    ? `${API_BASE}/api/rail/live-status/${encodeURIComponent(trainNo)}?date=${encodeURIComponent(date)}`
    : `${API_BASE}/api/rail/live-status/${encodeURIComponent(trainNo)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Live status fetch failed for ${trainNo}`);
  return await res.json();
}

export async function getStationLiveBoard(stationCode: string, hours: number = 4): Promise<StationBoardResponse> {
  const res = await fetch(`${API_BASE}/api/rail/station-board/${encodeURIComponent(stationCode)}?hours=${hours}`);
  if (!res.ok) throw new Error(`Station board fetch failed for ${stationCode}`);
  return await res.json();
}

export async function reverseGeocode(lat: number, lon: number): Promise<ReverseGeocodeResult> {
  try {
    const res = await fetch(`${API_BASE}/places/reverse-geocode?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
    if (!res.ok) throw new Error('Reverse geocoding failed');
    return await res.json();
  } catch (err) {
    console.warn('Reverse geocoding API error:', err);
    return {
      status: 'fallback',
      lat,
      lon,
      city: 'Current Location',
      matched_transit_city: null,
      locality: 'Current Location'
    };
  }
}
