'use client';

import { useBalance } from '@/hooks/useBalance';
import { WithdrawalForm } from '@/components/forms/WithdrawalForm';
import { Loader2 } from 'lucide-react';

export default function WithdrawPage() {
  const { data: balanceData, isLoading } = useBalance();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <WithdrawalForm availableBalance={balanceData?.balance || 0} />
    </div>
  );
}

