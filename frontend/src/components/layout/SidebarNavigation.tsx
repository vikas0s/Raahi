import React from 'react';
import { Compass, Route, Radio, Bookmark, Bot, Settings, ShieldCheck, LogIn, LogOut, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from '../../i18n/LanguageContext';

export type NavTab = 'discover' | 'plan' | 'live' | 'saved' | 'assistant' | 'settings' | 'auth';

interface Props {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  disruptionsCount?: number;
  savedRoutesCount?: number;
}

export const SidebarNavigation: React.FC<Props> = ({
  activeTab,
  onTabChange,
  disruptionsCount = 0,
  savedRoutesCount = 0
}) => {
  const { t } = useTranslation();
  const { user, isAuthenticated, signOut } = useAuth();

  const navItems = [
    { id: 'discover' as NavTab, label: t('navDiscover'), icon: <Compass size={17} /> },
    { id: 'plan' as NavTab, label: t('navPlan'), icon: <Route size={17} /> },
    {
      id: 'live' as NavTab,
      label: t('navLive'),
      icon: <Radio size={17} />,
      badge: disruptionsCount > 0 ? disruptionsCount : undefined,
      badgeColor: 'bg-[#BD4F44]'
    },
    {
      id: 'saved' as NavTab,
      label: t('navSaved'),
      icon: <Bookmark size={17} />,
      badge: savedRoutesCount > 0 ? savedRoutesCount : undefined,
      badgeColor: 'bg-[#64836D]'
    },
    { id: 'assistant' as NavTab, label: t('navAssistant'), icon: <Bot size={17} /> },
    { id: 'settings' as NavTab, label: t('navSettings'), icon: <Settings size={17} /> }
  ];

  return (
    <>
      {/* Desktop Refined Sidebar */}
      <aside className="hidden lg:flex flex-col justify-between w-64 h-[calc(100vh-61px)] sticky top-[61px] bg-[#F7F5EF] border-r border-[#E3E0D6] p-4 shrink-0">
        <nav className="space-y-1.5">
          <p className="px-3.5 text-[10px] font-extrabold uppercase tracking-wider text-[#52544D] mb-2">
            {t('navTitle')}
          </p>
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer ${
                  isActive
                    ? 'bg-[#253D30] text-[#FFFEFA] shadow-[0_2px_8px_rgba(37,61,48,0.25)]'
                    : 'text-[#1F231F] hover:bg-[#EEECE3] hover:text-[#253D30]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={isActive ? 'text-[#FFFEFA]' : 'text-[#52544D]'}>{item.icon}</span>
                  <span className="tracking-tight">{item.label}</span>
                </div>

                {item.badge !== undefined && (
                  <span
                    className={`px-1.5 py-0.5 rounded-full text-[10px] text-white font-extrabold shadow-2xs ${
                      isActive ? 'bg-[#5B8A6E]' : item.badgeColor
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* User Account / Profile Section */}
        {isAuthenticated && user ? (
          <div className="p-3 rounded-2xl bg-[#FFFEFA] border border-[#E3E0D6] shadow-[0_1px_4px_rgba(41,45,41,0.02)] mb-3">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-xl bg-[#253D30] text-[#FFFEFA] text-xs font-extrabold flex items-center justify-center uppercase shrink-0">
                  {user.name ? user.name.slice(0, 2) : 'U'}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-bold text-[#1F231F] truncate">{user.name}</p>
                  <p className="text-[10px] text-[#52544D] truncate">{user.email}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => signOut()}
                title={t('signOut') || 'Sign Out'}
                className="p-1.5 rounded-lg text-[#52544D] hover:text-[#BD4F44] hover:bg-[#BD4F44]/10 transition-colors cursor-pointer"
              >
                <LogOut size={14} />
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => onTabChange('auth')}
            className="w-full flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl bg-[#EEECE3] hover:bg-[#E3E0D6] border border-[#D8D4C7] text-xs font-bold text-[#253D30] transition-colors cursor-pointer mb-3 shadow-2xs"
          >
            <LogIn size={15} />
            <span>{t('signIn') || 'Sign In / Join Raahi'}</span>
          </button>
        )}

        {/* Bottom Mission Card (CropXpert-style subtle info surface) */}
        <div className="p-3.5 rounded-2xl bg-[#FFFEFA] border border-[#E3E0D6] shadow-[0_1px_4px_rgba(41,45,41,0.02)] text-left">
          <div className="flex items-center gap-1.5 text-[11px] font-extrabold text-[#253D30]">
            <ShieldCheck size={15} className="text-[#4E7C5F] stroke-[2.2]" />
            <span>{t('missionTag')}</span>
          </div>
          <p className="text-[10px] text-[#52544D] font-medium mt-1 leading-relaxed">
            {t('missionDesc')}
          </p>
        </div>
      </aside>

      {/* Mobile Bottom Navigation Bar */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-[#F7F5EF]/95 backdrop-blur-md border-t border-[#E3E0D6] px-2 py-2 flex items-center justify-around shadow-lg">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onTabChange(item.id)}
              className={`flex flex-col items-center gap-1 p-1.5 rounded-xl text-[10px] font-medium relative transition-colors cursor-pointer ${
                isActive ? 'text-[#304B3C] font-bold' : 'text-[#77776F]'
              }`}
            >
              <div className="relative">
                {item.icon}
                {item.badge !== undefined && (
                  <span className="absolute -top-1 -right-1.5 w-3.5 h-3.5 rounded-full bg-[#BD4F44] text-white text-[8px] font-bold flex items-center justify-center">
                    {item.badge}
                  </span>
                )}
              </div>
              <span className="text-[10px] truncate max-w-[60px]">{item.label}</span>
            </button>
          );
        })}
      </div>
    </>
  );
};
