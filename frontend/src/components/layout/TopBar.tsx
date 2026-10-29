import React from 'react';
import { MapPin, Bell, Bot } from 'lucide-react';
import type { AppLanguage } from '../../types/transit';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  selectedCity: string;
  onCityChange: (city: string) => void;
  language: AppLanguage;
  onLanguageChange: (lang: AppLanguage) => void;
  disruptionsCount: number;
  onOpenAssistant: () => void;
  onOpenNotifications: () => void;
}

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

  const handleLang = (lang: AppLanguage) => {
    setLanguage(lang);
    onLanguageChange(lang);
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-[#F7F5EF]/90 backdrop-blur-md border-b border-[#E3E0D6] px-4 sm:px-8 py-3 flex items-center justify-between gap-4">
      {/* Brand logo & tagline */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-[#304B3C] flex items-center justify-center text-[#FFFEFA] shadow-[0_2px_8px_rgba(48,75,60,0.25)]">
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

      {/* Right Controls: Location Indicator, Language Toggle, Alerts, Assistant Button */}
      <div className="flex items-center gap-2.5">
        {/* City Location Indicator & Selector */}
        <div className="relative flex items-center">
          <div className="absolute left-2.5 pointer-events-none flex items-center gap-1 text-[#4E7C5F]">
            <MapPin size={14} className="stroke-[2.2]" />
          </div>
          <select
            value={selectedCity}
            onChange={(e) => onCityChange(e.target.value)}
            className="pl-7 pr-7 py-1.5 bg-[#EEECE3] hover:bg-[#E3E0D6] focus:bg-[#FFFEFA] text-xs font-bold text-[#1F231F] rounded-xl border border-[#D8D4C7] focus:border-[#4E7C5F] outline-none appearance-none cursor-pointer transition-all shadow-2xs"
          >
            <option value="Delhi NCR">Delhi NCR</option>
            <option value="Mumbai">Mumbai</option>
            <option value="Bengaluru">Bengaluru</option>
          </select>
        </div>

        {/* Segmented Language Switcher */}
        <div className="hidden sm:inline-flex rounded-xl bg-[#EEECE3] p-0.5 border border-[#D8D4C7] text-xs font-bold">
          <button
            type="button"
            onClick={() => handleLang('en')}
            className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
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
            className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
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
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] active:scale-[0.98] text-[#FFFEFA] text-xs font-bold shadow-sm hover:shadow-md transition-all cursor-pointer border border-[#1A2E24]/30"
        >
          <Bot size={15} className="stroke-[2.2]" />
          <span className="hidden md:inline font-bold">{t('raahiAiButton')}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-[#E7B75B] animate-pulse" />
        </button>
      </div>
    </header>
  );
};
