import React, { useState } from 'react';
import { MapPin, Bell, Bot, Crosshair, AlertCircle, Loader2, Check } from 'lucide-react';
import type { AppLanguage } from '../../types/transit';
import { useTranslation } from '../../i18n/LanguageContext';
import { useLocation } from '../../context/LocationContext';

interface Props {
  selectedCity: string;
  onCityChange: (city: string) => void;
  language: AppLanguage;
  onLanguageChange: (lang: AppLanguage) => void;
  disruptionsCount: number;
  onOpenAssistant: () => void;
  onOpenNotifications: () => void;
}

const DEFAULT_CITIES = [
  'Delhi NCR',
  'Mathura & Vrindavan',
  'Mumbai',
  'Bengaluru'
];

export const TopBar: React.FC<Props> = ({
  selectedCity,
  onCityChange,
  language,
  onLanguageChange,
  disruptionsCount,
  onOpenAssistant,
  onOpenNotifications
}) => {
  const { t, setLanguage } = useTranslation();
  const {
    isLocating,
    permissionStatus,
    detectedCity,
    matchedTransitCity,
    detectedLocality,
    locationError,
    recenterMap,
    requestLocation
  } = useLocation();

  const [showLocationTip, setShowLocationTip] = useState(false);

  const handleLang = (lang: AppLanguage) => {
    setLanguage(lang);
    onLanguageChange(lang);
  };

  // Compile unique available city options dynamically
  const availableCities = [...DEFAULT_CITIES];
  if (matchedTransitCity && !availableCities.includes(matchedTransitCity)) {
    availableCities.unshift(matchedTransitCity);
  }
  if (detectedCity && !availableCities.includes(detectedCity) && detectedCity !== matchedTransitCity) {
    availableCities.unshift(detectedCity);
  }

  const handleLocateClick = async () => {
    if (permissionStatus === 'denied') {
      setShowLocationTip(true);
      setTimeout(() => setShowLocationTip(false), 5000);
    } else {
      await requestLocation();
      recenterMap();
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-[#F7F5EF]/95 backdrop-blur-md border-b border-[#E3E0D6] px-4 sm:px-8 py-2.5 flex items-center justify-between gap-4">
      {/* Brand logo & tagline */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-[#304B3C] flex items-center justify-center text-[#FFFEFA] shadow-[0_2px_8px_rgba(48,75,60,0.25)] shrink-0">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v3m0 14v3M2 12h3m14 0h3" />
            <path d="M4.93 4.93l2.12 2.12m9.9 9.9l2.12 2.12M4.93 19.07l2.12-2.12m9.9-9.9l2.12-2.12" />
          </svg>
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="font-heading font-bold text-lg text-[#1F231F] leading-tight tracking-tight">
              {t('appName')}
            </h1>
            <span className="hidden sm:inline-block text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-md bg-[#64836D]/20 text-[#253D30] font-bold">
              {t('missionTag')}
            </span>
          </div>
          <p className="text-[11px] text-[#52544D] font-medium hidden sm:block">
            {t('appTagline')}
          </p>
        </div>
      </div>

      {/* Right Controls: Dynamic Location Selector, Language Toggle, Alerts, Assistant */}
      <div className="flex items-center gap-2 sm:gap-2.5">
        {/* Dynamic City Selector & Live GPS Indicator */}
        <div className="relative flex items-center">
          <div className="relative flex items-center bg-[#EEECE3] hover:bg-[#E3E0D6] rounded-xl border border-[#D8D4C7] focus-within:border-[#4E7C5F] focus-within:bg-[#FFFEFA] transition-all shadow-2xs">
            {/* Location Status Icon */}
            <div className="pl-2.5 pr-1 flex items-center text-[#4E7C5F]">
              {isLocating ? (
                <Loader2 size={14} className="animate-spin text-[#4E7C5F]" />
              ) : permissionStatus === 'granted' ? (
                <div className="relative flex items-center justify-center">
                  <span className="absolute w-3 h-3 rounded-full bg-[#2563EB]/30 animate-ping" />
                  <span className="w-2 h-2 rounded-full bg-[#2563EB]" />
                </div>
              ) : permissionStatus === 'denied' ? (
                <button
                  type="button"
                  onClick={() => setShowLocationTip((prev) => !prev)}
                  title="Location access blocked. Click for help."
                  className="cursor-pointer text-[#C8795A] hover:text-[#BD4F44]"
                >
                  <AlertCircle size={14} />
                </button>
              ) : (
                <MapPin size={14} className="stroke-[2.2]" />
              )}
            </div>

            {/* City Dropdown with dynamically populated detected city */}
            <select
              value={selectedCity}
              onChange={(e) => onCityChange(e.target.value)}
              className="py-1.5 pl-1 pr-6 text-xs font-bold text-[#1F231F] bg-transparent outline-none appearance-none cursor-pointer"
            >
              {availableCities.map((c) => (
                <option key={c} value={c}>
                  {c === detectedCity ? `📍 ${c} (Current)` : c}
                </option>
              ))}
            </select>

            {/* Recenter / Use Current Location Trigger Button */}
            <button
              type="button"
              onClick={handleLocateClick}
              title={
                isLocating
                  ? 'Detecting your location...'
                  : permissionStatus === 'granted'
                  ? `Live GPS Active (${detectedLocality || detectedCity || 'Detected'}). Click to recenter.`
                  : 'Detect my live location'
              }
              className={`pr-2 pl-1 py-1 text-[#52544D] hover:text-[#2563EB] cursor-pointer transition-colors ${
                isLocating ? 'animate-pulse text-[#2563EB]' : ''
              }`}
            >
              <Crosshair size={13} className="stroke-[2.4]" />
            </button>
          </div>

          {/* Friendly Permission Denied Popover Tooltip */}
          {showLocationTip && (
            <div className="absolute top-full right-0 mt-2 w-72 bg-[#FFFEFA] rounded-xl border border-[#D8D4C7] p-3 shadow-xl z-50 text-xs text-[#1F231F] space-y-1.5 animate-in fade-in slide-in-from-top-1">
              <div className="flex items-center gap-1.5 font-bold text-[#C8795A]">
                <AlertCircle size={14} />
                <span>Enable Browser Location</span>
              </div>
              <p className="text-[11px] text-[#52544D] leading-normal">
                {locationError ||
                  'Location permission is blocked. Click the lock/settings icon in your browser address bar and enable "Location" to auto-detect your city.'}
              </p>
              <div className="flex items-center justify-between pt-1 border-t border-[#E3E0D6]">
                <button
                  type="button"
                  onClick={async () => {
                    setShowLocationTip(false);
                    await requestLocation();
                  }}
                  className="text-[11px] font-bold text-[#2563EB] hover:underline cursor-pointer"
                >
                  Retry Detection
                </button>
                <button
                  type="button"
                  onClick={() => setShowLocationTip(false)}
                  className="text-[11px] text-[#77776F] hover:text-[#1F231F] cursor-pointer"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Segmented Language Switcher */}
        <div className="hidden sm:inline-flex rounded-xl bg-[#EEECE3] p-0.5 border border-[#D8D4C7] text-xs font-bold">
          <button
            type="button"
            onClick={() => handleLang('en')}
            className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
              language === 'en'
                ? 'bg-[#FFFEFA] text-[#1F231F] shadow-xs font-bold ring-1 ring-[#D8D4C7]'
                : 'text-[#52544D] font-semibold hover:text-[#1F231F]'
            }`}
          >
            EN
          </button>
          <button
            type="button"
            onClick={() => handleLang('hi')}
            className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
              language === 'hi'
                ? 'bg-[#FFFEFA] text-[#1F231F] shadow-xs font-bold ring-1 ring-[#D8D4C7]'
                : 'text-[#52544D] font-semibold hover:text-[#1F231F]'
            }`}
          >
            हिन्दी
          </button>
        </div>

        {/* Live Disruption Alert Notification Indicator */}
        <button
          onClick={onOpenNotifications}
          title={t('liveAlerts')}
          className="relative p-2 rounded-xl bg-[#EEECE3] hover:bg-[#E3E0D6] text-[#1F231F] transition-all border border-[#D8D4C7] cursor-pointer shadow-2xs"
        >
          <Bell size={15} className="stroke-[2.2]" />
          {disruptionsCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#BD4F44] text-white text-[9px] font-bold flex items-center justify-center shadow-xs animate-pulse">
              {disruptionsCount}
            </span>
          )}
        </button>

        {/* Floating AI Assistant Trigger */}
        <button
          onClick={onOpenAssistant}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] active:scale-[0.98] text-[#FFFEFA] text-xs font-bold shadow-sm hover:shadow-md transition-all cursor-pointer border border-[#1A2E24]/30"
        >
          <Bot size={15} className="stroke-[2.2]" />
          <span className="hidden md:inline font-bold">{t('raahiAiButton')}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-[#E7B75B] animate-pulse" />
        </button>
      </div>
    </header>
  );
};
