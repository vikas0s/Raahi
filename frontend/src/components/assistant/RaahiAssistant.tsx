import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Bot, Sparkles, Navigation2 } from 'lucide-react';
import { chatWithAssistant } from '../../services/api';
import type { ChatMessage, RouteItinerary, AppLanguage } from '../../types/transit';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSelectRoute?: (route: RouteItinerary) => void;
  onNavigateToPlan?: () => void;
  onNavigateToSaved?: () => void;
  onNavigateToLive?: () => void;
  contextOrigin?: string;
  contextDestination?: string;
  city?: string;
  language?: AppLanguage;
}

export const RaahiAssistant: React.FC<Props> = ({
  isOpen,
  onClose,
  onSelectRoute,
  onNavigateToPlan,
  onNavigateToSaved,
  onNavigateToLive,
  contextOrigin,
  contextDestination,
  city = 'Delhi NCR',
  language: propLang
}) => {
  const { t, language } = useTranslation();
  const activeLang = propLang || language;

  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: 'welcome',
      sender: 'assistant',
      text: t('aiWelcome'),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggested_actions: [
        { label: 'Fastest route to Cyber City', action: 'prompt_fastest' },
        { label: 'Mujhe sabse sasta route batao', action: 'prompt_cheapest' },
        { label: 'Check metro delays', action: 'check_delays' }
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatWithAssistant(
        textToSend,
        language,
        contextOrigin,
        contextDestination,
        city
      );

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: response.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        action_type: response.action_type,
        route_data: response.route_data,
        suggested_actions: response.suggested_actions
      };

      setMessages(prev => [...prev, assistantMsg]);

      if (response.route_data && onSelectRoute) {
        onSelectRoute(response.route_data);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text: 'I encountered an issue connecting to the transit server. Please check your network or try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleActionClick = (action: string) => {
    if (action === 'prompt_fastest') {
      handleSend('Which route is fastest to reach my destination?');
    } else if (action === 'prompt_cheapest') {
      handleSend('Mujhe sabse sasta route batao');
    } else if (action === 'check_delays') {
      handleSend('Is any metro line delayed right now?');
    } else if (action === 'navigate_plan' && onNavigateToPlan) {
      onNavigateToPlan();
      onClose();
    } else if (action === 'navigate_saved' && onNavigateToSaved) {
      onNavigateToSaved();
      onClose();
    } else if (action === 'navigate_live' && onNavigateToLive) {
      onNavigateToLive();
      onClose();
    } else if (action === 'expand_route' && onNavigateToPlan) {
      onNavigateToPlan();
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[440px] bg-[#F7F5EF] border-l border-[#E3E0D6] shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="p-4 bg-[#FFFEFA] border-b border-[#D8D4C7] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-[#64836D]/20 flex items-center justify-center text-[#253D30]">
            <Bot size={20} className="stroke-[2.2]" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-sm text-[#1F231F] flex items-center gap-1.5">
              <span>Raahi AI Assistant</span>
              <span className="w-1.5 h-1.5 rounded-full bg-[#5B8A6E] animate-pulse" />
            </h3>
            <p className="text-[11px] text-[#52544D] font-medium">
              English • हिन्दी ({city})
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-[#52544D] hover:bg-[#EEECE3] hover:text-[#1F231F] transition-colors cursor-pointer"
        >
          <X size={18} className="stroke-[2.2]" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              <div className="flex items-end gap-2 max-w-[88%]">
                {!isUser && (
                  <div className="w-6 h-6 rounded-full bg-[#253D30] text-white flex items-center justify-center shrink-0 mb-1 text-xs font-bold">
                    <Bot size={13} className="stroke-[2.2]" />
                  </div>
                )}

                <div
                  className={`rounded-2xl px-4 py-3 text-xs leading-relaxed shadow-xs ${
                    isUser
                      ? 'bg-[#253D30] text-[#FFFEFA] font-medium rounded-br-none'
                      : 'bg-[#FFFEFA] text-[#1F231F] font-medium border border-[#D8D4C7] rounded-bl-none shadow-[0_1px_4px_rgba(41,45,41,0.02)]'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>

                  {/* Route Snippet Card */}
                  {msg.route_data && (
                    <div className="mt-2.5 p-3 rounded-xl bg-[#EEECE3]/70 border border-[#D8D4C7] text-xs space-y-1">
                      <div className="flex items-center justify-between font-extrabold text-[#253D30]">
                        <span>{msg.route_data.title}</span>
                        <span>₹{msg.route_data.total_fare_inr.toFixed(0)}</span>
                      </div>
                      <div className="text-[11px] text-[#52544D] font-semibold flex items-center gap-3">
                        <span>⏱️ {msg.route_data.total_duration_minutes} mins</span>
                        <span>🔄 {msg.route_data.transfers_count} transfers</span>
                      </div>
                    </div>
                  )}

                  <span className={`block text-[10px] mt-1.5 font-medium ${isUser ? 'text-[#FFFEFA]/80' : 'text-[#52544D]'}`}>
                    {msg.timestamp}
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2 ml-8">
                  {msg.suggested_actions.map((act, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleActionClick(act.action)}
                      className="px-3 py-1 rounded-xl bg-[#EEECE3] hover:bg-[#E3DFD4] text-[11px] font-bold text-[#253D30] border border-[#D8D4C7] transition-colors cursor-pointer shadow-2xs"
                    >
                      {act.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-[#52544D] font-semibold ml-8">
            <span className="w-2 h-2 rounded-full bg-[#4E7C5F] animate-ping" />
            <span>{t('aiAnalyzing')}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompt Chips */}
      <div className="px-4 py-2 bg-[#EEECE3]/70 border-t border-[#D8D4C7] flex items-center gap-1.5 overflow-x-auto">
        <button
          onClick={() => handleSend('Which route is fastest?')}
          className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
        >
          {t('aiFastestChip')}
        </button>
        <button
          onClick={() => handleSend('Mujhe sabse sasta route batao')}
          className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
        >
          {t('aiCheapestChip')}
        </button>
        <button
          onClick={() => handleSend('Is any metro line delayed?')}
          className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
        >
          {t('aiDelaysChip')}
        </button>
        <button
          onClick={() => handleSend('Kam walking wala route dikhao')}
          className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
        >
          {t('aiLessWalkingChip')}
        </button>
      </div>

      {/* Input Composer */}
      <div className="p-3 bg-[#FFFEFA] border-t border-[#D8D4C7]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('aiInputPlaceholder')}
            className="flex-1 px-3.5 py-2.5 bg-[#EEECE3]/60 focus:bg-[#FFFEFA] rounded-xl border border-[#D8D4C7] focus:border-[#253D30] focus:ring-1 focus:ring-[#253D30]/20 text-xs font-medium text-[#1F231F] outline-none transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-2.5 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-xs hover:shadow-sm"
          >
            <Send size={15} />
          </button>
        </form>
      </div>
    </div>
  );
};
