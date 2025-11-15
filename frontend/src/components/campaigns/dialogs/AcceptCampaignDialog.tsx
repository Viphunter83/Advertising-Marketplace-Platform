/**
 * components/campaigns/dialogs/AcceptCampaignDialog.tsx
 * Диалог принятия заявки
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
} from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { campaignsApi } from '@/lib/api/campaigns.api';
import toast from 'react-hot-toast';

const acceptSchema = z.object({
  owner_notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
});

type AcceptFormData = z.infer<typeof acceptSchema>;

interface AcceptCampaignDialogProps {
  campaignId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function AcceptCampaignDialog({
  campaignId,
  open,
  onOpenChange,
  onSuccess,
}: AcceptCampaignDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  
  const form = useForm<AcceptFormData>({
    resolver: zodResolver(acceptSchema),
    defaultValues: {
      owner_notes: '',
    },
  });
  
  const onSubmit = async (data: AcceptFormData) => {
    setIsLoading(true);
    
    try {
      await campaignsApi.acceptCampaign(campaignId, data.owner_notes);
      toast.success('Campaign accepted successfully!');
      form.reset();
      onOpenChange(false);
      onSuccess?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to accept campaign. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Accept Campaign</DialogTitle>
          <DialogDescription>
            Accept this campaign request. The seller's funds will be held in escrow.
          </DialogDescription>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="owner_notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Add any notes for the seller..."
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
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
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Accepting...' : 'Accept Campaign'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

