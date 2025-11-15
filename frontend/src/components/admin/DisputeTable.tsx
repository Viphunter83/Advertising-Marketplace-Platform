/**
 * components/admin/DisputeTable.tsx
 * Таблица споров для админа
 */
'use client';

import React from 'react';
import Link from 'next/link';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Dispute } from '@/lib/types';
import { format } from 'date-fns';
import { Eye } from 'lucide-react';

interface DisputeTableProps {
  disputes: Dispute[];
  isLoading?: boolean;
}

const statusConfig: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
  open: { label: 'Open', variant: 'destructive' },
  in_review: { label: 'In Review', variant: 'outline' },
  resolved: { label: 'Resolved', variant: 'default' },
  closed: { label: 'Closed', variant: 'secondary' },
};

export function DisputeTable({ disputes, isLoading }: DisputeTableProps) {
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  
  const filteredDisputes = React.useMemo(() => {
    if (statusFilter === 'all') return disputes;
    return disputes.filter(d => d.status === statusFilter);
  }, [disputes, statusFilter]);
  
  if (isLoading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Loading disputes...</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {/* Filter */}
      <div className="flex justify-end">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="in_review">In Review</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      {/* Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Campaign</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredDisputes.length > 0 ? (
              filteredDisputes.map((dispute) => {
                const statusInfo = statusConfig[dispute.status] || statusConfig.open;
                
                return (
                  <TableRow key={dispute.id}>
                    <TableCell className="font-mono text-sm">
                      {dispute.id.slice(0, 8)}
                    </TableCell>
                    <TableCell>
                      <Link 
                        href={`/admin/disputes/${dispute.id}`}
                        className="text-blue-600 hover:underline"
                      >
                        Campaign #{dispute.campaign_id.slice(0, 8)}
                      </Link>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {dispute.reason || '-'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
                    </TableCell>
                    <TableCell>
                      {format(new Date(dispute.created_at), 'MMM dd, yyyy')}
                    </TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline" asChild>
                        <Link href={`/admin/disputes/${dispute.id}`}>
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                  No disputes found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

