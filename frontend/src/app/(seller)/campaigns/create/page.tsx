'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { CreateCampaignForm } from '@/components/forms/CreateCampaignForm';
import { Loader2 } from 'lucide-react';

function CreateCampaignContent() {
  const searchParams = useSearchParams();
  const channelId = searchParams.get('channel_id');
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <CreateCampaignForm initialChannelId={channelId || undefined} />
    </div>
  );
}

export default function CreateCampaignPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    }>
      <CreateCampaignContent />
    </Suspense>
  );
}

