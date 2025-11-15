/**
 * components/admin/StatsOverview.tsx
 * Обзор статистики платформы
 */
'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PlatformStats } from '@/lib/types';
import { formatCurrency } from '@/lib/utils';
import { 
  DollarSign, 
  Users, 
  TrendingUp, 
  CheckCircle2,
  Activity
} from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface StatsOverviewProps {
  stats: PlatformStats | null;
  isLoading?: boolean;
}

export function StatsOverview({ stats, isLoading }: StatsOverviewProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  if (!stats) {
    return <div className="text-center py-8 text-gray-500">No statistics available</div>;
  }
  
  const completionRate = stats.total_campaigns > 0 
    ? ((stats.completed_campaigns / stats.total_campaigns) * 100).toFixed(1)
    : '0';
  
  const kpiCards = [
    {
      title: 'Total GMV',
      value: formatCurrency(stats.gmv || 0),
      icon: DollarSign,
      description: 'Gross Merchandise Value',
      color: 'text-green-600',
    },
    {
      title: 'Platform Revenue',
      value: formatCurrency(stats.platform_revenue || 0),
      icon: TrendingUp,
      description: 'Total commission earned',
      color: 'text-blue-600',
    },
    {
      title: 'Total Users',
      value: stats.total_users.toLocaleString(),
      icon: Users,
      description: 'Registered users',
      color: 'text-purple-600',
    },
    {
      title: 'Active Campaigns',
      value: (stats.total_campaigns - stats.completed_campaigns).toLocaleString(),
      icon: Activity,
      description: 'Currently running',
      color: 'text-orange-600',
    },
    {
      title: 'Completion Rate',
      value: `${completionRate}%`,
      icon: CheckCircle2,
      description: 'Campaigns completed',
      color: 'text-indigo-600',
    },
  ];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {kpiCards.map((kpi) => {
        const Icon = kpi.icon;
        return (
          <Card key={kpi.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{kpi.title}</CardTitle>
              <Icon className={`h-4 w-4 ${kpi.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpi.value}</div>
              <p className="text-xs text-gray-500 mt-1">{kpi.description}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

