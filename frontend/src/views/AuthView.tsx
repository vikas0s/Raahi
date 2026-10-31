import React, { useState } from 'react';
import {
  Mail,
  Lock,
  User,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Loader2,
  KeyRound,
  Sparkles,
  Train,
  X
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../i18n/LanguageContext';
import { apiForgotPassword, apiResetPassword } from '../services/api';
import type { AuthMode } from '../types/auth';

interface Props {
  initialMode?: AuthMode;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const AuthView: React.FC<Props> = ({
  initialMode = 'signin',
  onSuccess,
  onCancel
}) => {
  const { signIn, signUp, isLoading, error: authError, clearError } = useAuth();
  const { t, language } = useTranslation();

  const [mode, setMode] = useState<AuthMode>(initialMode === 'signup' ? 'signup' : 'signin');
  const [showForgotModal, setShowForgotModal] = useState(false);

  // Form states
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Local validation & feedback state
  const [localError, setLocalError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Forgot password modal states
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotSuccess, setForgotSuccess] = useState<string | null>(null);
  const [forgotError, setForgotError] = useState<string | null>(null);
  const [demoToken, setDemoToken] = useState<string | null>(null);

  // Reset password states (if demo token provided)
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [resetConfirmPass, setResetConfirmPass] = useState('');
  const [resetLoading, setResetLoading] = useState(false);

  // Password strength calculation
  const getPasswordStrength = (pass: string) => {
    let score = 0;
    if (pass.length >= 8) score += 1;
    if (pass.length >= 12) score += 1;
    if (/[A-Z]/.test(pass) && /[a-z]/.test(pass)) score += 1;
    if (/\d/.test(pass)) score += 1;
    if (/[^A-Za-z0-9]/.test(pass)) score += 1;
    return score; // 0 to 5
  };

  const passStrength = getPasswordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    setSuccessMessage(null);
    clearError();

    if (!email || !email.includes('@')) {
      setLocalError('Please enter a valid email address.');
      return;
    }

    if (!password) {
      setLocalError('Please enter your password.');
      return;
    }

    if (mode === 'signup') {
      if (!name.trim()) {
        setLocalError('Please enter your full name.');
        return;
      }
      if (password.length < 8) {
        setLocalError('Password must be at least 8 characters long.');
        return;
      }
      if (!/\d/.test(password) || !/[a-zA-Z]/.test(password)) {
        setLocalError('Password must contain at least one letter and one number.');
        return;
      }
      if (password !== confirmPassword) {
        setLocalError('Passwords do not match.');
        return;
      }
    }

    try {
      if (mode === 'signin') {
        await signIn(email, password, rememberMe);
        setSuccessMessage('Signed in successfully! Redirecting...');
      } else {
        await signUp(name, email, password, confirmPassword);
        setSuccessMessage('Account created successfully! Welcome to Raahi.');
      }
      if (onSuccess) {
        setTimeout(onSuccess, 600);
      }
    } catch (err: any) {
      setLocalError(err.message || 'Authentication failed. Please verify your details.');
    }
  };

  const handleDemoSignIn = async () => {
    setLocalError(null);
    setEmail('demo@raahi.in');
    setPassword('Demo@1234');
    try {
      await signIn('demo@raahi.in', 'Demo@1234', true);
      setSuccessMessage('Signed in as Demo Commuter!');
      if (onSuccess) {
        setTimeout(onSuccess, 500);
      }
    } catch (err: any) {
      setLocalError(err.message || 'Demo sign in failed.');
    }
  };

  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotError(null);
    setForgotSuccess(null);
    setForgotLoading(true);
    try {
      const res = await apiForgotPassword(forgotEmail);
      setForgotSuccess(res.message);
      if (res.demo_reset_token) {
        setDemoToken(res.demo_reset_token);
        setResetToken(res.demo_reset_token);
      }
    } catch (err: any) {
      setForgotError(err.message || 'Failed to request password reset.');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotError(null);
    setResetLoading(true);
    try {
      const res = await apiResetPassword(resetToken, newPassword, resetConfirmPass);
      setForgotSuccess(res.message);
      setTimeout(() => {
        setShowForgotModal(false);
        setMode('signin');
        setPassword(newPassword);
      }, 1500);
    } catch (err: any) {
      setForgotError(err.message || 'Failed to reset password.');
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-65px)] w-full bg-[#F7F5EF] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-4xl bg-[#FFFEFA] rounded-3xl border border-[#D8D4C7] shadow-[0_8px_30px_rgba(48,75,60,0.06)] overflow-hidden grid grid-cols-1 lg:grid-cols-12 relative animate-in fade-in zoom-in-95 duration-200">
        
        {/* Optional close button if shown in modal mode */}
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="absolute top-4 right-4 z-20 p-2 rounded-xl text-[#77776F] hover:text-[#1F231F] hover:bg-[#EEECE3] transition-colors cursor-pointer"
            title="Close"
          >
            <X size={18} />
          </button>
        )}

        {/* Left Branding / Value Props Panel (Hidden on small mobile) */}
        <div className="lg:col-span-5 bg-[#253D30] text-[#FFFEFA] p-6 sm:p-8 flex flex-col justify-between relative overflow-hidden">
          {/* Subtle background route polyline motif */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <svg className="w-full h-full" viewBox="0 0 400 600" fill="none">
              <path d="M 50 100 Q 180 200 120 350 T 320 500" stroke="#FFFEFA" strokeWidth="6" strokeDasharray="12 12" />
              <circle cx="50" cy="100" r="14" fill="#E7B75B" />
              <circle cx="120" cy="350" r="10" fill="#4E7C5F" />
              <circle cx="320" cy="500" r="16" fill="#BD4F44" />
            </svg>
          </div>

          <div className="relative z-10">
            {/* Header Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#304B3C]/80 border border-[#4E7C5F]/40 text-[#E7B75B] text-xs font-bold tracking-tight mb-6">
              <ShieldCheck size={14} className="stroke-[2.5]" />
              <span>{t('missionTag')}</span>
            </div>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-2xl bg-[#FFFEFA] text-[#253D30] flex items-center justify-center font-bold shadow-md">
                <Train size={20} className="stroke-[2.5]" />
              </div>
              <div>
                <h2 className="text-xl font-heading font-extrabold text-[#FFFEFA] tracking-tight">
                  {t('appName')}
                </h2>
                <p className="text-xs text-[#A3B899] font-medium">
                  {language === 'hi' ? 'आपकी यात्रा, सहज और संगठित' : 'Your City, Effortlessly Connected'}
                </p>
              </div>
            </div>

            <p className="text-xs text-[#E3E0D6] leading-relaxed mb-6 font-medium">
              {language === 'hi'
                ? 'दिल्ली एनसीआर, मुंबई, बेंगलुरु और मथुरा-वृंदावन में एकीकृत मेट्रो, लोकल ट्रेन, डीटीसी/बीईएसटी बस और लास्ट-मील कनेक्ट।'
                : 'Experience synchronized public transit intelligence: multi-modal routing, official fare slabs, and saved commute sync across India.'}
            </p>

            {/* Travel Highlights */}
            <div className="space-y-3 pt-2">
              <div className="flex items-start gap-2.5 text-xs text-[#FFFEFA]/90">
                <CheckCircle2 size={16} className="text-[#64836D] shrink-0 mt-0.5" />
                <span>Sync daily home and office commutes across devices</span>
              </div>
              <div className="flex items-start gap-2.5 text-xs text-[#FFFEFA]/90">
                <CheckCircle2 size={16} className="text-[#64836D] shrink-0 mt-0.5" />
                <span>Accurate gazetted fares & Pink Pass exemptions</span>
              </div>
              <div className="flex items-start gap-2.5 text-xs text-[#FFFEFA]/90">
                <CheckCircle2 size={16} className="text-[#64836D] shrink-0 mt-0.5" />
                <span>Real-time disruption alerts & suburban timetable search</span>
              </div>
            </div>
          </div>

          {/* Bottom Metros Badge */}
          <div className="relative z-10 pt-6 mt-6 border-t border-[#385B46]">
            <div className="flex items-center justify-between text-[11px] text-[#A3B899]">
              <span>Delhi • Mumbai • Bengaluru • Mathura</span>
              <span className="font-mono text-[#E7B75B]">v1.0.0</span>
            </div>
          </div>
        </div>

        {/* Right Form Panel */}
        <div className="lg:col-span-7 p-6 sm:p-8 flex flex-col justify-between">
          <div>
            {/* Mode Switcher Tabs */}
            <div className="flex items-center p-1 rounded-2xl bg-[#EEECE3] border border-[#D8D4C7] max-w-xs mb-6">
              <button
                type="button"
                onClick={() => {
                  setMode('signin');
                  setLocalError(null);
                  clearError();
                }}
                className={`flex-1 py-1.5 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  mode === 'signin'
                    ? 'bg-[#FFFEFA] text-[#1F231F] shadow-xs ring-1 ring-[#D8D4C7]'
                    : 'text-[#52544D] hover:text-[#1F231F]'
                }`}
              >
                {t('authSignIn')}
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode('signup');
                  setLocalError(null);
                  clearError();
                }}
                className={`flex-1 py-1.5 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  mode === 'signup'
                    ? 'bg-[#FFFEFA] text-[#1F231F] shadow-xs ring-1 ring-[#D8D4C7]'
                    : 'text-[#52544D] hover:text-[#1F231F]'
                }`}
              >
                {t('authSignUp')}
              </button>
            </div>

            {/* Form Heading */}
            <div className="mb-6 text-left">
              <h3 className="text-xl font-heading font-extrabold text-[#1F231F] tracking-tight">
                {mode === 'signin' ? t('authWelcomeBack') : t('authCreateHeading')}
              </h3>
              <p className="text-xs text-[#52544D] mt-1 font-medium leading-relaxed">
                {mode === 'signin' ? t('authSignInSub') : t('authCreateSub')}
              </p>
            </div>

            {/* Error or Success Feedback Banner */}
            {(localError || authError) && (
              <div className="flex items-start gap-2.5 p-3.5 mb-5 rounded-2xl bg-[#FEF2F2] border border-[#FECACA] text-[#991B1B] text-xs font-semibold leading-snug animate-in fade-in">
                <AlertCircle size={16} className="shrink-0 mt-0.5 text-[#BD4F44]" />
                <span className="flex-1">{localError || authError}</span>
              </div>
            )}

            {successMessage && (
              <div className="flex items-center gap-2.5 p-3.5 mb-5 rounded-2xl bg-[#F0FDF4] border border-[#BBF7D0] text-[#166534] text-xs font-semibold leading-snug animate-in fade-in">
                <CheckCircle2 size={16} className="shrink-0 text-[#16A34A]" />
                <span>{successMessage}</span>
              </div>
            )}

            {/* Auth Form */}
            <form onSubmit={handleSubmit} className="space-y-4 text-left">
              {/* Full Name field (Sign Up only) */}
              {mode === 'signup' && (
                <div>
                  <label className="block text-xs font-bold text-[#1F231F] mb-1.5">
                    {t('authFullName')}
                  </label>
                  <div className="relative flex items-center">
                    <User size={16} className="absolute left-3.5 text-[#77776F] pointer-events-none stroke-[2.2]" />
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g. Arjun Sharma"
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#4E7C5F] focus:ring-2 focus:ring-[#4E7C5F]/20 text-xs text-[#1F231F] font-medium outline-none transition-all placeholder:text-[#9A998E]"
                    />
                  </div>
                </div>
              )}

              {/* Email field */}
              <div>
                <label className="block text-xs font-bold text-[#1F231F] mb-1.5">
                  {t('authEmail')}
                </label>
                <div className="relative flex items-center">
                  <Mail size={16} className="absolute left-3.5 text-[#77776F] pointer-events-none stroke-[2.2]" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="commuter@raahi.in"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#4E7C5F] focus:ring-2 focus:ring-[#4E7C5F]/20 text-xs text-[#1F231F] font-medium outline-none transition-all placeholder:text-[#9A998E]"
                  />
                </div>
              </div>

              {/* Password field */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-[#1F231F]">
                    {t('authPassword')}
                  </label>
                  {mode === 'signin' && (
                    <button
                      type="button"
                      onClick={() => {
                        setForgotEmail(email);
                        setShowForgotModal(true);
                      }}
                      className="text-[11px] font-bold text-[#253D30] hover:text-[#4E7C5F] hover:underline cursor-pointer"
                    >
                      {t('authForgotPassword')}
                    </button>
                  )}
                </div>
                <div className="relative flex items-center">
                  <Lock size={16} className="absolute left-3.5 text-[#77776F] pointer-events-none stroke-[2.2]" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={mode === 'signup' ? 'Min. 8 chars with letters & numbers' : '••••••••'}
                    className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#4E7C5F] focus:ring-2 focus:ring-[#4E7C5F]/20 text-xs text-[#1F231F] font-medium outline-none transition-all placeholder:text-[#9A998E]"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-3 text-[#77776F] hover:text-[#1F231F] cursor-pointer"
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>

                {/* Password Strength Indicator (Sign Up only) */}
                {mode === 'signup' && password.length > 0 && (
                  <div className="mt-2 space-y-1">
                    <div className="flex gap-1 h-1.5 w-full">
                      <div className={`flex-1 rounded-full ${passStrength >= 1 ? 'bg-[#BD4F44]' : 'bg-[#EEECE3]'}`} />
                      <div className={`flex-1 rounded-full ${passStrength >= 3 ? 'bg-[#E7B75B]' : 'bg-[#EEECE3]'}`} />
                      <div className={`flex-1 rounded-full ${passStrength >= 4 ? 'bg-[#64836D]' : 'bg-[#EEECE3]'}`} />
                      <div className={`flex-1 rounded-full ${passStrength >= 5 ? 'bg-[#304B3C]' : 'bg-[#EEECE3]'}`} />
                    </div>
                    <p className="text-[10px] text-[#77776F]">
                      {passStrength < 3
                        ? 'Weak password. Add numbers and capital letters.'
                        : passStrength < 5
                        ? 'Good password strength.'
                        : 'Strong and resilient password!'}
                    </p>
                  </div>
                )}
              </div>

              {/* Confirm Password (Sign Up only) */}
              {mode === 'signup' && (
                <div>
                  <label className="block text-xs font-bold text-[#1F231F] mb-1.5">
                    {t('authConfirmPassword')}
                  </label>
                  <div className="relative flex items-center">
                    <KeyRound size={16} className="absolute left-3.5 text-[#77776F] pointer-events-none stroke-[2.2]" />
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Repeat password identically"
                      className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-[#FFFEFA] border border-[#D8D4C7] focus:border-[#4E7C5F] focus:ring-2 focus:ring-[#4E7C5F]/20 text-xs text-[#1F231F] font-medium outline-none transition-all placeholder:text-[#9A998E]"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword((prev) => !prev)}
                      className="absolute right-3 text-[#77776F] hover:text-[#1F231F] cursor-pointer"
                      title={showConfirmPassword ? 'Hide password' : 'Show password'}
                    >
                      {showConfirmPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  </div>
                </div>
              )}

              {/* Remember Me Checkbox (Sign In only) */}
              {mode === 'signin' && (
                <div className="flex items-center gap-2 pt-0.5">
                  <input
                    type="checkbox"
                    id="rememberMe"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-[#D8D4C7] text-[#304B3C] focus:ring-[#304B3C] cursor-pointer"
                  />
                  <label htmlFor="rememberMe" className="text-xs text-[#52544D] font-medium cursor-pointer">
                    {t('authRememberMe')}
                  </label>
                </div>
              )}

              {/* Primary Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-2 py-3 px-4 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] active:scale-[0.99] text-[#FFFEFA] text-xs font-extrabold flex items-center justify-center gap-2 shadow-sm hover:shadow-md transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span>{mode === 'signin' ? t('authSignIn') : t('authSignUp')}</span>
                    <ArrowRight size={15} className="stroke-[2.5]" />
                  </>
                )}
              </button>
            </form>

            {/* Quick Demo Commuter One-Click Button */}
            <div className="mt-4 pt-4 border-t border-[#EEECE3] flex flex-col gap-2.5">
              <button
                type="button"
                onClick={handleDemoSignIn}
                disabled={isLoading}
                className="w-full py-2.5 px-3 rounded-xl bg-[#EEECE3] hover:bg-[#E3E0D6] active:scale-[0.99] text-[#253D30] text-xs font-bold flex items-center justify-center gap-2 border border-[#D8D4C7] transition-all cursor-pointer"
              >
                <Sparkles size={14} className="text-[#E7B75B]" />
                <span>{t('authDemoAccount')} (demo@raahi.in)</span>
              </button>
            </div>
          </div>

          {/* Bottom Switcher and Guest Exploration */}
          <div className="pt-6 mt-6 border-t border-[#EEECE3] flex flex-wrap items-center justify-between text-xs text-[#52544D] gap-2">
            <div>
              <span>{mode === 'signin' ? t('authDontHaveAccount') : t('authAlreadyHaveAccount')} </span>
              <button
                type="button"
                onClick={() => {
                  setMode(mode === 'signin' ? 'signup' : 'signin');
                  setLocalError(null);
                  clearError();
                }}
                className="font-extrabold text-[#253D30] hover:underline cursor-pointer"
              >
                {mode === 'signin' ? t('authSignUp') : t('authSignIn')}
              </button>
            </div>

            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="text-xs font-bold text-[#77776F] hover:text-[#1F231F] hover:underline cursor-pointer"
              >
                {t('authGuestExplore')} →
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 bg-[#1F231F]/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-[#FFFEFA] rounded-3xl border border-[#D8D4C7] p-6 sm:p-8 shadow-2xl relative text-left animate-in fade-in zoom-in-95">
            <button
              type="button"
              onClick={() => {
                setShowForgotModal(false);
                setForgotSuccess(null);
                setForgotError(null);
                setDemoToken(null);
              }}
              className="absolute top-4 right-4 p-2 rounded-xl text-[#77776F] hover:text-[#1F231F] hover:bg-[#EEECE3] cursor-pointer"
            >
              <X size={18} />
            </button>

            <div className="w-10 h-10 rounded-2xl bg-[#EEECE3] text-[#253D30] flex items-center justify-center mb-4">
              <KeyRound size={20} className="stroke-[2.2]" />
            </div>

            <h3 className="text-lg font-heading font-extrabold text-[#1F231F]">
              {demoToken ? 'Reset Your Password' : t('authForgotPassword')}
            </h3>
            <p className="text-xs text-[#52544D] mt-1 mb-5">
              {demoToken
                ? 'Enter your verification token and your new strong password.'
                : 'Enter your registered email address to receive password reset instructions.'}
            </p>

            {forgotError && (
              <div className="p-3 mb-4 rounded-xl bg-[#FEF2F2] border border-[#FECACA] text-[#991B1B] text-xs font-semibold">
                {forgotError}
              </div>
            )}

            {forgotSuccess && (
              <div className="p-3 mb-4 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0] text-[#166534] text-xs font-semibold">
                {forgotSuccess}
              </div>
            )}

            {!demoToken ? (
              <form onSubmit={handleForgotPasswordSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-[#1F231F] mb-1.5">
                    {t('authEmail')}
                  </label>
                  <input
                    type="email"
                    required
                    value={forgotEmail}
                    onChange={(e) => setForgotEmail(e.target.value)}
                    placeholder="commuter@raahi.in"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#D8D4C7] focus:border-[#4E7C5F] focus:ring-2 focus:ring-[#4E7C5F]/20 text-xs text-[#1F231F] outline-none"
                  />
                </div>

                <button
                  type="submit"
                  disabled={forgotLoading}
                  className="w-full py-2.5 px-4 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-[#FFFEFA] text-xs font-extrabold flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
                >
                  {forgotLoading ? <Loader2 size={15} className="animate-spin" /> : 'Send Reset Instructions'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleResetPasswordSubmit} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-bold text-[#1F231F] mb-1">
                    Verification Token
                  </label>
                  <input
                    type="text"
                    required
                    value={resetToken}
                    onChange={(e) => setResetToken(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-[#D8D4C7] text-xs font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#1F231F] mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min. 8 characters"
                    className="w-full px-3.5 py-2 rounded-xl border border-[#D8D4C7] text-xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#1F231F] mb-1">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    required
                    value={resetConfirmPass}
                    onChange={(e) => setResetConfirmPass(e.target.value)}
                    placeholder="Re-enter new password"
                    className="w-full px-3.5 py-2 rounded-xl border border-[#D8D4C7] text-xs"
                  />
                </div>

                <button
                  type="submit"
                  disabled={resetLoading}
                  className="w-full py-2.5 px-4 rounded-xl bg-[#253D30] hover:bg-[#1A2E24] text-[#FFFEFA] text-xs font-extrabold flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
                >
                  {resetLoading ? <Loader2 size={15} className="animate-spin" /> : 'Update Password & Sign In'}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

