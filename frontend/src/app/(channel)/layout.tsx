'use client';

import { Header } from '@/components/layout/Header';
import { useAuthStore } from '@/lib/store/auth.store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ChannelLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Проверяем токены в localStorage для первоначальной загрузки
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token && !isAuthenticated) {
        // Если есть токен, но состояние еще не обновлено, пытаемся загрузить user
        return;
      }
    }

    if (!isAuthenticated || !user) {
      router.replace('/login');
      return;
    }

    if (user.user_type !== 'channel_owner') {
      const redirectUrl = user.user_type === 'seller' 
        ? '/seller/dashboard' 
        : user.user_type === 'admin'
        ? '/admin/dashboard'
        : '/';
      router.replace(redirectUrl);
      return;
    }
  }, [isAuthenticated, user, router]);

  // Получаем токен один раз
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  // Показываем loading если есть токен, но состояние еще не загружено
  if (token && (!isAuthenticated || !user)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Если нет токена и не авторизован - показываем null (будет редирект в useEffect)
  if (!token && (!isAuthenticated || !user)) {
    return null; // Будет редирект на /login
  }

  // Проверяем тип пользователя
  if (user && user.user_type !== 'channel_owner') {
    return null; // Будет редирект в useEffect
  }

  // Если все проверки пройдены, но нет user - показываем loading (fallback)
  if (!user || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main>{children}</main>
    </div>
  );
}

