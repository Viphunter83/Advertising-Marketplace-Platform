/**
 * components/common/AuthInitializer.tsx
 * Компонент для инициализации состояния аутентификации из localStorage
 */
'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/lib/store/auth.store';
import { authApi } from '@/lib/api/auth.api';

export function AuthInitializer() {
  const { setUser, setLoading } = useAuthStore();

  useEffect(() => {
    const initializeAuth = async () => {
      if (typeof window === 'undefined') return;

      const token = localStorage.getItem('access_token');
      if (!token) return;

      // Если есть токен, но нет user в store, загружаем user
      const { user, isAuthenticated } = useAuthStore.getState();
      if (token && !isAuthenticated && !user) {
        setLoading(true);
        try {
          const userData = await authApi.getCurrentUser();
          const refreshToken = localStorage.getItem('refresh_token') || '';
          useAuthStore.getState().login(userData, {
            access_token: token,
            refresh_token: refreshToken,
            token_type: 'bearer',
          });
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          // Если токен невалидный, очищаем
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          useAuthStore.getState().logout();
        } finally {
          setLoading(false);
        }
      }
    };

    initializeAuth();
  }, [setLoading]);

  return null;
}

