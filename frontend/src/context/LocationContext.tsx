import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { reverseGeocode } from '../services/api';
import type { ReverseGeocodeResult } from '../types/transit';

export type PermissionState = 'prompt' | 'granted' | 'denied' | 'unsupported';

export interface LocationResult {
  lat: number;
  lon: number;
  locality?: string;
  city?: string;
}

export interface LocationContextType {
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  detectedCity: string | null;
  detectedLocality: string | null;
  formattedAddress: string | null;
  matchedTransitCity: string | null;
  permissionStatus: PermissionState;
  isLocating: boolean;
  hasExplicitlyLocated: boolean;
  locationError: string | null;
  recenterCount: number;
  requestLocation: () => Promise<LocationResult | null>;
  recenterMap: () => void;
  clearError: () => void;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

function calculateDistanceMeters(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371e3; // Earth radius in meters
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

export const LocationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [accuracy, setAccuracy] = useState<number | null>(null);

  const [detectedCity, setDetectedCity] = useState<string | null>(null);
  const [detectedLocality, setDetectedLocality] = useState<string | null>(null);
  const [formattedAddress, setFormattedAddress] = useState<string | null>(null);
  const [matchedTransitCity, setMatchedTransitCity] = useState<string | null>(null);

  const [permissionStatus, setPermissionStatus] = useState<PermissionState>('prompt');
  const [isLocating, setIsLocating] = useState<boolean>(false);
  const [hasExplicitlyLocated, setHasExplicitlyLocated] = useState<boolean>(false);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [recenterCount, setRecenterCount] = useState<number>(0);

  const lastGeocodedCoords = useRef<{ lat: number; lon: number } | null>(null);
  const watchIdRef = useRef<number | null>(null);
  const isMountedRef = useRef<boolean>(true);

  // Perform reverse geocoding with distance throttling (> 400m)
  const performReverseGeocode = useCallback(async (lat: number, lon: number): Promise<{ locality?: string; city?: string } | null> => {
    if (lastGeocodedCoords.current) {
      const dist = calculateDistanceMeters(
        lastGeocodedCoords.current.lat,
        lastGeocodedCoords.current.lon,
        lat,
        lon
      );
      if (dist < 400) {
        return {
          locality: detectedLocality || undefined,
          city: matchedTransitCity || detectedCity || undefined
        };
      }
    }

    try {
      const result: ReverseGeocodeResult = await reverseGeocode(lat, lon);
      if (!isMountedRef.current) return null;

      lastGeocodedCoords.current = { lat, lon };
      if (result.city) {
        setDetectedCity(result.city);
      }
      if (result.locality) {
        setDetectedLocality(result.locality);
      }
      if (result.formatted_address) {
        setFormattedAddress(result.formatted_address);
      }
      if (result.matched_transit_city) {
        setMatchedTransitCity(result.matched_transit_city);
      }

      return {
        locality: result.locality || undefined,
        city: (result.matched_transit_city || result.city) || undefined
      };
    } catch (err) {
      console.warn('Reverse geocoding failed:', err);
      return null;
    }
  }, [detectedLocality, matchedTransitCity, detectedCity]);

  // Handle position update from Geolocation API
  const handlePositionSuccess = useCallback(
    (pos: GeolocationPosition) => {
      if (!isMountedRef.current) return;
      const { latitude: lat, longitude: lon, accuracy: acc } = pos.coords;

      setLatitude(lat);
      setLongitude(lon);
      setAccuracy(acc);
      setPermissionStatus('granted');
      setIsLocating(false);
      setLocationError(null);

      // Convert coordinates to city via reverse geocoding
      performReverseGeocode(lat, lon);
    },
    [performReverseGeocode]
  );

  // Handle geolocation error
  const handlePositionError = useCallback((err: GeolocationPositionError) => {
    if (!isMountedRef.current) return;
    setIsLocating(false);

    switch (err.code) {
      case err.PERMISSION_DENIED:
        setPermissionStatus('denied');
        setLocationError(
          'Location permission was denied. You can enable location in your browser address bar (lock/tune icon) or select a city manually.'
        );
        break;
      case err.POSITION_UNAVAILABLE:
        setLocationError('GPS position is currently unavailable. Please verify device location settings or enter your origin manually.');
        break;
      case err.TIMEOUT:
        setLocationError('Location request timed out. You can tap retry or enter your origin manually.');
        break;
      default:
        setLocationError('Unable to retrieve location. Please enter your origin manually.');
        break;
    }
  }, []);

  // Explicit user-triggered location request handler
  const requestLocation = useCallback(async (): Promise<LocationResult | null> => {
    if (typeof window === 'undefined' || !('geolocation' in navigator)) {
      setPermissionStatus('unsupported');
      setLocationError('Geolocation is not supported by your browser.');
      setIsLocating(false);
      return null;
    }

    setIsLocating(true);
    setLocationError(null);

    // Stop existing watch if any
    if (watchIdRef.current !== null) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }

    return new Promise<LocationResult | null>((resolve) => {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          if (!isMountedRef.current) {
            resolve(null);
            return;
          }
          const { latitude: lat, longitude: lon, accuracy: acc } = pos.coords;

          setLatitude(lat);
          setLongitude(lon);
          setAccuracy(acc);
          setPermissionStatus('granted');
          setHasExplicitlyLocated(true);
          setIsLocating(false);
          setLocationError(null);
          setRecenterCount((c) => c + 1);

          // Start watching for smooth live updates only after explicit user permission
          if (watchIdRef.current === null && 'geolocation' in navigator) {
            watchIdRef.current = navigator.geolocation.watchPosition(
              handlePositionSuccess,
              handlePositionError,
              {
                enableHighAccuracy: true,
                timeout: 12000,
                maximumAge: 20000
              }
            );
          }

          const geocodeRes = await performReverseGeocode(lat, lon);
          resolve({
            lat,
            lon,
            locality: geocodeRes?.locality,
            city: geocodeRes?.city
          });
        },
        (err) => {
          handlePositionError(err);
          resolve(null);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 5000
        }
      );
    });
  }, [handlePositionSuccess, handlePositionError, performReverseGeocode]);

  const recenterMap = useCallback(() => {
    if (latitude !== null && longitude !== null) {
      setRecenterCount((c) => c + 1);
    } else {
      requestLocation();
    }
  }, [latitude, longitude, requestLocation]);

  const clearError = useCallback(() => {
    setLocationError(null);
  }, []);

  // Cleanup on unmount - do NOT request location automatically
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
    };
  }, []);

  return (
    <LocationContext.Provider
      value={{
        latitude,
        longitude,
        accuracy,
        detectedCity,
        detectedLocality,
        formattedAddress,
        matchedTransitCity,
        permissionStatus,
        isLocating,
        hasExplicitlyLocated,
        locationError,
        recenterCount,
        requestLocation,
        recenterMap,
        clearError
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = (): LocationContextType => {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocation must be used within a LocationProvider');
  }
  return context;
};
