/**
 * components/campaigns/CampaignActions.tsx
 * Действия для заявки в зависимости от статуса и типа пользователя
 */
'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Campaign, UserType } from '@/lib/types';
import { AcceptCampaignDialog } from './dialogs/AcceptCampaignDialog';
import { RejectCampaignDialog } from './dialogs/RejectCampaignDialog';
import { SubmitPlacementDialog } from './dialogs/SubmitPlacementDialog';
import { ConfirmCampaignDialog } from './dialogs/ConfirmCampaignDialog';
import { CheckCircle2, XCircle, Send, AlertTriangle, Ban } from 'lucide-react';
import { campaignsApi } from '@/lib/api/campaigns.api';
import toast from 'react-hot-toast';

interface CampaignActionsProps {
  campaign: Campaign;
  userType: UserType;
  onActionComplete?: () => void;
}

export function CampaignActions({ campaign, userType, onActionComplete }: CampaignActionsProps) {
  const [acceptOpen, setAcceptOpen] = React.useState(false);
  const [rejectOpen, setRejectOpen] = React.useState(false);
  const [submitOpen, setSubmitOpen] = React.useState(false);
  const [confirmOpen, setConfirmOpen] = React.useState(false);
  
  // Для channel_owner
  if (userType === 'channel_owner') {
    if (campaign.status === 'pending') {
      return (
        <>
          <div className="flex gap-2">
            <Button onClick={() => setAcceptOpen(true)}>
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Accept
            </Button>
            <Button variant="destructive" onClick={() => setRejectOpen(true)}>
              <XCircle className="mr-2 h-4 w-4" />
              Reject
            </Button>
          </div>
          
          <AcceptCampaignDialog
            campaignId={campaign.id}
            open={acceptOpen}
            onOpenChange={setAcceptOpen}
            onSuccess={onActionComplete}
          />
          
          <RejectCampaignDialog
            campaignId={campaign.id}
            open={rejectOpen}
            onOpenChange={setRejectOpen}
            onSuccess={onActionComplete}
          />
        </>
      );
    }
    
    if (campaign.status === 'accepted') {
      return (
        <>
          <Button onClick={() => setSubmitOpen(true)}>
            <Send className="mr-2 h-4 w-4" />
            Submit Placement
          </Button>
          
          <SubmitPlacementDialog
            campaignId={campaign.id}
            open={submitOpen}
            onOpenChange={setSubmitOpen}
            onSuccess={onActionComplete}
          />
        </>
      );
    }
  }
  
  // Для seller
  if (userType === 'seller') {
    if (campaign.status === 'pending') {
      return (
        <Button
          variant="destructive"
          onClick={async () => {
            if (confirm('Are you sure you want to cancel this campaign? Funds will be returned.')) {
              try {
                await campaignsApi.cancelCampaign(campaign.id);
                toast.success('Campaign cancelled. Funds will be returned.');
                onActionComplete?.();
              } catch (err: any) {
                const errorMessage = err.response?.data?.detail || 'Failed to cancel campaign.';
                toast.error(errorMessage);
              }
            }
          }}
        >
          <Ban className="mr-2 h-4 w-4" />
          Cancel Campaign
        </Button>
      );
    }
    
    if (campaign.status === 'in_progress' && campaign.owner_submitted_at) {
      return (
        <>
          <Button onClick={() => setConfirmOpen(true)}>
            <CheckCircle2 className="mr-2 h-4 w-4" />
            Review & Confirm
          </Button>
          
          <ConfirmCampaignDialog
            campaign={campaign}
            open={confirmOpen}
            onOpenChange={setConfirmOpen}
            onSuccess={onActionComplete}
          />
        </>
      );
    }
  }
  
  // Нет доступных действий
  return null;
}

