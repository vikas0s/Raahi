import React, { useState } from 'react';
import { Sliders, RefreshCw, CloudRain, Users, Train, Bus } from 'lucide-react';
import { simulateDelay } from '../../services/api';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  onSimulationUpdated: () => void;
  className?: string;
}

export const DemoControls: React.FC<Props> = ({ onSimulationUpdated, className = '' }) => {
  const { t } = useTranslation();
  const [activeScenario, setActiveScenario] = useState<string>('normal');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('');

  const trigger = async (
    scenario: 'metro_signal_delay' | 'bus_breakdown' | 'peak_hour_surge' | 'monsoon_rain' | 'reset',
    label: string
  ) => {
    setIsLoading(true);
    setStatusMessage(`Applying scenario: ${label}...`);
    try {
      const res = await simulateDelay(scenario);
      setActiveScenario(scenario);
      setStatusMessage(res.message || 'Scenario updated');
      onSimulationUpdated();
    } catch (err) {
      setStatusMessage('Error updating simulation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`bg-[#FFFEFA] rounded-2xl border border-[#E3E0D6] p-5 shadow-[0_2px_12px_rgba(41,45,41,0.03)] ${className}`}>
      {/* Title & Honest Simulation Badge */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#E7B75B]/20 flex items-center justify-center text-[#925C15]">
            <Sliders size={16} />
          </div>
          <div>
            <h4 className="font-heading font-bold text-sm text-[#1F231F]">
              {t('incidentSimulator')}
            </h4>
            <p className="text-[11px] text-[#52544D] font-medium">
              {t('incidentSimulatorDesc')}
            </p>
          </div>
        </div>

        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-mono uppercase bg-[#D9943B]/20 text-[#7A4B0F] border border-[#D9943B]/40 font-extrabold tracking-wider shadow-2xs">
          {t('simulatedBadge')}
        </span>
      </div>

      {/* Scenario Metric Cards (CropXpert-style sensor tiles) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 my-3">
        {/* Scenario 1: Metro Delay */}
        <button
          type="button"
          disabled={isLoading}
          onClick={() => trigger('metro_signal_delay', 'Metro Signal Delay')}
          className={`flex items-start gap-3 p-3.5 rounded-xl border text-left text-xs transition-all cursor-pointer ${
            activeScenario === 'metro_signal_delay'
              ? 'bg-[#E5A919]/15 border-[#E5A919] ring-2 ring-[#E5A919] shadow-xs'
              : 'bg-[#EEECE3]/50 hover:bg-[#EEECE3] border-[#D8D4C7]'
          }`}
        >
          <div className="w-7 h-7 rounded-lg bg-[#E5A919]/25 flex items-center justify-center text-[#B57C0A] shrink-0 mt-0.5">
            <Train size={15} className="stroke-[2.2]" />
          </div>
          <div>
            <p className="font-bold text-[#1F231F]">{t('scenarioYellowLine')}</p>
            <p className="text-[11px] text-[#52544D] font-medium mt-0.5">{t('scenarioYellowLineSub')}</p>
          </div>
        </button>

        {/* Scenario 2: Bus Breakdown */}
        <button
          type="button"
          disabled={isLoading}
          onClick={() => trigger('bus_breakdown', 'Bus Breakdown')}
          className={`flex items-start gap-3 p-3.5 rounded-xl border text-left text-xs transition-all cursor-pointer ${
            activeScenario === 'bus_breakdown'
              ? 'bg-[#C8795A]/15 border-[#C8795A] ring-2 ring-[#C8795A] shadow-xs'
              : 'bg-[#EEECE3]/50 hover:bg-[#EEECE3] border-[#D8D4C7]'
          }`}
        >
          <div className="w-7 h-7 rounded-lg bg-[#C8795A]/25 flex items-center justify-center text-[#9E4523] shrink-0 mt-0.5">
            <Bus size={15} className="stroke-[2.2]" />
          </div>
          <div>
            <p className="font-bold text-[#1F231F]">{t('scenarioBus')}</p>
            <p className="text-[11px] text-[#52544D] font-medium mt-0.5">{t('scenarioBusSub')}</p>
          </div>
        </button>

        {/* Scenario 3: Peak Hour Surge */}
        <button
          type="button"
          disabled={isLoading}
          onClick={() => trigger('peak_hour_surge', 'Peak Crowd Surge')}
          className={`flex items-start gap-3 p-3.5 rounded-xl border text-left text-xs transition-all cursor-pointer ${
            activeScenario === 'peak_hour_surge'
              ? 'bg-[#BD4F44]/15 border-[#BD4F44] ring-2 ring-[#BD4F44] shadow-xs'
              : 'bg-[#EEECE3]/50 hover:bg-[#EEECE3] border-[#D8D4C7]'
          }`}
        >
          <div className="w-7 h-7 rounded-lg bg-[#BD4F44]/25 flex items-center justify-center text-[#942A21] shrink-0 mt-0.5">
            <Users size={15} className="stroke-[2.2]" />
          </div>
          <div>
            <p className="font-bold text-[#1F231F]">{t('scenarioPeak')}</p>
            <p className="text-[11px] text-[#52544D] font-medium mt-0.5">{t('scenarioPeakSub')}</p>
          </div>
        </button>

        {/* Scenario 4: Monsoon Rain */}
        <button
          type="button"
          disabled={isLoading}
          onClick={() => trigger('monsoon_rain', 'Monsoon Downpour')}
          className={`flex items-start gap-3 p-3.5 rounded-xl border text-left text-xs transition-all cursor-pointer ${
            activeScenario === 'monsoon_rain'
              ? 'bg-[#4E7C5F]/20 border-[#4E7C5F] ring-2 ring-[#4E7C5F] shadow-xs'
              : 'bg-[#EEECE3]/50 hover:bg-[#EEECE3] border-[#D8D4C7]'
          }`}
        >
          <div className="w-7 h-7 rounded-lg bg-[#4E7C5F]/25 flex items-center justify-center text-[#253D30] shrink-0 mt-0.5">
            <CloudRain size={15} className="stroke-[2.2]" />
          </div>
          <div>
            <p className="font-bold text-[#1F231F]">{t('scenarioMonsoon')}</p>
            <p className="text-[11px] text-[#52544D] font-medium mt-0.5">{t('scenarioMonsoonSub')}</p>
          </div>
        </button>
      </div>

      {/* Reset & Status Bar */}
      <div className="flex items-center justify-between pt-2.5 border-t border-[#D8D4C7] text-xs">
        <span className="text-[#52544D] font-medium italic line-clamp-1">
          {statusMessage || t('scenarioPrompt')}
        </span>

        <button
          type="button"
          onClick={() => trigger('reset', 'Reset to Normal')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-[#253D30] hover:bg-[#EEECE3] transition-colors cursor-pointer"
        >
          <RefreshCw size={12} className={isLoading ? 'animate-spin' : 'stroke-[2.2]'} />
          <span>{t('resetScenario')}</span>
        </button>
      </div>
    </div>
  );
};
