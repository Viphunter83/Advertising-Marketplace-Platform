'use client';

import React from 'react';
import { useDisputes } from '@/hooks/useDisputes';
import { DisputeTable } from '@/components/admin/DisputeTable';
import { Loader2 } from 'lucide-react';

export default function AdminDisputesPage() {
  const { data: disputes, isLoading, refetch } = useDisputes();
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Disputes</h1>
      
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <DisputeTable disputes={disputes || []} isLoading={isLoading} />
      )}
    </div>
  );
}

