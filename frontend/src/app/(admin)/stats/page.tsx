'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/lib/api/admin.api';
import { StatsOverview } from '@/components/admin/StatsOverview';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

export default function AdminStatsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: async () => {
      return await adminApi.getPlatformStats();
    },
  });
  
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Platform Statistics</h1>
      
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <>
          <StatsOverview stats={stats || null} isLoading={isLoading} />
          
          <Card>
            <CardHeader>
              <CardTitle>Detailed Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Active Sellers</div>
                    <div className="text-2xl font-bold">{stats?.active_sellers || 0}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Active Channels</div>
                    <div className="text-2xl font-bold">{stats?.active_channels || 0}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Total Campaigns</div>
                    <div className="text-2xl font-bold">{stats?.total_campaigns || 0}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Completed Campaigns</div>
                    <div className="text-2xl font-bold">{stats?.completed_campaigns || 0}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

