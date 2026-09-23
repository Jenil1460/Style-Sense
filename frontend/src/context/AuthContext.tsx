import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import { api } from '../lib/api';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_verified: boolean;
  avatar_url?: string;
  gender?: string;
  height?: number;
  weight?: number;
  body_type?: string;
  preferred_styles?: string[];
  favorite_colors?: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
  updateUser: (userData: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = Cookies.get('access_token');
      if (token) {
        try {
          // Verify token and fetch latest profile
          const response = await api.get('/profile/');
          setUser(response.data);
        } catch (error) {
          console.error("Token invalid or expired", error);
          Cookies.remove('access_token');
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  const login = (token: string, userData: User) => {
    Cookies.set('access_token', token, { expires: 1 }); // 1 day
    setUser(userData);
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (e) {
      console.error(e);
    }
    Cookies.remove('access_token');
    setUser(null);
  };

  const updateUser = (userData: User) => {
    setUser(userData);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
