'use client';

import React from 'react';
import Link from 'next/link';
import { useBalance } from '@/hooks/useBalance';
import { useTransactions } from '@/hooks/useTransactions';
import { TransactionTable } from '@/components/payments/TransactionTable';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/lib/utils';
import { DollarSign, Plus, Loader2 } from 'lucide-react';

export default function BalancePage() {
  const { data: balanceData, isLoading: balanceLoading } = useBalance();
  const { data: transactions, isLoading: transactionsLoading } = useTransactions();
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Balance</h1>
        <Button asChild>
          <Link href="/seller/balance/deposit">
            <Plus className="mr-2 h-4 w-4" />
            Deposit Funds
          </Link>
        </Button>
      </div>
      
      {/* Balance Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Current Balance
          </CardTitle>
          <CardDescription>Available funds for creating campaigns</CardDescription>
        </CardHeader>
        <CardContent>
          {balanceLoading ? (
            <Loader2 className="h-8 w-8 animate-spin" />
          ) : (
            <div className="text-4xl font-bold">
              {formatCurrency(balanceData?.balance || 0)}
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Transaction History */}
      <Card>
        <CardHeader>
          <CardTitle>Transaction History</CardTitle>
          <CardDescription>All your deposits, payments, and refunds</CardDescription>
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

