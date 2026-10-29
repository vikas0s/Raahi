import React, { useState } from 'react';
import { ArrowLeft, Bookmark, Navigation, MapPin, Leaf, Check } from 'lucide-react';
import { RouteComparisonCard } from '../components/journey/RouteComparisonCard';
import { JourneyTimeline } from '../components/journey/JourneyTimeline';
import { TransitMap } from '../components/map/TransitMap';
import { createSavedRoute } from '../services/api';
import type { RouteItinerary, GeoLocation } from '../types/transit';
import { useTranslation } from '../i18n/LanguageContext';

interface Props {
  originLocation: GeoLocation | null;
  destLocation: GeoLocation | null;
  routes: RouteItinerary[];
  selectedRoute: RouteItinerary | null;
  city: string;
  onSelectRoute: (route: RouteItinerary) => void;
  onBackToSearch: () => void;
  onRouteSaved?: () => void;
}

export const PlanJourneyView: React.FC<Props> = ({
  originLocation,
  destLocation,
  routes,
  selectedRoute,
  city,
  onSelectRoute,
  onBackToSearch,
  onRouteSaved
}) => {
  const { t } = useTranslation();
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveCurrentRoute = async () => {
    if (!originLocation || !destLocation || !selectedRoute) return;
    setIsSaving(true);
    try {
      const name = `${originLocation.name.split('(')[0].trim()} to ${destLocation.name.split('(')[0].trim()}`;
      await createSavedRoute(
        name,
        originLocation.name,
        destLocation.name,
        city,
        selectedRoute.tag.toLowerCase().replace(' ', '_')
      );
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      if (onRouteSaved) onRouteSaved();
    } catch (err) {
      console.error('Failed to save route:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Route Journey Header Card */}
      <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_2px_14px_rgba(41,45,41,0.04)] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <button
            type="button"
            onClick={onBackToSearch}
            className="inline-flex items-center gap-1.5 text-xs text-[#304B3C] hover:text-[#1F231F] mb-2.5 cursor-pointer font-bold tracking-tight transition-colors"
          >
            <ArrowLeft size={14} className="stroke-[2.5]" />
            <span>{t('modifySearch')}</span>
          </button>

          <div className="flex flex-wrap items-center gap-2.5 text-lg font-bold text-[#1F231F]">
            <span className="flex items-center gap-1.5 text-[#2E5A3D]">
              <MapPin size={18} className="stroke-[2.5]" />
              <span>{originLocation?.name || 'Origin'}</span>
            </span>
            <span className="text-[#A8A499] font-medium">→</span>
            <span className="flex items-center gap-1.5 text-[#B85732]">
              <Navigation size={18} className="stroke-[2.5]" />
              <span>{destLocation?.name || 'Destination'}</span>
            </span>
          </div>

          <p className="text-xs font-semibold text-[#52544D] mt-1.5">
            {routes.length} transit itineraries calculated • {city} Transit Grid
          </p>
        </div>

        {/* Save Route Action Button */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleSaveCurrentRoute}
            disabled={isSaving || saveSuccess}
            className={`inline-flex items-center gap-2 px-4.5 py-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer shadow-xs active:scale-95 ${
              saveSuccess
                ? 'bg-[#4E7C5F]/20 text-[#21432E] border-[#4E7C5F]/40'
                : 'bg-[#EEECE3] hover:bg-[#E3DFD4] text-[#1F231F] border-[#D8D4C7] hover:border-[#304B3C]/40'
            }`}
          >
            {saveSuccess ? (
              <Check size={15} className="text-[#21432E] stroke-[2.5]" />
            ) : (
              <Bookmark size={15} className="text-[#304B3C] stroke-[2.5]" />
            )}
            <span>{saveSuccess ? t('saved') : t('saveRoute')}</span>
          </button>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Route Options Cards */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-heading font-bold text-lg text-[#1F231F] tracking-tight">
              {t('availableRoutes')}
            </h3>
            <span className="text-xs font-bold text-[#52544D]">{t('clickToInspect')}</span>
          </div>

          <div className="space-y-3.5">
            {routes.map((route) => (
              <RouteComparisonCard
                key={route.id}
                route={route}
                isSelected={selectedRoute?.id === route.id}
                onSelect={() => onSelectRoute(route)}
              />
            ))}
          </div>

          {/* Environmental Carbon Savings Metric Tile */}
          {selectedRoute && (
            <div className="p-4 rounded-2xl bg-[#FFFEFA] border border-[#D8D4C7] text-xs text-[#21432E] flex items-center justify-between shadow-[0_1px_4px_rgba(41,45,41,0.03)]">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-[#4E7C5F]/20 flex items-center justify-center text-[#21432E] shrink-0">
                  <Leaf size={16} className="stroke-[2.5]" />
                </div>
                <div>
                  <p className="font-bold text-[#1F231F]">Clean Transit Impact</p>
                  <p className="text-[11.5px] font-semibold text-[#52544D]">Saves ~{selectedRoute.eco_carbon_savings_kg} kg CO₂ emissions</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-[#21432E] bg-[#4E7C5F]/18 px-2.5 py-1 rounded-full border border-[#4E7C5F]/30">
                Eco Verified
              </span>
            </div>
          )}
        </div>

        {/* Right Column: Synchronized Map & Step-by-Step Directions */}
        <div className="lg:col-span-7 space-y-5">
          <div className="h-[360px] sm:h-[420px] w-full">
            <TransitMap
              selectedRoute={selectedRoute}
              allRoutes={routes}
              origin={originLocation}
              destination={destLocation}
            />
          </div>

          {selectedRoute && (
            <JourneyTimeline route={selectedRoute} />
          )}
        </div>
      </div>
    </div>
  );
};
