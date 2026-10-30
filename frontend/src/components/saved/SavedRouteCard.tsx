import React, { useState } from 'react';
import { MapPin, Navigation, Clock, IndianRupee, ArrowLeftRight, Trash2, Check, X, Play } from 'lucide-react';
import type { SavedRoute } from '../../types/transit';
import { DelayStatusBadge } from '../common/DelayStatusBadge';
import { useTranslation } from '../../i18n/LanguageContext';
import { localizeRouteTag } from '../../i18n/translations';

interface Props {
  route: SavedRoute;
  onReplan: (route: SavedRoute) => void;
  onDelete: (id: string) => void;
}

export const SavedRouteCard: React.FC<Props> = ({ route, onReplan, onDelete }) => {
  const { t, language } = useTranslation();
  const [isDeleting, setIsDeleting] = useState(false);

  const preferredLabel = localizeRouteTag(
    route.preferred_mode.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    language
  );

  return (
    <div className="bg-[#FFFEFA] rounded-2xl border border-[#E3E0D6] p-5 shadow-[0_1px_4px_rgba(41,45,41,0.02)] hover:shadow-[0_4px_18px_rgba(48,75,60,0.07)] transition-all flex flex-col justify-between">
      <div>
        {/* Header: Name & Delay status */}
        <div className="flex items-start justify-between gap-2 mb-2.5">
          <div>
            <h4 className="font-heading font-bold text-base text-[#1F231F]">
              {route.name}
            </h4>
            <span className="text-[11px] text-[#52544D] uppercase tracking-wider font-bold">
              {route.city} • {t('preferredLabel')} {preferredLabel}
            </span>
          </div>

          <DelayStatusBadge delayMinutes={route.current_delay_minutes} />
        </div>

        {/* Origin -> Destination Track */}
        <div className="bg-[#EEECE3]/60 rounded-xl p-3 border border-[#D8D4C7] space-y-1.5 my-3 text-xs">
          <div className="flex items-center gap-2">
            <MapPin size={14} className="text-[#4E7C5F] shrink-0 stroke-[2.2]" />
            <span className="font-bold text-[#1F231F] truncate">{route.origin}</span>
          </div>
          <div className="pl-1.5 border-l border-dashed border-[#C4C0B5] ml-1.5 h-2" />
          <div className="flex items-center gap-2">
            <Navigation size={14} className="text-[#C8795A] shrink-0 stroke-[2.2]" />
            <span className="font-bold text-[#1F231F] truncate">{route.destination}</span>
          </div>
        </div>

        {/* Metrics Row: Duration, Fare, Transfers */}
        <div className="flex items-center justify-between text-xs text-[#52544D] py-2 border-t border-[#D8D4C7] mb-3">
          <span className="flex items-center gap-1 font-bold text-[#1F231F]">
            <Clock size={13} className="text-[#52544D] stroke-[2.2]" />
            <span>~{route.typical_duration_minutes}m</span>
          </span>
          <span className="flex items-center gap-0.5 font-extrabold text-[#253D30] text-sm">
            <IndianRupee size={13} className="stroke-[2.5]" />
            <span>{route.typical_fare_inr.toFixed(0)}</span>
          </span>
          <span className="flex items-center gap-1 font-semibold text-[#1F231F]">
            <ArrowLeftRight size={13} />
            <span>{route.typical_transfers === 0 ? t('direct') : `${route.typical_transfers} ${t('transfer')}`}</span>
          </span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-[#D8D4C7]">
        {isDeleting ? (
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#BD4F44] font-bold">{t('confirmDelete')}</span>
            <button
              onClick={() => onDelete(route.id)}
              className="p-1.5 rounded-lg bg-[#BD4F44] text-white hover:bg-[#A8382E] transition-colors cursor-pointer"
            >
              <Check size={13} />
            </button>
            <button
              onClick={() => setIsDeleting(false)}
              className="p-1.5 rounded-lg bg-[#EEECE3] text-[#1F231F] hover:bg-[#E3E0D6] transition-colors cursor-pointer"
            >
              <X size={13} />
            </button>
          </div>
        ) : (
          <button
            onClick={() => setIsDeleting(true)}
            className="inline-flex items-center gap-1 text-xs text-[#52544D] hover:text-[#BD4F44] transition-colors cursor-pointer font-bold"
            title="Delete saved route"
          >
            <Trash2 size={13} />
            <span>{t('remove')}</span>
          </button>
        )}

        <button
          onClick={() => onReplan(route)}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] active:scale-[0.98] text-[#FFFEFA] text-xs font-bold shadow-xs hover:shadow-sm transition-all cursor-pointer"
        >
          <Play size={11} className="fill-current" />
          <span>{t('replanJourney')}</span>
        </button>
      </div>
    </div>
  );
};
