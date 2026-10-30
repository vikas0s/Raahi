import React, { useState, useRef, useEffect } from 'react';
import {
  X,
  Send,
  Bot,
  Sparkles,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  RotateCcw,
  ArrowRight,
  Clock,
  IndianRupee,
  Compass,
  AlertCircle,
  CheckCircle2,
  Bus,
  Footprints,
  Car
} from 'lucide-react';
import {
  chatWithAssistant,
  resetAssistantSession,
  transcribeAudio,
  synthesizeSpeech
} from '../../services/api';
import type { ChatMessage, RouteItinerary, AppLanguage } from '../../types/transit';
import {
  startLiveSpeechRecognition,
  isWebSpeechSupported,
  startWavRecording,
  type WavRecorder
} from '../../utils/audio';
import { useTranslation } from '../../i18n/LanguageContext';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSelectRoute?: (route: RouteItinerary) => void;
  onNavigateToPlan?: (route?: RouteItinerary) => void;
  onNavigateToSaved?: () => void;
  onNavigateToLive?: () => void;
  contextOrigin?: string;
  contextDestination?: string;
  city?: string;
  language?: AppLanguage;
}

// Markdown parser helper for assistant responses
const renderMarkdown = (text: string) => {
  const lines = text.split('\n');
  return lines.map((line, idx) => {
    // Empty lines
    if (!line.trim()) {
      return <div key={idx} className="h-1.5" />;
    }

    // Italic note lines: *(...)*
    if (line.startsWith('*(') && line.endsWith(')*')) {
      const inner = line.slice(2, -2);
      return (
        <p key={idx} className="text-[11px] text-[#52544D] italic mt-1.5 pt-1.5 border-t border-[#D8D4C7]/60">
          {inner}
        </p>
      );
    }

    // Bullet points
    const isBullet = line.trim().startsWith('•') || line.trim().startsWith('-') || line.trim().startsWith('*');
    const content = isBullet ? line.trim().replace(/^[•\-\*]\s*/, '') : line;

    // Parse **bold** tokens
    const parts = content.split(/(\*\*.*?\*\*)/g);
    const parsedLine = parts.map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={pIdx} className="font-bold text-[#1F231F]">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <span key={pIdx}>{part}</span>;
    });

    if (isBullet) {
      return (
        <div key={idx} className="flex items-start gap-1.5 my-0.5 ml-1">
          <span className="text-[#304B3C] font-extrabold text-xs select-none">•</span>
          <span className="flex-1">{parsedLine}</span>
        </div>
      );
    }

    return (
      <p key={idx} className="my-0.5">
        {parsedLine}
      </p>
    );
  });
};

export const RaahiAssistant: React.FC<Props> = ({
  isOpen,
  onClose,
  onSelectRoute,
  onNavigateToPlan,
  onNavigateToSaved,
  onNavigateToLive,
  contextOrigin,
  contextDestination,
  city = 'Mathura & Vrindavan'
}) => {
  const { t, language } = useTranslation();

  // Session ID for multi-turn conversation memory
  const [sessionId, setSessionId] = useState<string>(() => {
    try {
      return crypto.randomUUID();
    } catch {
      return `raahi-session-${Date.now()}`;
    }
  });

  const getInitialWelcome = (): ChatMessage => {
    const isMathura = city.includes('Mathura') || city.includes('Vrindavan');
    let welcomeText = '';
    let actions: { label: string; action: string }[] = [];

    if (language === 'hi') {
      if (isMathura) {
        welcomeText = 'राधे राधे! मैं राही (Raahi AI) हूँ — आपका ब्रज यात्रा व आवागमन साथी। आप मुझसे मथुरा–वृंदावन के मंदिर दर्शन समय, ई-रिक्शा, टेम्पो व इलेक्ट्रिक बस रूट्स, और लाइव ट्रैफिक स्थिति के बारे में पूछ सकते हैं।';
        actions = [
          { label: 'मथुरा जंक्शन से बांके बिहारी', action: 'prompt_mathura_bihari' },
          { label: 'प्रेम मंदिर लाइट शो टाइमिंग', action: 'prompt_prem_mandir' },
          { label: 'गोवर्धन परिक्रमा रूट', action: 'prompt_govardhan' }
        ];
      } else {
        welcomeText = `नमस्ते! मैं राही (Raahi AI) हूँ — आपका स्मार्ट यात्रा साथी। आप मुझसे ${city} के सबसे तेज़ व सबसे सस्ते मार्ग, लाइव बस-मेट्रो स्थिति और किराए के बारे में पूछ सकते हैं।`;
        actions = [
          { label: 'साइबर सिटी के लिए सबसे तेज़ मार्ग', action: 'prompt_fastest' },
          { label: 'सबसे सस्ता मार्ग बताओ', action: 'prompt_cheapest' },
          { label: 'मेट्रो में कोई देरी है কি?', action: 'check_delays' }
        ];
      }
    } else {
      if (isMathura) {
        welcomeText = 'Radhe Radhe! I am Raahi AI — your dedicated transit companion for Mathura–Vrindavan. Ask me about temple darshan timings, auto/e-rickshaw fares, electric city buses, and optimal travel routes across Braj.';
        actions = [
          { label: 'Mathura Jn to Bankey Bihari', action: 'prompt_mathura_bihari' },
          { label: 'Prem Mandir Light Show', action: 'prompt_prem_mandir' },
          { label: 'Govardhan Parikrama Route', action: 'prompt_govardhan' }
        ];
      } else {
        welcomeText = `Hello! I am Raahi AI — your smart mobility companion. Ask me for fastest or cheapest routes, live transit disruptions, and step-by-step directions across ${city}.`;
        actions = [
          { label: 'Fastest route to Cyber City', action: 'prompt_fastest' },
          { label: 'Cheapest transit option', action: 'prompt_cheapest' },
          { label: 'Check transit delays', action: 'check_delays' }
        ];
      }
    }

    return {
      id: 'welcome',
      sender: 'assistant',
      text: welcomeText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggested_actions: actions
    };
  };

  const [messages, setMessages] = useState<ChatMessage[]>([getInitialWelcome()]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);

  // Voice recording & TTS state
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [isListening, setIsListening] = useState(false);
  const [micPermissionBlocked, setMicPermissionBlocked] = useState(false);
  const liveRecognitionRef = useRef<{ stop: () => void } | null>(null);
  const wavRecorderRef = useRef<WavRecorder | null>(null);
  const [playingMessageId, setPlayingMessageId] = useState<string | null>(null);
  const [isSynthesizing, setIsSynthesizing] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordIntervalRef = useRef<number | null>(null);
  const activeAudioRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync initial welcome when language or city changes and chat has only welcome
  useEffect(() => {
    setMessages(prev => {
      if (prev.length === 1 && prev[0].id === 'welcome') {
        return [getInitialWelcome()];
      }
      return prev;
    });
  }, [language, city]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  // Clean up recording on unmount or close
  useEffect(() => {
    return () => {
      if (recordIntervalRef.current) clearInterval(recordIntervalRef.current);
      if (liveRecognitionRef.current) {
        liveRecognitionRef.current.stop();
        liveRecognitionRef.current = null;
      }
      if (wavRecorderRef.current) {
        wavRecorderRef.current.cancel();
        wavRecorderRef.current = null;
      }
      if (activeAudioRef.current) {
        activeAudioRef.current.pause();
      }
    };
  }, []);

  // Reset Conversation
  const handleResetChat = async () => {
    try {
      await resetAssistantSession(sessionId);
    } catch {
      // ignore
    }
    const newId = `raahi-session-${Date.now()}`;
    setSessionId(newId);
    setMessages([getInitialWelcome()]);
    setInput('');
    setLastFailedMessage(null);
    if (activeAudioRef.current) {
      activeAudioRef.current.pause();
    }
    setPlayingMessageId(null);
  };

  // Send message
  const handleSend = async (messageText?: string) => {
    const textToSend = (messageText || input).trim();
    if (!textToSend || isLoading) return;

    setLastFailedMessage(null);
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
        language === 'hi' ? 'hi' : 'en',
        contextOrigin,
        contextDestination,
        city,
        sessionId
      );

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: response.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        action_type: response.action_type,
        route_data: response.route_data,
        suggested_actions: response.suggested_actions,
        is_grounded_route: response.is_grounded_route,
        audio_base64: response.audio_base64
      };

      setMessages(prev => [...prev, assistantMsg]);

// Route is rendered inside chat; user explicitly taps View in Journey Planner
    } catch {
      setLastFailedMessage(textToSend);
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text: language === 'hi'
            ? 'सर्वर से कनेक्ट करने में समस्या आई। कृपया अपना इंटरनेट कनेक्शन जांचें या पुनः प्रयास करें।'
            : 'Unable to reach the transit server. Please check your connection or retry.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isError: true,
          canRetry: true
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fallback to WAV Audio Recording via AudioContext + Sarvam Saaras AI
  const fallbackToWavRecording = async () => {
    try {
      setIsRecording(true);
      setRecordingSeconds(0);
      const recorder = await startWavRecording();
      wavRecorderRef.current = recorder;
      recordIntervalRef.current = window.setInterval(() => {
        setRecordingSeconds((s) => s + 1);
      }, 1000);
    } catch (err: any) {
      console.warn('Microphone permission error:', err);
      setIsRecording(false);
      if (recordIntervalRef.current) {
        clearInterval(recordIntervalRef.current);
        recordIntervalRef.current = null;
      }
      if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
        setMicPermissionBlocked(true);
      } else {
        alert(language === 'hi' ? 'माइक्रोफ़ोन शुरू करने में समस्या आई।' : 'Could not access microphone.');
      }
    }
  };

  // Dual-Tier Voice Handling (Web Speech API live streaming + Sarvam Saaras WAV fallback)
  const handleToggleVoice = async () => {
    // If currently listening or recording, stop immediately
    if (isListening || isRecording) {
      if (liveRecognitionRef.current) {
        liveRecognitionRef.current.stop();
        liveRecognitionRef.current = null;
      }
      setIsListening(false);

      if (wavRecorderRef.current) {
        const recorder = wavRecorderRef.current;
        wavRecorderRef.current = null;
        setIsRecording(false);
        if (recordIntervalRef.current) {
          clearInterval(recordIntervalRef.current);
          recordIntervalRef.current = null;
        }
        setIsTranscribing(true);
        try {
          const wavBlob = await recorder.stop();
          if (wavBlob && wavBlob.size > 2000) {
            const transcript = await transcribeAudio(wavBlob);
            if (transcript.trim()) {
              setInput(transcript);
              await handleSend(transcript);
            }
          }
        } catch (err) {
          console.warn('WAV Transcription error:', err);
        } finally {
          setIsTranscribing(false);
        }
      }
      return;
    }

    setMicPermissionBlocked(false);

    // Tier 1: Instant Native Browser Speech Recognition (Google Chrome / Edge)
    if (isWebSpeechSupported()) {
      try {
        setIsListening(true);
        const rec = startLiveSpeechRecognition(
          language === 'hi' ? 'hi' : 'en',
          {
            onInterim: (text) => {
              setInput(text);
            },
            onFinal: (text) => {
              setInput(text);
              setIsListening(false);
              liveRecognitionRef.current = null;
              handleSend(text);
            },
            onError: (errCode) => {
              console.warn('Speech recognition error:', errCode);
              setIsListening(false);
              liveRecognitionRef.current = null;
              if (errCode === 'not-allowed' || errCode === 'permission-denied') {
                setMicPermissionBlocked(true);
              } else if (errCode !== 'no-speech' && errCode !== 'aborted') {
                fallbackToWavRecording();
              }
            },
            onEnd: () => {
              setIsListening(false);
              liveRecognitionRef.current = null;
            }
          }
        );
        liveRecognitionRef.current = rec;
        return;
      } catch (err: any) {
        console.warn('Live speech recognition failed to start:', err);
        setIsListening(false);
      }
    }

    // Tier 2: 16kHz PCM WAV Recording with Sarvam Saaras AI
    await fallbackToWavRecording();
  };

  // Text-To-Speech Playback
  const handlePlayTTS = async (msg: ChatMessage) => {
    // If currently playing this message, toggle pause
    if (playingMessageId === msg.id && activeAudioRef.current) {
      activeAudioRef.current.pause();
      setPlayingMessageId(null);
      return;
    }

    if (activeAudioRef.current) {
      activeAudioRef.current.pause();
    }

    let audioBase64 = msg.audio_base64;
    if (!audioBase64) {
      setIsSynthesizing(msg.id);
      try {
        const langCode = language === 'hi' ? 'hi-IN' : 'en-IN';
        const cleanForTTS = msg.text.replace(/[\*•#_`]/g, '').trim();
        audioBase64 = (await synthesizeSpeech(cleanForTTS, langCode)) || undefined;
        msg.audio_base64 = audioBase64;
      } catch {
        // ignore
      } finally {
        setIsSynthesizing(null);
      }
    }

    if (!audioBase64) return;

    try {
      const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
      activeAudioRef.current = audio;
      setPlayingMessageId(msg.id);
      audio.onended = () => {
        setPlayingMessageId(null);
      };
      audio.onerror = () => {
        setPlayingMessageId(null);
      };
      await audio.play();
    } catch (err) {
      console.warn('Audio playback error:', err);
      setPlayingMessageId(null);
    }
  };

  const handleActionClick = (action: string) => {
    if (action === 'prompt_janmasthan') {
      handleSend(language === 'hi' ? 'मथुरा जंक्शन से श्रीकृष्ण जन्मस्थान कैसे जाएँ?' : 'Mathura Junction to Shri Krishna Janmasthan kaise jaye?');
    } else if (action === 'prompt_bankey_bihari' || action === 'prompt_mathura_bihari') {
      handleSend(language === 'hi' ? 'मथुरा जंक्शन से बांके बिहारी मंदिर का सबसे तेज़ रूट क्या है?' : 'What is the fastest route from Mathura Junction to Bankey Bihari Temple?');
    } else if (action === 'prompt_gla') {
      handleSend(language === 'hi' ? 'मथुरा जंक्शन से GLA University कैसे जाएँ?' : 'Mathura Junction se GLA University kaise jaye?');
    } else if (action === 'prompt_mathura_bihari_legacy') {
      handleSend(language === 'hi' ? 'मथुरा जंक्शन से बांके बिहारी मंदिर का सबसे तेज़ रूट क्या है?' : 'What is the fastest route from Mathura Junction to Bankey Bihari Temple?');
    } else if (action === 'prompt_prem_mandir') {
      handleSend(language === 'hi' ? 'प्रेम मंदिर में लाइट शो का समय क्या है और कैसे जाएँ?' : 'What are the Prem Mandir light show timings and how to reach?');
    } else if (action === 'prompt_govardhan') {
      handleSend(language === 'hi' ? 'गोवर्धन परिक्रमा के लिए ई-रिक्शा और रूट बताओ' : 'Tell me the Govardhan Parikrama route and e-rickshaw options');
    } else if (action === 'prompt_fastest') {
      handleSend(language === 'hi' ? 'गंतव्य तक पहुंचने के लिए सबसे तेज़ मार्ग कौन सा है?' : 'Which route is fastest to reach my destination?');
    } else if (action === 'prompt_cheapest') {
      handleSend(language === 'hi' ? 'मुझे सबसे कम किराए वाला मार्ग बताओ' : 'Mujhe sabse sasta route batao');
    } else if (action === 'check_delays') {
      handleSend(language === 'hi' ? 'क्या किसी रूट या लाइन पर देरी है?' : 'Is there any delay on transit routes right now?');
    } else if (action === 'prompt_timings') {
      handleSend(language === 'hi' ? 'मंदिर के दर्शन और आरती का समय क्या है?' : 'What are the temple darshan and aarti timings?');
    } else if (action === 'save_route') {
      handleSend(language === 'hi' ? 'इस रूट को मेरे Saved Routes में सेव करो' : 'Save this route to my saved commutes');
    } else if (action === 'navigate_plan') {
      const lastRouteMsg = [...messages].reverse().find(m => m.route_data);
      if (lastRouteMsg?.route_data) {
        if (onNavigateToPlan) {
          onNavigateToPlan(lastRouteMsg.route_data);
        } else if (onSelectRoute) {
          onSelectRoute(lastRouteMsg.route_data);
        }
      } else if (onNavigateToPlan) {
        onNavigateToPlan();
      }
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

  const isMathura = city.includes('Mathura') || city.includes('Vrindavan');

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[460px] bg-[#F7F5EF] border-l border-[#D8D4C7] shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="p-4 bg-[#FFFEFA] border-b border-[#D8D4C7] flex items-center justify-between shadow-2xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-[#304B3C]/10 border border-[#304B3C]/20 flex items-center justify-center text-[#253D30] shadow-2xs">
            <Bot size={22} className="stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-heading font-extrabold text-sm text-[#1F231F]">
                {t('aiAssistantTitle')}
              </h3>
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-[#304B3C]/10 text-[#253D30]">
                <Sparkles size={10} />
                <span>Gemini & Sarvam AI</span>
              </span>
            </div>
            <p className="text-[11px] text-[#52544D] font-medium flex items-center gap-1.5 mt-0.5">
              <span>{isMathura ? 'मथुरा–वृंदावन ब्रज साथी' : city}</span>
              <span className="text-[#A09C90]">•</span>
              <span>English • हिन्दी</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {/* Reset / New Chat Button */}
          <button
            onClick={handleResetChat}
            title={language === 'hi' ? 'नई बातचीत शुरू करें' : 'Start new conversation'}
            className="p-2 rounded-xl text-[#52544D] hover:bg-[#EEECE3] hover:text-[#1F231F] transition-colors cursor-pointer"
          >
            <RotateCcw size={17} className="stroke-[2.2]" />
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-[#52544D] hover:bg-[#EEECE3] hover:text-[#1F231F] transition-colors cursor-pointer"
          >
            <X size={19} className="stroke-[2.2]" />
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const isPlaying = playingMessageId === msg.id;
          const isSynthesizingThis = isSynthesizing === msg.id;

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              <div className="flex items-end gap-2 max-w-[92%]">
                {!isUser && (
                  <div className="w-7 h-7 rounded-xl bg-[#253D30] text-white flex items-center justify-center shrink-0 mb-1 text-xs font-bold shadow-2xs">
                    <Bot size={15} className="stroke-[2.2]" />
                  </div>
                )}

                <div
                  className={`rounded-2xl px-4 py-3 text-xs leading-relaxed shadow-xs ${
                    isUser
                      ? 'bg-[#253D30] text-[#FFFEFA] font-medium rounded-br-none'
                      : msg.isError
                      ? 'bg-[#FDF2F2] text-[#991B1B] border border-[#FCA5A5] rounded-bl-none'
                      : 'bg-[#FFFEFA] text-[#1F231F] font-medium border border-[#D8D4C7] rounded-bl-none shadow-[0_1px_4px_rgba(41,45,41,0.03)]'
                  }`}
                >
                  <div className="space-y-1">
                    {renderMarkdown(msg.text)}
                  </div>

                  {/* Grounded Interactive Route Card */}
                  {msg.route_data && (
                    <div className="mt-3 p-3.5 rounded-xl bg-[#F7F5EF] border border-[#D8D4C7] text-xs space-y-2.5 shadow-2xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <span className="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase bg-[#304B3C] text-white">
                            {msg.route_data.tag}
                          </span>
                          <span className="font-extrabold text-[#253D30] text-xs">
                            {msg.route_data.title}
                          </span>
                        </div>
                        <span className="font-extrabold text-sm text-[#253D30]">
                          ₹{msg.route_data.total_fare_inr.toFixed(0)}
                        </span>
                      </div>

                      <div className="flex items-center gap-3 text-[11px] text-[#52544D] font-semibold border-y border-[#E3E0D6] py-1.5">
                        <span className="flex items-center gap-1">
                          <Clock size={12} className="text-[#304B3C]" />
                          <span>~{msg.route_data.total_duration_minutes} {t('mins')}</span>
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <IndianRupee size={12} className="text-[#304B3C]" />
                          <span>₹{msg.route_data.total_fare_inr} fare</span>
                        </span>
                        <span>•</span>
                        <span>🔄 {msg.route_data.transfers_count} {t('transfers')}</span>
                      </div>

                      {/* Legs preview */}
                      <div className="flex flex-wrap items-center gap-1.5 text-[10px] text-[#52544D]">
                        {msg.route_data.legs.map((leg, lIdx) => (
                          <span
                            key={lIdx}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#FFFEFA] border border-[#D8D4C7] font-bold text-[#253D30]"
                          >
                            {leg.mode === 'walk' ? (
                              <Footprints size={10} className="text-[#75776E]" />
                            ) : leg.mode.includes('bus') ? (
                              <Bus size={10} className="text-[#304B3C]" />
                            ) : (
                              <Car size={10} className="text-[#304B3C]" />
                            )}
                            <span>{leg.line_name || leg.mode} ({leg.duration_minutes}m)</span>
                          </span>
                        ))}
                      </div>

                      {/* Primary Action Button */}
                      <button
                        onClick={() => {
                          if (msg.route_data) {
                            if (onNavigateToPlan) {
                              onNavigateToPlan(msg.route_data);
                            } else if (onSelectRoute) {
                              onSelectRoute(msg.route_data);
                            }
                          } else if (onNavigateToPlan) {
                            onNavigateToPlan();
                          }
                          onClose();
                        }}
                        className="w-full mt-1 py-2 px-3 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-white font-bold text-[11px] flex items-center justify-center gap-1.5 transition-colors cursor-pointer shadow-xs"
                      >
                        <span>{language === 'hi' ? 'प्लानर में पूरा रूट देखें' : 'View in Journey Planner'}</span>
                        <ArrowRight size={13} />
                      </button>
                    </div>
                  )}

                  {/* Message Footer: Timestamp, Voice TTS, and Retry if Error */}
                  <div className="flex items-center justify-between gap-3 mt-2 pt-1 border-t border-[#D8D4C7]/40 text-[10px]">
                    <span className={`font-medium ${isUser ? 'text-[#FFFEFA]/80' : 'text-[#52544D]'}`}>
                      {msg.timestamp}
                    </span>

                    <div className="flex items-center gap-1.5">
                      {/* Retry Button if Error */}
                      {msg.canRetry && lastFailedMessage && (
                        <button
                          onClick={() => handleSend(lastFailedMessage)}
                          className="font-bold text-[#B91C1C] hover:underline flex items-center gap-1 cursor-pointer"
                        >
                          <RotateCcw size={10} />
                          <span>{language === 'hi' ? 'पुनः प्रयास करें' : 'Retry'}</span>
                        </button>
                      )}

                      {/* Text-To-Speech Listen Button */}
                      {!isUser && !msg.isError && (
                        <button
                          onClick={() => handlePlayTTS(msg)}
                          disabled={isSynthesizingThis}
                          title={isPlaying ? 'Pause speech' : 'Listen to audio response'}
                          className={`p-1 rounded-md transition-colors cursor-pointer ${
                            isPlaying
                              ? 'bg-[#304B3C] text-white'
                              : 'text-[#52544D] hover:bg-[#EEECE3] hover:text-[#1F231F]'
                          }`}
                        >
                          {isSynthesizingThis ? (
                            <span className="w-2.5 h-2.5 rounded-full border-2 border-[#304B3C] border-t-transparent animate-spin inline-block" />
                          ) : isPlaying ? (
                            <VolumeX size={12} />
                          ) : (
                            <Volume2 size={12} />
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2 ml-9">
                  {msg.suggested_actions.map((act, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleActionClick(act.action)}
                      className="px-3 py-1.5 rounded-xl bg-[#FFFEFA] hover:bg-[#EEECE3] text-[11px] font-bold text-[#253D30] border border-[#D8D4C7] transition-all cursor-pointer shadow-2xs hover:shadow-xs active:scale-[0.98]"
                    >
                      {act.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {/* Loading / Analyzing Indicator */}
        {isLoading && (
          <div className="flex items-center gap-2.5 text-xs text-[#52544D] font-semibold ml-9 p-2 rounded-xl bg-[#FFFEFA] border border-[#D8D4C7] w-fit shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-[#304B3C] animate-ping" />
            <span>{language === 'hi' ? 'मार्ग विश्लेषण व गणना हो रही है...' : 'Raahi is analyzing transit routes...'}</span>
          </div>
        )}

        {/* Voice Transcribing Indicator */}
        {isTranscribing && (
          <div className="flex items-center gap-2 text-xs text-[#253D30] font-semibold ml-9 p-2 rounded-xl bg-[#FFFEFA] border border-[#304B3C]/30 w-fit">
            <Mic size={14} className="animate-bounce text-[#304B3C]" />
            <span>{language === 'hi' ? 'आवाज़ पहचानी जा रही है (Sarvam Saaras)...' : 'Transcribing voice via Sarvam Saaras...'}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompt Chips */}
      <div className="px-4 py-2 bg-[#EEECE3]/70 border-t border-[#D8D4C7] flex items-center gap-1.5 overflow-x-auto no-scrollbar">
        {isMathura ? (
          <>
            <button
              onClick={() => handleSend(language === 'hi' ? 'मथुरा जंक्शन से बांके बिहारी मंदिर का सबसे तेज़ रूट' : 'Fastest route from Mathura Junction to Bankey Bihari')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {language === 'hi' ? 'बांके बिहारी रूट' : 'Bankey Bihari Route'}
            </button>
            <button
              onClick={() => handleSend(language === 'hi' ? 'प्रेम मंदिर लाइट शो का समय क्या है?' : 'What are the Prem Mandir light show timings?')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {language === 'hi' ? 'प्रेम मंदिर शो समय' : 'Prem Mandir Timings'}
            </button>
            <button
              onClick={() => handleSend(language === 'hi' ? 'सबसे सस्ता ई-रिक्शा या टेम्पो रूट बताओ' : 'Cheapest shared auto or tempo route')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {language === 'hi' ? 'सस्ता टेम्पो / ई-रिक्शा' : 'Cheapest E-Rickshaw'}
            </button>
            <button
              onClick={() => handleSend(language === 'hi' ? 'गोवर्धन परिक्रमा मार्ग कैसे करें?' : 'How to do Govardhan Parikrama?')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {language === 'hi' ? 'गोवर्धन परिक्रमा' : 'Govardhan Parikrama'}
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => handleSend(language === 'hi' ? 'सबसे तेज़ मार्ग कौन सा है?' : 'Which route is fastest?')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {t('aiFastestChip')}
            </button>
            <button
              onClick={() => handleSend(language === 'hi' ? 'मुझे सबसे सस्ता मार्ग बताओ' : 'Mujhe sabse sasta route batao')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {t('aiCheapestChip')}
            </button>
            <button
              onClick={() => handleSend(language === 'hi' ? 'क्या किसी मेट्रो लाइन पर देरी है?' : 'Is any metro line delayed?')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {t('aiDelaysChip')}
            </button>
            <button
              onClick={() => handleSend(language === 'hi' ? 'कम पैदल चलने वाला मार्ग दिखाओ' : 'Kam walking wala route dikhao')}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-[#FFFEFA] border border-[#D8D4C7] text-[11px] font-bold text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              {t('aiLessWalkingChip')}
            </button>
          </>
        )}
      </div>

      {/* Input Composer */}
      <div className="p-3 bg-[#FFFEFA] border-t border-[#D8D4C7]">
        {/* Microphone Permission Blocked Notice */}
        {micPermissionBlocked && (
          <div className="mb-2.5 p-3 rounded-xl bg-[#FEF2F2] border border-[#F87171] text-xs text-[#991B1B] space-y-1.5 animate-in fade-in">
            <div className="flex items-center justify-between font-bold">
              <span className="flex items-center gap-1.5">
                <MicOff size={14} className="text-[#DC2626]" />
                {language === 'hi' ? 'माइक्रोफ़ोन अनुमति ब्लॉक है' : 'Microphone Permission Blocked'}
              </span>
              <button
                type="button"
                onClick={() => setMicPermissionBlocked(false)}
                className="text-[#991B1B] hover:text-[#7F1D1D] font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>
            <p className="text-[11px] leading-relaxed text-[#7F1D1D]">
              {language === 'hi'
                ? 'Chrome के URL बार में सबसे ऊपर दाईं ओर दिए गए कैमरा/माइक आइकन (🚫) पर क्लिक करें, "Always allow" चुनें और नीचे Retry पर क्लिक करें।'
                : 'Click the camera/mic icon (🚫) at the right end of Chrome address bar, select "Always allow", and click Retry.'}
            </p>
            <div className="pt-1 flex gap-2">
              <button
                type="button"
                onClick={handleToggleVoice}
                className="px-2.5 py-1 rounded-lg bg-[#DC2626] text-white font-bold text-[11px] hover:bg-[#B91C1C] transition-colors cursor-pointer"
              >
                {language === 'hi' ? 'पुनः प्रयास करें (Retry Mic)' : 'Retry Mic Access'}
              </button>
            </div>
          </div>
        )}

        {/* Live Listening Banner */}
        {isListening && (
          <div className="mb-2 px-3 py-2 rounded-xl bg-[#ECFDF5] border border-[#A7F3D0] flex items-center justify-between text-xs text-[#065F46] animate-pulse">
            <div className="flex items-center gap-2 font-bold">
              <span className="w-2.5 h-2.5 rounded-full bg-[#10B981] animate-ping" />
              <span>{language === 'hi' ? 'सुन रहे हैं... बोलिए (बोलते ही ट्रांसक्राइब होगा)' : 'Listening... speak now (real-time transcribe)'}</span>
            </div>
            <button
              type="button"
              onClick={handleToggleVoice}
              className="px-2.5 py-1 rounded-lg bg-[#059669] text-white font-bold text-[11px] hover:bg-[#047857] transition-colors cursor-pointer"
            >
              {language === 'hi' ? 'समाप्त' : 'Done'}
            </button>
          </div>
        )}

        {/* Active WAV recording state banner */}
        {isRecording && !isListening && (
          <div className="mb-2 px-3 py-2 rounded-xl bg-[#FEE2E2] border border-[#FCA5A5] flex items-center justify-between text-xs text-[#991B1B] animate-pulse">
            <div className="flex items-center gap-2 font-bold">
              <span className="w-2.5 h-2.5 rounded-full bg-[#DC2626] animate-ping" />
              <span>{language === 'hi' ? 'आवाज़ रिकॉर्ड हो रही है...' : 'Recording voice...'} ({recordingSeconds}s)</span>
            </div>
            <button
              type="button"
              onClick={handleToggleVoice}
              className="px-2.5 py-1 rounded-lg bg-[#DC2626] text-white font-bold text-[11px] hover:bg-[#B91C1C] transition-colors cursor-pointer"
            >
              {language === 'hi' ? 'समाप्त करें' : 'Done'}
            </button>
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          {/* Voice Input Button */}
          <button
            type="button"
            onClick={handleToggleVoice}
            disabled={isLoading || isTranscribing}
            title={isListening || isRecording ? 'Stop listening' : 'Speak your query (Mic)'}
            className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
              isListening
                ? 'bg-[#059669] text-white border-[#059669] animate-pulse'
                : isRecording
                ? 'bg-[#DC2626] text-white border-[#DC2626] animate-pulse'
                : 'bg-[#EEECE3]/70 text-[#253D30] border-[#D8D4C7] hover:bg-[#E3DFD4]'
            }`}
          >
            {isListening || isRecording ? <MicOff size={16} /> : <Mic size={16} />}
          </button>

          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              language === 'hi'
                ? (isMathura ? 'मथुरा-वृंदावन का कोई भी रूट या सवाल पूछें...' : 'कोई भी रूट या देरी के बारे में पूछें...')
                : (isMathura ? 'Ask about any Mathura-Vrindavan route or temple...' : t('aiInputPlaceholder'))
            }
            disabled={isLoading || isRecording || isListening}
            className="flex-1 px-3.5 py-2.5 bg-[#EEECE3]/60 focus:bg-[#FFFEFA] rounded-xl border border-[#D8D4C7] focus:border-[#253D30] focus:ring-1 focus:ring-[#253D30]/20 text-xs font-medium text-[#1F231F] outline-none transition-all placeholder:text-[#8C8A80]"
          />

          <button
            type="submit"
            disabled={!input.trim() || isLoading || isRecording || isListening}
            className="p-2.5 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-xs hover:shadow-sm"
          >
            <Send size={15} />
          </button>
        </form>
      </div>
    </div>
  );
};
