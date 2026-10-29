import React from 'react';
import { IndianRupee, ArrowLeftRight, Footprints, Sparkles, ChevronRight, Check } from 'lucide-react';
import type { RouteItinerary } from '../../types/transit';
import { DelayStatusBadge } from '../common/DelayStatusBadge';
import { CrowdLevelIndicator } from '../common/CrowdLevelIndicator';
import { TransitModeIcon } from '../common/TransitModeIcon';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  route: RouteItinerary;
  isSelected: boolean;
  onSelect: () => void;
}

export const RouteComparisonCard: React.FC<Props> = ({ route, isSelected, onSelect }) => {
  const { t } = useTranslation();

  const getTagBadgeClass = () => {
    switch (route.tag) {
      case 'Fastest':
        return 'bg-[#64836D]/18 text-[#253D30] border-[#64836D]/40 font-bold';
      case 'Lowest Fare':
        return 'bg-[#C8795A]/18 text-[#8C3D1E] border-[#C8795A]/40 font-bold';
      case 'Least Crowded':
        return 'bg-[#E7B75B]/30 text-[#6B4905] border-[#E7B75B]/50 font-bold';
      default:
        return 'bg-[#EEECE3] text-[#1F231F] border-[#D8D4C7] font-bold';
    }
  };

  return (
    <div
      onClick={onSelect}
      className={`relative w-full rounded-2xl p-5 transition-all duration-200 cursor-pointer border text-left ${
        isSelected
          ? 'bg-[#FFFEFA] border-[#304B3C] shadow-[0_4px_22px_-2px_rgba(48,75,60,0.14)] ring-2 ring-[#304B3C]'
          : 'bg-[#FFFEFA] hover:bg-white border-[#D8D4C7] hover:border-[#304B3C]/50 shadow-[0_1px_4px_rgba(41,45,41,0.03)] hover:shadow-[0_4px_18px_rgba(48,75,60,0.08)]'
      }`}
    >
      {/* Header: Recommendation Tag, Timings & Delay badge */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs border tracking-tight shadow-2xs ${getTagBadgeClass()}`}>
            <Sparkles size={12} className="shrink-0" />
            <span>{route.tag}</span>
          </span>
          <span className="text-xs font-semibold text-[#52544D] font-mono tracking-tight">
            {route.departure_time} → {route.arrival_time}
          </span>
        </div>

        <DelayStatusBadge delayMinutes={route.total_delay_minutes} />
      </div>

      {/* Main Metric Row: Duration & Total Fare */}
      <div className="flex items-baseline justify-between gap-3 mb-3.5">
        <div>
          <h3 className="font-heading font-extrabold text-2xl text-[#1F231F] tracking-tight">
            {route.total_duration_minutes} <span className="text-xs font-bold uppercase tracking-wider text-[#52544D] ml-0.5">{t('mins')}</span>
          </h3>
          <p className="text-xs font-semibold text-[#454841] mt-0.5 line-clamp-1">{route.title}</p>
        </div>

        <div className="text-right">
          <div className="flex items-center justify-end font-heading font-extrabold text-2xl text-[#304B3C]">
            <IndianRupee size={18} className="mt-0.5 stroke-[2.5]" />
            <span>{route.total_fare_inr.toFixed(0)}</span>
          </div>
          <span className="text-[11px] font-bold uppercase tracking-wide text-[#52544D]">{t('totalFare')}</span>
        </div>
      </div>

      {/* Mode Sequence Strip */}
      <div className="flex items-center gap-2 py-2 px-3 rounded-xl bg-[#EEECE3]/60 border border-[#D8D4C7] mb-3.5 overflow-x-auto">
        {route.legs.map((leg, idx) => (
          <React.Fragment key={leg.id || idx}>
            <div className="flex items-center gap-1.5 shrink-0 text-xs text-[#1F231F]">
              <TransitModeIcon mode={leg.mode} size={14} />
              <span className="text-xs font-bold max-w-[95px] truncate">
                {leg.line_name || (leg.mode === 'walk' ? `${leg.duration_minutes}m ${t('walking')}` : leg.mode)}
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
          <span className="flex items-center gap-1.5 font-bold text-[#2A2E2A]" title="Transfers count">
            <ArrowLeftRight size={14} className="text-[#52544D]" />
            <span>{route.transfers_count === 0 ? t('direct') : `${route.transfers_count} ${t('transfer')}`}</span>
          </span>
          <span className="flex items-center gap-1.5 font-bold text-[#2A2E2A]" title="Walking time">
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
