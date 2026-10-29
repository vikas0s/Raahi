import React, { useState } from 'react';
import { Bookmark, Plus } from 'lucide-react';
import { SavedRouteCard } from '../components/saved/SavedRouteCard';
import type { SavedRoute } from '../types/transit';
import { createSavedRoute } from '../services/api';
import { useTranslation } from '../i18n/LanguageContext';

interface Props {
  savedRoutes: SavedRoute[];
  city: string;
  onReplan: (route: SavedRoute) => void;
  onDelete: (id: string) => void;
  onRefresh: () => void;
}

export const SavedRoutesView: React.FC<Props> = ({
  savedRoutes,
  city,
  onReplan,
  onDelete,
  onRefresh
}) => {
  const { t } = useTranslation();
  const [showAddModal, setShowAddModal] = useState(false);
  const [name, setName] = useState('');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [preferredMode, setPreferredMode] = useState('fastest');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !origin || !destination) return;
    setIsSubmitting(true);
    try {
      await createSavedRoute(name, origin, destination, city, preferredMode);
      setShowAddModal(false);
      setName('');
      setOrigin('');
      setDestination('');
      onRefresh();
    } catch (err) {
      console.error('Failed to create saved commute:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Bookmark size={20} className="text-[#4E7C5F] stroke-[2.2]" />
            <h2 className="font-heading font-bold text-2xl text-[#1F231F]">
              {t('savedCommutesTitle')}
            </h2>
          </div>
          <p className="text-xs text-[#52544D] font-medium mt-1">
            {t('savedCommutesSubtitle')}
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-[#FFFEFA] text-xs font-bold shadow-xs hover:shadow-sm transition-all cursor-pointer"
        >
          <Plus size={15} className="stroke-[2.2]" />
          <span>{t('addCustomCommute')}</span>
        </button>
      </div>

      {/* Routes Grid */}
      {savedRoutes.length === 0 ? (
        <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-12 text-center shadow-[0_1px_4px_rgba(41,45,41,0.02)]">
          <div className="w-12 h-12 rounded-full bg-[#64836D]/15 text-[#253D30] flex items-center justify-center mx-auto mb-3">
            <Bookmark size={22} className="stroke-[2.2]" />
          </div>
          <h4 className="font-heading font-bold text-base text-[#1F231F]">
            {t('noSavedJourneys')}
          </h4>
          <p className="text-xs text-[#52544D] font-medium max-w-sm mx-auto mt-1 mb-4">
            {t('noSavedJourneysDesc')}
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-xl bg-[#253D30] text-white text-xs font-bold hover:bg-[#1A2E24] transition-all cursor-pointer shadow-xs"
          >
            {t('createFirstCommute')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {savedRoutes.map((route) => (
            <SavedRouteCard
              key={route.id}
              route={route}
              onReplan={onReplan}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}

      {/* Add Custom Commute Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#FFFEFA] rounded-2xl border border-[#D8D4C7] p-6 max-w-md w-full shadow-2xl animate-in fade-in duration-200">
            <h3 className="font-heading font-bold text-lg text-[#1F231F] mb-1">
              {t('saveRegularCommute')}
            </h3>
            <p className="text-xs text-[#52544D] font-medium mb-4">
              {t('saveRegularCommuteDesc')}
            </p>

            <form onSubmit={handleCreate} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-[#1F231F] mb-1">
                  {t('commuteLabel')}
                </label>
                <input
                  type="text"
                  required
                  placeholder={t('commuteLabelPlaceholder')}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl bg-[#EEECE3]/60 focus:bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#253D30] focus:ring-1 focus:ring-[#253D30]/20 outline-none transition-all text-[#1F231F]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#1F231F] mb-1">
                  {t('startingOrigin')}
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Rajiv Chowk (Connaught Place)"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl bg-[#EEECE3]/60 focus:bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#253D30] focus:ring-1 focus:ring-[#253D30]/20 outline-none transition-all text-[#1F231F]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#1F231F] mb-1">
                  {t('targetDestination')}
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Cyber City (Gurugram)"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs font-semibold rounded-xl bg-[#EEECE3]/60 focus:bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#253D30] focus:ring-1 focus:ring-[#253D30]/20 outline-none transition-all text-[#1F231F]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#1F231F] mb-1">
                  {t('preferredOptimization')}
                </label>
                <select
                  value={preferredMode}
                  onChange={(e) => setPreferredMode(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs font-bold rounded-xl bg-[#EEECE3]/60 focus:bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#253D30] outline-none cursor-pointer text-[#1F231F]"
                >
                  <option value="fastest">{t('prefFastest')}</option>
                  <option value="cheapest">{t('prefCheapest')}</option>
                  <option value="least_crowded">{t('prefLessCrowded')}</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#D8D4C7]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-[#52544D] hover:bg-[#EEECE3] transition-colors cursor-pointer"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !name || !origin || !destination}
                  className="px-4 py-2 rounded-xl bg-[#253D30] text-white text-xs font-bold shadow-xs hover:bg-[#1A2E24] transition-all cursor-pointer"
                >
                  {isSubmitting ? 'Saving...' : t('saveCommuteButton')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
