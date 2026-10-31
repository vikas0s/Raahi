import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { User, AuthResponse } from '../types/auth';
import {
  apiSignIn,
  apiSignUp,
  apiSignOut,
  apiGetCurrentUser
} from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  signIn: (email: string, password: string, rememberMe?: boolean) => Promise<AuthResponse>;
  signUp: (name: string, email: string, password: string, confirmPassword: string) => Promise<AuthResponse>;
  signOut: () => Promise<void>;
  clearError: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const cached = localStorage.getItem('raahi_user_profile');
    if (cached) {
      try {
        return JSON.parse(cached);
      } catch {
        return null;
      }
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize and verify session on load
  const refreshUser = useCallback(async () => {
    try {
      const activeUser = await apiGetCurrentUser();
      if (activeUser) {
        setUser(activeUser);
        localStorage.setItem('raahi_user_profile', JSON.stringify(activeUser));
      } else {
        setUser(null);
        localStorage.removeItem('raahi_user_profile');
      }
    } catch {
      setUser(null);
      localStorage.removeItem('raahi_user_profile');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const signIn = async (email: string, password: string, rememberMe: boolean = true): Promise<AuthResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiSignIn(email, password, rememberMe);
      setUser(res.user);
      localStorage.setItem('raahi_user_profile', JSON.stringify(res.user));
      return res;
    } catch (err: any) {
      const msg = err.message || 'Invalid email or password';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const signUp = async (
    name: string,
    email: string,
    password: string,
    confirmPassword: string
  ): Promise<AuthResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiSignUp(name, email, password, confirmPassword);
      setUser(res.user);
      localStorage.setItem('raahi_user_profile', JSON.stringify(res.user));
      return res;
    } catch (err: any) {
      const msg = err.message || 'Failed to create account';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async (): Promise<void> => {
    setIsLoading(true);
    try {
      await apiSignOut();
    } finally {
      setUser(null);
      localStorage.removeItem('raahi_user_profile');
      setIsLoading(false);
    }
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        signIn,
        signUp,
        signOut,
        clearError,
        refreshUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

