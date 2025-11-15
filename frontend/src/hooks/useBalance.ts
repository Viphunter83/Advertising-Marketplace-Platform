/**
 * hooks/useBalance.ts
 * Hook для работы с балансом
 */
import { useQuery } from '@tanstack/react-query';
import { paymentsApi } from '@/lib/api/payments.api';

export function useBalance() {
  return useQuery({
    queryKey: ['balance'],
    queryFn: async () => {
      return await paymentsApi.getBalance();
    },
    staleTime: 30 * 1000, // 30 seconds
  });
}

