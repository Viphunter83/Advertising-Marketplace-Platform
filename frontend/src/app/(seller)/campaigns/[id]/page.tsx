'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useCampaignById } from '@/hooks/useCampaignById';
import { CampaignDetails } from '@/components/campaigns/CampaignDetails';
import { useAuthStore } from '@/lib/store/auth.store';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function CampaignDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  const campaignId = params.id as string;
  
  const { data: campaign, isLoading, refetch } = useCampaignById(campaignId);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  if (!campaign) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Campaign not found</h1>
          <Button asChild>
            <Link href="/seller/campaigns">Back to Campaigns</Link>
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-4">
        <Button variant="outline" onClick={() => router.back()}>
          ← Back
        </Button>
      </div>
      <CampaignDetails
        campaign={campaign}
        userType={user?.user_type || 'seller'}
        onActionComplete={() => {
          refetch();
        }}
      />
    </div>
  );
}

