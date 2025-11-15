/**
 * components/forms/SellerProfileForm.tsx
 * Форма профиля продавца
 */
'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { sellersApi } from '@/lib/api/sellers.api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import toast from 'react-hot-toast';
import { SellerProfile } from '@/lib/types';

const sellerProfileSchema = z.object({
  shop_name: z.string().min(2, 'Shop name must be at least 2 characters').max(255, 'Shop name is too long'),
  shop_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  shop_description: z.string().max(1000, 'Description is too long').optional(),
  category: z.string().min(1, 'Please select a category'),
  notification_email: z.string().email('Invalid email').optional().or(z.literal('')),
});

type SellerProfileFormData = z.infer<typeof sellerProfileSchema>;

interface SellerProfileFormProps {
  initialData?: SellerProfile;
  onSuccess?: () => void;
}

const CATEGORIES = [
  'Мода и одежда',
  'Техника и электроника',
  'Красота и здоровье',
  'Дом и сад',
  'Спорт и отдых',
  'Детские товары',
  'Автотовары',
  'Книги и медиа',
  'Еда и напитки',
  'Другое',
];

export function SellerProfileForm({ initialData, onSuccess }: SellerProfileFormProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  
  const form = useForm<SellerProfileFormData>({
    resolver: zodResolver(sellerProfileSchema),
    defaultValues: {
      shop_name: initialData?.shop_name || '',
      shop_url: initialData?.shop_url || '',
      shop_description: initialData?.shop_description || '',
      category: initialData?.category || '',
      notification_email: initialData?.notification_email || '',
    },
  });
  
  const onSubmit = async (data: SellerProfileFormData) => {
    setIsLoading(true);
    
    try {
      if (initialData) {
        // Обновление существующего профиля
        await sellersApi.updateProfile({
          shop_name: data.shop_name,
          shop_url: data.shop_url || undefined,
          shop_description: data.shop_description || undefined,
          category: data.category,
          logo_url: undefined, // TODO: Добавить загрузку логотипа
        });
        toast.success('Profile updated successfully!');
      } else {
        // Создание нового профиля
        await sellersApi.createProfile({
          shop_name: data.shop_name,
          shop_url: data.shop_url || undefined,
          shop_description: data.shop_description || undefined,
          category: data.category,
          logo_url: undefined,
        });
        toast.success('Profile created successfully!');
      }
      
      onSuccess?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to save profile. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{initialData ? 'Edit Seller Profile' : 'Create Seller Profile'}</CardTitle>
        <CardDescription>
          {initialData 
            ? 'Update your shop information' 
            : 'Complete your seller profile to start creating campaigns'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="shop_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Shop Name *</FormLabel>
                  <FormControl>
                    <Input placeholder="My Awesome Shop" {...field} />
                  </FormControl>
                  <FormDescription>
                    The name of your shop or brand
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="shop_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Shop URL</FormLabel>
                  <FormControl>
                    <Input 
                      type="url" 
                      placeholder="https://example.com" 
                      {...field} 
                    />
                  </FormControl>
                  <FormDescription>
                    Link to your shop on marketplace (Wildberries, Ozon, etc.)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="category"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {CATEGORIES.map((cat) => (
                        <SelectItem key={cat} value={cat}>
                          {cat}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="shop_description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Tell us about your shop..." 
                      className="min-h-[100px]"
                      {...field} 
                    />
                  </FormControl>
                  <FormDescription>
                    Brief description of your shop and products (max 1000 characters)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="notification_email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notification Email</FormLabel>
                  <FormControl>
                    <Input 
                      type="email" 
                      placeholder="notifications@example.com" 
                      {...field} 
                    />
                  </FormControl>
                  <FormDescription>
                    Email for campaign notifications (optional, defaults to your account email)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="flex gap-4">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Saving...' : initialData ? 'Update Profile' : 'Create Profile'}
              </Button>
              {onSuccess && (
                <Button type="button" variant="outline" onClick={onSuccess}>
                  Cancel
                </Button>
              )}
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

