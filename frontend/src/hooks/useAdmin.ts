/**
 * hooks/useAdmin.ts
 * Hook для админ функций
 */
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/lib/api/admin.api';
import { PlatformStats } from '@/lib/types';

export function usePlatformStats() {
  return useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: async (): Promise<PlatformStats> => {
      return await adminApi.getPlatformStats();
    },
    staleTime: 60 * 1000, // 1 minute
  });
}

