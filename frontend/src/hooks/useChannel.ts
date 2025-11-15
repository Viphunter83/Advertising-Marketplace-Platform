/**
 * hooks/useChannel.ts
 * Hook для работы с профилем канала
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { channelsApi, ChannelProfilePayload } from '@/lib/api/channels.api';
import { ChannelProfile } from '@/lib/types';

export function useChannelProfile() {
  return useQuery({
    queryKey: ['channel', 'profile'],
    queryFn: async () => {
      return await channelsApi.getProfile();
    },
    retry: 1,
  });
}

export function useCreateChannelProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ChannelProfilePayload) => {
      return await channelsApi.createProfile(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['channel', 'profile'] });
    },
  });
}

export function useUpdateChannelProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: Partial<ChannelProfilePayload>) => {
      return await channelsApi.updateProfile(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['channel', 'profile'] });
    },
  });
}

