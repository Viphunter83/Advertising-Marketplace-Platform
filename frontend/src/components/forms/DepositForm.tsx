/**
 * components/forms/DepositForm.tsx
 * Форма пополнения баланса
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
import { Info } from 'lucide-react';
import toast from 'react-hot-toast';
import { formatCurrency } from '@/lib/utils';

const depositSchema = z.object({
  amount: z.number().min(100, 'Minimum deposit is ₽100').max(500000, 'Maximum deposit is ₽500,000'),
  payment_method: z.enum(['yoomoney', 'sbp']),
});

type DepositFormData = z.infer<typeof depositSchema>;

export function DepositForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = React.useState(false);
  
  const form = useForm<DepositFormData>({
    resolver: zodResolver(depositSchema),
    defaultValues: {
      amount: 100,
      payment_method: 'yoomoney',
    },
  });
  
  const amount = form.watch('amount');
  const paymentMethod = form.watch('payment_method');
  
  // Комиссия (пример: 2% для YooMoney, 0% для SBP)
  const commission = paymentMethod === 'yoomoney' ? amount * 0.02 : 0;
  const totalAmount = amount + commission;
  
  const onSubmit = async (data: DepositFormData) => {
    setIsLoading(true);
    
    try {
      const response = await paymentsApi.createDeposit({
        amount: data.amount,
        payment_method: data.payment_method,
      });
      
      if (response.payment_url) {
        toast.success('Redirecting to payment...');
        // Редирект на платежный сервис
        window.location.href = response.payment_url;
      } else {
        toast.success('Deposit request created. Please check your email for payment instructions.');
        router.push('/seller/balance');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create deposit. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Deposit Funds</CardTitle>
        <CardDescription>
          Add funds to your account to create advertising campaigns
        </CardDescription>
      </CardHeader>
      <CardContent>
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
                      max={500000}
                      {...field}
                      onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    />
                  </FormControl>
                  <FormDescription>
                    Minimum: ₽100, Maximum: ₽500,000
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
                      <SelectItem value="yoomoney">YooMoney (2% commission)</SelectItem>
                      <SelectItem value="sbp">SBP (Fast Payment System)</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {/* Summary */}
            <div className="p-4 bg-gray-50 rounded-lg space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Deposit Amount:</span>
                <span className="font-semibold">{formatCurrency(amount)}</span>
              </div>
              {commission > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Commission ({paymentMethod === 'yoomoney' ? '2%' : '0%'}):</span>
                  <span className="font-semibold">{formatCurrency(commission)}</span>
                </div>
              )}
              <div className="flex justify-between text-lg font-bold pt-2 border-t">
                <span>Total to Pay:</span>
                <span>{formatCurrency(totalAmount)}</span>
              </div>
            </div>
            
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                After clicking "Proceed to Payment", you will be redirected to the payment service to complete the transaction.
              </AlertDescription>
            </Alert>
            
            <div className="flex gap-4">
              <Button type="submit" disabled={isLoading} className="flex-1">
                {isLoading ? 'Processing...' : 'Proceed to Payment'}
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

