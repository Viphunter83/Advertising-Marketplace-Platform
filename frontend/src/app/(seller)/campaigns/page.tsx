'use client';

import React from 'react';
import { useCampaigns } from '@/hooks/useCampaigns';
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
import Link from 'next/link';
import { useAuthStore } from '@/lib/store/auth.store';
import { Loader2, Plus } from 'lucide-react';

export default function SellerCampaignsPage() {
  const { user } = useAuthStore();
  const { data: campaigns, isLoading } = useCampaigns();
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  const [searchQuery, setSearchQuery] = React.useState('');
  
  const filteredCampaigns = React.useMemo(() => {
    if (!campaigns) return [];
    
    let filtered = campaigns;
    
    if (statusFilter !== 'all') {
      filtered = filtered.filter(c => c.status === statusFilter);
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(c => 
        c.id.toLowerCase().includes(query) ||
        c.creative_text.toLowerCase().includes(query)
      );
    }
    
    return filtered;
  }, [campaigns, statusFilter, searchQuery]);
  
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">My Campaigns</h1>
        <Button asChild>
          <Link href="/seller/campaigns/create">
            <Plus className="mr-2 h-4 w-4" />
            Create Campaign
          </Link>
        </Button>
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
            <SelectItem value="cancelled">Cancelled</SelectItem>
            <SelectItem value="disputed">Disputed</SelectItem>
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
          {filteredCampaigns.map((campaign) => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              userType={user?.user_type || 'seller'}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">
            {searchQuery || statusFilter !== 'all'
              ? 'No campaigns match your filters'
              : 'No campaigns yet'}
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <Button asChild>
              <Link href="/seller/campaigns/create">Create Your First Campaign</Link>
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

