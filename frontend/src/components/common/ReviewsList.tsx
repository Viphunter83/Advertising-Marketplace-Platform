/**
 * components/common/ReviewsList.tsx
 * Список отзывов
 */
'use client';

import React from 'react';
import { Review } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { Star } from 'lucide-react';
import { formatDate } from '@/lib/formatting';

interface ReviewsListProps {
  reviews: Review[];
  isLoading?: boolean;
}

export function ReviewsList({ reviews, isLoading }: ReviewsListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/4" />
                <div className="h-4 bg-gray-200 rounded w-3/4" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  if (!reviews || reviews.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No reviews yet
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <Card key={review.id}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-4 w-4 ${
                      star <= review.rating
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-xs text-gray-500">
                {formatDate(review.created_at)}
              </span>
            </div>
            
            {review.title && (
              <h4 className="font-semibold mb-1">{review.title}</h4>
            )}
            
            <p className="text-sm text-gray-600">{review.comment}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

