'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useSellerProfile } from '@/hooks/useSeller';
import { SellerProfileForm } from '@/components/forms/SellerProfileForm';
import { Loader2 } from 'lucide-react';

export default function EditSellerProfilePage() {
  const router = useRouter();
  const { data: profile, isLoading } = useSellerProfile();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <SellerProfileForm 
        initialData={profile || undefined}
        onSuccess={() => router.push('/seller/profile')}
      />
    </div>
  );
}

