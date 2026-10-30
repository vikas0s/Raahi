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
  const { t, language } = useTranslation();
  const [activeScenario, setActiveScenario] = useState<string>('normal');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('');

  const getScenariosForCity = (cityName: string): ScenarioConfig[] => {
    const c = (cityName || '').toLowerCase();
    const isHi = language === 'hi';

    if (c.includes('mumbai')) {
      return [
        {
          id: 'mumbai_interchange_rush',
          title: isHi ? 'दादर इंटरचेंज भीड़' : 'Dadar Interchange Rush',
          subtitle: isHi ? '+12 मिनट पश्चिमी/मध्य प्लेटफॉर्म भीड़' : '+12m Western/Central platform crowd',
          icon: Train,
          colorBg: 'bg-[#BD4F44]/15',
          colorBorder: 'border-[#BD4F44]',
          colorText: 'text-[#942A21]',
          colorIconBg: 'bg-[#BD4F44]/25'
        },
        {
          id: 'mumbai_mega_block',
          title: isHi ? 'रविवार मेगा ब्लॉक' : 'Sunday Mega Block',
          subtitle: isHi ? '+20 मिनट फास्ट से स्लो लाइन डायवर्सन' : '+20m fast-to-slow line diversion',
          icon: Sliders,
          colorBg: 'bg-[#E5A919]/15',
          colorBorder: 'border-[#E5A919]',
          colorText: 'text-[#B57C0A]',
          colorIconBg: 'bg-[#E5A919]/25'
        },
        {
          id: 'mumbai_traffic_jam',
          title: isHi ? 'WEH और BKC भारी ट्रैफिक' : 'WEH & BKC Road Traffic',
          subtitle: isHi ? '+22 मिनट कलानगर व सी लिंक जाम' : '+22m Kalanagar & Sea Link jam',
          icon: Car,
          colorBg: 'bg-[#C8795A]/15',
          colorBorder: 'border-[#C8795A]',
          colorText: 'text-[#9E4523]',
          colorIconBg: 'bg-[#C8795A]/25'
        },
        {
          id: 'mumbai_monsoon_waterlogging',
          title: isHi ? 'कुर्ला / सायन जलभराव' : 'Kurla / Sion High Tide',
          subtitle: isHi ? '+16 मिनट ट्रैक पर जलभराव नियमन' : '+16m track waterlogging regulation',
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
          title: isHi ? 'बांके बिहारी दर्शन भीड़' : 'Bankey Bihari Darshan Surge',
          subtitle: isHi ? '+25 मिनट संध्या आरती व परिक्रमा भीड़' : '+25m evening aarti crowd & parikrama',
          icon: Users,
          colorBg: 'bg-[#BD4F44]/15',
          colorBorder: 'border-[#BD4F44]',
          colorText: 'text-[#942A21]',
          colorIconBg: 'bg-[#BD4F44]/25'
        },
        {
          id: 'mathura_parikrama_rush',
          title: isHi ? 'गोवर्धन परिक्रमा भीड़' : 'Govardhan Parikrama Surge',
          subtitle: isHi ? '+30 मिनट एकादशी/पूर्णिमा 50हजार+ भीड़' : '+30m Ekadashi/Purnima 50k+ rush',
          icon: Sparkles,
          colorBg: 'bg-[#E5A919]/15',
          colorBorder: 'border-[#E5A919]',
          colorText: 'text-[#B57C0A]',
          colorIconBg: 'bg-[#E5A919]/25'
        },
        {
          id: 'mathura_kapat_reopen',
          title: isHi ? 'मंदिर कपाट पुनः दर्शन' : 'Temple Kapat Reopening',
          subtitle: isHi ? '+15 मिनट 4:30 बजे दर्शनार्थी आगमन' : '+15m 4:30 PM Darshan rush after rest',
          icon: AlertTriangle,
          colorBg: 'bg-[#C8795A]/15',
          colorBorder: 'border-[#C8795A]',
          colorText: 'text-[#9E4523]',
          colorIconBg: 'bg-[#C8795A]/25'
        },
        {
          id: 'mathura_traffic_diversion',
          title: isHi ? 'छटीकरा बाहरी डायवर्सन' : 'Chatikara Outer Diversion',
          subtitle: isHi ? '+18 मिनट हाईवे शटल कतार' : '+18m highway cut shuttle queue',
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
          title: isHi ? 'सिल्क बोर्ड जंक्शन जाम' : 'Silk Board Junction Jam',
          subtitle: isHi ? '+25 मिनट आउटर रिंग रोड रुकावट' : '+25m Outer Ring Road crawl',
          icon: Car,
          colorBg: 'bg-[#BD4F44]/15',
          colorBorder: 'border-[#BD4F44]',
          colorText: 'text-[#942A21]',
          colorIconBg: 'bg-[#BD4F44]/25'
        },
        {
          id: 'blr_metro_peak',
          title: isHi ? 'नम्मा मेट्रो पर्पल लाइन' : 'Namma Metro Purple Line',
          subtitle: isHi ? '+8 मिनट मैजेस्टिक इंटरचेंज भीड़' : '+8m Majestic interchange rush',
          icon: Train,
          colorBg: 'bg-[#E5A919]/15',
          colorBorder: 'border-[#E5A919]',
          colorText: 'text-[#B57C0A]',
          colorIconBg: 'bg-[#E5A919]/25'
        },
        {
          id: 'blr_airport_surge',
          title: isHi ? 'एयरपोर्ट रोड हेब्बल जाम' : 'Airport Road Hebbal Jam',
          subtitle: isHi ? '+20 मिनट केआईए एयरपोर्ट हाईवे देरी' : '+20m KIA airport highway delay',
          icon: Bus,
          colorBg: 'bg-[#C8795A]/15',
          colorBorder: 'border-[#C8795A]',
          colorText: 'text-[#9E4523]',
          colorIconBg: 'bg-[#C8795A]/25'
        },
        {
          id: 'monsoon_rain',
          title: isHi ? 'मानसून बारिश / जलभराव' : 'Monsoon Rain Downpour',
          subtitle: isHi ? '+15 मिनट जलभराव प्रभावित मार्ग' : '+15m waterlogged corridors',
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
        title: isHi ? 'येलो लाइन देरी' : 'Yellow Line Delay',
        subtitle: isHi ? '+14 मिनट सिग्नल सुधार' : '+14m signal calibration',
        icon: Train,
        colorBg: 'bg-[#E5A919]/15',
        colorBorder: 'border-[#E5A919]',
        colorText: 'text-[#B57C0A]',
        colorIconBg: 'bg-[#E5A919]/25'
      },
      {
        id: 'bus_breakdown',
        title: isHi ? 'डीटीसी बस डायवर्सन' : 'DTC Bus Diversion',
        subtitle: isHi ? '+20 मिनट रिंग रोड जाम' : '+20m Ring Road block',
        icon: Bus,
        colorBg: 'bg-[#C8795A]/15',
        colorBorder: 'border-[#C8795A]',
        colorText: 'text-[#9E4523]',
        colorIconBg: 'bg-[#C8795A]/25'
      },
      {
        id: 'peak_hour_surge',
        title: isHi ? 'कॉनकोर्स पीक भीड़' : 'Concourse Peak Surge',
        subtitle: isHi ? 'राजीव चौक और कश्मीरी गेट' : 'Rajiv Chowk & Kashmere Gate',
        icon: Users,
        colorBg: 'bg-[#BD4F44]/15',
        colorBorder: 'border-[#BD4F44]',
        colorText: 'text-[#942A21]',
        colorIconBg: 'bg-[#BD4F44]/25'
      },
      {
        id: 'monsoon_rain',
        title: isHi ? 'मानसून बारिश' : 'Monsoon Rain',
        subtitle: isHi ? '+15 मिनट मिंटो ब्रिज सड़क देरी' : '+15m Minto Bridge road delay',
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
    setStatusMessage(language === 'hi' ? `परिदृश्य लागू किया जा रहा है: ${label}...` : `Applying scenario: ${label}...`);
    try {
      const res = await simulateDelay(scenarioId, city);
      setActiveScenario(scenarioId);
      setStatusMessage(res.message || (language === 'hi' ? 'परिदृश्य अद्यतित' : 'Scenario updated'));
      onSimulationUpdated();
    } catch {
      setStatusMessage(language === 'hi' ? 'सिम्युलेशन अद्यतन में त्रुटि' : 'Error updating simulation');
    } finally {
      setIsLoading(false);
    }
  };

  const reset = async () => {
    setIsLoading(true);
    setStatusMessage(language === 'hi' ? 'सामान्य समय सारिणी पर रीसेट हो रहा है...' : 'Resetting to normal schedule...');
    try {
      const res = await simulateDelay('reset', city);
      setActiveScenario('normal');
      setStatusMessage(res.message || (language === 'hi' ? 'परिवहन नेटवर्क मानक समय सारिणी पर रीसेट' : 'Transit network reset to standard schedule'));
      onSimulationUpdated();
    } catch {
      setStatusMessage(language === 'hi' ? 'रीसेट करने में त्रुटि' : 'Error resetting simulation');
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
