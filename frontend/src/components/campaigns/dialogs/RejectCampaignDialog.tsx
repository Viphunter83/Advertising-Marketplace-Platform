/**
 * components/campaigns/dialogs/RejectCampaignDialog.tsx
 * Диалог отклонения заявки
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle } from 'lucide-react';
import { campaignsApi } from '@/lib/api/campaigns.api';
import toast from 'react-hot-toast';

const rejectSchema = z.object({
  reason: z.string().min(10, 'Reason must be at least 10 characters').max(500, 'Reason must be less than 500 characters'),
});

type RejectFormData = z.infer<typeof rejectSchema>;

interface RejectCampaignDialogProps {
  campaignId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function RejectCampaignDialog({
  campaignId,
  open,
  onOpenChange,
  onSuccess,
}: RejectCampaignDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  
  const form = useForm<RejectFormData>({
    resolver: zodResolver(rejectSchema),
    defaultValues: {
      reason: '',
    },
  });
  
  const onSubmit = async (data: RejectFormData) => {
    setIsLoading(true);
    
    try {
      await campaignsApi.rejectCampaign(campaignId, data.reason);
      toast.success('Campaign rejected. Funds will be returned to the seller.');
      form.reset();
      onOpenChange(false);
      onSuccess?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to reject campaign. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Reject Campaign</DialogTitle>
          <DialogDescription>
            Reject this campaign request. The seller's funds will be returned.
          </DialogDescription>
        </DialogHeader>
        
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Rejecting this campaign will return the funds to the seller. This action cannot be undone.
          </AlertDescription>
        </Alert>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="reason"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Reason for Rejection *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Please provide a reason for rejecting this campaign..."
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    This reason will be shared with the seller.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" variant="destructive" disabled={isLoading}>
                {isLoading ? 'Rejecting...' : 'Reject Campaign'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

