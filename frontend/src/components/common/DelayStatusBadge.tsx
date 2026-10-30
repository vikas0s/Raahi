import React from 'react';
import { Clock, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  delayMinutes: number;
  isSimulated?: boolean;
  className?: string;
  showIcon?: boolean;
}

export const DelayStatusBadge: React.FC<Props> = ({
  delayMinutes,
  isSimulated = false,
  className = '',
  showIcon = true
}) => {
  const { t, language } = useTranslation();

  if (delayMinutes === 0) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-[#4E7C5F]/15 text-[#21432E] border border-[#4E7C5F]/30 shadow-2xs ${className}`}
      >
        {showIcon && <CheckCircle2 size={13} className="text-[#3A6B4B] stroke-[2.5]" />}
        <span>{t('onTime')}</span>
        {isSimulated && (
          <span className="text-[10px] text-[#52544D] uppercase tracking-wider font-mono ml-1 font-bold">
            {language === 'hi' ? '[डेमो]' : '[DEMO]'}
          </span>
        )}
      </span>
    );
  }

  const isSevere = delayMinutes >= 15;
  const colorClass = isSevere
    ? 'bg-[#B54237]/15 text-[#8A251C] border-[#B54237]/35 shadow-2xs'
    : 'bg-[#C78229]/18 text-[#7A4B0C] border-[#C78229]/40 shadow-2xs';

  const delayText = language === 'hi'
    ? `+${delayMinutes} मिनट देरी`
    : `+${delayMinutes}m delay`;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${colorClass} ${className}`}
    >
      {showIcon && (isSevere ? <AlertTriangle size={13} className="stroke-[2.5]" /> : <Clock size={13} className="stroke-[2.5]" />)}
      <span>{delayText}</span>
      {isSimulated && (
        <span className="text-[10px] uppercase tracking-wider font-mono opacity-90 ml-0.5 font-bold">
          {language === 'hi' ? '[सिम्युलेटेड]' : '[SIMULATED]'}
        </span>
      )}
    </span>
  );
};
