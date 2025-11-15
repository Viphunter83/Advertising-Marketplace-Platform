/**
 * hooks/useTransactions.ts
 * Hook для работы с транзакциями
 */
import { useQuery } from '@tanstack/react-query';
import { paymentsApi } from '@/lib/api/payments.api';
import { Transaction } from '@/lib/types';

export function useTransactions() {
  return useQuery({
    queryKey: ['transactions'],
    queryFn: async (): Promise<Transaction[]> => {
      return await paymentsApi.getTransactionHistory();
    },
    staleTime: 60 * 1000, // 1 minute
  });
}

