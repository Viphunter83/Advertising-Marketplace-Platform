/**
 * components/forms/ReviewForm.tsx
 * Форма создания отзыва
 */
'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { reviewSchema } from '@/lib/validators';
import * as z from 'zod';
import { useCreateReview } from '@/hooks/useReviews';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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
import { Star } from 'lucide-react';
import toast from 'react-hot-toast';

type ReviewFormData = z.infer<typeof reviewSchema>;

interface ReviewFormProps {
  campaignId: string;
  onSuccess?: () => void;
}

export function ReviewForm({ campaignId, onSuccess }: ReviewFormProps) {
  const createReview = useCreateReview();
  
  const form = useForm<ReviewFormData>({
    resolver: zodResolver(reviewSchema),
    defaultValues: {
      rating: 5,
      title: '',
      comment: '',
    },
  });
  
  const rating = form.watch('rating');
  
  const onSubmit = async (data: ReviewFormData) => {
    try {
      await createReview.mutateAsync({
        campaign_id: campaignId,
        ...data,
      });
      
      toast.success('Review submitted successfully!');
      form.reset();
      onSuccess?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to submit review. Please try again.';
      toast.error(errorMessage);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Write a Review</CardTitle>
        <CardDescription>Share your experience with this campaign</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="rating"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Rating *</FormLabel>
                  <FormControl>
                    <div className="flex items-center gap-2">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          type="button"
                          onClick={() => field.onChange(star)}
                          className="focus:outline-none"
                        >
                          <Star
                            className={`h-8 w-8 ${
                              star <= rating
                                ? 'fill-yellow-400 text-yellow-400'
                                : 'text-gray-300'
                            }`}
                          />
                        </button>
                      ))}
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title (Optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="Review title..." {...field} />
                  </FormControl>
                  <FormDescription>
                    {(field.value || '').length}/100 characters
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="comment"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Comment *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Write your review..."
                      className="min-h-[120px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    {field.value.length}/1000 characters
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <Button type="submit" disabled={createReview.isPending}>
              {createReview.isPending ? 'Submitting...' : 'Submit Review'}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

