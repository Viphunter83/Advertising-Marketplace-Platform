'use client';

import React from 'react';
import { useAuthStore } from '@/lib/store/auth.store';
import { useCampaigns } from '@/hooks/useCampaigns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function SellerDashboard() {
  const { user } = useAuthStore();
  const { data: campaigns, isLoading } = useCampaigns();
  
  const activeCampaigns = campaigns?.filter(c => 
    ['pending', 'accepted', 'in_progress'].includes(c.status)
  ).length || 0;
  
  const completedCampaigns = campaigns?.filter(c => c.status === 'completed').length || 0;
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Seller Dashboard</h1>
      
      <div className="grid grid-cols-3 gap-4 mb-8">
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
            <CardTitle className="text-sm font-normal text-gray-600">Balance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₽0.00</div>
          </CardContent>
        </Card>
      </div>
      
      <div className="flex gap-4 mb-8">
        <Button asChild>
          <Link href="/seller/campaigns/create">Create Campaign</Link>
        </Button>
        
        <Button variant="outline" asChild>
          <Link href="/seller/channels">Search Channels</Link>
        </Button>
      </div>
      
      <div>
        <h2 className="text-xl font-bold mb-4">Recent Campaigns</h2>
        {isLoading ? (
          <div>Loading...</div>
        ) : campaigns?.length ? (
          <div className="grid gap-4">
            {campaigns.slice(0, 5).map(campaign => (
              <Card key={campaign.id}>
                <CardContent className="p-4 flex justify-between items-center">
                  <div>
                    <div className="font-bold">{campaign.id}</div>
                    <div className="text-sm text-gray-600">Status: {campaign.status}</div>
                  </div>
                  <Button variant="outline" asChild>
                    <Link href={`/seller/campaigns/${campaign.id}`}>View</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-600">
            No campaigns yet. Create your first one!
          </div>
        )}
      </div>
    </div>
  );
}

