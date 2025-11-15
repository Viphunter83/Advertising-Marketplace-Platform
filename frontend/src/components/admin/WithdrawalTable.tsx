/**
 * components/admin/WithdrawalTable.tsx
 * Таблица запросов на вывод для админа
 */
'use client';

import React from 'react';
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { formatCurrency } from '@/lib/utils';
import { format } from 'date-fns';
import { CheckCircle2, XCircle } from 'lucide-react';
import { adminApi } from '@/lib/api/admin.api';
import toast from 'react-hot-toast';

interface Withdrawal {
  id: string;
  user_id: string;
  user_email?: string;
  amount: number;
  payment_method: string;
  account_number: string;
  status: 'pending' | 'processing' | 'completed' | 'rejected';
  created_at: string;
  processed_at?: string;
  admin_notes?: string;
}

interface WithdrawalTableProps {
  withdrawals: Withdrawal[];
  isLoading?: boolean;
  onUpdate?: () => void;
}

const statusConfig: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
  pending: { label: 'Pending', variant: 'outline' },
  processing: { label: 'Processing', variant: 'default' },
  completed: { label: 'Completed', variant: 'default' },
  rejected: { label: 'Rejected', variant: 'destructive' },
};

export function WithdrawalTable({ withdrawals, isLoading, onUpdate }: WithdrawalTableProps) {
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  const [selectedWithdrawal, setSelectedWithdrawal] = React.useState<Withdrawal | null>(null);
  const [actionDialogOpen, setActionDialogOpen] = React.useState(false);
  const [actionType, setActionType] = React.useState<'approve' | 'reject' | null>(null);
  const [notes, setNotes] = React.useState('');
  const [isProcessing, setIsProcessing] = React.useState(false);
  
  const filteredWithdrawals = React.useMemo(() => {
    if (statusFilter === 'all') return withdrawals;
    return withdrawals.filter(w => w.status === statusFilter);
  }, [withdrawals, statusFilter]);
  
  const handleAction = (withdrawal: Withdrawal, type: 'approve' | 'reject') => {
    setSelectedWithdrawal(withdrawal);
    setActionType(type);
    setActionDialogOpen(true);
    setNotes('');
  };
  
  const confirmAction = async () => {
    if (!selectedWithdrawal || !actionType) return;
    
    setIsProcessing(true);
    
    try {
      if (actionType === 'approve') {
        await adminApi.approveWithdrawal(selectedWithdrawal.id, notes || undefined);
        toast.success('Withdrawal approved successfully');
      } else {
        if (!notes.trim()) {
          toast.error('Notes are required for rejection');
          setIsProcessing(false);
          return;
        }
        await adminApi.rejectWithdrawal(selectedWithdrawal.id, notes);
        toast.success('Withdrawal rejected');
      }
      
      setActionDialogOpen(false);
      setSelectedWithdrawal(null);
      setActionType(null);
      setNotes('');
      onUpdate?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to process withdrawal.';
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Loading withdrawals...</p>
      </div>
    );
  }
  
  return (
    <>
      <div className="space-y-4">
        {/* Filter */}
        <div className="flex justify-end">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        {/* Table */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Account</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredWithdrawals.length > 0 ? (
                filteredWithdrawals.map((withdrawal) => {
                  const statusInfo = statusConfig[withdrawal.status] || statusConfig.pending;
                  const canApprove = withdrawal.status === 'pending';
                  const canReject = withdrawal.status === 'pending' || withdrawal.status === 'processing';
                  
                  return (
                    <TableRow key={withdrawal.id}>
                      <TableCell className="font-mono text-sm">
                        {withdrawal.id.slice(0, 8)}
                      </TableCell>
                      <TableCell>
                        {withdrawal.user_email || withdrawal.user_id.slice(0, 8)}
                      </TableCell>
                      <TableCell className="font-semibold">
                        {formatCurrency(withdrawal.amount)}
                      </TableCell>
                      <TableCell className="capitalize">
                        {withdrawal.payment_method}
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {withdrawal.account_number.slice(0, 8)}...
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
                      </TableCell>
                      <TableCell>
                        {format(new Date(withdrawal.created_at), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {canApprove && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleAction(withdrawal, 'approve')}
                            >
                              <CheckCircle2 className="h-4 w-4 mr-1" />
                              Approve
                            </Button>
                          )}
                          {canReject && (
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleAction(withdrawal, 'reject')}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Reject
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    No withdrawals found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
      
      {/* Action Dialog */}
      <Dialog open={actionDialogOpen} onOpenChange={setActionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {actionType === 'approve' ? 'Approve' : 'Reject'} Withdrawal
            </DialogTitle>
            <DialogDescription>
              {selectedWithdrawal && (
                <>
                  Amount: {formatCurrency(selectedWithdrawal.amount)}
                  <br />
                  Method: {selectedWithdrawal.payment_method}
                  <br />
                  Account: {selectedWithdrawal.account_number}
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="notes">
                Notes {actionType === 'reject' && '*'}
              </Label>
              <Textarea
                id="notes"
                placeholder={actionType === 'approve' 
                  ? 'Optional notes for approval...'
                  : 'Reason for rejection (required)...'}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="mt-2"
                required={actionType === 'reject'}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setActionDialogOpen(false);
                setSelectedWithdrawal(null);
                setActionType(null);
                setNotes('');
              }}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button
              variant={actionType === 'approve' ? 'default' : 'destructive'}
              onClick={confirmAction}
              disabled={isProcessing || (actionType === 'reject' && !notes.trim())}
            >
              {isProcessing 
                ? 'Processing...' 
                : actionType === 'approve' 
                ? 'Approve' 
                : 'Reject'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

