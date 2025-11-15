/**
 * components/forms/WithdrawalForm.tsx
 * Форма вывода средств
 */
'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { paymentsApi } from '@/lib/api/payments.api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle, Info } from 'lucide-react';
import toast from 'react-hot-toast';
import { formatCurrency } from '@/lib/utils';

const withdrawalSchema = z.object({
  amount: z.number().min(100, 'Minimum withdrawal is ₽100'),
  payment_method: z.enum(['yoomoney', 'sbp', 'card_mir', 'qiwi']),
  account_number: z.string().min(1, 'Account number is required'),
});

type WithdrawalFormData = z.infer<typeof withdrawalSchema>;

interface WithdrawalFormProps {
  availableBalance: number;
}

export function WithdrawalForm({ availableBalance }: WithdrawalFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = React.useState(false);
  
  const form = useForm<WithdrawalFormData>({
    resolver: zodResolver(withdrawalSchema),
    defaultValues: {
      amount: 100,
      payment_method: 'yoomoney',
      account_number: '',
    },
  });
  
  const amount = form.watch('amount');
  const paymentMethod = form.watch('payment_method');
  
  // Комиссия (пример: 1% для всех методов)
  const commission = amount * 0.01;
  const netAmount = amount - commission;
  
  // Валидация максимальной суммы
  const maxAmount = availableBalance;
  
  React.useEffect(() => {
    if (amount > maxAmount) {
      form.setValue('amount', maxAmount);
    }
  }, [maxAmount, form]);
  
  const onSubmit = async (data: WithdrawalFormData) => {
    if (data.amount > availableBalance) {
      toast.error('Insufficient balance');
      return;
    }
    
    setIsLoading(true);
    
    try {
      await paymentsApi.createWithdrawal({
        amount: data.amount,
        payment_method: data.payment_method,
        account_number: data.account_number,
      });
      
      toast.success('Withdrawal request submitted. Pending admin approval.');
      router.push('/channel/earnings');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create withdrawal. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  const getAccountPlaceholder = () => {
    switch (paymentMethod) {
      case 'yoomoney':
        return 'YooMoney wallet number';
      case 'sbp':
        return 'Phone number or card number';
      case 'card_mir':
        return 'Card number (16 digits)';
      case 'qiwi':
        return 'QIWI wallet number';
      default:
        return 'Account number';
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Withdraw Funds</CardTitle>
        <CardDescription>
          Request withdrawal of your earnings
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Alert className="mb-6">
          <Info className="h-4 w-4" />
          <AlertDescription>
            Available Balance: <strong>{formatCurrency(availableBalance)}</strong>
          </AlertDescription>
        </Alert>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="amount"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Amount (RUB) *</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="100"
                      min={100}
                      max={maxAmount}
                      {...field}
                      onChange={(e) => {
                        const value = parseFloat(e.target.value) || 0;
                        field.onChange(Math.min(value, maxAmount));
                      }}
                    />
                  </FormControl>
                  <FormDescription>
                    Minimum: ₽100, Maximum: {formatCurrency(maxAmount)}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="payment_method"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Payment Method *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="yoomoney">YooMoney</SelectItem>
                      <SelectItem value="sbp">SBP (Fast Payment System)</SelectItem>
                      <SelectItem value="card_mir">Bank Card (MIR)</SelectItem>
                      <SelectItem value="qiwi">QIWI</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="account_number"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Account Number *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder={getAccountPlaceholder()}
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    {paymentMethod === 'card_mir' && 'Enter 16-digit card number'}
                    {paymentMethod === 'sbp' && 'Enter phone number or card number linked to SBP'}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {/* Summary */}
            <div className="p-4 bg-gray-50 rounded-lg space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Withdrawal Amount:</span>
                <span className="font-semibold">{formatCurrency(amount)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Commission (1%):</span>
                <span className="font-semibold">{formatCurrency(commission)}</span>
              </div>
              <div className="flex justify-between text-lg font-bold pt-2 border-t">
                <span>You Will Receive:</span>
                <span className="text-green-600">{formatCurrency(netAmount)}</span>
              </div>
            </div>
            
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Your withdrawal request will be reviewed by an administrator. Processing time: 1-3 business days.
              </AlertDescription>
            </Alert>
            
            <div className="flex gap-4">
              <Button type="submit" disabled={isLoading || amount > availableBalance} className="flex-1">
                {isLoading ? 'Submitting...' : 'Submit Withdrawal Request'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={isLoading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

