/**
 * hooks/useChannels.ts
 * Hook для работы с каналами
 */
import { useQuery } from '@tanstack/react-query';
import { channelsApi, ChannelFilters } from '@/lib/api/channels.api';
import { ChannelProfile } from '@/lib/types';

export function useChannelSearch(filters?: ChannelFilters) {
  return useQuery({
    queryKey: ['channels', 'search', filters],
    queryFn: async () => {
      return await channelsApi.searchChannels(filters);
    },
    staleTime: 30 * 1000, // 30 seconds
  });
}

export function useChannelById(channelId: string) {
  return useQuery({
    queryKey: ['channels', channelId],
    queryFn: async () => {
      return await channelsApi.getChannel(channelId);
    },
    enabled: !!channelId,
  });
}

