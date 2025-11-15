'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/lib/api/admin.api';
import { useCampaignById } from '@/hooks/useCampaignById';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatCurrency } from '@/lib/utils';
import { format } from 'date-fns';
import { Loader2, ArrowLeft } from 'lucide-react';
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
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import toast from 'react-hot-toast';

export default function DisputeDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const disputeId = params.id as string;
  const [resolveDialogOpen, setResolveDialogOpen] = React.useState(false);
  const [decision, setDecision] = React.useState<'refund' | 'release_payment' | 'partial_refund'>('refund');
  const [notes, setNotes] = React.useState('');
  const [refundAmount, setRefundAmount] = React.useState('');
  const [isProcessing, setIsProcessing] = React.useState(false);
  
  const { data: disputes } = useQuery({
    queryKey: ['disputes'],
    queryFn: async () => {
      return await adminApi.getDisputes();
    },
  });
  
  const dispute = disputes?.find(d => d.id === disputeId);
  const { data: campaign } = useCampaignById(dispute?.campaign_id || '');
  
  const handleResolve = async () => {
    if (!dispute) return;
    
    setIsProcessing(true);
    
    try {
      await adminApi.resolveDispute(dispute.id, {
        decision,
        refund_amount: decision === 'partial_refund' ? parseFloat(refundAmount) : undefined,
        notes,
      });
      
      toast.success('Dispute resolved successfully');
      setResolveDialogOpen(false);
      router.push('/admin/disputes');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to resolve dispute.';
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };
  
  if (!dispute) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <h1 className="text-3xl font-bold">Dispute Details</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Dispute Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm text-gray-600">Status</div>
              <Badge>{dispute.status}</Badge>
            </div>
            <div>
              <div className="text-sm text-gray-600">Created</div>
              <div>{format(new Date(dispute.created_at), 'PPP p')}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Reason</div>
              <div className="font-semibold">{dispute.reason}</div>
            </div>
            {dispute.description && (
              <div>
                <div className="text-sm text-gray-600">Description</div>
                <div>{dispute.description}</div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {campaign && (
          <Card>
            <CardHeader>
              <CardTitle>Campaign Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-gray-600">Campaign ID</div>
                <div className="font-mono">{campaign.id.slice(0, 8)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Budget</div>
                <div className="font-semibold">{formatCurrency(campaign.budget)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Status</div>
                <Badge>{campaign.status}</Badge>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
      
      {dispute.status !== 'resolved' && dispute.status !== 'closed' && (
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={() => setResolveDialogOpen(true)}>
              Resolve Dispute
            </Button>
          </CardContent>
        </Card>
      )}
      
      {/* Resolve Dialog */}
      <Dialog open={resolveDialogOpen} onOpenChange={setResolveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolve Dispute</DialogTitle>
            <DialogDescription>
              Choose how to resolve this dispute
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label>Decision</Label>
              <RadioGroup value={decision} onValueChange={(v) => setDecision(v as any)}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="refund" id="refund" />
                  <Label htmlFor="refund">Full Refund to Seller</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="release_payment" id="release" />
                  <Label htmlFor="release">Release Payment to Channel Owner</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="partial_refund" id="partial" />
                  <Label htmlFor="partial">Partial Refund</Label>
                </div>
              </RadioGroup>
            </div>
            
            {decision === 'partial_refund' && campaign && (
              <div>
                <Label>Refund Amount (max {formatCurrency(campaign.budget)})</Label>
                <input
                  type="number"
                  value={refundAmount}
                  onChange={(e) => setRefundAmount(e.target.value)}
                  max={campaign.budget}
                  min={0}
                  className="mt-2 w-full px-3 py-2 border rounded-md"
                />
              </div>
            )}
            
            <div>
              <Label>Notes *</Label>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add notes about the resolution..."
                className="mt-2"
                required
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setResolveDialogOpen(false)}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleResolve}
              disabled={isProcessing || !notes.trim()}
            >
              {isProcessing ? 'Processing...' : 'Resolve'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

