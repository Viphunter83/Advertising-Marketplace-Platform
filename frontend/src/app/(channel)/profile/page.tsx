'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useChannelProfile } from '@/hooks/useChannel';
import { ChannelProfileForm } from '@/components/forms/ChannelProfileForm';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { Loader2, Edit, Star } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function ChannelProfilePage() {
  const router = useRouter();
  const { data: profile, isLoading, error } = useChannelProfile();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  if (error) {
    // Профиль не найден - показываем форму создания
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <ChannelProfileForm 
          onSuccess={() => {
            router.push('/channel/dashboard');
          }}
        />
      </div>
    );
  }
  
  // Профиль существует - показываем данные
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Channel Profile</h1>
        <Button asChild>
          <Link href="/channel/profile/edit">
            <Edit className="mr-2 h-4 w-4" />
            Edit Profile
          </Link>
        </Button>
      </div>
      
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">{profile?.channel_name}</CardTitle>
              <CardDescription className="mt-2">
                {profile?.platform?.toUpperCase()} • {profile?.category}
              </CardDescription>
            </div>
            {profile?.verified && (
              <Badge variant="default">Verified</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {profile?.channel_url && (
            <div>
              <p className="text-sm text-gray-600 mb-1">Channel URL</p>
              <a 
                href={profile.channel_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {profile.channel_url}
              </a>
            </div>
          )}
          
          {profile?.channel_description && (
            <div>
              <p className="text-sm text-gray-600 mb-1">Description</p>
              <p>{profile.channel_description}</p>
            </div>
          )}
          
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Subscribers</p>
              <p className="text-2xl font-bold">{profile?.subscribers_count?.toLocaleString() || '0'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Reach</p>
              <p className="text-2xl font-bold">{profile?.avg_reach?.toLocaleString() || '0'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Engagement Rate</p>
              <p className="text-2xl font-bold">{profile?.engagement_rate?.toFixed(1) || '0'}%</p>
            </div>
          </div>
          
          {profile?.rating && (
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
              <span className="text-xl font-bold">{profile.rating.toFixed(1)}</span>
              <span className="text-sm text-gray-600">
                ({profile.total_orders || 0} orders)
              </span>
            </div>
          )}
          
          <div className="border-t pt-4">
            <h3 className="font-semibold mb-3">Pricing</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Post</p>
                <p className="text-xl font-bold">₽{profile?.price_per_post?.toLocaleString() || '0'}</p>
              </div>
              {profile?.price_per_story && (
                <div>
                  <p className="text-sm text-gray-600">Story</p>
                  <p className="text-xl font-bold">₽{profile.price_per_story.toLocaleString()}</p>
                </div>
              )}
              {profile?.price_per_video && (
                <div>
                  <p className="text-sm text-gray-600">Video</p>
                  <p className="text-xl font-bold">₽{profile.price_per_video.toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 pt-4 border-t">
            <div>
              <p className="text-sm text-gray-600">Total Earned</p>
              <p className="text-2xl font-bold">₽{profile?.total_earned?.toLocaleString() || '0'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Completed Orders</p>
              <p className="text-2xl font-bold">{profile?.completed_orders || '0'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold">{profile?.total_orders || '0'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

