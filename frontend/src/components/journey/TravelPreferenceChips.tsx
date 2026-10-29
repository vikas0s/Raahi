import React from 'react';
import { Zap, IndianRupee, Users, ArrowLeftRight, Footprints, Accessibility, Bus, CarTaxiFront, Sparkles } from 'lucide-react';
import type { TravelPreferences } from '../../types/transit';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  preferences: TravelPreferences;
  onChange: (prefs: TravelPreferences) => void;
  className?: string;
}

export const TravelPreferenceChips: React.FC<Props> = ({ preferences, onChange, className = '' }) => {
  const { t } = useTranslation();

  const toggle = (key: keyof TravelPreferences) => {
    const updated = { ...preferences, [key]: !preferences[key] };
    if (key === 'cheapest' && updated.cheapest) {
      updated.fastest = false;
      updated.less_crowded = false;
    } else if (key === 'fastest' && updated.fastest) {
      updated.cheapest = false;
      updated.less_crowded = false;
    } else if (key === 'less_crowded' && updated.less_crowded) {
      updated.fastest = false;
      updated.cheapest = false;
    }
    onChange(updated);
  };

  const chips: { key: keyof TravelPreferences; label: string; icon: React.ReactNode; isPink?: boolean }[] = [
    { key: 'fastest', label: t('prefFastest'), icon: <Zap size={13} /> },
    { key: 'cheapest', label: t('prefCheapest'), icon: <IndianRupee size={13} /> },
    { key: 'prefer_ebus', label: t('prefEBus'), icon: <Bus size={13} /> },
    { key: 'allow_auto', label: t('prefAutoTaxi'), icon: <CarTaxiFront size={13} /> },
    { key: 'pink_pass', label: t('prefPinkPass'), icon: <Sparkles size={13} />, isPink: true },
    { key: 'less_crowded', label: t('prefLessCrowded'), icon: <Users size={13} /> },
    { key: 'fewer_transfers', label: t('prefFewerTransfers'), icon: <ArrowLeftRight size={13} /> },
    { key: 'less_walking', label: t('prefLessWalking'), icon: <Footprints size={13} /> },
    { key: 'accessible', label: t('prefAccessible'), icon: <Accessibility size={13} /> }
  ];

  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      {chips.map(({ key, label, icon, isPink }) => {
        const isSelected = !!preferences[key];
        const selectedClass = isPink
          ? 'bg-[#C2185B] text-white shadow-xs ring-1.5 ring-[#880E4F]'
          : 'bg-[#2E5A3D] text-[#FFFEFA] shadow-xs ring-1.5 ring-[#1F3D29]';

        return (
          <button
            key={key}
            type="button"
            onClick={() => toggle(key)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer ${
              isSelected
                ? selectedClass
                : isPink
                ? 'bg-[#FCE4EC] text-[#C2185B] hover:bg-[#F8BBD0] border border-[#F48FB1]'
                : 'bg-[#EEECE3]/90 text-[#1F231F] hover:bg-[#E3DFD4] hover:text-[#253D30] border border-[#D8D4C7]'
            }`}
          >
            <span className={isSelected ? 'text-[#FFFEFA]' : isPink ? 'text-[#C2185B]' : 'text-[#52544D]'}>{icon}</span>
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
};
