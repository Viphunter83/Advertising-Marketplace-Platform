/**
 * components/forms/CreateCampaignForm.tsx
 * Форма создания заявки
 */
'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { channelsApi } from '@/lib/api/channels.api';
import { campaignsApi } from '@/lib/api/campaigns.api';
import { paymentsApi } from '@/lib/api/payments.api';
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

const createCampaignSchema = z.object({
  channel_id: z.string().min(1, 'Please select a channel'),
  budget: z.number().min(1, 'Budget must be at least 1 RUB'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  ad_format: z.enum(['post', 'story', 'video', 'integration']),
  creative_text: z.string().min(10, 'Creative text must be at least 10 characters').max(2000),
  creative_images: z.array(z.string().url()).optional(),
  creative_video_url: z.string().url().optional().or(z.literal('')),
}).refine((data) => {
  const start = new Date(data.start_date);
  const end = new Date(data.end_date);
  return end > start;
}, {
  message: 'End date must be after start date',
  path: ['end_date'],
});

type CreateCampaignFormData = z.infer<typeof createCampaignSchema>;

export function CreateCampaignForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = React.useState(false);
  const [balance, setBalance] = React.useState<number | null>(null);
  const [imagesInput, setImagesInput] = React.useState('');
  
  // Загружаем баланс
  React.useEffect(() => {
    paymentsApi.getBalance().then((res) => {
      setBalance(res.balance);
    }).catch(() => {
      setBalance(0);
    });
  }, []);
  
  // Загружаем список каналов
  const { data: channels, isLoading: channelsLoading } = useQuery({
    queryKey: ['channels', 'search'],
    queryFn: async () => {
      return await channelsApi.searchChannels();
    },
  });
  
  const form = useForm<CreateCampaignFormData>({
    resolver: zodResolver(createCampaignSchema),
    defaultValues: {
      channel_id: '',
      budget: 0,
      start_date: format(new Date(), 'yyyy-MM-dd'),
      end_date: format(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd'),
      ad_format: 'post',
      creative_text: '',
      creative_images: [],
      creative_video_url: '',
    },
  });
  
  const selectedBudget = form.watch('budget');
  const hasEnoughBalance = balance !== null && balance >= selectedBudget;
  
  const handleImagesChange = (value: string) => {
    setImagesInput(value);
    const urls = value.split(',').map(url => url.trim()).filter(url => {
      try {
        new URL(url);
        return true;
      } catch {
        return false;
      }
    });
    form.setValue('creative_images', urls);
  };
  
  const onSubmit = async (data: CreateCampaignFormData) => {
    if (!hasEnoughBalance) {
      toast.error('Insufficient balance. Please top up your account.');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const campaign = await campaignsApi.createCampaign({
        channel_id: data.channel_id,
        budget: data.budget,
        start_date: data.start_date,
        end_date: data.end_date,
        ad_format: data.ad_format,
        creative_text: data.creative_text,
        creative_images: data.creative_images && data.creative_images.length > 0 ? data.creative_images : undefined,
        creative_video_url: data.creative_video_url || undefined,
      });
      
      toast.success('Campaign created successfully!');
      router.push(`/seller/campaigns/${campaign.id}`);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create campaign. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Create New Campaign</CardTitle>
        <CardDescription>
          Create a new advertising campaign for your products
        </CardDescription>
      </CardHeader>
      <CardContent>
        {balance !== null && (
          <Alert className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Current Balance: ₽{balance.toLocaleString()}
            </AlertDescription>
          </Alert>
        )}
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="channel_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Select Channel *</FormLabel>
                  {channelsLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a channel" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {channels?.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            <div className="flex flex-col">
                              <span className="font-semibold">{channel.channel_name}</span>
                              <span className="text-xs text-gray-500">
                                {channel.platform} • {channel.subscribers_count.toLocaleString()} subscribers • ₽{channel.price_per_post.toLocaleString()}/post
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="start_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Start Date *</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="end_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>End Date *</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="ad_format"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Ad Format *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="post">Post</SelectItem>
                        <SelectItem value="story">Story</SelectItem>
                        <SelectItem value="video">Video</SelectItem>
                        <SelectItem value="integration">Integration</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="budget"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Budget (RUB) *</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="10000"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                      />
                    </FormControl>
                    {selectedBudget > 0 && balance !== null && (
                      <FormDescription>
                        {hasEnoughBalance ? (
                          <span className="text-green-600">✓ Sufficient balance</span>
                        ) : (
                          <span className="text-red-600">
                            ✗ Insufficient balance. Need ₽{(selectedBudget - balance).toLocaleString()} more
                          </span>
                        )}
                      </FormDescription>
                    )}
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <FormField
              control={form.control}
              name="creative_text"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Creative Text *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter the text for your advertisement..."
                      className="min-h-[120px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    {field.value.length}/2000 characters
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="creative_images"
              render={() => (
                <FormItem>
                  <FormLabel>Image URLs (comma-separated)</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="https://example.com/image1.jpg, https://example.com/image2.jpg"
                      value={imagesInput}
                      onChange={(e) => handleImagesChange(e.target.value)}
                    />
                  </FormControl>
                  <FormDescription>
                    Enter image URLs separated by commas
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="creative_video_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Video URL (Optional)</FormLabel>
                  <FormControl>
                    <Input
                      type="url"
                      placeholder="https://example.com/video.mp4"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="flex gap-4">
              <Button type="submit" disabled={isLoading || !hasEnoughBalance}>
                {isLoading ? 'Creating...' : 'Create Campaign'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={isLoading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

