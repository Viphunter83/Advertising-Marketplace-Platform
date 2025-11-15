/**
 * hooks/useReviews.ts
 * Hook для работы с отзывами
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reviewsApi, CreateReviewPayload } from '@/lib/api/reviews.api';
import { Review } from '@/lib/types';

export function useCampaignReviews(campaignId: string) {
  return useQuery({
    queryKey: ['reviews', 'campaign', campaignId],
    queryFn: async (): Promise<Review[]> => {
      return await reviewsApi.getCampaignReviews(campaignId);
    },
    enabled: !!campaignId,
  });
}

export function useCreateReview() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (payload: CreateReviewPayload) => {
      return await reviewsApi.createReview(payload);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['reviews', 'campaign', variables.campaign_id] });
    },
  });
}

