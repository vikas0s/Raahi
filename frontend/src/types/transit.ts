export type TransitMode = 'walk' | 'metro' | 'bus' | 'rail' | 'auto' | 'taxi' | 'erickshaw' | 'ebus';
export type CrowdLevel = 'Low' | 'Moderate' | 'High' | 'Very High';
export type SeverityLevel = 'minor' | 'moderate' | 'severe';
export type AppLanguage = 'en' | 'hi';
export type TimeMode = 'now' | 'depart_at' | 'arrive_by';

export interface GeoLocation {
  name: string;
  lat: float;
  lon: float;
  category: string;
  city: string;
  aliases?: string[];
  has_direct_metro?: boolean;
  nearest_metro?: string;
  metro_dist_km?: number;
}

export type float = number;

export interface TravelPreferences {
  fastest: boolean;
  cheapest: boolean;
  less_crowded: boolean;
  fewer_transfers: boolean;
  less_walking: boolean;
  accessible: boolean;
  prefer_ebus?: boolean;
  allow_auto?: boolean;
  allow_taxi?: boolean;
  pink_pass?: boolean; // Delhi Govt free bus travel for women
  prefer_multimodal?: boolean;
  prefer_rail?: boolean; // Indian Railways & Local Trains
}

export interface TransitLeg {
  id: string;
  mode: TransitMode;
  line_name?: string;
  line_color?: string;
  origin_name: string;
  destination_name: string;
  origin_coords: [number, number]; // [lon, lat]
  destination_coords: [number, number]; // [lon, lat]
  path_coords: [number, number][]; // [[lon, lat], ...]
  duration_minutes: number;
  distance_meters: number;
  departure_time: string;
  arrival_time: string;
  stops_count: number;
  intermediate_stops: string[];
  instructions: string;
  crowd_level: CrowdLevel;
  delay_minutes: number;
  is_delayed: boolean;
  accessibility: boolean;
  fare_inr?: number;
  fare_details?: string;
  train_number?: string;
  train_name?: string;
  train_type?: string;
  platform?: string;
  coach_classes?: string[];
  data_source?: string;
}

export interface RouteItinerary {
  id: string;
  title: string;
  tag: string;
  tag_reason: string;
  total_duration_minutes: number;
  departure_time: string;
  arrival_time: string;
  total_fare_inr: number;
  pink_pass_fare_inr?: number;
  fare_breakdown?: string;
  route_type?: string;
  transfers_count: number;
  walking_duration_minutes: number;
  walking_distance_meters: number;
  overall_crowd: CrowdLevel;
  total_delay_minutes: number;
  legs: TransitLeg[];
  eco_carbon_savings_kg: number;
  service_available?: boolean;       // Whether this transit mode is currently operational
  unavailable_reason?: string;       // e.g. "Metro closed (11 PM – 6 AM)"
}

export interface PlanResponse {
  origin: GeoLocation;
  destination: GeoLocation;
  generated_at: string;
  routes: RouteItinerary[];
  active_disruptions_count: number;
}

export interface TransitIncident {
  id: string;
  line_name: string;
  mode: TransitMode;
  severity: SeverityLevel;
  delay_minutes: number;
  crowd_level: CrowdLevel;
  affected_stations: string[];
  headline: string;
  description: string;
  last_updated: string;
  is_simulated: boolean;
}

export interface CityRealtimeContext {
  city: string;
  day_name: string;
  day_type: string;
  current_time_str: string;
  time_window: string;
  status_headline: string;
  status_description: string;
  crowd_level: CrowdLevel;
  recommended_mode: string;
  special_advisory?: string;
}

export interface SavedRoute {
  id: string;
  name: string;
  origin: string;
  destination: string;
  city: string;
  preferred_mode: string;
  created_at: string;
  typical_duration_minutes: number;
  typical_fare_inr: number;
  typical_transfers: number;
  current_delay_minutes: number;
  active_status: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  action_type?: string;
  route_data?: RouteItinerary;
  suggested_actions?: { label: string; action: string }[];
}

export interface LiveVehicle {
  id: string;
  route_short_name: string;
  agency: string;
  lat: number;
  lon: number;
  speed_kmh: number;
  bearing: number;
  current_status: string;
  timestamp: string;
  is_live_telemetry: boolean;
  data_source: string;
}

// ==============================================================================
// Raahi RailConnect — Indian Railways Types
// ==============================================================================

export interface RailStation {
  code: string;
  name: string;
  city: string;
  state?: string;
  lat: number;
  lon: number;
  platforms_count?: number;
  category?: string;
  aliases?: string[];
  zone?: string;
}

export interface TrainHalt {
  station_code: string;
  station_name: string;
  arrival_time: string;
  departure_time: string;
  halt_minutes: number;
  distance_km: number;
  platform?: string;
  day_offset: number;
}

export interface TrainSchedule {
  train_number: string;
  train_name: string;
  train_type: string;
  origin_code: string;
  origin_name: string;
  destination_code: string;
  destination_name: string;
  halts: TrainHalt[];
  running_days: string[];
}

export interface TrainSummary {
  train_number: string;
  train_name: string;
  train_type: 'Superfast' | 'Express' | 'Passenger' | 'MEMU' | 'DEMU' | 'EMU / Local' | 'Rail Bus' | 'Shatabdi' | 'Vande Bharat' | string;
  origin_code: string;
  origin_name: string;
  destination_code: string;
  destination_name: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  distance_km: number;
  running_days: string[];
  classes: string[];
  fares: Record<string, number>;
  halts_count: number;
  platform_origin?: string;
  platform_dest?: string;
  live_delay_mins: number;
  live_status: string;
  is_live: boolean;
  data_source: string;
}

export interface LiveRunningStatus {
  train_number: string;
  train_name: string;
  train_type?: string;
  current_station: string;
  current_status: string;
  delay_minutes: number;
  speed_kmh?: number;
  last_reported_time?: string;
  next_station?: string;
  eta_destination: string;
  is_live: boolean;
  data_source: string;
}

export interface StationBoardItem {
  train_number: string;
  train_name: string;
  train_type: string;
  origin_code: string;
  destination_code: string;
  destination_name: string;
  scheduled_time: string;
  expected_time: string;
  platform: string;
  status: string;
  delay_minutes: number;
  is_live: boolean;
}

export interface StationBoardResponse {
  station: RailStation;
  departures: StationBoardItem[];
  generated_at: string;
}

export interface RailSearchResponse {
  from_station: RailStation;
  to_station: RailStation;
  date: string;
  trains_count: number;
  trains: TrainSummary[];
  data_source: string;
}
