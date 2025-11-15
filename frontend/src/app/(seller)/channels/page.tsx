'use client';

import React from 'react';
import { useChannelSearch } from '@/hooks/useChannels';
import { ChannelSearch } from '@/components/channels/ChannelSearch';
import { ChannelFilters } from '@/components/channels/ChannelFilters';
import { ChannelDetailModal } from '@/components/channels/ChannelDetailModal';
import { ChannelFilters as ChannelFiltersType } from '@/lib/api/channels.api';
import { ChannelProfile } from '@/lib/types';
import { Loader2 } from 'lucide-react';

export default function ChannelsPage() {
  const [filters, setFilters] = React.useState<ChannelFiltersType>({});
  const [selectedChannel, setSelectedChannel] = React.useState<ChannelProfile | null>(null);
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  
  const { data: channels, isLoading } = useChannelSearch(filters);
  
  const handleChannelSelect = (channel: ChannelProfile) => {
    setSelectedChannel(channel);
    setIsModalOpen(true);
  };
  
  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Find Channels</h1>
        <p className="text-gray-600">
          Discover channels to promote your products and reach your target audience
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <ChannelFilters
            onFiltersChange={(newFilters) => {
              setFilters(newFilters);
            }}
            isLoading={isLoading}
          />
        </div>
        
        {/* Results */}
        <div className="lg:col-span-3">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : (
            <ChannelSearch
              channels={channels || []}
              isLoading={isLoading}
              onChannelSelect={handleChannelSelect}
              selectable={true}
            />
          )}
        </div>
      </div>
      
      {/* Detail Modal */}
      <ChannelDetailModal
        channel={selectedChannel}
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
      />
    </div>
  );
}

