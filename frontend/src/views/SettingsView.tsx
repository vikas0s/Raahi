import React from 'react';
import { Settings, Globe, MapPin, Accessibility, Shield, Zap, Key, CheckCircle2 } from 'lucide-react';
import type { AppLanguage } from '../types/transit';
import { useTranslation } from '../i18n/LanguageContext';

interface Props {
  selectedCity: string;
  onCityChange: (city: string) => void;
  language: AppLanguage;
  onLanguageChange: (lang: AppLanguage) => void;
  accessibleOnly: boolean;
  onAccessibleChange: (val: boolean) => void;
  reducedMotion: boolean;
  onReducedMotionChange: (val: boolean) => void;
}

export const SettingsView: React.FC<Props> = ({
  selectedCity,
  onCityChange,
  language: propLang,
  onLanguageChange,
  accessibleOnly,
  onAccessibleChange,
  reducedMotion,
  onReducedMotionChange
}) => {
  const { t, language, setLanguage } = useTranslation();
  const activeLang = propLang || language;

  const handleLang = (lang: AppLanguage) => {
    setLanguage(lang);
    onLanguageChange(lang);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Settings size={20} className="text-[#304B3C]" />
          <h2 className="font-heading font-bold text-2xl text-[#1F231F]">
            {t('settingsTitle')}
          </h2>
        </div>
        <p className="text-xs text-[#52544D] font-medium mt-1">
          {t('settingsSubtitle')}
        </p>
      </div>

      <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] divide-y divide-[#D8D4C7] shadow-[0_2px_12px_rgba(41,45,41,0.03)]">
        {/* City Network Selector */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h4 className="font-heading font-bold text-sm text-[#1F231F] flex items-center gap-2">
              <MapPin size={16} className="text-[#4E7C5F]" />
              <span>{t('regionalCity')}</span>
            </h4>
            <p className="text-xs text-[#52544D] font-medium mt-0.5">
              Select the active metropolitan public transport network.
            </p>
          </div>
          <select
            value={selectedCity}
            onChange={(e) => onCityChange(e.target.value)}
            className="px-3.5 py-2 text-xs font-bold rounded-xl bg-[#EEECE3] text-[#1F231F] border border-[#D8D4C7] outline-none cursor-pointer"
          >
            <option value="Delhi NCR">Delhi NCR (DMRC Metro, DTC Electric Bus)</option>
            <option value="Mumbai">Mumbai (Local Rail, Mumbai Metro, BEST)</option>
            <option value="Bengaluru">Bengaluru (Namma Metro, BMTC)</option>
          </select>
        </div>

        {/* Interface Language */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h4 className="font-heading font-bold text-sm text-[#1F231F] flex items-center gap-2">
              <Globe size={16} className="text-[#4E7C5F]" />
              <span>{t('appLanguage')}</span>
            </h4>
            <p className="text-xs text-[#52544D] font-medium mt-0.5">
              Support for English and Hindi (हिन्दी).
            </p>
          </div>
          <div className="inline-flex rounded-xl bg-[#EEECE3] p-1 border border-[#D8D4C7] text-xs font-bold">
            <button
              onClick={() => handleLang('en')}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                activeLang === 'en' ? 'bg-[#253D30] text-white font-bold shadow-xs' : 'text-[#52544D] hover:text-[#1F231F]'
              }`}
            >
              English
            </button>
            <button
              onClick={() => handleLang('hi')}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                activeLang === 'hi' ? 'bg-[#253D30] text-white font-bold shadow-xs' : 'text-[#52544D] hover:text-[#1F231F]'
              }`}
            >
              हिन्दी
            </button>
          </div>
        </div>

        {/* Accessibility Features */}
        <div className="p-5 flex items-center justify-between gap-3">
          <div>
            <h4 className="font-heading font-bold text-sm text-[#1F231F] flex items-center gap-2">
              <Accessibility size={16} className="text-[#4E7C5F]" />
              <span>{t('accessibleRouting')}</span>
            </h4>
            <p className="text-xs text-[#52544D] font-medium mt-0.5">
              {t('accessibleRoutingDesc')}
            </p>
          </div>
          <input
            type="checkbox"
            checked={accessibleOnly}
            onChange={(e) => onAccessibleChange(e.target.checked)}
            className="w-5 h-5 accent-[#253D30] rounded cursor-pointer"
          />
        </div>

        {/* Reduced Motion */}
        <div className="p-5 flex items-center justify-between gap-3">
          <div>
            <h4 className="font-heading font-bold text-sm text-[#1F231F] flex items-center gap-2">
              <Zap size={16} className="text-[#4E7C5F]" />
              <span>{t('reducedMotionSetting')}</span>
            </h4>
            <p className="text-xs text-[#52544D] font-medium mt-0.5">
              {t('reducedMotionDesc')}
            </p>
          </div>
          <input
            type="checkbox"
            checked={reducedMotion}
            onChange={(e) => onReducedMotionChange(e.target.checked)}
            className="w-5 h-5 accent-[#253D30] rounded cursor-pointer"
          />
        </div>
      </div>

      {/* Transit API Keys & Mobility Networks Integration Card */}
      <div className="rounded-2xl border border-[#D8D4C7] bg-[#FFFEFA] p-5 shadow-[0_2px_12px_rgba(41,45,41,0.04)] space-y-4">
        <div className="flex items-center justify-between border-b border-[#D8D4C7] pb-3">
          <div className="flex items-center gap-2">
            <Key size={18} className="text-[#304B3C]" />
            <h3 className="font-heading font-bold text-base text-[#1F231F]">
              Transit API Credentials & Fare Calculation Engines
            </h3>
          </div>
          <span className="inline-flex items-center gap-1 text-xs font-bold text-[#2A4D38] bg-[#64836D]/15 px-2.5 py-1 rounded-full border border-[#64836D]/30">
            <CheckCircle2 size={13} />
            <span>3 Active Services</span>
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
          {/* OTD Delhi */}
          <div className="p-3.5 rounded-xl bg-[#EEECE3]/70 border border-[#D8D4C7] space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#1F231F]">1. Open Transit Data Delhi (OTD)</span>
              <span className="text-[10px] font-bold text-[#2E7D32] bg-[#E8F5E9] px-2 py-0.5 rounded border border-[#C8E6C9]">Configured (.env)</span>
            </div>
            <p className="text-[#52544D] leading-relaxed">
              Live GPS telemetry for 7,000+ DTC & DIMTS cluster electric/CNG buses, route IDs, agency feeds, and arrival estimates.
            </p>
            <code className="text-[11px] block bg-white/80 p-1.5 rounded font-mono text-[#304B3C] border border-[#D8D4C7]">
              OTD_DELHI_API_KEY=hAGgv0...H3a
            </code>
          </div>

          {/* Delhi Govt Fare Tariff Engine */}
          <div className="p-3.5 rounded-xl bg-[#EEECE3]/70 border border-[#D8D4C7] space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#1F231F]">2. Delhi Govt Gazetted Fare Engine</span>
              <span className="text-[10px] font-bold text-[#2E7D32] bg-[#E8F5E9] px-2 py-0.5 rounded border border-[#C8E6C9]">Built-in & Active</span>
            </div>
            <p className="text-[#52544D] leading-relaxed">
              Auto meter tariff (₹30 first 1.5km + ₹11/km), DTC E-Bus slabs (₹10/₹15/₹20/₹25), DTC Non-AC (₹5/₹10/₹15), and Pink Ticket (₹0 Free for Women).
            </p>
            <div className="text-[11px] font-bold text-[#64836D]">
              Auto TSR + E-Rickshaw + DTC Bus + DMRC Metro
            </div>
          </div>

          {/* Google Maps Directions */}
          <div className="p-3.5 rounded-xl bg-[#EEECE3]/70 border border-[#D8D4C7] space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#1F231F]">3. Google Maps Road Traffic API</span>
              <span className="text-[10px] font-bold text-[#B85732] bg-[#FBE9E7] px-2 py-0.5 rounded border border-[#FFCCBC]">Optional Key</span>
            </div>
            <p className="text-[#52544D] leading-relaxed">
              Provides live congestion road duration for Auto/Cab navigation. <em>(Built-in OpenStreetMap OSRM engine active as default)</em>.
            </p>
            <code className="text-[11px] block bg-white/80 p-1.5 rounded font-mono text-[#52544D] border border-[#D8D4C7]">
              GOOGLE_MAPS_API_KEY (optional)
            </code>
          </div>

          {/* ONDC & Mobility */}
          <div className="p-3.5 rounded-xl bg-[#EEECE3]/70 border border-[#D8D4C7] space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#1F231F]">4. ONDC / Ride-Hailing Cab API</span>
              <span className="text-[10px] font-bold text-[#B85732] bg-[#FBE9E7] px-2 py-0.5 rounded border border-[#FFCCBC]">Optional Key</span>
            </div>
            <p className="text-[#52544D] leading-relaxed">
              Enables real-time dynamic booking estimates with BluSmart EV and open-mobility auto networks via Beckn protocol.
            </p>
            <code className="text-[11px] block bg-white/80 p-1.5 rounded font-mono text-[#52544D] border border-[#D8D4C7]">
              UBER_SERVER_TOKEN / ONDC_BAP_KEY (optional)
            </code>
          </div>
        </div>
      </div>

      {/* Engineering Compliance Card */}
      <div className="p-5 rounded-2xl bg-[#EEECE3]/60 border border-[#D8D4C7] space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-[#253D30] uppercase tracking-wider">
          <Shield size={14} className="stroke-[2.2]" />
          <span>{t('missionTag')} Engineering Notes</span>
        </div>
        <p className="text-xs text-[#52544D] font-medium leading-relaxed">
          Raahi is designed to minimize multi-modal commuter friction across Indian megacities.
          All simulated alerts are transparently designated as <code className="text-[#BD4F44]">[SIMULATED]</code> to preserve data integrity.
        </p>
      </div>
    </div>
  );
};
