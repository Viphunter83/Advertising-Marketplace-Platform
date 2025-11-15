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
    if (!isAuthenticated || !user) {
      router.push('/login');
      return;
    }

    if (user.user_type !== 'channel_owner') {
      router.push(`/${user.user_type}/dashboard`);
      return;
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || !user || user.user_type !== 'channel_owner') {
    return null;
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main>{children}</main>
    </div>
  );
}

