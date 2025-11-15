'use client';

import React from 'react';
import { useAuthStore } from '@/lib/store/auth.store';
import { useChannelProfile } from '@/hooks/useChannel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { campaignsApi } from '@/lib/api/campaigns.api';
import { Loader2 } from 'lucide-react';

export default function ChannelDashboard() {
  const { user } = useAuthStore();
  const { data: profile } = useChannelProfile();
  
  // Получаем заявки для канала
  const { data: campaigns, isLoading: campaignsLoading } = useQuery({
    queryKey: ['campaigns', 'channel'],
    queryFn: async () => {
      // TODO: Добавить API endpoint для получения заявок канала
      // Пока используем общий endpoint
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/campaigns/my-campaigns`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        if (response.ok) {
          return await response.json();
        }
        return [];
      } catch {
        return [];
      }
    },
    enabled: !!user,
  });
  
  const pendingCampaigns = campaigns?.filter((c: any) => c.status === 'pending').length || 0;
  const activeCampaigns = campaigns?.filter((c: any) => 
    ['accepted', 'in_progress'].includes(c.status)
  ).length || 0;
  const completedCampaigns = campaigns?.filter((c: any) => c.status === 'completed').length || 0;
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Channel Dashboard</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-normal text-gray-600">Pending Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{pendingCampaigns}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-normal text-gray-600">Active Campaigns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{activeCampaigns}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-normal text-gray-600">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{completedCampaigns}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-normal text-gray-600">Total Earned</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₽{profile?.total_earned?.toLocaleString() || '0'}</div>
          </CardContent>
        </Card>
      </div>
      
      <div className="flex gap-4 mb-8">
        <Button variant="outline" asChild>
          <Link href="/channel/campaigns">View All Campaigns</Link>
        </Button>
        
        <Button variant="outline" asChild>
          <Link href="/channel/earnings">View Earnings</Link>
        </Button>
      </div>
      
      <div>
        <h2 className="text-xl font-bold mb-4">Recent Campaign Requests</h2>
        {campaignsLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : campaigns?.length ? (
          <div className="grid gap-4">
            {campaigns.slice(0, 5).map((campaign: any) => (
              <Card key={campaign.id}>
                <CardContent className="p-4 flex justify-between items-center">
                  <div>
                    <div className="font-bold">Campaign #{campaign.id.slice(0, 8)}</div>
                    <div className="text-sm text-gray-600">
                      Status: {campaign.status} • Budget: ₽{campaign.budget?.toLocaleString()}
                    </div>
                  </div>
                  <Button variant="outline" asChild>
                    <Link href={`/channel/campaigns/${campaign.id}`}>View</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-600">
            No campaign requests yet. Your channel will appear in search results once you complete your profile.
          </div>
        )}
      </div>
    </div>
  );
}

