/**
 * components/campaigns/CampaignDetails.tsx
 * Детальная информация о заявке
 */
'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Campaign, UserType } from '@/lib/types';
import { formatCurrency } from '@/lib/utils';
import { format } from 'date-fns';
import { CampaignTimeline } from './CampaignTimeline';
import { CampaignActions } from './CampaignActions';
import { Calendar, DollarSign, User, Link as LinkIcon, Image as ImageIcon, Video } from 'lucide-react';

interface CampaignDetailsProps {
  campaign: Campaign;
  userType: UserType;
  onActionComplete?: () => void;
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

export function CampaignDetails({ campaign, userType, onActionComplete }: CampaignDetailsProps) {
  const statusInfo = statusConfig[campaign.status] || statusConfig.pending;
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            Campaign #{campaign.id.slice(0, 8)}
          </h1>
          <div className="flex items-center gap-2">
            <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
            <Badge variant="outline">{campaign.ad_format}</Badge>
          </div>
        </div>
        <CampaignActions
          campaign={campaign}
          userType={userType}
          onActionComplete={onActionComplete}
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Campaign Info */}
          <Card>
            <CardHeader>
              <CardTitle>Campaign Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Budget</div>
                  <div className="text-2xl font-bold flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    {formatCurrency(campaign.budget)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Commission</div>
                  <div className="text-lg">
                    {campaign.platform_commission_percent}% ({formatCurrency(campaign.budget * campaign.platform_commission_percent / 100)})
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1 flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Start Date
                  </div>
                  <div>{format(new Date(campaign.start_date), 'PPP')}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1 flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    End Date
                  </div>
                  <div>{format(new Date(campaign.end_date), 'PPP')}</div>
                </div>
              </div>
              
              {campaign.actual_completion_date && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Completed On</div>
                  <div>{format(new Date(campaign.actual_completion_date), 'PPP')}</div>
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* Creative Content */}
          <Card>
            <CardHeader>
              <CardTitle>Creative Content</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-gray-600 mb-2">Text</div>
                <p className="whitespace-pre-wrap">{campaign.creative_text}</p>
              </div>
              
              {campaign.creative_images && campaign.creative_images.length > 0 && (
                <div>
                  <div className="text-sm text-gray-600 mb-2 flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" />
                    Images
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {campaign.creative_images.map((url, idx) => (
                      <a
                        key={idx}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block"
                      >
                        <img
                          src={url}
                          alt={`Creative ${idx + 1}`}
                          className="w-full h-32 object-cover rounded border"
                        />
                      </a>
                    ))}
                  </div>
                </div>
              )}
              
              {campaign.creative_video_url && (
                <div>
                  <div className="text-sm text-gray-600 mb-2 flex items-center gap-2">
                    <Video className="h-4 w-4" />
                    Video
                  </div>
                  <a
                    href={campaign.creative_video_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {campaign.creative_video_url}
                  </a>
                </div>
              )}
              
              {campaign.ad_url && (
                <div>
                  <div className="text-sm text-gray-600 mb-2 flex items-center gap-2">
                    <LinkIcon className="h-4 w-4" />
                    Ad URL
                  </div>
                  <a
                    href={campaign.ad_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {campaign.ad_url}
                  </a>
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* Placement Proof */}
          {campaign.placement_proof_url && (
            <Card>
              <CardHeader>
                <CardTitle>Placement Proof</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-gray-600 mb-2">Type: {campaign.placement_proof_type}</div>
                <a
                  href={campaign.placement_proof_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {campaign.placement_proof_url}
                </a>
                {campaign.placement_proof_type === 'screenshot' && (
                  <img
                    src={campaign.placement_proof_url}
                    alt="Placement proof"
                    className="mt-4 w-full rounded border"
                  />
                )}
              </CardContent>
            </Card>
          )}
          
          {/* Notes */}
          {(campaign.seller_notes || campaign.owner_notes) && (
            <Card>
              <CardHeader>
                <CardTitle>Notes</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {campaign.seller_notes && (
                  <div>
                    <div className="text-sm font-semibold mb-1">Seller Notes</div>
                    <p className="text-sm text-gray-600">{campaign.seller_notes}</p>
                  </div>
                )}
                {campaign.owner_notes && (
                  <div>
                    <div className="text-sm font-semibold mb-1">Channel Owner Notes</div>
                    <p className="text-sm text-gray-600">{campaign.owner_notes}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <CampaignTimeline campaign={campaign} />
            </CardContent>
          </Card>
          
          {/* Created Info */}
          <Card>
            <CardHeader>
              <CardTitle>Created</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-600">
                {format(new Date(campaign.created_at), 'PPP p')}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

