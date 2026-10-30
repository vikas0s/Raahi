import React, { useState, useEffect, useRef } from 'react';
import { ArrowUpDown, MapPin, Navigation, Clock, Search, Sparkles, RotateCcw, Crosshair } from 'lucide-react';
import { useLocation } from '../../context/LocationContext';
import { searchPlaces } from '../../services/api';
import type { GeoLocation, TimeMode } from '../../types/transit';
import { useTranslation } from '../../i18n/LanguageContext';
import { formatTime12, getCurrentTime24, addMinutesToTime } from '../../utils/time';

interface Props {
  origin: string;
  destination: string;
  city: string;
  onOriginChange: (val: string, coords?: [number, number]) => void;
  onDestinationChange: (val: string, coords?: [number, number]) => void;
  onUseCurrentLocation?: (name: string, coords: [number, number]) => void;
  onSubmit: (departureTime?: string, arrivalTime?: string, timeMode?: TimeMode) => void;
  isLoading?: boolean;
}

export const JourneySearch: React.FC<Props> = ({
  origin,
  destination,
  city,
  onOriginChange,
  onDestinationChange,
  onUseCurrentLocation,
  onSubmit,
  isLoading = false
}) => {
  const { t } = useTranslation();
  const {
    latitude: userLat,
    longitude: userLon,
    detectedLocality,
    detectedCity,
    isLocating,
    locationError,
    clearError,
    requestLocation,
    recenterMap
  } = useLocation();

  const handleUseCurrentLocation = async () => {
    const loc = await requestLocation();
    if (!loc) {
      return;
    }
    const locName = loc.locality
      ? `${loc.locality}${loc.city ? `, ${loc.city}` : ''}`
      : loc.city
      ? `My Current Location (${loc.city})`
      : 'My Current Location';

    const coords: [number, number] = [loc.lon, loc.lat];

    if (onUseCurrentLocation) {
      onUseCurrentLocation(locName, coords);
    } else {
      onOriginChange(locName, coords);
    }
    recenterMap();
  };

  const [originSuggestions, setOriginSuggestions] = useState<GeoLocation[]>([]);
  const [destSuggestions, setDestSuggestions] = useState<GeoLocation[]>([]);
  const [activeInput, setActiveInput] = useState<'origin' | 'dest' | null>(null);

  const [depOption, setDepOption] = useState<TimeMode>('now');
  const [selectedTime, setSelectedTime] = useState<string>(getCurrentTime24());

  const [isSwapping, setIsSwapping] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setActiveInput(null);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  useEffect(() => {
    if (activeInput === 'origin' && origin.length >= 1) {
      searchPlaces(origin, city).then(setOriginSuggestions);
    } else {
      setOriginSuggestions([]);
    }
  }, [origin, activeInput, city]);

  useEffect(() => {
    if (activeInput === 'dest' && destination.length >= 1) {
      searchPlaces(destination, city).then(setDestSuggestions);
    } else {
      setDestSuggestions([]);
    }
  }, [destination, activeInput, city]);

  const handleSwap = () => {
    setIsSwapping(true);
    setTimeout(() => setIsSwapping(false), 300);
    const temp = origin;
    onOriginChange(destination);
    onDestinationChange(temp);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!origin || !destination) return;
    setActiveInput(null);

    if (depOption === 'now') {
      onSubmit(undefined, undefined, 'now');
    } else if (depOption === 'depart_at') {
      onSubmit(selectedTime, undefined, 'depart_at');
    } else if (depOption === 'arrive_by') {
      onSubmit(undefined, selectedTime, 'arrive_by');
    }
  };

  const handleQuickAdd = (minutes: number) => {
    setSelectedTime((prev) => addMinutesToTime(prev, minutes));
  };

  const handleResetNow = () => {
    setSelectedTime(getCurrentTime24());
  };

  return (
    <div ref={containerRef} className="w-full bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_2px_14px_rgba(41,45,41,0.04)]">
      {locationError && (
        <div className="mb-3 p-3 rounded-xl bg-[#C8795A]/15 text-[#8F3D1F] border border-[#C8795A]/30 text-xs font-semibold flex items-center justify-between gap-2 animate-in fade-in">
          <span>{locationError}</span>
          <button
            type="button"
            onClick={clearError}
            className="text-[#8F3D1F] hover:text-[#521C0B] font-bold text-xs px-1.5 py-0.5 rounded cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}
      <form onSubmit={handleFormSubmit} className="space-y-4">
        {/* Origin and Destination Row */}
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] items-center gap-3.5 relative">
          {/* Origin Input */}
          <div className="relative">
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-[#2E5A3D] flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#4E7C5F]" /> {t('startingOrigin')}
              </label>
              <button
                type="button"
                onClick={handleUseCurrentLocation}
                title="Use current GPS location"
                className="text-[11px] font-bold text-[#2563EB] hover:text-[#1D4ED8] inline-flex items-center gap-1 cursor-pointer transition-colors"
              >
                <Crosshair size={12} className={`stroke-[2.5] ${isLocating ? 'animate-spin' : ''}`} />
                <span>{isLocating ? 'Locating...' : 'Use current location'}</span>
              </button>
            </div>
            <div className="relative flex items-center">
              <MapPin size={17} className="absolute left-3.5 text-[#2E5A3D] pointer-events-none stroke-[2.5]" />
              <input
                type="text"
                value={origin}
                onChange={(e) => onOriginChange(e.target.value)}
                onFocus={() => setActiveInput('origin')}
                placeholder={t('originPlaceholder')}
                className="w-full pl-10.5 pr-4 py-2.5 bg-[#EEECE3]/60 hover:bg-[#EEECE3] focus:bg-[#FFFEFA] text-sm text-[#1F231F] font-semibold rounded-xl border border-[#D8D4C7] focus:border-[#2E5A3D] focus:ring-2 focus:ring-[#2E5A3D]/20 outline-none transition-all shadow-2xs"
              />
            </div>

            {/* Origin Autocomplete Dropdown */}
            {activeInput === 'origin' && originSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1.5 bg-[#FFFEFA] rounded-xl border border-[#D8D4C7] shadow-[0_6px_24px_rgba(41,45,41,0.12)] max-h-56 overflow-y-auto z-30 py-1 divide-y divide-[#D8D4C7]/50">
                {originSuggestions.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      onOriginChange(item.name, [item.lon, item.lat]);
                      setActiveInput(null);
                    }}
                    className="w-full text-left px-3.5 py-2.5 text-xs hover:bg-[#EEECE3]/80 flex items-center justify-between text-[#1F231F] font-semibold transition-colors cursor-pointer"
                  >
                    <span className="truncate">{item.name}</span>
                    <span className="text-[10px] text-[#454841] capitalize bg-[#EEECE3] px-2 py-0.5 rounded-full ml-2 shrink-0 font-bold border border-[#D8D4C7]">
                      {item.category.replace('_', ' ')}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Animated Swap Button */}
          <div className="flex justify-center md:pt-5">
            <button
              type="button"
              onClick={handleSwap}
              title="Swap origin and destination"
              className={`p-2.5 rounded-xl bg-[#EEECE3] text-[#21432E] hover:bg-[#D8D4C7] transition-all duration-300 border border-[#D8D4C7] cursor-pointer shadow-xs active:scale-95 ${
                isSwapping ? 'rotate-180 scale-110' : ''
              }`}
            >
              <ArrowUpDown size={16} className="stroke-[2.5]" />
            </button>
          </div>

          {/* Destination Input */}
          <div className="relative">
            <label className="block text-xs font-bold uppercase tracking-wider text-[#B85732] mb-1.5 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#B85732]" /> {t('targetDestination')}
            </label>
            <div className="relative flex items-center">
              <Navigation size={17} className="absolute left-3.5 text-[#B85732] pointer-events-none stroke-[2.5]" />
              <input
                type="text"
                value={destination}
                onChange={(e) => onDestinationChange(e.target.value)}
                onFocus={() => setActiveInput('dest')}
                placeholder={t('destinationPlaceholder')}
                className="w-full pl-10.5 pr-4 py-2.5 bg-[#EEECE3]/60 hover:bg-[#EEECE3] focus:bg-[#FFFEFA] text-sm text-[#1F231F] font-semibold rounded-xl border border-[#D8D4C7] focus:border-[#B85732] focus:ring-2 focus:ring-[#B85732]/20 outline-none transition-all shadow-2xs"
              />
            </div>

            {/* Destination Autocomplete Dropdown */}
            {activeInput === 'dest' && destSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1.5 bg-[#FFFEFA] rounded-xl border border-[#D8D4C7] shadow-[0_6px_24px_rgba(41,45,41,0.12)] max-h-56 overflow-y-auto z-30 py-1 divide-y divide-[#D8D4C7]/50">
                {destSuggestions.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      onDestinationChange(item.name, [item.lon, item.lat]);
                      setActiveInput(null);
                    }}
                    className="w-full text-left px-3.5 py-2.5 text-xs hover:bg-[#EEECE3]/80 flex items-center justify-between text-[#1F231F] font-semibold transition-colors cursor-pointer"
                  >
                    <span className="truncate">{item.name}</span>
                    <span className="text-[10px] text-[#454841] capitalize bg-[#EEECE3] px-2 py-0.5 rounded-full ml-2 shrink-0 font-bold border border-[#D8D4C7]">
                      {item.category.replace('_', ' ')}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Departure Time Controls & Submit Button */}
        <div className="pt-3 border-t border-[#D8D4C7] space-y-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            {/* Mode Selector Tabs */}
            <div className="flex items-center gap-2">
              <Clock size={16} className="text-[#52544D] stroke-[2.2] shrink-0" />
              <div className="inline-flex rounded-xl bg-[#EEECE3] p-1 border border-[#D8D4C7] text-xs font-bold">
                <button
                  type="button"
                  onClick={() => setDepOption('now')}
                  className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
                    depOption === 'now'
                      ? 'bg-[#FFFEFA] text-[#253D30] shadow-xs font-extrabold'
                      : 'text-[#52544D] hover:text-[#1F231F]'
                  }`}
                >
                  <span>⚡</span>
                  <span>{t('leaveNow')}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setDepOption('depart_at')}
                  className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
                    depOption === 'depart_at'
                      ? 'bg-[#FFFEFA] text-[#253D30] shadow-xs font-extrabold'
                      : 'text-[#52544D] hover:text-[#1F231F]'
                  }`}
                >
                  <span>🛫</span>
                  <span>{t('departAt')}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setDepOption('arrive_by')}
                  className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
                    depOption === 'arrive_by'
                      ? 'bg-[#FFFEFA] text-[#253D30] shadow-xs font-extrabold'
                      : 'text-[#52544D] hover:text-[#1F231F]'
                  }`}
                >
                  <span>🎯</span>
                  <span>{t('arriveBy')}</span>
                </button>
              </div>

              {depOption === 'now' && (
                <span className="hidden md:inline-flex items-center gap-1 text-[11px] font-bold text-[#5B8A6E] bg-[#5B8A6E]/10 px-2.5 py-1 rounded-lg border border-[#5B8A6E]/20">
                  <span>●</span>
                  <span>Live (~{formatTime12(getCurrentTime24())})</span>
                </span>
              )}
            </div>

            {/* Prominent Primary CTA Button */}
            <button
              type="submit"
              disabled={isLoading || !origin || !destination}
              className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-[#253D30] hover:bg-[#1B2F24] active:scale-[0.98] text-[#FFFEFA] text-xs font-bold tracking-wider shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer border border-[#1B2F24]"
            >
              {isLoading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>{t('searching')}</span>
                </>
              ) : (
                <>
                  <Search size={15} className="stroke-[2.5]" />
                  <span>{t('searchJourneys')}</span>
                </>
              )}
            </button>
          </div>

          {/* Dedicated Rich Time Picker & Presets Tray for Depart At / Arrive By */}
          {depOption !== 'now' && (
            <div className="bg-[#EEECE3]/60 rounded-xl p-3.5 border border-[#D8D4C7] space-y-2.5 transition-all animate-fadeIn">
              <div className="flex flex-wrap items-center justify-between gap-3">
                {/* Time Input with 12-Hour formatted display */}
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-extrabold text-[#253D30] uppercase tracking-wider">
                    {depOption === 'depart_at' ? 'Departure Time:' : 'Target Arrival:'}
                  </span>

                  <div className="flex items-center gap-2">
                    <input
                      type="time"
                      value={selectedTime}
                      onChange={(e) => setSelectedTime(e.target.value)}
                      className="px-3 py-1.5 bg-[#FFFEFA] border border-[#D8D4C7] rounded-xl text-xs font-extrabold text-[#1F231F] outline-none shadow-2xs focus:border-[#4E7C5F] focus:ring-2 focus:ring-[#4E7C5F]/20 cursor-pointer"
                    />

                    <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-[#253D30] text-[#FFFEFA] font-mono text-xs font-black shadow-xs">
                      <Clock size={12} className="stroke-[2.5]" />
                      <span>{formatTime12(selectedTime)}</span>
                    </span>
                  </div>
                </div>

                {/* Quick Increment Controls */}
                <div className="flex items-center gap-1.5 text-xs">
                  <span className="text-[11px] font-bold text-[#52544D] mr-1">Quick Add:</span>
                  <button
                    type="button"
                    onClick={() => handleQuickAdd(15)}
                    className="px-2.5 py-1 rounded-lg bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] font-bold text-[#1F231F] text-[11px] transition-all cursor-pointer shadow-2xs active:scale-95"
                  >
                    +15m
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickAdd(30)}
                    className="px-2.5 py-1 rounded-lg bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] font-bold text-[#1F231F] text-[11px] transition-all cursor-pointer shadow-2xs active:scale-95"
                  >
                    +30m
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickAdd(60)}
                    className="px-2.5 py-1 rounded-lg bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] font-bold text-[#1F231F] text-[11px] transition-all cursor-pointer shadow-2xs active:scale-95"
                  >
                    +1h
                  </button>
                  <button
                    type="button"
                    onClick={handleResetNow}
                    title="Reset to current time"
                    className="p-1.5 rounded-lg bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] text-[#52544D] hover:text-[#1F231F] transition-all cursor-pointer shadow-2xs active:scale-95 ml-1"
                  >
                    <RotateCcw size={12} className="stroke-[2.2]" />
                  </button>
                </div>
              </div>

              {/* Commuter Presets & Helper Text */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#D8D4C7]/60 text-xs">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-[11px] font-bold text-[#52544D] mr-0.5">Presets:</span>
                  <button
                    type="button"
                    onClick={() => setSelectedTime('09:00')}
                    className="px-2 py-0.5 rounded-md bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] text-[10px] font-bold text-[#1F231F] transition-all cursor-pointer"
                  >
                    🌅 09:00 AM (Morning Peak)
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedTime('13:00')}
                    className="px-2 py-0.5 rounded-md bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] text-[10px] font-bold text-[#1F231F] transition-all cursor-pointer"
                  >
                    ☀️ 01:00 PM (Midday)
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedTime('18:00')}
                    className="px-2 py-0.5 rounded-md bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] text-[10px] font-bold text-[#1F231F] transition-all cursor-pointer"
                  >
                    🌆 06:00 PM (Evening Rush)
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedTime('21:00')}
                    className="px-2 py-0.5 rounded-md bg-[#FFFEFA] hover:bg-[#EEECE3] border border-[#D8D4C7] text-[10px] font-bold text-[#1F231F] transition-all cursor-pointer"
                  >
                    🌙 09:00 PM (Late Night)
                  </button>
                </div>

                <p className="text-[11px] text-[#52544D] font-medium italic">
                  {depOption === 'depart_at'
                    ? `Journeys departing at or after ${formatTime12(selectedTime)}`
                    : `Journeys planned backwards to arrive by ${formatTime12(selectedTime)}`}
                </p>
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};
