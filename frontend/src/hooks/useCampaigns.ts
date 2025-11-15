/**
 * hooks/useCampaigns.ts
 * Hook для работы с заявками
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignsApi, CreateCampaignPayload, UpdateCampaignPayload } from '@/lib/api/campaigns.api';
import { Campaign } from '@/lib/types';

export function useCampaigns() {
  return useQuery({
    queryKey: ['campaigns', 'my'],
    queryFn: async () => {
      return await campaignsApi.getMyCampaigns();
    },
  });
}


export function useCreateCampaign() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateCampaignPayload) => {
      return await campaignsApi.createCampaign(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
    },
  });
}

export function useUpdateCampaign() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ campaignId, data }: { campaignId: string; data: UpdateCampaignPayload }) => {
      return await campaignsApi.updateCampaign(campaignId, data);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns', variables.campaignId] });
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
    },
  });
}

