/**
 * hooks/useDisputes.ts
 * Hook для работы со спорами
 */
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/lib/api/admin.api';
import { Dispute } from '@/lib/types';

export function useDisputes(status?: string) {
  return useQuery({
    queryKey: ['disputes', status],
    queryFn: async (): Promise<Dispute[]> => {
      return await adminApi.getDisputes(status);
    },
    staleTime: 30 * 1000, // 30 seconds
  });
}

