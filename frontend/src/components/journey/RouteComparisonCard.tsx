import React from 'react';
import { IndianRupee, ArrowLeftRight, Footprints, Sparkles, ChevronRight, Check, MoonStar, Ban, Clock } from 'lucide-react';
import type { RouteItinerary } from '../../types/transit';
import { formatTime12 } from '../../utils/time';
import { DelayStatusBadge } from '../common/DelayStatusBadge';
import { CrowdLevelIndicator } from '../common/CrowdLevelIndicator';
import { TransitModeIcon } from '../common/TransitModeIcon';
import { useTranslation } from '../../i18n/LanguageContext';
import { localizeRouteTag, localizeMode } from '../../i18n/translations';

interface Props {
  route: RouteItinerary;
  isSelected: boolean;
  onSelect: () => void;
}

export const RouteComparisonCard: React.FC<Props> = ({ route, isSelected, onSelect }) => {
  const { t, language } = useTranslation();
  const isUnavailable = route.service_available === false;

  const getTagBadgeClass = () => {
    if (isUnavailable) {
      return 'bg-[#78716C]/15 text-[#57534E] border-[#A8A29E]/50 font-bold';
    }
    if (route.tag.startsWith('🚆') || route.route_type === 'rail_connect') {
      return 'bg-[#8B1E1E]/15 text-[#6B1414] border-[#8B1E1E]/40 font-bold ring-1 ring-[#8B1E1E]/20';
    }
    switch (route.tag) {
      case 'Fastest':
        return 'bg-[#64836D]/18 text-[#253D30] border-[#64836D]/40 font-bold';
      case 'Multi-Transport (Auto + Metro)':
        return 'bg-[#7C3AED]/20 text-[#5B21B6] border-[#7C3AED]/50 font-extrabold ring-1 ring-[#7C3AED]/30';
      case 'Multi-Transport (E-Rickshaw + Metro)':
        return 'bg-[#059669]/20 text-[#065F46] border-[#059669]/50 font-bold';
      case 'Multi-Transport (Braj Feeder)':
        return 'bg-[#D97706]/20 text-[#92400E] border-[#D97706]/50 font-bold';
      case 'Lowest Fare':
        return 'bg-[#C8795A]/18 text-[#8C3D1E] border-[#C8795A]/40 font-bold';
      case 'Least Crowded':
        return 'bg-[#E7B75B]/30 text-[#6B4905] border-[#E7B75B]/50 font-bold';
      case 'Govt Metered Taxi':
        return 'bg-[#EAB308]/20 text-[#854D0E] border-[#EAB308]/50 font-bold ring-1 ring-[#EAB308]/30';
      case 'Mumbai Suburban Local':
        return 'bg-[#1E3A8A]/18 text-[#1E3A8A] border-[#1E3A8A]/45 font-extrabold ring-1 ring-[#1E3A8A]/25';
      case 'Maha Mumbai Metro':
        return 'bg-[#0D9488]/18 text-[#0F766E] border-[#0D9488]/45 font-bold';
      case 'BEST Electric Bus':
        return 'bg-[#15803D]/18 text-[#166534] border-[#15803D]/45 font-bold';
      case 'Namma Metro':
        return 'bg-[#7E22CE]/18 text-[#6B21A8] border-[#7E22CE]/45 font-bold';
      case 'BMTC Electric Bus':
        return 'bg-[#0284C7]/18 text-[#0369A1] border-[#0284C7]/45 font-bold';
      case 'DTC Electric Bus':
        return 'bg-[#00A86B]/15 text-[#006A44] border-[#00A86B]/40 font-bold';
      case 'Govt Metered Auto':
        return 'bg-[#E68A00]/15 text-[#8F5500] border-[#E68A00]/40 font-bold';
      case 'Short Distance Recommended':
        return 'bg-[#E68A00]/22 text-[#78350F] border-[#E68A00]/50 font-extrabold ring-1 ring-[#E68A00]/30';
      case 'Local E-Rickshaw Hop':
        return 'bg-[#00897B]/20 text-[#004D40] border-[#00897B]/50 font-bold';
      case 'Metro (Alternative)':
        return 'bg-[#1976D2]/15 text-[#0D47A1] border-[#1976D2]/40 font-bold';
      case 'Direct Cab':
        return 'bg-[#3B5360]/15 text-[#24353E] border-[#3B5360]/40 font-bold';
      case 'Most Popular':
        return 'bg-[#00897B]/18 text-[#004D40] border-[#00897B]/40 font-bold';
      case 'Green Electric Bus':
        return 'bg-[#00A86B]/15 text-[#006A44] border-[#00A86B]/40 font-bold';
      case 'Direct Reserved Auto':
        return 'bg-[#D97706]/15 text-[#92400E] border-[#D97706]/40 font-bold';
      case 'Private Taxi (Limited)':
        return 'bg-[#475569]/15 text-[#334155] border-[#475569]/40 font-bold';
      case 'Metro Closed':
        return 'bg-[#EF4444]/12 text-[#991B1B] border-[#EF4444]/30 font-bold';
      default:
        return 'bg-[#EEECE3] text-[#1F231F] border-[#D8D4C7] font-bold';
    }
  };

  const localizedTag = localizeRouteTag(route.tag, language);

  return (
    <div
      onClick={isUnavailable ? undefined : onSelect}
      className={`relative w-full rounded-2xl p-5 transition-all duration-200 border text-left ${
        isUnavailable
          ? 'bg-[#F5F5F4] border-[#D6D3D1] opacity-65 cursor-not-allowed'
          : isSelected
          ? 'bg-[#FFFEFA] border-[#304B3C] shadow-[0_4px_22px_-2px_rgba(48,75,60,0.14)] ring-2 ring-[#304B3C] cursor-pointer'
          : 'bg-[#FFFEFA] hover:bg-white border-[#D8D4C7] hover:border-[#304B3C]/50 shadow-[0_1px_4px_rgba(41,45,41,0.03)] hover:shadow-[0_4px_18px_rgba(48,75,60,0.08)] cursor-pointer'
      }`}
    >
      {/* Unavailable banner */}
      {isUnavailable && (
        <div className="flex items-center gap-2 px-3.5 py-2 mb-3.5 rounded-xl bg-[#FEF2F2] border border-[#FECACA] text-[#991B1B]">
          <MoonStar size={15} className="shrink-0 stroke-[2.5]" />
          <span className="text-xs font-bold leading-snug">
            {route.unavailable_reason || t('serviceUnavailable')}
          </span>
        </div>
      )}

      {/* Header: Recommendation Tag, Timings & Delay badge */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs border tracking-tight shadow-2xs ${getTagBadgeClass()}`}>
            {isUnavailable ? <Ban size={12} className="shrink-0" /> : <Sparkles size={12} className="shrink-0" />}
            <span>{localizedTag}</span>
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#EEECE3]/70 font-mono text-xs font-bold text-[#253D30] border border-[#D8D4C7]/80">
            <Clock size={12} className="text-[#5B8A6E] stroke-[2.2]" />
            <span>{formatTime12(route.departure_time)}</span>
            <span className="text-[#888B82]">→</span>
            <span>{formatTime12(route.arrival_time)}</span>
          </span>
        </div>

        {isUnavailable ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-[#EF4444]/12 text-[#991B1B] border border-[#EF4444]/30 shadow-2xs">
            <Ban size={12} className="stroke-[2.5]" />
            <span>{language === 'hi' ? 'सेवा बंद' : 'Closed'}</span>
          </span>
        ) : (
          <DelayStatusBadge delayMinutes={route.total_delay_minutes} />
        )}
      </div>

      {/* Main Metric Row: Duration & Total Fare */}
      <div className="flex items-baseline justify-between gap-3 mb-2.5">
        <div>
          <h3 className="font-heading font-extrabold text-2xl text-[#1F231F] tracking-tight">
            {route.total_duration_minutes} <span className="text-xs font-bold uppercase tracking-wider text-[#52544D] ml-0.5">{t('mins')}</span>
          </h3>
          <p className="text-xs font-semibold text-[#454841] mt-0.5 line-clamp-1">{route.title}</p>
          {route.fare_breakdown && (
            <p className="text-[11px] font-bold text-[#64836D] mt-1 line-clamp-1">
              📊 {route.fare_breakdown}
            </p>
          )}
        </div>

        <div className="text-right shrink-0">
          <div className="flex items-center justify-end font-heading font-extrabold text-2xl text-[#304B3C]">
            <IndianRupee size={18} className="mt-0.5 stroke-[2.5]" />
            <span>{route.total_fare_inr.toFixed(0)}</span>
          </div>
          <span className="text-[11px] font-bold uppercase tracking-wide text-[#52544D] block">{t('totalFare')}</span>
          {route.pink_pass_fare_inr !== undefined && (
            <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#C2185B] bg-[#FCE4EC] px-2 py-0.5 rounded-full border border-[#F8BBD0] mt-1">
              🌸 {language === 'hi' ? 'गुलाबी टिकट: ₹0 (मुफ्त)' : 'Pink Pass: ₹0'}
            </span>
          )}
        </div>
      </div>

      {/* Mode Sequence Strip */}
      <div className="flex items-center gap-2 py-2 px-3 rounded-xl bg-[#EEECE3]/60 border border-[#D8D4C7] mb-3.5 overflow-x-auto">
        {route.legs.map((leg, idx) => (
          <React.Fragment key={leg.id || idx}>
            <div className="flex items-center gap-1.5 shrink-0 text-xs text-[#1F231F]">
              <TransitModeIcon mode={leg.mode} size={14} />
              <span className="text-xs font-bold max-w-[120px] truncate">
                {leg.mode === 'rail' && leg.train_number
                  ? `${leg.train_number} ${leg.train_name || 'Train'}`
                  : (leg.line_name || (leg.mode === 'walk' ? `${leg.duration_minutes}m ${t('walking')}` : localizeMode(leg.mode, language)))}
              </span>
            </div>
            {idx < route.legs.length - 1 && (
              <ChevronRight size={13} className="text-[#A8A499] shrink-0" />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Metadata Row: Transfers, Walk Duration, Crowd Level */}
      <div className="flex items-center justify-between text-xs text-[#454841] pt-2.5 border-t border-[#D8D4C7]">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 font-bold text-[#2A2E2A]" title={t('transfersCountTooltip')}>
            <ArrowLeftRight size={14} className="text-[#52544D]" />
            <span>{route.transfers_count === 0 ? t('direct') : `${route.transfers_count} ${t('transfer')}`}</span>
          </span>
          <span className="flex items-center gap-1.5 font-bold text-[#2A2E2A]" title={t('walkingTimeTooltip')}>
            <Footprints size={14} className="text-[#52544D]" />
            <span>{route.walking_duration_minutes}m {t('walking')}</span>
          </span>
        </div>

        <CrowdLevelIndicator level={route.overall_crowd} />
      </div>

      {/* Footer Recommendation Explanation & Selection state */}
      <div className="mt-3 pt-2.5 border-t border-[#D8D4C7]/60 text-xs font-semibold flex items-center justify-between">
        <span className="text-[#304B3C] line-clamp-1 flex items-center gap-1">
          <span>💡</span>
          <span>{route.tag_reason}</span>
        </span>
        {isSelected ? (
          <span className="inline-flex items-center gap-1 font-bold text-[#FFFEFA] text-xs shrink-0 ml-2 bg-[#304B3C] px-3 py-1 rounded-full shadow-2xs">
            <Check size={13} className="stroke-[2.5]" />
            {t('selected')}
          </span>
        ) : (
          <span className="text-[11px] font-bold text-[#64836D] group-hover:underline">
            {t('selectRouteArrow')}
          </span>
        )}
      </div>
    </div>
  );
};
