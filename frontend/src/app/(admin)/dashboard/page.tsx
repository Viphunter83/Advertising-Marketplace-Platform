'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/lib/api/admin.api';
import { StatsOverview } from '@/components/admin/StatsOverview';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

export default function AdminDashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: async () => {
      return await adminApi.getPlatformStats();
    },
  });
  
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Admin Dashboard</h1>
      
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <>
          <StatsOverview stats={stats || null} isLoading={isLoading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common administrative tasks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <a href="/admin/disputes" className="block text-blue-600 hover:underline">
                  Review Disputes
                </a>
                <a href="/admin/withdrawals" className="block text-blue-600 hover:underline">
                  Process Withdrawals
                </a>
                <a href="/admin/stats" className="block text-blue-600 hover:underline">
                  View Detailed Statistics
                </a>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest platform events</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500">Recent activity will be displayed here</p>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}

