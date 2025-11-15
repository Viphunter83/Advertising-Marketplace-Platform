/**
 * components/campaigns/CampaignTimeline.tsx
 * Timeline с этапами заявки
 */
'use client';

import React from 'react';
import { Campaign } from '@/lib/types';
import { format } from 'date-fns';
import { 
  CheckCircle2, 
  Circle, 
  Clock, 
  XCircle,
  FileText,
  Send,
  CheckSquare,
  Trophy
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TimelineStep {
  id: string;
  label: string;
  icon: React.ReactNode;
  date?: string;
  completed: boolean;
  current: boolean;
}

export function CampaignTimeline({ campaign }: { campaign: Campaign }) {
  const steps: TimelineStep[] = [
    {
      id: 'created',
      label: 'Created',
      icon: <FileText className="h-5 w-5" />,
      date: campaign.created_at,
      completed: true,
      current: campaign.status === 'pending',
    },
    {
      id: 'accepted',
      label: 'Accepted',
      icon: <CheckCircle2 className="h-5 w-5" />,
      date: campaign.status === 'accepted' || campaign.status === 'in_progress' || campaign.status === 'completed' 
        ? campaign.updated_at 
        : undefined,
      completed: ['accepted', 'in_progress', 'completed'].includes(campaign.status),
      current: campaign.status === 'accepted',
    },
    {
      id: 'submitted',
      label: 'Placement Submitted',
      icon: <Send className="h-5 w-5" />,
      date: campaign.owner_submitted_at,
      completed: !!campaign.owner_submitted_at,
      current: campaign.status === 'in_progress' && !!campaign.owner_submitted_at,
    },
    {
      id: 'confirmed',
      label: 'Confirmed by Seller',
      icon: <CheckSquare className="h-5 w-5" />,
      date: campaign.seller_confirmed_at,
      completed: !!campaign.seller_confirmed_at,
      current: campaign.status === 'completed' && !!campaign.seller_confirmed_at,
    },
    {
      id: 'completed',
      label: 'Completed',
      icon: <Trophy className="h-5 w-5" />,
      date: campaign.actual_completion_date || campaign.seller_confirmed_at,
      completed: campaign.status === 'completed',
      current: campaign.status === 'completed',
    },
  ];
  
  // Если отклонено или отменено
  if (campaign.status === 'rejected' || campaign.status === 'cancelled') {
    steps[1] = {
      ...steps[1],
      label: campaign.status === 'rejected' ? 'Rejected' : 'Cancelled',
      icon: <XCircle className="h-5 w-5" />,
      completed: true,
      current: false,
    };
  }
  
  return (
    <div className="relative">
      <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />
      
      <div className="space-y-6">
        {steps.map((step, index) => (
          <div key={step.id} className="relative flex items-start gap-4">
            <div
              className={cn(
                "relative z-10 flex h-10 w-10 items-center justify-center rounded-full border-2 bg-white",
                step.completed
                  ? "border-green-500 bg-green-50 text-green-600"
                  : step.current
                  ? "border-blue-500 bg-blue-50 text-blue-600"
                  : "border-gray-300 bg-gray-50 text-gray-400"
              )}
            >
              {step.completed ? (
                <CheckCircle2 className="h-5 w-5" />
              ) : step.current ? (
                <Clock className="h-5 w-5" />
              ) : (
                <Circle className="h-5 w-5" />
              )}
            </div>
            
            <div className="flex-1 pt-1">
              <div className="flex items-center justify-between">
                <h4
                  className={cn(
                    "font-semibold",
                    step.completed || step.current
                      ? "text-gray-900"
                      : "text-gray-400"
                  )}
                >
                  {step.label}
                </h4>
                {step.date && (
                  <span className="text-sm text-gray-500">
                    {format(new Date(step.date), 'MMM dd, yyyy HH:mm')}
                  </span>
                )}
              </div>
              
              {step.current && !step.completed && (
                <p className="mt-1 text-sm text-blue-600">In progress...</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

