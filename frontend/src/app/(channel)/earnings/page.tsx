'use client';

import React from 'react';
import Link from 'next/link';
import { useBalance } from '@/hooks/useBalance';
import { useTransactions } from '@/hooks/useTransactions';
import { TransactionTable } from '@/components/payments/TransactionTable';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/lib/utils';
import { DollarSign, TrendingUp, Clock, Download, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api/client';

export default function EarningsPage() {
  const { data: balanceData, isLoading: balanceLoading } = useBalance();
  const { data: transactions, isLoading: transactionsLoading } = useTransactions();
  
  // Получаем статистику заработка
  const { data: earningsStats } = useQuery({
    queryKey: ['earnings', 'stats'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/channels/profile');
        return {
          total_earned: response.data.total_earned || 0,
          pending_withdrawals: 0, // TODO: получить из API
        };
      } catch {
        return { total_earned: 0, pending_withdrawals: 0 };
      }
    },
  });
  
  const availableBalance = balanceData?.balance || 0;
  const totalEarned = earningsStats?.total_earned || 0;
  const pendingWithdrawals = earningsStats?.pending_withdrawals || 0;
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Earnings</h1>
        <Button asChild>
          <Link href="/channel/earnings/withdraw">
            <Download className="mr-2 h-4 w-4" />
            Withdraw Funds
          </Link>
        </Button>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <TrendingUp className="h-4 w-4" />
              Total Earned
            </CardTitle>
          </CardHeader>
          <CardContent>
            {balanceLoading ? (
              <Loader2 className="h-6 w-6 animate-spin" />
            ) : (
              <div className="text-2xl font-bold">{formatCurrency(totalEarned)}</div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <DollarSign className="h-4 w-4" />
              Available Balance
            </CardTitle>
          </CardHeader>
          <CardContent>
            {balanceLoading ? (
              <Loader2 className="h-6 w-6 animate-spin" />
            ) : (
              <div className="text-2xl font-bold">{formatCurrency(availableBalance)}</div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <Clock className="h-4 w-4" />
              Pending Withdrawals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(pendingWithdrawals)}</div>
          </CardContent>
        </Card>
      </div>
      
      {/* Transaction History */}
      <Card>
        <CardHeader>
          <CardTitle>Transaction History</CardTitle>
          <CardDescription>All your earnings and withdrawals</CardDescription>
        </CardHeader>
        <CardContent>
          <TransactionTable 
            transactions={transactions || []} 
            isLoading={transactionsLoading}
          />
        </CardContent>
      </Card>
    </div>
  );
}

