'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useSellerProfile } from '@/hooks/useSeller';
import { SellerProfileForm } from '@/components/forms/SellerProfileForm';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { Loader2, Edit } from 'lucide-react';

export default function SellerProfilePage() {
  const router = useRouter();
  const { data: profile, isLoading, error } = useSellerProfile();
  
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
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <SellerProfileForm 
          onSuccess={() => router.push('/seller/dashboard')}
        />
      </div>
    );
  }
  
  // Профиль существует - показываем данные и кнопку редактирования
  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Seller Profile</h1>
        <Button asChild>
          <Link href="/seller/profile/edit">
            <Edit className="mr-2 h-4 w-4" />
            Edit Profile
          </Link>
        </Button>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>{profile?.shop_name}</CardTitle>
          <CardDescription>{profile?.category}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {profile?.shop_url && (
            <div>
              <p className="text-sm text-gray-600">Shop URL</p>
              <a 
                href={profile.shop_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {profile.shop_url}
              </a>
            </div>
          )}
          
          {profile?.shop_description && (
            <div>
              <p className="text-sm text-gray-600">Description</p>
              <p>{profile.shop_description}</p>
            </div>
          )}
          
          <div className="grid grid-cols-3 gap-4 pt-4 border-t">
            <div>
              <p className="text-sm text-gray-600">Balance</p>
              <p className="text-2xl font-bold">₽{profile?.balance?.toLocaleString() || '0'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Spent</p>
              <p className="text-2xl font-bold">₽{profile?.total_spent?.toLocaleString() || '0'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Campaigns</p>
              <p className="text-2xl font-bold">{profile?.total_campaigns || '0'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

