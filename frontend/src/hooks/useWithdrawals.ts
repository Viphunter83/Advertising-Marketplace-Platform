/**
 * hooks/useWithdrawals.ts
 * Hook для работы с выводами
 */
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/lib/api/admin.api';

export interface Withdrawal {
  id: string;
  user_id: string;
  user_email?: string;
  amount: number;
  payment_method: string;
  account_number: string;
  status: 'pending' | 'processing' | 'completed' | 'rejected';
  created_at: string;
  processed_at?: string;
  admin_notes?: string;
}

export function useWithdrawals(status?: string) {
  return useQuery({
    queryKey: ['withdrawals', status],
    queryFn: async (): Promise<Withdrawal[]> => {
      return await adminApi.getWithdrawals(status);
    },
    staleTime: 30 * 1000, // 30 seconds
  });
}

