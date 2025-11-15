/**
 * hooks/useCampaignById.ts
 * Hook для получения заявки по ID
 */
import { useQuery } from '@tanstack/react-query';
import { campaignsApi } from '@/lib/api/campaigns.api';
import { Campaign } from '@/lib/types';

export function useCampaignById(campaignId: string) {
  return useQuery({
    queryKey: ['campaigns', campaignId],
    queryFn: async (): Promise<Campaign> => {
      return await campaignsApi.getCampaign(campaignId);
    },
    enabled: !!campaignId,
  });
}

