'use client';

import React from 'react';
import { useWithdrawals } from '@/hooks/useWithdrawals';
import { WithdrawalTable } from '@/components/admin/WithdrawalTable';
import { Loader2 } from 'lucide-react';

export default function AdminWithdrawalsPage() {
  const { data: withdrawals, isLoading, refetch } = useWithdrawals();
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Withdrawal Requests</h1>
      
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <WithdrawalTable 
          withdrawals={withdrawals || []} 
          isLoading={isLoading}
          onUpdate={refetch}
        />
      )}
    </div>
  );
}

