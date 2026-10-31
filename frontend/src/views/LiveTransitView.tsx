import React from 'react';
import { Radio, Clock, ArrowRight, CheckCircle2, Calendar, Compass, Info } from 'lucide-react';
import { DemoControls } from '../components/live/DemoControls';
import type { TransitIncident, CityRealtimeContext } from '../types/transit';
import { DelayStatusBadge } from '../components/common/DelayStatusBadge';
import { CrowdLevelIndicator } from '../components/common/CrowdLevelIndicator';
import { TransitModeIcon } from '../components/common/TransitModeIcon';
import { useTranslation } from '../i18n/LanguageContext';

interface Props {
  incidents: TransitIncident[];
  city: string;
  realtimeContext?: CityRealtimeContext | null;
  onRefreshIncidents: () => void;
  onPlanAlternative: (lineName: string) => void;
}

const HINDI_DAYS: Record<string, string> = {
  Monday: 'सोमवार',
  Tuesday: 'मंगलवार',
  Wednesday: 'बुधवार',
  Thursday: 'गुरुवार',
  Friday: 'शुक्रवार',
  Saturday: 'शनिवार',
  Sunday: 'रविवार',
  Weekday: 'कार्यदिवस',
  Weekend: 'सप्ताहांत'
};

export const LiveTransitView: React.FC<Props> = ({
  incidents,
  city,
  realtimeContext,
  onRefreshIncidents,
  onPlanAlternative
}) => {
  const { t, language } = useTranslation();

  const getCityEmptyStateDesc = (cityName: string) => {
    const c = (cityName || '').toLowerCase();
    if (language === 'hi') {
      if (c.includes('mumbai')) {
        return 'मुंबई उपनगरीय रेलवे (पश्चिमी, मध्य एवं हार्बर लाइन), मेट्रो लाइन 3 एक्वा लाइन और बेस्ट बसें सामान्य रूप से संचालित हैं। परिदृश्यों के परीक्षण के लिए ऊपर सिम्युलेटर का उपयोग करें।';
      }
      if (c.includes('mathura') || c.includes('vrindavan')) {
        return 'सभी ब्रज ट्रांजिट मार्ग, मथुरा जंक्शन ट्रेन कनेक्टिविटी, नगर सेवा इलेक्ट्रिक बसें और ई-रिक्शा सामान्य रूप से संचालित हैं। दर्शन या परिक्रमा भीड़ के परीक्षण के लिए सिम्युलेटर का उपयोग करें।';
      }
      if (c.includes('bengaluru') || c.includes('bangalore')) {
        return 'नम्मा मेट्रो (पर्पल व ग्रीन लाइन) और बीएमटीसी बसें निर्धारित समय पर संचालित हो रही हैं। परीक्षण के लिए ऊपर सिम्युलेटर का उपयोग करें।';
      }
      return t('allCorridorsDesc');
    }

    if (c.includes('mumbai')) {
      return 'All Mumbai Suburban corridors (Western, Central & Harbour Lines), Metro Line 3 Aqua Line, and BEST electric buses are running normally. Use the Incident Simulator above to test simulated rush hour or mega block scenarios.';
    }
    if (c.includes('mathura') || c.includes('vrindavan')) {
      return 'All Braj transit corridors, Mathura Junction train connections, Nagar Seva electric buses, and battery rickshaw feeders are operating smoothly. Use the Incident Simulator above to test simulated temple darshan or parikrama rush scenarios.';
    }
    if (c.includes('bengaluru') || c.includes('bangalore')) {
      return 'Namma Metro (Purple & Green lines) and BMTC bus routes are operating as scheduled across Bengaluru. Use the Incident Simulator above to test simulated disruption scenarios.';
    }
    return t('allCorridorsDesc');
  };

  const dayName = realtimeContext?.day_name
    ? (language === 'hi' ? HINDI_DAYS[realtimeContext.day_name] || realtimeContext.day_name : realtimeContext.day_name)
    : '';

  const dayType = realtimeContext?.day_type
    ? (language === 'hi' ? HINDI_DAYS[realtimeContext.day_type] || realtimeContext.day_type : realtimeContext.day_type)
    : '';

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Radio size={20} className="text-[#BD4F44] animate-pulse" />
            <h2 className="font-heading font-bold text-2xl text-[#1F231F]">
              {t('liveTransitTitle')}
            </h2>
          </div>
          <p className="text-xs text-[#52544D] font-medium mt-1">
            {t('liveTransitSubtitle')} {city}.
          </p>
        </div>

        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-[#EEECE3] text-[#253D30] border border-[#D8D4C7]">
          <span className="w-2 h-2 rounded-full bg-[#5B8A6E]" />
          <span>{t('syncActive')}</span>
        </span>
      </div>

      {/* Real-Time Operational Context & Temple/Rush Intelligence Banner */}
      {realtimeContext && (
        <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_2px_12px_rgba(41,45,41,0.03)]">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#EEECE3]">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#253D30]/10 text-[#253D30] font-bold">
                <Clock size={13} />
                <span>{realtimeContext.current_time_str}</span>
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#EEECE3] text-[#52544D] font-medium border border-[#D8D4C7]">
                <Calendar size={13} />
                <span>{dayName} • {dayType}</span>
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs font-medium text-[#52544D]">
                <span>{t('crowdInflow')}</span>
                <CrowdLevelIndicator level={realtimeContext.crowd_level} compact />
              </div>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-mono uppercase bg-[#5B8A6E]/15 text-[#253D30] font-bold">
                {t('liveTimetableBadge')}
              </span>
            </div>
          </div>

          <div className="mt-3.5 space-y-2">
            <h3 className="font-heading font-bold text-base text-[#1F231F] flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#E5A919]" />
              {realtimeContext.status_headline}
            </h3>
            <p className="text-xs text-[#52544D] font-medium leading-relaxed">
              {realtimeContext.status_description}
            </p>
          </div>

          {/* Recommended Mode & Special Advisory Pill */}
          <div className="mt-4 pt-3 border-t border-[#EEECE3] flex flex-wrap items-center justify-between gap-3 text-xs">
            {realtimeContext.recommended_mode && (
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#5B8A6E]/10 border border-[#5B8A6E]/20 text-[#253D30] font-bold">
                <Compass size={14} className="text-[#5B8A6E]" />
                <span>{t('recommendedModeLabel')} {realtimeContext.recommended_mode}</span>
              </div>
            )}

            {realtimeContext.special_advisory && (
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#E7B75B]/15 border border-[#E7B75B]/30 text-[#7A4B0F] font-semibold text-[11px]">
                <Info size={13} className="text-[#925C15] shrink-0" />
                <span>{realtimeContext.special_advisory}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Demo Controls Panel (City-specific scenarios) */}
      <DemoControls city={city} onSimulationUpdated={onRefreshIncidents} />

      {/* Active Service Alerts Feed */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-heading font-bold text-base text-[#1F231F] flex items-center gap-2">
            <span>{t('activeAdvisories')}</span>
            <span className="px-2 py-0.5 rounded-full text-xs bg-[#EEECE3] text-[#52544D] font-mono font-bold">
              {incidents.length}
            </span>
          </h3>
          <span className="text-xs text-[#52544D] font-medium">{t('updatedEvery30s')}</span>
        </div>

        {incidents.length === 0 ? (
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-10 text-center shadow-xs">
            <div className="w-12 h-12 rounded-full bg-[#5B8A6E]/15 text-[#5B8A6E] flex items-center justify-center mx-auto mb-3">
              <CheckCircle2 size={24} />
            </div>
            <h4 className="font-heading font-bold text-base text-[#1F231F]">
              {t('allCorridorsOnSchedule')}
            </h4>
            <p className="text-xs text-[#52544D] font-medium max-w-lg mx-auto mt-1">
              {getCityEmptyStateDesc(city)}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-5 shadow-[0_1px_4px_rgba(41,45,41,0.02)] hover:border-[#4E7C5F] transition-all"
              >
                <div className="flex flex-wrap items-start justify-between gap-3 mb-2.5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-[#BD4F44]/15 flex items-center justify-center text-[#BD4F44]">
                      <TransitModeIcon mode={inc.mode} size={16} />
                    </div>
                    <div>
                      <h4 className="font-heading font-bold text-base text-[#1F231F]">
                        {inc.headline}
                      </h4>
                      <p className="text-xs text-[#52544D] font-medium">
                        {t('lineLabel')} <span className="text-[#253D30] font-bold">{inc.line_name}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <DelayStatusBadge delayMinutes={inc.delay_minutes} isSimulated={inc.is_simulated} />
                  </div>
                </div>

                <p className="text-xs text-[#1F231F] font-medium leading-relaxed mb-3 bg-[#EEECE3]/60 p-3 rounded-xl border border-[#D8D4C7]">
                  {inc.description}
                </p>

                {/* Affected Stations */}
                {inc.affected_stations && inc.affected_stations.length > 0 && (
                  <div className="mb-3 flex flex-wrap items-center gap-1.5 text-xs">
                    <span className="text-[11px] font-bold text-[#52544D] mr-1">
                      {t('affectedStops')}
                    </span>
                    {inc.affected_stations.map((st, sIdx) => (
                      <span
                        key={sIdx}
                        className="px-2 py-0.5 rounded-md bg-[#EEECE3] text-[#1F231F] text-[11px] font-bold border border-[#D8D4C7]"
                      >
                        {st}
                      </span>
                    ))}
                  </div>
                )}

                {/* Footer: Timestamp, Crowd, and Alternative Action */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#D8D4C7] text-xs">
                  <div className="flex items-center gap-4 text-[#52544D]">
                    <span className="flex items-center gap-1 font-mono font-medium">
                      <Clock size={12} />
                      <span>{t('lastReported')} {inc.last_updated}</span>
                    </span>
                    <CrowdLevelIndicator level={inc.crowd_level} compact />
                  </div>

                  <button
                    type="button"
                    onClick={() => onPlanAlternative(inc.line_name)}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-[#FFFEFA] text-xs font-bold transition-all cursor-pointer shadow-xs hover:shadow-sm"
                  >
                    <span>{t('planAlternative')}</span>
                    <ArrowRight size={13} className="stroke-[2.2]" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
