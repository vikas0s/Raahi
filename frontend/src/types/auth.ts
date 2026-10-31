export interface User {
  id: string;
  name: string;
  email: string;
  role?: string;
  avatar_url?: string | null;
  email_verified?: boolean;
  status?: string;
  created_at: string;
  last_login_at?: string | null;
}

export interface AuthResponse {
  user: User;
  token: string;
  token_type: string;
  message: string;
}

export type AuthMode = 'signin' | 'signup' | 'forgot' | 'reset';

