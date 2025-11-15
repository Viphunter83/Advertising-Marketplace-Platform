/**
 * components/common/RealTimeNotifications.tsx
 * Компонент для отображения real-time уведомлений через WebSocket
 */
'use client';

import React from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useNotifications, useMarkNotificationAsRead } from '@/hooks/useNotifications';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Bell, Check } from 'lucide-react';
import { formatRelativeTime } from '@/lib/formatting';

export function RealTimeNotifications() {
  // WebSocket уже инициализирован в providers.tsx, не нужно вызывать здесь
  // useWebSocket(); // УДАЛЕНО: дублирование инициализации
  const { data: notifications, isLoading } = useNotifications();
  const markAsRead = useMarkNotificationAsRead();
  
  const unreadCount = notifications?.filter(n => !n.read).length || 0;
  
  const handleMarkAsRead = async (notificationId: string) => {
    await markAsRead.mutateAsync(notificationId);
  };
  
  if (isLoading) {
    return (
      <Button variant="ghost" size="icon" disabled>
        <Bell className="h-5 w-5" />
      </Button>
    );
  }
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs">
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notifications</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {notifications && notifications.length > 0 ? (
          <>
            {notifications.slice(0, 5).map((notification) => (
              <DropdownMenuItem
                key={notification.id}
                className="flex flex-col items-start gap-1 p-3"
                onSelect={() => {
                  if (!notification.read) {
                    handleMarkAsRead(notification.id);
                  }
                }}
              >
                <div className="flex items-start justify-between w-full">
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{notification.title}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {notification.message}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {formatRelativeTime(notification.created_at || notification.timestamp)}
                    </div>
                  </div>
                  {!notification.read && (
                    <div className="h-2 w-2 bg-blue-500 rounded-full ml-2" />
                  )}
                </div>
              </DropdownMenuItem>
            ))}
            {notifications.length > 5 && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-center justify-center">
                  View all notifications
                </DropdownMenuItem>
              </>
            )}
          </>
        ) : (
          <DropdownMenuItem disabled>No notifications</DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

