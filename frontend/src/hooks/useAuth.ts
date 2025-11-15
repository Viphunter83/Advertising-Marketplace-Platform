/**
 * hooks/useAuth.ts
 * Hook для работы с аутентификацией
 */
import { useAuthStore } from '@/lib/store/auth.store';

export function useAuth() {
  const store = useAuthStore();
  
  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    logout: store.logout,
    setUser: store.setUser,
    isUserType: store.isUserType,
    canAccessRoute: store.canAccessRoute,
  };
}

