import {
  PlanResponse,
  TransitIncident,
  CityRealtimeContext,
  SavedRoute,
  TravelPreferences,
  TimeMode,
  GeoLocation,
  RailStation,
  TrainSchedule,
  LiveRunningStatus,
  StationBoardResponse,
  RailSearchResponse,
  ReverseGeocodeResult,
  AssistantChatResponse
} from '../types/transit';
import type { User, AuthResponse } from '../types/auth';

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


// ==============================================================================
// Persistent MongoDB Database API Clients
// ==============================================================================

export interface DatabaseHealth {
  status: string;
  database: string;
  engine: string;
  latency_ms: number;
  collections_count: number;
  ping: boolean;
  is_connected: boolean;
  error?: string | null;
}

export interface CityData {
  id: string;
  name: string;
  country: string;
  timezone: string;
  center_lat: number;
  center_lon: number;
  is_active: boolean;
  supported_transport_modes: string[];
}

export interface StationData {
  id: string;
  name: string;
  city_id: string;
  latitude: number;
  longitude: number;
  stop_type: string;
  external_stop_id?: string | null;
  source?: string | null;
}

export interface SavedPlace {
  id: string;
  user_id: string;
  name: string;
  address: string;
  category: string;
  latitude: number;
  longitude: number;
  city: string;
  created_at: string;
}

export interface UserPreferencesData {
  id: string;
  user_id: string;
  preferred_language: string;
  selected_city: string;
  accessible_only: boolean;
  reduced_motion: boolean;
  travel_preferences: Record<string, any>;
}

export async function fetchDbHealth(): Promise<DatabaseHealth> {
  try {
    const res = await fetch(`${API_BASE}/api/health/database`);
    if (!res.ok) throw new Error('Database health check failed');
    return await res.json();
  } catch {
    return {
      status: 'disconnected',
      database: 'raahi',
      engine: 'MongoDB',
      latency_ms: -1,
      collections_count: 0,
      ping: false,
      is_connected: false,
      error: 'Cannot reach backend database service'
    };
  }
}

export async function fetchCities(): Promise<CityData[]> {
  try {
    const res = await fetch(`${API_BASE}/api/cities`);
    if (!res.ok) throw new Error('Cities fetch failed');
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch cities from database, using fallback:', err);
    return [];
  }
}

export async function fetchStations(cityId?: string, stopType?: string, limit: number = 100): Promise<StationData[]> {
  try {
    const params = new URLSearchParams();
    if (cityId) params.append('city_id', cityId);
    if (stopType) params.append('stop_type', stopType);
    params.append('limit', String(limit));
    const res = await fetch(`${API_BASE}/api/stations?${params.toString()}`);
    if (!res.ok) throw new Error('Stations fetch failed');
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch stations:', err);
    return [];
  }
}

export async function searchStations(query: string, city?: string): Promise<StationData[]> {
  try {
    const params = new URLSearchParams({ q: query });
    if (city) params.append('city', city);
    const res = await fetch(`${API_BASE}/api/stations/search?${params.toString()}`);
    if (!res.ok) throw new Error('Stations search failed');
    return await res.json();
  } catch (err) {
    console.warn('Stations search failed:', err);
    return [];
  }
}

export async function getSavedPlaces(): Promise<SavedPlace[]> {
  try {
    const res = await fetch(`${API_BASE}/api/saved-places`);
    if (!res.ok) throw new Error('Saved places fetch failed');
    return await res.json();
  } catch (err) {
    console.warn('Failed to get saved places:', err);
    return [];
  }
}

export async function createSavedPlace(data: {
  name: string;
  address: string;
  category?: string;
  latitude: number;
  longitude: number;
  city?: string;
}): Promise<SavedPlace | null> {
  try {
    const res = await fetch(`${API_BASE}/api/saved-places`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create saved place');
    return await res.json();
  } catch (err) {
    console.error('Error saving place:', err);
    return null;
  }
}

export async function deleteSavedPlace(placeId: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/saved-places/${encodeURIComponent(placeId)}`, {
      method: 'DELETE'
    });
    return res.ok;
  } catch (err) {
    console.error('Error deleting saved place:', err);
    return false;
  }
}

export async function getUserPreferences(): Promise<UserPreferencesData | null> {
  try {
    const res = await fetch(`${API_BASE}/api/preferences`);
    if (!res.ok) throw new Error('Preferences fetch failed');
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch user preferences:', err);
    return null;
  }
}

export async function updateUserPreferences(updates: Partial<UserPreferencesData>): Promise<UserPreferencesData | null> {
  try {
    const res = await fetch(`${API_BASE}/api/preferences`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    if (!res.ok) throw new Error('Preferences update failed');
    return await res.json();
  } catch (err) {
    console.error('Failed to update preferences:', err);
    return null;
  }
}


// =============================================================================
// Authentication & Commuter Session API Client
// =============================================================================

export function getAuthToken(): string | null {
  return localStorage.getItem('raahi_auth_token') || sessionStorage.getItem('raahi_auth_token');
}

export function setAuthToken(token: string, rememberMe: boolean = true): void {
  if (rememberMe) {
    localStorage.setItem('raahi_auth_token', token);
    sessionStorage.removeItem('raahi_auth_token');
  } else {
    sessionStorage.setItem('raahi_auth_token', token);
    localStorage.removeItem('raahi_auth_token');
  }
}

export function removeAuthToken(): void {
  localStorage.removeItem('raahi_auth_token');
  sessionStorage.removeItem('raahi_auth_token');
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function apiSignIn(email: string, password: string, rememberMe: boolean = true): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/signin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password, remember_me: rememberMe })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to sign in' }));
    throw new Error(errorData.detail || 'Invalid email or password');
  }

  const data: AuthResponse = await res.json();
  if (data.token) {
    setAuthToken(data.token, rememberMe);
  }
  return data;
}

export async function apiSignUp(
  name: string,
  email: string,
  password: string,
  confirmPassword: string
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      name,
      email,
      password,
      confirm_password: confirmPassword
    })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(errorData.detail || 'Could not create account');
  }

  const data: AuthResponse = await res.json();
  if (data.token) {
    setAuthToken(data.token, true);
  }
  return data;
}

export async function apiSignOut(): Promise<void> {
  try {
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'include'
    });
  } catch (err) {
    console.warn('Network error during logout:', err);
  } finally {
    removeAuthToken();
  }
}

export async function apiGetCurrentUser(): Promise<User | null> {
  try {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'include'
    });

    if (!res.ok) {
      if (res.status === 401) {
        removeAuthToken();
      }
      return null;
    }

    return await res.json();
  } catch (err) {
    console.warn('Could not verify active session:', err);
    return null;
  }
}

export async function apiForgotPassword(email: string): Promise<{ message: string; demo_reset_token?: string }> {
  const res = await fetch(`${API_BASE}/api/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to request reset' }));
    throw new Error(errorData.detail || 'Failed to process request');
  }

  return await res.json();
}

export async function apiResetPassword(
  token: string,
  newPassword: string,
  confirmPassword: string
): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Reset failed' }));
    throw new Error(errorData.detail || 'Invalid or expired reset token');
  }

  return await res.json();
}
