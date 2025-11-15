/**
 * components/campaigns/dialogs/ConfirmCampaignDialog.tsx
 * Диалог подтверждения размещения или открытия спора
 */
'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { campaignsApi } from '@/lib/api/campaigns.api';
import { Campaign } from '@/lib/types';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

const confirmSchema = z.object({
  confirmed: z.boolean(),
  reason: z.string().min(10, 'Reason must be at least 10 characters').optional(),
}).refine((data) => {
  if (!data.confirmed) {
    return data.reason && data.reason.length >= 10;
  }
  return true;
}, {
  message: 'Please provide a reason for disputing',
  path: ['reason'],
});

type ConfirmFormData = z.infer<typeof confirmSchema>;

interface ConfirmCampaignDialogProps {
  campaign: Campaign;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function ConfirmCampaignDialog({
  campaign,
  open,
  onOpenChange,
  onSuccess,
}: ConfirmCampaignDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  
  const form = useForm<ConfirmFormData>({
    resolver: zodResolver(confirmSchema),
    defaultValues: {
      confirmed: true,
      reason: '',
    },
  });
  
  const confirmed = form.watch('confirmed');
  
  const onSubmit = async (data: ConfirmFormData) => {
    setIsLoading(true);
    
    try {
      await campaignsApi.confirmCampaign(campaign.id, data.confirmed);
      
      if (data.confirmed) {
        toast.success('Campaign confirmed! Payment will be processed.');
      } else {
        toast.success('Dispute opened. Admin will review your case.');
      }
      
      form.reset();
      onOpenChange(false);
      onSuccess?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to process. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Вычисляем сумму выплаты (бюджет - комиссия)
  const commission = campaign.budget * (campaign.platform_commission_percent / 100);
  const paymentAmount = campaign.budget - commission;
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Confirm Placement</DialogTitle>
          <DialogDescription>
            Review the placement and confirm or open a dispute.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Campaign Budget</div>
            <div className="text-2xl font-bold">{formatCurrency(campaign.budget)}</div>
            <div className="text-sm text-gray-600 mt-2">
              Commission ({campaign.platform_commission_percent}%): {formatCurrency(commission)}
            </div>
            <div className="text-sm font-semibold mt-1">
              Payment to Channel Owner: {formatCurrency(paymentAmount)}
            </div>
          </div>
          
          {campaign.placement_proof_url && (
            <div>
              <div className="text-sm font-semibold mb-2">Placement Proof</div>
              <a
                href={campaign.placement_proof_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                {campaign.placement_proof_url}
              </a>
            </div>
          )}
        </div>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="confirmed"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <RadioGroup
                      onValueChange={(value) => field.onChange(value === 'confirm')}
                      value={field.value ? 'confirm' : 'dispute'}
                    >
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="confirm" id="confirm" />
                        <Label htmlFor="confirm" className="flex items-center gap-2 cursor-pointer">
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                          <span>Confirm placement and release payment</span>
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="dispute" id="dispute" />
                        <Label htmlFor="dispute" className="flex items-center gap-2 cursor-pointer">
                          <AlertTriangle className="h-4 w-4 text-orange-600" />
                          <span>Open a dispute</span>
                        </Label>
                      </div>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {!confirmed && (
              <FormField
                control={form.control}
                name="reason"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reason for Dispute *</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Please describe the issue..."
                        className="min-h-[100px]"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Provide details about why you are disputing this placement.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
            
            {!confirmed && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Opening a dispute will pause payment processing. An admin will review your case.
                </AlertDescription>
              </Alert>
            )}
            
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant={confirmed ? 'default' : 'destructive'}
                disabled={isLoading}
              >
                {isLoading
                  ? 'Processing...'
                  : confirmed
                  ? 'Confirm & Release Payment'
                  : 'Open Dispute'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

