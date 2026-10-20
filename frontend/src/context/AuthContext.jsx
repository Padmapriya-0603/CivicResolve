import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

// BroadcastChannel for instant cross-tab/window synchronization
const authChannel = typeof window !== 'undefined' && 'BroadcastChannel' in window
  ? new BroadcastChannel('grievance_auth_sync')
  : null;

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('grievance_token'));
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem('grievance_token');
    setToken(null);
    setUser(null);
    if (authChannel) {
      authChannel.postMessage({ type: 'LOGOUT' });
    }
  }, []);

  // Initialize auth on mount
  useEffect(() => {
    async function initAuth() {
      const storedToken = localStorage.getItem('grievance_token');
      if (storedToken) {
        try {
          const userData = await api.getMe();
          setUser(userData);
          setToken(storedToken);
        } catch (err) {
          console.error('Session expired or invalid', err);
          logout();
        } finally {
          setLoading(false);
        }
      } else {
        setUser(null);
        setToken(null);
        setLoading(false);
      }
    }
    initAuth();
  }, [logout]);

  // Multi-window and multi-tab synchronization listeners
  useEffect(() => {
    // 1. Cross-tab storage event: fires in all other tabs/windows when localStorage is modified
    const handleStorageChange = async (e) => {
      if (!e.key || e.key === 'grievance_token') {
        const currentStored = localStorage.getItem('grievance_token');
        if (!currentStored) {
          // Logged out in another tab/window
          setToken(null);
          setUser(null);
        } else if (currentStored !== token) {
          // Logged in as a different user in another tab/window
          setToken(currentStored);
          try {
            const userData = await api.getMe();
            setUser(userData);
          } catch {
            logout();
          }
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // 2. BroadcastChannel: instant explicit notification between tabs/windows
    if (authChannel) {
      authChannel.onmessage = (event) => {
        if (event.data?.type === 'LOGOUT') {
          setToken(null);
          setUser(null);
        } else if (event.data?.type === 'LOGIN') {
          setToken(event.data.token);
          setUser(event.data.user);
        }
      };
    }

    // 3. Tab focus / visibility change: verify session is still valid when window regains focus
    const handleSyncOnFocus = async () => {
      const currentStored = localStorage.getItem('grievance_token');
      if (!currentStored && user) {
        // Token was cleared in another window while this window was in background
        setToken(null);
        setUser(null);
      } else if (currentStored && currentStored !== token) {
        // Account switched in another window
        setToken(currentStored);
        try {
          const userData = await api.getMe();
          setUser(userData);
        } catch {
          logout();
        }
      }
    };

    document.addEventListener('visibilitychange', handleSyncOnFocus);
    window.addEventListener('focus', handleSyncOnFocus);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      document.removeEventListener('visibilitychange', handleSyncOnFocus);
      window.removeEventListener('focus', handleSyncOnFocus);
      if (authChannel) {
        authChannel.onmessage = null;
      }
    };
  }, [token, user]);

  const login = async (email, password) => {
    const res = await api.login({ email, password });
    localStorage.setItem('grievance_token', res.access_token);
    setToken(res.access_token);
    const userData = {
      id: res.user_id,
      name: res.name,
      email: res.email,
      role: res.role,
      department_id: res.department_id,
      department_name: res.department_name,
    };
    setUser(userData);
    if (authChannel) {
      authChannel.postMessage({ type: 'LOGIN', token: res.access_token, user: userData });
    }
    return userData;
  };

  const register = async (name, email, password, phone) => {
    const res = await api.register({ name, email, password, phone });
    localStorage.setItem('grievance_token', res.access_token);
    setToken(res.access_token);
    const userData = {
      id: res.user_id,
      name: res.name,
      email: res.email,
      role: res.role,
      department_id: res.department_id,
      department_name: res.department_name,
    };
    setUser(userData);
    if (authChannel) {
      authChannel.postMessage({ type: 'LOGIN', token: res.access_token, user: userData });
    }
    return userData;
  };

  const refreshUser = async () => {
    try {
      const updated = await api.getMe();
      setUser(updated);
    } catch (err) {
      console.error('Failed to refresh user', err);
      logout();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        role: user?.role || null,
        login,
        register,
        logout,
        refreshUser,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
