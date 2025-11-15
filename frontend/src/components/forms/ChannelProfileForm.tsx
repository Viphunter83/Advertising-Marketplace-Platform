/**
 * components/forms/ChannelProfileForm.tsx
 * Форма профиля канала
 */
'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { channelsApi } from '@/lib/api/channels.api';
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
import { ChannelProfile, Platform } from '@/lib/types';

const channelProfileSchema = z.object({
  platform: z.enum(['vk', 'telegram', 'pinterest', 'instagram', 'tiktok']),
  channel_url: z.string().url('Invalid URL').min(1, 'Channel URL is required'),
  channel_name: z.string().min(2, 'Channel name must be at least 2 characters').max(255),
  channel_description: z.string().max(1000, 'Description is too long').optional(),
  category: z.string().min(1, 'Please select a category'),
  tags: z.array(z.string()).max(10, 'Maximum 10 tags allowed').optional(),
  subscribers_count: z.number().min(0, 'Subscribers count must be positive'),
  avg_reach: z.number().min(0, 'Average reach must be positive').optional(),
  engagement_rate: z.number().min(0, 'Engagement rate must be between 0 and 100').max(100).optional(),
  audience_geo: z.string().optional(),
  audience_age_group: z.string().optional(),
  audience_gender: z.string().optional(),
  price_per_post: z.number().min(0, 'Price must be positive'),
  price_per_story: z.number().min(0).optional(),
  price_per_video: z.number().min(0).optional(),
});

type ChannelProfileFormData = z.infer<typeof channelProfileSchema>;

interface ChannelProfileFormProps {
  initialData?: ChannelProfile;
  onSuccess?: () => void;
}

const PLATFORMS: { value: Platform; label: string }[] = [
  { value: 'vk', label: 'VKontakte' },
  { value: 'telegram', label: 'Telegram' },
  { value: 'pinterest', label: 'Pinterest' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'tiktok', label: 'TikTok' },
];

const CATEGORIES = [
  'Развлечения',
  'Образование',
  'Технологии',
  'Мода и стиль',
  'Красота',
  'Здоровье и фитнес',
  'Путешествия',
  'Еда и кулинария',
  'Бизнес',
  'Новости',
  'Другое',
];

const AGE_GROUPS = [
  '13-18',
  '18-25',
  '25-35',
  '35-45',
  '45+',
];

const GENDERS = [
  'Мужской',
  'Женский',
  'Смешанный',
];

export function ChannelProfileForm({ initialData, onSuccess }: ChannelProfileFormProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  const [tagsInput, setTagsInput] = React.useState(
    initialData?.tags?.join(', ') || ''
  );
  
  const form = useForm<ChannelProfileFormData>({
    resolver: zodResolver(channelProfileSchema),
    defaultValues: {
      platform: initialData?.platform || 'vk',
      channel_url: initialData?.channel_url || '',
      channel_name: initialData?.channel_name || '',
      channel_description: initialData?.channel_description || '',
      category: initialData?.category || '',
      tags: initialData?.tags || [],
      subscribers_count: initialData?.subscribers_count || 0,
      avg_reach: initialData?.avg_reach || 0,
      engagement_rate: initialData?.engagement_rate || 0,
      audience_geo: initialData?.audience_geo || '',
      audience_age_group: initialData?.audience_age_group || '',
      audience_gender: initialData?.audience_gender || '',
      price_per_post: initialData?.price_per_post || 0,
      price_per_story: initialData?.price_per_story || undefined,
      price_per_video: initialData?.price_per_video || undefined,
    },
  });
  
  const handleTagsChange = (value: string) => {
    setTagsInput(value);
    const tags = value.split(',').map(t => t.trim()).filter(t => t.length > 0);
    form.setValue('tags', tags);
  };
  
  const onSubmit = async (data: ChannelProfileFormData) => {
    setIsLoading(true);
    
    try {
      if (initialData) {
        await channelsApi.updateProfile({
          platform: data.platform,
          channel_url: data.channel_url,
          channel_name: data.channel_name,
          channel_description: data.channel_description,
          category: data.category,
          tags: data.tags,
          subscribers_count: data.subscribers_count,
          avg_reach: data.avg_reach,
          engagement_rate: data.engagement_rate,
          audience_geo: data.audience_geo,
          audience_age_group: data.audience_age_group,
          audience_gender: data.audience_gender,
          price_per_post: data.price_per_post,
          price_per_story: data.price_per_story,
          price_per_video: data.price_per_video,
        });
        toast.success('Profile updated successfully!');
      } else {
        await channelsApi.createProfile({
          platform: data.platform,
          channel_url: data.channel_url,
          channel_name: data.channel_name,
          channel_description: data.channel_description,
          category: data.category,
          tags: data.tags,
          subscribers_count: data.subscribers_count,
          avg_reach: data.avg_reach,
          engagement_rate: data.engagement_rate,
          audience_geo: data.audience_geo,
          audience_age_group: data.audience_age_group,
          audience_gender: data.audience_gender,
          price_per_post: data.price_per_post,
          price_per_story: data.price_per_story,
          price_per_video: data.price_per_video,
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
        <CardTitle>{initialData ? 'Edit Channel Profile' : 'Create Channel Profile'}</CardTitle>
        <CardDescription>
          {initialData 
            ? 'Update your channel information' 
            : 'Complete your channel profile to start receiving campaign requests'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="platform"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Platform *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select platform" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {PLATFORMS.map((platform) => (
                          <SelectItem key={platform.value} value={platform.value}>
                            {platform.label}
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
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
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
            </div>
            
            <FormField
              control={form.control}
              name="channel_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Channel Name *</FormLabel>
                  <FormControl>
                    <Input placeholder="My Awesome Channel" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="channel_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Channel URL *</FormLabel>
                  <FormControl>
                    <Input 
                      type="url" 
                      placeholder="https://vk.com/my_channel" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="channel_description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Tell us about your channel..." 
                      className="min-h-[100px]"
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="subscribers_count"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Subscribers *</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        placeholder="10000" 
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="avg_reach"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Avg Reach</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        placeholder="5000" 
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="engagement_rate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Engagement Rate (%)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number" 
                        placeholder="5.5" 
                        step="0.1"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="audience_geo"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Audience Geo</FormLabel>
                    <FormControl>
                      <Input placeholder="Russia" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="audience_age_group"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Age Group</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select age group" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {AGE_GROUPS.map((age) => (
                          <SelectItem key={age} value={age}>
                            {age}
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
                name="audience_gender"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gender</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {GENDERS.map((gender) => (
                          <SelectItem key={gender} value={gender}>
                            {gender}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <FormField
              control={form.control}
              name="tags"
              render={() => (
                <FormItem>
                  <FormLabel>Tags (comma-separated)</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="fashion, lifestyle, beauty"
                      value={tagsInput}
                      onChange={(e) => handleTagsChange(e.target.value)}
                    />
                  </FormControl>
                  <FormDescription>
                    Enter tags separated by commas (max 10 tags)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="border-t pt-4">
              <h3 className="text-lg font-semibold mb-4">Pricing</h3>
              <div className="grid grid-cols-3 gap-4">
                <FormField
                  control={form.control}
                  name="price_per_post"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Price per Post (RUB) *</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          placeholder="10000" 
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="price_per_story"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Price per Story (RUB)</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          placeholder="5000" 
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value) || undefined)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="price_per_video"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Price per Video (RUB)</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          placeholder="20000" 
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value) || undefined)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
            
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

