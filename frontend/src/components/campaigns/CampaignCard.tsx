/**
 * components/campaigns/CampaignCard.tsx
 * Карточка заявки
 */
'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Campaign, UserType } from '@/lib/types';
import { formatCurrency } from '@/lib/utils';
import { format } from 'date-fns';
import { Calendar, DollarSign, Clock, Star } from 'lucide-react';

interface CampaignCardProps {
  campaign: Campaign;
  userType: UserType;
  onAction?: (action: string, campaignId: string) => void;
}

const statusConfig: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
  pending: { label: 'Pending', variant: 'outline' },
  accepted: { label: 'Accepted', variant: 'default' },
  rejected: { label: 'Rejected', variant: 'destructive' },
  in_progress: { label: 'In Progress', variant: 'default' },
  completed: { label: 'Completed', variant: 'default' },
  disputed: { label: 'Disputed', variant: 'destructive' },
  cancelled: { label: 'Cancelled', variant: 'outline' },
};

export function CampaignCard({ campaign, userType, onAction }: CampaignCardProps) {
  const statusInfo = statusConfig[campaign.status] || statusConfig.pending;
  
  // Вычисляем прогресс по времени
  const startDate = new Date(campaign.start_date);
  const endDate = new Date(campaign.end_date);
  const now = new Date();
  const totalDuration = endDate.getTime() - startDate.getTime();
  const elapsed = now.getTime() - startDate.getTime();
  const progress = Math.max(0, Math.min(100, (elapsed / totalDuration) * 100));
  
  const getDetailUrl = () => {
    if (userType === 'seller') {
      return `/seller/campaigns/${campaign.id}`;
    }
    return `/channel/campaigns/${campaign.id}`;
  };
  
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg mb-2">
              Campaign #{campaign.id.slice(0, 8)}
            </CardTitle>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
              <span className="text-sm text-gray-500">
                {campaign.ad_format}
              </span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-gray-500" />
            <span className="font-semibold">{formatCurrency(campaign.budget)}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <span>{format(new Date(campaign.start_date), 'MMM dd, yyyy')}</span>
          </div>
        </div>
        
        {campaign.status === 'in_progress' && (
          <div>
            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
        
        {campaign.creative_text && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {campaign.creative_text}
          </p>
        )}
        
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Clock className="h-3 w-3" />
            <span>Ends: {format(new Date(campaign.end_date), 'MMM dd')}</span>
          </div>
          <Button variant="outline" size="sm" asChild>
            <Link href={getDetailUrl()}>View Details</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

