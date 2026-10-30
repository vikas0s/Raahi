import React from 'react';
import { Users } from 'lucide-react';
import type { CrowdLevel } from '../../types/transit';
import { useTranslation } from '../../i18n/LanguageContext';
import { localizeCrowdLevel } from '../../i18n/translations';

interface Props {
  level: CrowdLevel;
  className?: string;
  compact?: boolean;
}

export const CrowdLevelIndicator: React.FC<Props> = ({ level, className = '', compact = false }) => {
  const { language } = useTranslation();

  const getDotColors = () => {
    switch (level) {
      case 'Low':
        return ['bg-[#4E7C5F]', 'bg-[#D8D4C7]', 'bg-[#D8D4C7]'];
      case 'Moderate':
        return ['bg-[#C78229]', 'bg-[#C78229]', 'bg-[#D8D4C7]'];
      case 'High':
      case 'Very High':
        return ['bg-[#B54237]', 'bg-[#B54237]', 'bg-[#B54237]'];
      default:
        return ['bg-[#4E7C5F]', 'bg-[#D8D4C7]', 'bg-[#D8D4C7]'];
    }
  };

  const dots = getDotColors();
  const label = localizeCrowdLevel(level, language);

  return (
    <div className={`inline-flex items-center gap-1.5 text-xs text-[#52544D] ${className}`}>
      {!compact && <Users size={13} className="text-[#52544D]" />}
      <div className="flex items-center gap-1" title={language === 'hi' ? `भीड़ स्तर: ${label}` : `Crowd level: ${level}`}>
        <span className={`w-2 h-2 rounded-full ${dots[0]}`} />
        <span className={`w-2 h-2 rounded-full ${dots[1]}`} />
        <span className={`w-2 h-2 rounded-full ${dots[2]}`} />
      </div>
      <span className="font-bold text-[#1F231F]">{label}</span>
    </div>
  );
};
