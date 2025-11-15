/**
 * components/channels/ChannelSearch.tsx
 * Поиск каналов с результатами
 */
'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { ChannelCard } from './ChannelCard';
import { ChannelProfile } from '@/lib/types';
import { Loader2, Search } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface ChannelSearchProps {
  channels: ChannelProfile[];
  isLoading?: boolean;
  onChannelSelect?: (channel: ChannelProfile) => void;
  selectable?: boolean;
}

export function ChannelSearch({ 
  channels, 
  isLoading, 
  onChannelSelect,
  selectable = false 
}: ChannelSearchProps) {
  const [searchQuery, setSearchQuery] = React.useState('');
  
  const filteredChannels = React.useMemo(() => {
    if (!searchQuery) return channels;
    
    const query = searchQuery.toLowerCase();
    return channels.filter(channel =>
      channel.channel_name.toLowerCase().includes(query) ||
      channel.channel_description?.toLowerCase().includes(query) ||
      channel.category.toLowerCase().includes(query) ||
      channel.platform.toLowerCase().includes(query)
    );
  }, [channels, searchQuery]);
  
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search channels..."
            className="pl-10"
            disabled
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="space-y-3">
              <Skeleton className="h-48 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search channels by name, category, platform..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>
      
      {/* Results Count */}
      {filteredChannels.length > 0 && (
        <div className="text-sm text-gray-600">
          Found {filteredChannels.length} {filteredChannels.length === 1 ? 'channel' : 'channels'}
        </div>
      )}
      
      {/* Results Grid */}
      {filteredChannels.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredChannels.map((channel) => (
            <ChannelCard
              key={channel.id}
              channel={channel}
              onClick={() => onChannelSelect?.(channel)}
              showPrice={true}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-2">No channels found</p>
          <p className="text-sm text-gray-500">
            {searchQuery 
              ? 'Try adjusting your search or filters'
              : 'No channels match your filters'}
          </p>
        </div>
      )}
    </div>
  );
}

