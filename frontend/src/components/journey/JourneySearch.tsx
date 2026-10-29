import React, { useState, useEffect, useRef } from 'react';
import { ArrowUpDown, MapPin, Navigation, Clock, Search } from 'lucide-react';
import { searchPlaces } from '../../services/api';
import type { GeoLocation } from '../../types/transit';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  origin: string;
  destination: string;
  city: string;
  onOriginChange: (val: string) => void;
  onDestinationChange: (val: string) => void;
  onSubmit: (departureTime?: string) => void;
  isLoading?: boolean;
}

export const JourneySearch: React.FC<Props> = ({
  origin,
  destination,
  city,
  onOriginChange,
  onDestinationChange,
  onSubmit,
  isLoading = false
}) => {
  const { t } = useTranslation();
  const [originSuggestions, setOriginSuggestions] = useState<GeoLocation[]>([]);
  const [destSuggestions, setDestSuggestions] = useState<GeoLocation[]>([]);
  const [activeInput, setActiveInput] = useState<'origin' | 'dest' | null>(null);

  const [depOption, setDepOption] = useState<'now' | 'depart_at' | 'arrive_by'>('now');
  const [customTime, setCustomTime] = useState(
    new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
  );

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
    const depTime = depOption === 'now' ? undefined : customTime;
    onSubmit(depTime);
  };

  return (
    <div ref={containerRef} className="w-full bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_2px_14px_rgba(41,45,41,0.04)]">
      <form onSubmit={handleFormSubmit} className="space-y-4">
        {/* Origin and Destination Row */}
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] items-center gap-3.5 relative">
          {/* Origin Input */}
          <div className="relative">
            <label className="block text-xs font-bold uppercase tracking-wider text-[#2E5A3D] mb-1.5 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#4E7C5F]" /> {t('startingOrigin')}
            </label>
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
                      onOriginChange(item.name);
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
                      onDestinationChange(item.name);
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
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-3 border-t border-[#D8D4C7]">
          <div className="flex items-center gap-2">
            <Clock size={15} className="text-[#52544D] stroke-[2]" />
            <div className="inline-flex rounded-xl bg-[#EEECE3] p-1 border border-[#D8D4C7] text-xs font-bold">
              <button
                type="button"
                onClick={() => setDepOption('now')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  depOption === 'now' ? 'bg-[#FFFEFA] text-[#1F231F] shadow-xs' : 'text-[#52544D] hover:text-[#1F231F]'
                }`}
              >
                {t('leaveNow')}
              </button>
              <button
                type="button"
                onClick={() => setDepOption('depart_at')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  depOption === 'depart_at' ? 'bg-[#FFFEFA] text-[#1F231F] shadow-xs' : 'text-[#52544D] hover:text-[#1F231F]'
                }`}
              >
                {t('departAt')}
              </button>
              <button
                type="button"
                onClick={() => setDepOption('arrive_by')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  depOption === 'arrive_by' ? 'bg-[#FFFEFA] text-[#1F231F] shadow-xs' : 'text-[#52544D] hover:text-[#1F231F]'
                }`}
              >
                {t('arriveBy')}
              </button>
            </div>

            {depOption !== 'now' && (
              <input
                type="time"
                value={customTime}
                onChange={(e) => setCustomTime(e.target.value)}
                className="px-2.5 py-1 bg-[#EEECE3] border border-[#D8D4C7] rounded-xl text-xs font-bold text-[#1F231F] outline-none"
              />
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
      </form>
    </div>
  );
};
