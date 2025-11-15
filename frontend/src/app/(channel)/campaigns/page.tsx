'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { campaignsApi } from '@/lib/api/campaigns.api';
import { CampaignCard } from '@/components/campaigns/CampaignCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useAuthStore } from '@/lib/store/auth.store';
import { Loader2 } from 'lucide-react';
import apiClient from '@/lib/api/client';

export default function ChannelCampaignsPage() {
  const { user } = useAuthStore();
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  const [searchQuery, setSearchQuery] = React.useState('');
  
  // Получаем заявки для канала
  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns', 'channel'],
    queryFn: async () => {
      // TODO: Добавить API endpoint для получения заявок канала
      // Пока используем общий endpoint
      try {
        const response = await apiClient.get('/campaigns/my-campaigns');
        return response.data;
      } catch {
        return [];
      }
    },
    enabled: !!user,
  });
  
  const filteredCampaigns = React.useMemo(() => {
    if (!campaigns) return [];
    
    let filtered = campaigns;
    
    if (statusFilter !== 'all') {
      filtered = filtered.filter((c: any) => c.status === statusFilter);
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((c: any) => 
        c.id.toLowerCase().includes(query) ||
        c.creative_text?.toLowerCase().includes(query)
      );
    }
    
    return filtered;
  }, [campaigns, statusFilter, searchQuery]);
  
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Campaign Requests</h1>
      </div>
      
      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <Input
          placeholder="Search campaigns..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
        />
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="accepted">Accepted</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      {/* Campaigns List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : filteredCampaigns.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCampaigns.map((campaign: any) => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              userType={user?.user_type || 'channel_owner'}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600">
            {searchQuery || statusFilter !== 'all'
              ? 'No campaigns match your filters'
              : 'No campaign requests yet'}
          </p>
        </div>
      )}
    </div>
  );
}

