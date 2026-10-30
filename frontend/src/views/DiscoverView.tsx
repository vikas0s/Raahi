import React from 'react';
import { Sparkles, ArrowRight, ShieldCheck, Bookmark, Zap } from 'lucide-react';
import { JourneySearch } from '../components/journey/JourneySearch';
import { TravelPreferenceChips } from '../components/journey/TravelPreferenceChips';
import { MiniCityScene } from '../components/scene/MiniCityScene';
import { DelayStatusBadge } from '../components/common/DelayStatusBadge';
import type { SavedRoute, TravelPreferences, TransitIncident, TimeMode } from '../types/transit';
import { useTranslation } from '../i18n/LanguageContext';

interface Props {
  origin: string;
  destination: string;
  city: string;
  preferences: TravelPreferences;
  savedRoutes: SavedRoute[];
  incidents: TransitIncident[];
  onOriginChange: (val: string, coords?: [number, number]) => void;
  onDestinationChange: (val: string, coords?: [number, number]) => void;
  onUseCurrentLocation?: (name: string, coords: [number, number]) => void;
  onPreferencesChange: (prefs: TravelPreferences) => void;
  onSearch: (departureTime?: string, arrivalTime?: string, timeMode?: TimeMode) => void;
  onReplanSaved: (route: SavedRoute) => void;
  onNavigateToPlan: () => void;
  onNavigateToLive: () => void;
  isLoading?: boolean;
}

export const DiscoverView: React.FC<Props> = ({
  origin,
  destination,
  city,
  preferences,
  savedRoutes,
  incidents,
  onOriginChange,
  onDestinationChange,
  onUseCurrentLocation,
  onPreferencesChange,
  onSearch,
  onReplanSaved,
  onNavigateToLive,
  isLoading
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Welcome Hero Section */}
      <section className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pt-1">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#64836D]/20 text-[#253D30] border border-[#64836D]/30 mb-2">
            <Sparkles size={13} className="text-[#4E7C5F]" />
            <span>{t('missionTag')}</span>
          </div>
          <h2 className="font-heading font-bold text-2xl sm:text-3xl text-[#1F231F] tracking-tight">
            {t('heroTitle')}
          </h2>
          <p className="text-sm text-[#52544D] font-medium max-w-xl mt-1 leading-relaxed">
            {t('heroDesc')}
          </p>
        </div>

        {/* Live System Status Pill */}
        <button
          onClick={onNavigateToLive}
          className="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-[#FFFEFA] border border-[#D8D4C7] shadow-[0_1px_4px_rgba(41,45,41,0.03)] hover:border-[#4E7C5F] transition-all cursor-pointer"
        >
          <span className={`w-2.5 h-2.5 rounded-full ${incidents.length > 0 ? 'bg-[#D9943B] animate-ping' : 'bg-[#5B8A6E]'}`} />
          <div className="text-left">
            <p className="text-xs font-extrabold text-[#1F231F]">
              {incidents.length > 0 ? `${incidents.length} ${t('serviceAlerts')}` : t('allLinesNormal')}
            </p>
            <p className="text-[10px] text-[#52544D] font-medium">{city} {t('transitGrid')}</p>
          </div>
          <ArrowRight size={14} className="text-[#52544D] ml-1 stroke-[2.2]" />
        </button>
      </section>

      {/* Main Grid: Search & Preferences + 3D Isometric Mini City */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Search & Preferences */}
        <div className="lg:col-span-8 space-y-4">
          <JourneySearch
            origin={origin}
            destination={destination}
            city={city}
            onOriginChange={onOriginChange}
            onDestinationChange={onDestinationChange}
            onUseCurrentLocation={onUseCurrentLocation}
            onSubmit={onSearch}
            isLoading={isLoading}
          />

          {/* Travel Preferences Chips Panel */}
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-4.5 shadow-[0_2px_12px_rgba(41,45,41,0.03)]">
            <span className="block text-xs font-extrabold uppercase tracking-wider text-[#52544D] mb-3">
              {t('routePriorities')}
            </span>
            <TravelPreferenceChips
              preferences={preferences}
              onChange={onPreferencesChange}
              city={city}
            />
          </div>
        </div>

        {/* Right Column: 3D Miniature City Scene */}
        <div className="lg:col-span-4 h-[340px] lg:h-[380px]">
          <MiniCityScene />
        </div>
      </div>

      {/* Frequent Commutes Section (CropXpert-style metric cards) */}
      <section className="space-y-3.5 pt-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bookmark size={16} className="text-[#4E7C5F] stroke-[2.2]" />
            <h3 className="font-heading font-bold text-lg text-[#1F231F]">
              {t('frequentCommutes')}
            </h3>
          </div>
          <span className="text-xs text-[#52544D] font-bold">{t('oneTapReplan')}</span>
        </div>

        {savedRoutes.length === 0 ? (
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-8 text-center shadow-xs">
            <p className="text-sm font-bold text-[#1F231F]">{t('noSavedJourneys')}</p>
            <p className="text-xs text-[#52544D] font-medium mt-1 max-w-sm mx-auto">
              {t('noSavedJourneysDesc')}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {savedRoutes.slice(0, 3).map((item) => (
              <div
                key={item.id}
                className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-4.5 shadow-[0_1px_4px_rgba(41,45,41,0.02)] hover:shadow-[0_4px_18px_rgba(48,75,60,0.07)] transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h4 className="font-heading font-bold text-sm text-[#1F231F] line-clamp-1">
                      {item.name}
                    </h4>
                    <DelayStatusBadge delayMinutes={item.current_delay_minutes} />
                  </div>

                  <p className="text-xs text-[#52544D] font-medium line-clamp-1">
                    {item.origin} → {item.destination}
                  </p>

                  <div className="flex items-center gap-3 mt-3 text-xs text-[#1F231F] font-bold">
                    <span>⏱️ ~{item.typical_duration_minutes}m</span>
                    <span className="text-[#253D30] font-extrabold">💰 ₹{item.typical_fare_inr.toFixed(0)}</span>
                    <span className="text-[#52544D] font-semibold">
                      {item.typical_transfers === 0 ? t('direct') : `${item.typical_transfers} ${t('transfers')}`}
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => onReplanSaved(item)}
                  className="mt-4 w-full py-2.5 px-3 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-xs hover:shadow-sm"
                >
                  <Zap size={13} className="fill-current" />
                  <span>{t('replanNow')}</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Official Telemetry Grounding Banner */}
      <section className="bg-[#EEECE3]/70 rounded-2xl border border-[#D8D4C7] p-4.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-xl bg-[#5B8A6E]/20 flex items-center justify-center text-[#253D30] shrink-0">
            <ShieldCheck size={20} className="stroke-[2.2]" />
          </div>
          <div>
            <h4 className="text-xs font-extrabold text-[#1F231F] uppercase tracking-wide">
              {t('officialTelemetry')}
            </h4>
            <p className="text-xs text-[#52544D] font-medium mt-0.5">
              {t('officialTelemetryDesc')}
            </p>
          </div>
        </div>

        <button
          onClick={onNavigateToLive}
          className="px-4 py-2 rounded-xl bg-[#FFFEFA] border border-[#D8D4C7] text-xs font-bold text-[#253D30] hover:bg-white shadow-2xs transition-all cursor-pointer shrink-0"
        >
          {t('viewSystemStatus')}
        </button>
      </section>
    </div>
  );
};
