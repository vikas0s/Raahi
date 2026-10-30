import React, { useState } from 'react';
import { Sliders, RefreshCw, CloudRain, Users, Train, Bus, Car, Sparkles, AlertTriangle } from 'lucide-react';
import { simulateDelay } from '../../services/api';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  city?: string;
  onSimulationUpdated: () => void;
  className?: string;
}

interface ScenarioConfig {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  colorBg: string;
  colorBorder: string;
  colorText: string;
  colorIconBg: string;
}

export const DemoControls: React.FC<Props> = ({ city = 'Delhi NCR', onSimulationUpdated, className = '' }) => {
  const { t } = useTranslation();
  const [activeScenario, setActiveScenario] = useState<string>('normal');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('');

  const getScenariosForCity = (cityName: string): ScenarioConfig[] => {
    const c = (cityName || '').toLowerCase();
    if (c.includes('mumbai')) {
      return [
        {
          id: 'mumbai_interchange_rush',
          title: 'Dadar Interchange Rush',
          subtitle: '+12m Western/Central platform crowd',
          icon: Train,
          colorBg: 'bg-[#BD4F44]/15',
          colorBorder: 'border-[#BD4F44]',
          colorText: 'text-[#942A21]',
          colorIconBg: 'bg-[#BD4F44]/25'
        },
        {
          id: 'mumbai_mega_block',
          title: 'Sunday Mega Block',
          subtitle: '+20m fast-to-slow line diversion',
          icon: Sliders,
          colorBg: 'bg-[#E5A919]/15',
          colorBorder: 'border-[#E5A919]',
          colorText: 'text-[#B57C0A]',
          colorIconBg: 'bg-[#E5A919]/25'
        },
        {
          id: 'mumbai_traffic_jam',
          title: 'WEH & BKC Road Traffic',
          subtitle: '+22m Kalanagar & Sea Link jam',
          icon: Car,
          colorBg: 'bg-[#C8795A]/15',
          colorBorder: 'border-[#C8795A]',
          colorText: 'text-[#9E4523]',
          colorIconBg: 'bg-[#C8795A]/25'
        },
        {
          id: 'mumbai_monsoon_waterlogging',
          title: 'Kurla / Sion High Tide',
          subtitle: '+16m track waterlogging regulation',
          icon: CloudRain,
          colorBg: 'bg-[#4E7C5F]/20',
          colorBorder: 'border-[#4E7C5F]',
          colorText: 'text-[#253D30]',
          colorIconBg: 'bg-[#4E7C5F]/25'
        }
      ];
    }
    if (c.includes('mathura') || c.includes('vrindavan')) {
      return [
        {
          id: 'mathura_darshan_surge',
          title: 'Bankey Bihari Darshan Surge',
          subtitle: '+25m evening aarti crowd & parikrama',
          icon: Users,
          colorBg: 'bg-[#BD4F44]/15',
          colorBorder: 'border-[#BD4F44]',
          colorText: 'text-[#942A21]',
          colorIconBg: 'bg-[#BD4F44]/25'
        },
        {
          id: 'mathura_parikrama_rush',
          title: 'Govardhan Parikrama Surge',
          subtitle: '+30m Ekadashi/Purnima 50k+ rush',
          icon: Sparkles,
          colorBg: 'bg-[#E5A919]/15',
          colorBorder: 'border-[#E5A919]',
          colorText: 'text-[#B57C0A]',
          colorIconBg: 'bg-[#E5A919]/25'
        },
        {
          id: 'mathura_kapat_reopen',
          title: 'Temple Kapat Reopening',
          subtitle: '+15m 4:30 PM Darshan rush after rest',
          icon: AlertTriangle,
          colorBg: 'bg-[#C8795A]/15',
          colorBorder: 'border-[#C8795A]',
          colorText: 'text-[#9E4523]',
          colorIconBg: 'bg-[#C8795A]/25'
        },
        {
          id: 'mathura_traffic_diversion',
          title: 'Chatikara Outer Diversion',
          subtitle: '+18m highway cut shuttle queue',
          icon: Bus,
          colorBg: 'bg-[#4E7C5F]/20',
          colorBorder: 'border-[#4E7C5F]',
          colorText: 'text-[#253D30]',
          colorIconBg: 'bg-[#4E7C5F]/25'
        }
      ];
    }
    if (c.includes('bengaluru') || c.includes('bangalore')) {
      return [
        {
          id: 'blr_silk_board_jam',
          title: 'Silk Board Junction Jam',
          subtitle: '+25m Outer Ring Road crawl',
          icon: Car,
          colorBg: 'bg-[#BD4F44]/15',
          colorBorder: 'border-[#BD4F44]',
          colorText: 'text-[#942A21]',
          colorIconBg: 'bg-[#BD4F44]/25'
        },
        {
          id: 'blr_metro_peak',
          title: 'Namma Metro Purple Line',
          subtitle: '+8m Majestic interchange rush',
          icon: Train,
          colorBg: 'bg-[#E5A919]/15',
          colorBorder: 'border-[#E5A919]',
          colorText: 'text-[#B57C0A]',
          colorIconBg: 'bg-[#E5A919]/25'
        },
        {
          id: 'blr_airport_surge',
          title: 'Airport Road Hebbal Jam',
          subtitle: '+20m KIA airport highway delay',
          icon: Bus,
          colorBg: 'bg-[#C8795A]/15',
          colorBorder: 'border-[#C8795A]',
          colorText: 'text-[#9E4523]',
          colorIconBg: 'bg-[#C8795A]/25'
        },
        {
          id: 'monsoon_rain',
          title: 'Monsoon Rain Downpour',
          subtitle: '+15m waterlogged corridors',
          icon: CloudRain,
          colorBg: 'bg-[#4E7C5F]/20',
          colorBorder: 'border-[#4E7C5F]',
          colorText: 'text-[#253D30]',
          colorIconBg: 'bg-[#4E7C5F]/25'
        }
      ];
    }
    // Default: Delhi NCR
    return [
      {
        id: 'metro_signal_delay',
        title: 'Yellow Line Delay',
        subtitle: '+14m signal calibration',
        icon: Train,
        colorBg: 'bg-[#E5A919]/15',
        colorBorder: 'border-[#E5A919]',
        colorText: 'text-[#B57C0A]',
        colorIconBg: 'bg-[#E5A919]/25'
      },
      {
        id: 'bus_breakdown',
        title: 'DTC Bus Diversion',
        subtitle: '+20m Ring Road block',
        icon: Bus,
        colorBg: 'bg-[#C8795A]/15',
        colorBorder: 'border-[#C8795A]',
        colorText: 'text-[#9E4523]',
        colorIconBg: 'bg-[#C8795A]/25'
      },
      {
        id: 'peak_hour_surge',
        title: 'Concourse Peak Surge',
        subtitle: 'Rajiv Chowk & Kashmere Gate',
        icon: Users,
        colorBg: 'bg-[#BD4F44]/15',
        colorBorder: 'border-[#BD4F44]',
        colorText: 'text-[#942A21]',
        colorIconBg: 'bg-[#BD4F44]/25'
      },
      {
        id: 'monsoon_rain',
        title: 'Monsoon Rain',
        subtitle: '+15m Minto Bridge road delay',
        icon: CloudRain,
        colorBg: 'bg-[#4E7C5F]/20',
        colorBorder: 'border-[#4E7C5F]',
        colorText: 'text-[#253D30]',
        colorIconBg: 'bg-[#4E7C5F]/25'
      }
    ];
  };

  const scenarios = getScenariosForCity(city);

  const trigger = async (scenarioId: string, label: string) => {
    setIsLoading(true);
    setStatusMessage(`Applying scenario: ${label}...`);
    try {
      const res = await simulateDelay(scenarioId, city);
      setActiveScenario(scenarioId);
      setStatusMessage(res.message || 'Scenario updated');
      onSimulationUpdated();
    } catch (err) {
      setStatusMessage('Error updating simulation');
    } finally {
      setIsLoading(false);
    }
  };

  const reset = async () => {
    setIsLoading(true);
    setStatusMessage('Resetting to normal schedule...');
    try {
      const res = await simulateDelay('reset', city);
      setActiveScenario('normal');
      setStatusMessage(res.message || 'Transit network reset to standard schedule');
      onSimulationUpdated();
    } catch (err) {
      setStatusMessage('Error resetting simulation');
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
              {t('incidentSimulator')} — {city}
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
        {scenarios.map((scen) => {
          const IconComponent = scen.icon;
          const isActive = activeScenario === scen.id;
          return (
            <button
              key={scen.id}
              type="button"
              disabled={isLoading}
              onClick={() => trigger(scen.id, scen.title)}
              className={`flex items-start gap-3 p-3.5 rounded-xl border text-left text-xs transition-all cursor-pointer ${
                isActive
                  ? `${scen.colorBg} ${scen.colorBorder} ring-2 ring-current shadow-xs`
                  : 'bg-[#EEECE3]/50 hover:bg-[#EEECE3] border-[#D8D4C7]'
              }`}
            >
              <div className={`w-7 h-7 rounded-lg ${scen.colorIconBg} flex items-center justify-center ${scen.colorText} shrink-0 mt-0.5`}>
                <IconComponent size={15} className="stroke-[2.2]" />
              </div>
              <div>
                <p className="font-bold text-[#1F231F] leading-tight">{scen.title}</p>
                <p className="text-[11px] text-[#52544D] font-medium mt-0.5">{scen.subtitle}</p>
              </div>
            </button>
          );
        })}
      </div>

      {/* Reset & Status Bar */}
      <div className="flex items-center justify-between pt-2.5 border-t border-[#D8D4C7] text-xs">
        <span className="text-[#52544D] font-medium italic line-clamp-1">
          {statusMessage || t('scenarioPrompt')}
        </span>

        <button
          type="button"
          onClick={reset}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-[#253D30] hover:bg-[#EEECE3] transition-colors cursor-pointer"
        >
          <RefreshCw size={12} className={isLoading ? 'animate-spin' : 'stroke-[2.2]'} />
          <span>{t('resetScenario')}</span>
        </button>
      </div>
    </div>
  );
};
