/**
 * hooks/useSeller.ts
 * Hook для работы с профилем продавца
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sellersApi } from '@/lib/api/sellers.api';
import { SellerProfile } from '@/lib/types';

export function useSellerProfile() {
  return useQuery({
    queryKey: ['seller', 'profile'],
    queryFn: async () => {
      return await sellersApi.getProfile();
    },
    retry: 1,
  });
}

export function useCreateSellerProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: any) => {
      return await sellersApi.createProfile(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seller', 'profile'] });
    },
  });
}

export function useUpdateSellerProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: any) => {
      return await sellersApi.updateProfile(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seller', 'profile'] });
    },
  });
}

