'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useChannelProfile } from '@/hooks/useChannel';
import { ChannelProfileForm } from '@/components/forms/ChannelProfileForm';
import { Loader2 } from 'lucide-react';

export default function EditChannelProfilePage() {
  const router = useRouter();
  const { data: profile, isLoading } = useChannelProfile();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <ChannelProfileForm 
        initialData={profile || undefined}
        onSuccess={() => router.push('/channel/profile')}
      />
    </div>
  );
}

