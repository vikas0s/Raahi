import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Info, Clock } from 'lucide-react';
import type { RouteItinerary } from '../../types/transit';
import { formatTime12 } from '../../utils/time';
import { TransitModeIcon } from '../common/TransitModeIcon';
import { DelayStatusBadge } from '../common/DelayStatusBadge';
import { CrowdLevelIndicator } from '../common/CrowdLevelIndicator';
import { useTranslation } from '../../i18n/LanguageContext';
import { localizeMode } from '../../i18n/translations';

interface Props {
  route: RouteItinerary;
  className?: string;
}

export const JourneyTimeline: React.FC<Props> = ({ route, className = '' }) => {
  const { t, language } = useTranslation();
  const [expandedLegs, setExpandedLegs] = useState<Record<string, boolean>>({});

  const toggleLegStops = (legId: string) => {
    setExpandedLegs(prev => ({ ...prev, [legId]: !prev[legId] }));
  };

  return (
    <div className={`w-full bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_2px_14px_rgba(41,45,41,0.04)] ${className}`}>
      {/* Route Header Overview */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[#D8D4C7]">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#304B3C]">
            {t('stepByStepItinerary')}
          </span>
          <h3 className="font-heading font-bold text-lg text-[#1F231F] mt-0.5 tracking-tight">
            {route.title}
          </h3>
        </div>

        <div className="flex items-center gap-2.5 text-xs">
          <span className="px-3 py-1.5 rounded-xl bg-[#EEECE3] font-bold text-[#1F231F] flex items-center gap-1.5 border border-[#D8D4C7]">
            <Clock size={13} className="text-[#304B3C] stroke-[2.5]" />
            <span>{formatTime12(route.departure_time)} → {formatTime12(route.arrival_time)} ({route.total_duration_minutes}m)</span>
          </span>
          <span className="px-3 py-1.5 rounded-xl bg-[#4E7C5F]/20 font-bold text-[#21432E] border border-[#4E7C5F]/35">
            ₹{route.total_fare_inr.toFixed(0)} {t('totalFare').toLowerCase()}
          </span>
        </div>
      </div>

      {/* Vertical Timeline Legs */}
      <div className="mt-5 space-y-6 relative pl-3 before:absolute before:left-6.5 before:top-3 before:bottom-4 before:w-0.5 before:bg-[#D8D4C7]">
        {route.legs.map((leg, index) => {
          const isExpanded = !!expandedLegs[leg.id];
          const hasStops = leg.intermediate_stops && leg.intermediate_stops.length > 0;

          return (
            <div key={leg.id || index} className="relative flex items-start gap-4">
              {/* Timeline Mode Icon Node */}
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 z-10 shadow-xs border-2 ${
                  leg.mode === 'walk'
                    ? 'bg-[#EEECE3] border-[#52544D]'
                    : 'bg-[#FFFEFA] border-[#253D30]'
                }`}
                style={{ borderColor: leg.line_color || (leg.mode === 'walk' ? '#52544D' : '#253D30') }}
              >
                <TransitModeIcon mode={leg.mode} size={14} />
              </div>

              {/* Leg Details Card */}
              <div className="flex-1 bg-[#FFFEFA] rounded-xl border border-[#D8D4C7] p-4 shadow-[0_1px_4px_rgba(41,45,41,0.03)] transition-all hover:border-[#304B3C]/50">
                {/* Leg Header */}
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-heading font-bold text-sm text-[#1F231F]">
                      {leg.line_name || (leg.mode === 'walk' ? t('walkingSection') : localizeMode(leg.mode, language))}
                    </span>
                    {leg.is_delayed && (
                      <DelayStatusBadge delayMinutes={leg.delay_minutes} />
                    )}
                  </div>
                  <span className="text-xs font-mono font-bold text-[#52544D]">
                    {formatTime12(leg.departure_time)} – {formatTime12(leg.arrival_time)} ({leg.duration_minutes}m)
                  </span>
                </div>

                {/* Railway Special Badge Strip */}
                {leg.mode === 'rail' && (
                  <div className="flex flex-wrap items-center gap-2 mb-2.5 p-2 rounded-xl bg-[#8B1E1E]/8 border border-[#8B1E1E]/25 text-xs">
                    <span className="inline-flex items-center gap-1 font-extrabold text-[#8B1E1E]">
                      <span>{language === 'hi' ? '🚆 भारतीय रेल' : '🚆 Indian Railways'}</span>
                    </span>
                    {leg.platform && (
                      <span className="px-2 py-0.5 rounded-md bg-[#8B1E1E]/15 font-bold text-[#8B1E1E] border border-[#8B1E1E]/30">
                        {leg.platform}
                      </span>
                    )}
                    {leg.coach_classes && leg.coach_classes.length > 0 && (
                      <span className="px-2 py-0.5 rounded-md bg-[#EEECE3] font-bold text-[#454841] border border-[#D8D4C7]">
                        {t('classesLabel')} {leg.coach_classes.join(' · ')}
                      </span>
                    )}
                    <span className="ml-auto text-[11px] font-semibold text-[#8B1E1E]">
                      {leg.data_source === 'railradar_live' ? t('liveNTES') : t('verifiedTimetable')}
                    </span>
                  </div>
                )}

                {/* Origin / Destination for Leg */}
                <div className="text-xs space-y-1.5 mb-2.5">
                  <p className="flex items-center gap-2 font-bold text-[#1F231F]">
                    <span className="w-2 h-2 rounded-full bg-[#4E7C5F]" />
                    <span>{t('fromLabel')} {leg.origin_name}</span>
                  </p>
                  <p className="flex items-center gap-2 font-bold text-[#1F231F]">
                    <span className="w-2 h-2 rounded-full bg-[#B85732]" />
                    <span>{t('toLabel')} {leg.destination_name}</span>
                  </p>
                </div>

                {/* Commuter Guidance Callout */}
                <div className="text-xs text-[#1F231F] font-semibold bg-[#EEECE3]/70 rounded-xl p-3 border border-[#D8D4C7] mb-2.5 flex items-start gap-2.5 leading-relaxed">
                  <Info size={15} className="text-[#304B3C] shrink-0 mt-0.5 stroke-[2.5]" />
                  <p>{leg.instructions}</p>
                </div>

                {/* Leg Fare & Tariff Details */}
                {leg.fare_details && (
                  <div className="text-xs font-bold text-[#2A4D38] bg-[#64836D]/15 rounded-xl px-3 py-2 border border-[#64836D]/30 mb-2.5 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <span>🏷️</span>
                      <span>{leg.fare_details}</span>
                    </span>
                    {leg.fare_inr !== undefined && leg.fare_inr > 0 && (
                      <span className="font-extrabold text-[#1F231F] text-sm shrink-0 ml-2">₹{leg.fare_inr.toFixed(0)}</span>
                    )}
                  </div>
                )}

                {/* Intermediate Stops Toggle */}
                {hasStops && (
                  <div>
                    <button
                      type="button"
                      onClick={() => toggleLegStops(leg.id)}
                      className="inline-flex items-center gap-1.5 text-xs text-[#253D30] font-bold hover:underline cursor-pointer"
                    >
                      <span>{leg.stops_count} {t('intermediateStops')}</span>
                      {isExpanded ? <ChevronUp size={14} className="stroke-[2.5]" /> : <ChevronDown size={14} className="stroke-[2.5]" />}
                    </button>

                    {isExpanded && (
                      <div className="mt-2.5 pl-3 border-l-2 border-[#D8D4C7] space-y-1 text-xs font-semibold text-[#3D4039]">
                        {leg.intermediate_stops.map((stop, sIdx) => (
                          <div key={sIdx} className="flex items-center gap-2 py-0.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#52544D]" />
                            <span>{stop}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Footer Metadata */}
                <div className="mt-3 pt-2.5 border-t border-[#D8D4C7]/60 flex items-center justify-between text-xs font-bold text-[#52544D]">
                  <span>{t('distanceLabel')} {(leg.distance_meters / 1000).toFixed(1)} km</span>
                  <CrowdLevelIndicator level={leg.crowd_level} compact />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
