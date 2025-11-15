/**
 * hooks/useWebSocket.ts
 * Hook для работы с WebSocket
 */
import { useEffect, useRef } from 'react';
import { connectSocket, disconnectSocket, onNotification, offNotification, isSocketConnected } from '@/lib/socket';
import { useAuthStore } from '@/lib/store/auth.store';
import toast from 'react-hot-toast';

export function useWebSocket() {
  const { user, isAuthenticated } = useAuthStore();
  const notificationHandlerRef = useRef<((notification: any) => void) | null>(null);
  
  useEffect(() => {
    if (!isAuthenticated || !user) {
      return;
    }
    
    // Получаем токен из localStorage
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      return;
    }
    
    // Подключаемся к WebSocket
    connectSocket(accessToken);
    
    // Обработчик уведомлений
    const handleNotification = (notification: any) => {
      toast.success(notification.message || 'New notification', {
        duration: 5000,
      });
    };
    
    notificationHandlerRef.current = handleNotification;
    onNotification(handleNotification);
    
    return () => {
      if (notificationHandlerRef.current) {
        offNotification(notificationHandlerRef.current);
      }
      disconnectSocket();
    };
  }, [isAuthenticated, user]);
  
  return {
    isConnected: isSocketConnected() || false,
  };
}

