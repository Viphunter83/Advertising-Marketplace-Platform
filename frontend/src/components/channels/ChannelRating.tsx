/**
 * components/channels/ChannelRating.tsx
 * Рейтинг канала с отзывами
 */
'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { channelsApi } from '@/lib/api/channels.api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Star } from 'lucide-react';
import { Loader2 } from 'lucide-react';
import { ChannelRating as ChannelRatingType } from '@/lib/types';

interface ChannelRatingProps {
  channelId: string;
}

export function ChannelRating({ channelId }: ChannelRatingProps) {
  const { data: ratingData, isLoading } = useQuery({
    queryKey: ['channel', channelId, 'rating'],
    queryFn: async () => {
      return await channelsApi.getChannelRating(channelId);
    },
    enabled: !!channelId,
  });
  
  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <Loader2 className="h-6 w-6 animate-spin mx-auto" />
        </CardContent>
      </Card>
    );
  }
  
  if (!ratingData || ratingData.total_reviews === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Rating</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">No reviews yet</p>
        </CardContent>
      </Card>
    );
  }
  
  const { average_rating, total_reviews, rating_distribution, recent_reviews } = ratingData;
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Rating & Reviews</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Rating */}
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-4xl font-bold">{average_rating.toFixed(1)}</div>
            <div className="flex items-center justify-center mt-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`h-5 w-5 ${
                    star <= Math.round(average_rating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {total_reviews} {total_reviews === 1 ? 'review' : 'reviews'}
            </div>
          </div>
          
          {/* Distribution */}
          <div className="flex-1 space-y-2">
            {[5, 4, 3, 2, 1].map((rating) => {
              const count = rating_distribution[rating] || 0;
              const percentage = total_reviews > 0 ? (count / total_reviews) * 100 : 0;
              
              return (
                <div key={rating} className="flex items-center gap-2">
                  <div className="flex items-center gap-1 w-16">
                    <span className="text-sm">{rating}</span>
                    <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                  </div>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-yellow-400 transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 w-12 text-right">
                    {count}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Recent Reviews */}
        {recent_reviews && recent_reviews.length > 0 && (
          <div className="border-t pt-4">
            <h4 className="font-semibold mb-3">Recent Reviews</h4>
            <div className="space-y-4">
              {recent_reviews.slice(0, 3).map((review: any) => (
                <div key={review.id} className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="flex">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`h-3 w-3 ${
                            star <= review.rating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(review.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {review.title && (
                    <div className="font-semibold text-sm">{review.title}</div>
                  )}
                  <p className="text-sm text-gray-600">{review.comment}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

