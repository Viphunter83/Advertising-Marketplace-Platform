/**
 * hooks/index.ts
 * Экспорт всех hooks
 */
export { useAuth } from './useAuth';
export * from './useSeller';
export * from './useChannel';
export { useCampaigns } from './useCampaigns';
export { useCampaignById } from './useCampaignById';
export { useChannelSearch, useChannelById } from './useChannels';
export { useBalance } from './useBalance';
export { useTransactions } from './useTransactions';
export { useCampaignReviews, useCreateReview } from './useReviews';
export { useDisputes } from './useDisputes';
export { useWithdrawals } from './useWithdrawals';
export { usePlatformStats } from './useAdmin';
export { useNotifications, useMarkNotificationAsRead, useMarkAllNotificationsAsRead } from './useNotifications';
export { useWebSocket } from './useWebSocket';

