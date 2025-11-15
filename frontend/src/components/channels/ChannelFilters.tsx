/**
 * components/channels/ChannelFilters.tsx
 * Фильтры для поиска каналов
 */
'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { ChannelFilters as ChannelFiltersType } from '@/lib/api/channels.api';
import { X } from 'lucide-react';

interface ChannelFiltersProps {
  onFiltersChange: (filters: ChannelFiltersType) => void;
  isLoading?: boolean;
}

const PLATFORMS = [
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

const SORT_OPTIONS = [
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
  { value: 'rating_desc', label: 'Rating: High to Low' },
  { value: 'subscribers_desc', label: 'Subscribers: High to Low' },
  { value: 'engagement_desc', label: 'Engagement: High to Low' },
];

export function ChannelFilters({ onFiltersChange, isLoading }: ChannelFiltersProps) {
  const [filters, setFilters] = React.useState<ChannelFiltersType>({
    platforms: [],
    category: undefined,
    min_subscribers: undefined,
    max_subscribers: undefined,
    min_engagement_rate: undefined,
    max_engagement_rate: undefined,
    max_price: undefined,
    audience_geo: undefined,
    min_rating: undefined,
    verified: undefined,
  });
  
  const [sortBy, setSortBy] = React.useState<string>('price_asc');
  const [subscribersRange, setSubscribersRange] = React.useState<[number, number]>([0, 10000000]);
  const [engagementRange, setEngagementRange] = React.useState<[number, number]>([0, 100]);
  const [priceRange, setPriceRange] = React.useState<[number, number]>([0, 1000000]);
  
  React.useEffect(() => {
    const updatedFilters: ChannelFiltersType = {
      ...filters,
      min_subscribers: subscribersRange[0] > 0 ? subscribersRange[0] : undefined,
      max_subscribers: subscribersRange[1] < 10000000 ? subscribersRange[1] : undefined,
      min_engagement_rate: engagementRange[0] > 0 ? engagementRange[0] : undefined,
      max_engagement_rate: engagementRange[1] < 100 ? engagementRange[1] : undefined,
      max_price: priceRange[1] < 1000000 ? priceRange[1] : undefined,
    };
    setFilters(updatedFilters);
    onFiltersChange(updatedFilters);
  }, [subscribersRange, engagementRange, priceRange]);
  
  const handlePlatformToggle = (platform: string) => {
    const current = filters.platforms || [];
    const updated = current.includes(platform)
      ? current.filter(p => p !== platform)
      : [...current, platform];
    
    const newFilters = { ...filters, platforms: updated };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };
  
  const handleFilterChange = (key: keyof ChannelFiltersType, value: any) => {
    const newFilters = { ...filters, [key]: value || undefined };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };
  
  const clearFilters = () => {
    const cleared: ChannelFiltersType = {
      platforms: [],
      category: undefined,
      min_subscribers: undefined,
      max_subscribers: undefined,
      min_engagement_rate: undefined,
      max_engagement_rate: undefined,
      max_price: undefined,
      audience_geo: undefined,
      min_rating: undefined,
      verified: undefined,
    };
    setFilters(cleared);
    setSubscribersRange([0, 10000000]);
    setEngagementRange([0, 100]);
    setPriceRange([0, 1000000]);
    setSortBy('price_asc');
    onFiltersChange(cleared);
  };
  
  const hasActiveFilters = 
    (filters.platforms && filters.platforms.length > 0) ||
    filters.category ||
    filters.audience_geo ||
    filters.min_rating ||
    filters.verified !== undefined;
  
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Filters</CardTitle>
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X className="h-4 w-4 mr-1" />
              Clear
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Sort */}
        <div>
          <Label>Sort By</Label>
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {SORT_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Platforms */}
        <div>
          <Label className="mb-3 block">Platforms</Label>
          <div className="space-y-2">
            {PLATFORMS.map((platform) => (
              <div key={platform.value} className="flex items-center space-x-2">
                <Checkbox
                  id={platform.value}
                  checked={filters.platforms?.includes(platform.value)}
                  onCheckedChange={() => handlePlatformToggle(platform.value)}
                />
                <Label
                  htmlFor={platform.value}
                  className="text-sm font-normal cursor-pointer"
                >
                  {platform.label}
                </Label>
              </div>
            ))}
          </div>
        </div>
        
        {/* Category */}
        <div>
          <Label>Category</Label>
          <Select
            value={filters.category || ''}
            onValueChange={(value) => handleFilterChange('category', value || undefined)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All categories</SelectItem>
              {CATEGORIES.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Subscribers Range */}
        <div>
          <Label>
            Subscribers: {subscribersRange[0].toLocaleString()} - {subscribersRange[1].toLocaleString()}
          </Label>
          <Slider
            value={subscribersRange}
            onValueChange={(value) => setSubscribersRange(value as [number, number])}
            min={0}
            max={10000000}
            step={10000}
            className="mt-2"
          />
        </div>
        
        {/* Engagement Rate Range */}
        <div>
          <Label>
            Engagement Rate: {engagementRange[0].toFixed(1)}% - {engagementRange[1].toFixed(1)}%
          </Label>
          <Slider
            value={engagementRange}
            onValueChange={(value) => setEngagementRange(value as [number, number])}
            min={0}
            max={100}
            step={0.1}
            className="mt-2"
          />
        </div>
        
        {/* Price Range */}
        <div>
          <Label>
            Max Price: ₽{priceRange[1].toLocaleString()}
          </Label>
          <Slider
            value={[priceRange[1]]}
            onValueChange={(value) => setPriceRange([0, value[0]])}
            min={0}
            max={1000000}
            step={1000}
            className="mt-2"
          />
        </div>
        
        {/* Audience Geo */}
        <div>
          <Label>Audience Location</Label>
          <Input
            placeholder="Russia, Ukraine, etc."
            value={filters.audience_geo || ''}
            onChange={(e) => handleFilterChange('audience_geo', e.target.value || undefined)}
          />
        </div>
        
        {/* Age Group */}
        <div>
          <Label>Age Group</Label>
          <Select
            value={filters.audience_age_group || ''}
            onValueChange={(value) => handleFilterChange('audience_age_group', value || undefined)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Any</SelectItem>
              {AGE_GROUPS.map((age) => (
                <SelectItem key={age} value={age}>
                  {age}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Gender */}
        <div>
          <Label>Gender</Label>
          <Select
            value={filters.audience_gender || ''}
            onValueChange={(value) => handleFilterChange('audience_gender', value || undefined)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Any</SelectItem>
              {GENDERS.map((gender) => (
                <SelectItem key={gender} value={gender}>
                  {gender}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Min Rating */}
        <div>
          <Label>Min Rating</Label>
          <Select
            value={filters.min_rating?.toString() || ''}
            onValueChange={(value) => handleFilterChange('min_rating', value ? parseFloat(value) : undefined)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Any</SelectItem>
              {[4.5, 4.0, 3.5, 3.0, 2.5, 2.0].map((rating) => (
                <SelectItem key={rating} value={rating.toString()}>
                  {rating}+ stars
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Verified Only */}
        <div className="flex items-center space-x-2">
          <Checkbox
            id="verified"
            checked={filters.verified === true}
            onCheckedChange={(checked) => handleFilterChange('verified', checked ? true : undefined)}
          />
          <Label htmlFor="verified" className="text-sm font-normal cursor-pointer">
            Verified channels only
          </Label>
        </div>
      </CardContent>
    </Card>
  );
}

