/**
 * components/channels/ChannelDetailModal.tsx
 * Модальное окно с детальной информацией о канале
 */
'use client';

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ChannelProfile } from '@/lib/types';
import { ChannelRating } from './ChannelRating';
import { formatCurrency } from '@/lib/utils';
import { 
  Users, 
  TrendingUp, 
  MapPin, 
  Calendar,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { useRouter } from 'next/navigation';

interface ChannelDetailModalProps {
  channel: ChannelProfile | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const platformIcons: Record<string, string> = {
  vk: '🔵',
  telegram: '💬',
  pinterest: '📌',
  instagram: '📷',
  tiktok: '🎵',
};

export function ChannelDetailModal({ channel, open, onOpenChange }: ChannelDetailModalProps) {
  const router = useRouter();
  
  if (!channel) return null;
  
  const handleCreateCampaign = () => {
    onOpenChange(false);
    router.push(`/seller/campaigns/create?channel_id=${channel.id}`);
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={channel.channel_avatar_url} />
              <AvatarFallback className="text-2xl">
                {platformIcons[channel.platform] || '📱'}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <DialogTitle className="text-2xl">{channel.channel_name}</DialogTitle>
                {channel.verified && (
                  <Badge className="bg-green-500">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Verified
                  </Badge>
                )}
              </div>
              <DialogDescription className="text-base">
                <div className="flex items-center gap-2">
                  <span>{platformIcons[channel.platform]}</span>
                  <span className="capitalize">{channel.platform}</span>
                  {channel.category && (
                    <>
                      <span>•</span>
                      <span>{channel.category}</span>
                    </>
                  )}
                </div>
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>
        
        <div className="space-y-6 mt-4">
          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <Users className="h-6 w-6 mx-auto mb-2 text-gray-600" />
              <div className="text-2xl font-bold">{channel.subscribers_count.toLocaleString()}</div>
              <div className="text-xs text-gray-600">Subscribers</div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <TrendingUp className="h-6 w-6 mx-auto mb-2 text-gray-600" />
              <div className="text-2xl font-bold">{channel.engagement_rate?.toFixed(1) || '0'}%</div>
              <div className="text-xs text-gray-600">Engagement</div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">{channel.avg_reach?.toLocaleString() || '0'}</div>
              <div className="text-xs text-gray-600">Avg Reach</div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">{formatCurrency(channel.price_per_post)}</div>
              <div className="text-xs text-gray-600">Per Post</div>
            </div>
          </div>
          
          {/* Description */}
          {channel.channel_description && (
            <div>
              <h3 className="font-semibold mb-2">About</h3>
              <p className="text-gray-600">{channel.channel_description}</p>
            </div>
          )}
          
          {/* Channel URL */}
          {channel.channel_url && (
            <div>
              <h3 className="font-semibold mb-2">Channel Link</h3>
              <a
                href={channel.channel_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline flex items-center gap-2"
              >
                {channel.channel_url}
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          )}
          
          {/* Audience Info */}
          <div className="grid grid-cols-3 gap-4">
            {channel.audience_geo && (
              <div>
                <div className="text-sm text-gray-600 mb-1 flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Location
                </div>
                <div className="font-medium">{channel.audience_geo}</div>
              </div>
            )}
            
            {channel.audience_age_group && (
              <div>
                <div className="text-sm text-gray-600 mb-1">Age Group</div>
                <div className="font-medium">{channel.audience_age_group}</div>
              </div>
            )}
            
            {channel.audience_gender && (
              <div>
                <div className="text-sm text-gray-600 mb-1">Gender</div>
                <div className="font-medium">{channel.audience_gender}</div>
              </div>
            )}
          </div>
          
          {/* Pricing */}
          <div>
            <h3 className="font-semibold mb-3">Pricing</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="p-3 border rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Post</div>
                <div className="text-xl font-bold">{formatCurrency(channel.price_per_post)}</div>
              </div>
              {channel.price_per_story && (
                <div className="p-3 border rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Story</div>
                  <div className="text-xl font-bold">{formatCurrency(channel.price_per_story)}</div>
                </div>
              )}
              {channel.price_per_video && (
                <div className="p-3 border rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Video</div>
                  <div className="text-xl font-bold">{formatCurrency(channel.price_per_video)}</div>
                </div>
              )}
            </div>
          </div>
          
          {/* Tags */}
          {channel.tags && channel.tags.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {channel.tags.map((tag, idx) => (
                  <Badge key={idx} variant="outline">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          
          {/* Rating */}
          <ChannelRating channelId={channel.id} />
          
          {/* Action Button */}
          <div className="flex justify-end pt-4 border-t">
            <Button onClick={handleCreateCampaign} size="lg">
              Create Campaign with this Channel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

