/**
 * components/channels/ChannelCard.tsx
 * Карточка канала
 */
'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ChannelProfile } from '@/lib/types';
import { formatCurrency } from '@/lib/utils';
import { 
  Users, 
  TrendingUp, 
  Star, 
  ExternalLink,
  CheckCircle2
} from 'lucide-react';

interface ChannelCardProps {
  channel: ChannelProfile;
  onClick?: () => void;
  showPrice?: boolean;
}

const platformIcons: Record<string, string> = {
  vk: '🔵',
  telegram: '💬',
  pinterest: '📌',
  instagram: '📷',
  tiktok: '🎵',
};

export function ChannelCard({ channel, onClick, showPrice = true }: ChannelCardProps) {
  const platformIcon = platformIcons[channel.platform] || '📱';
  
  return (
    <Card 
      className="hover:shadow-lg transition-all duration-200 cursor-pointer group"
      onClick={onClick}
    >
      <CardContent className="p-0">
        {/* Image/Header */}
        <div className="relative h-48 bg-gradient-to-br from-blue-50 to-purple-50 overflow-hidden">
          {channel.channel_avatar_url ? (
            <img
              src={channel.channel_avatar_url}
              alt={channel.channel_name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-6xl">
              {platformIcon}
            </div>
          )}
          
          {channel.verified && (
            <div className="absolute top-2 right-2">
              <Badge className="bg-green-500">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Verified
              </Badge>
            </div>
          )}
        </div>
        
        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Title and Platform */}
          <div>
            <h3 className="font-semibold text-lg mb-1 line-clamp-1 group-hover:text-blue-600 transition-colors">
              {channel.channel_name}
            </h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>{platformIcon}</span>
              <span className="capitalize">{channel.platform}</span>
              {channel.category && (
                <>
                  <span>•</span>
                  <span>{channel.category}</span>
                </>
              )}
            </div>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-gray-500" />
              <span className="font-medium">
                {channel.subscribers_count.toLocaleString()}
              </span>
              <span className="text-gray-500">subs</span>
            </div>
            
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-gray-500" />
              <span className="font-medium">
                {channel.engagement_rate?.toFixed(1) || '0'}%
              </span>
              <span className="text-gray-500">ER</span>
            </div>
          </div>
          
          {/* Rating */}
          {channel.rating > 0 && (
            <div className="flex items-center gap-2">
              <div className="flex items-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-4 w-4 ${
                      star <= Math.round(channel.rating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm font-medium">{channel.rating.toFixed(1)}</span>
              <span className="text-sm text-gray-500">
                ({channel.total_orders || 0} orders)
              </span>
            </div>
          )}
          
          {/* Price */}
          {showPrice && (
            <div className="pt-2 border-t">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs text-gray-500">Price per post</div>
                  <div className="text-xl font-bold">
                    {formatCurrency(channel.price_per_post)}
                  </div>
                </div>
                <Button size="sm" asChild onClick={(e) => e.stopPropagation()}>
                  <Link href={`/seller/channels/${channel.id}`}>
                    View Details
                  </Link>
                </Button>
              </div>
            </div>
          )}
          
          {/* Tags */}
          {channel.tags && channel.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 pt-2">
              {channel.tags.slice(0, 3).map((tag, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {channel.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{channel.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

