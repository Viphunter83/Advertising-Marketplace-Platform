/**
 * components/campaigns/dialogs/SubmitPlacementDialog.tsx
 * Диалог отправки подтверждения размещения
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
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { campaignsApi } from '@/lib/api/campaigns.api';
import toast from 'react-hot-toast';

const submitSchema = z.object({
  placement_proof_url: z.string().url('Invalid URL').min(1, 'Proof URL is required'),
  placement_proof_type: z.enum(['screenshot', 'post_link', 'other']),
  owner_notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
});

type SubmitFormData = z.infer<typeof submitSchema>;

interface SubmitPlacementDialogProps {
  campaignId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function SubmitPlacementDialog({
  campaignId,
  open,
  onOpenChange,
  onSuccess,
}: SubmitPlacementDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  
  const form = useForm<SubmitFormData>({
    resolver: zodResolver(submitSchema),
    defaultValues: {
      placement_proof_url: '',
      placement_proof_type: 'screenshot',
      owner_notes: '',
    },
  });
  
  const onSubmit = async (data: SubmitFormData) => {
    setIsLoading(true);
    
    try {
      await campaignsApi.submitCampaign(
        campaignId,
        data.placement_proof_url,
        data.placement_proof_type
      );
      toast.success('Placement submitted successfully!');
      form.reset();
      onOpenChange(false);
      onSuccess?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to submit placement. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Submit Placement Proof</DialogTitle>
          <DialogDescription>
            Submit proof that you have placed the advertisement in your channel.
          </DialogDescription>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="placement_proof_type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Proof Type *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select proof type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="screenshot">Screenshot</SelectItem>
                      <SelectItem value="post_link">Post Link</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="placement_proof_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Proof URL *</FormLabel>
                  <FormControl>
                    <Input
                      type="url"
                      placeholder="https://example.com/screenshot.png or https://vk.com/wall..."
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    URL to screenshot, post link, or other proof of placement
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="owner_notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Add any additional notes..."
                      className="min-h-[80px]"
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
                {isLoading ? 'Submitting...' : 'Submit Placement'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

