"""
app/core/websocket.py
WebSocket сервер для real-time уведомлений.
"""
import logging
import socketio
from typing import Dict, Set
from app.config import settings

logger = logging.getLogger(__name__)

# Создаём Socket.io сервер
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.websocket_cors_origins,
    logger=True,
    engineio_logger=True
)

# Хранилище активных подключений: user_id -> set of session_ids
active_connections: Dict[str, Set[str]] = {}


@sio.event
async def connect(sid, environ, auth):
    """
    Клиент подключается к WebSocket.
    
    Auth должен содержать JWT токен:
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    """
    try:
        if not auth or 'token' not in auth:
            logger.warning(f"Connection rejected: no token provided (sid={sid})")
            return False
        
        # Декодируем токен
        from app.core.security import decode_token
        
        token = auth['token']
        payload = decode_token(token, settings.jwt_secret_key)
        
        if not payload or payload.get('type') != 'access':
            logger.warning(f"Connection rejected: invalid token (sid={sid})")
            return False
        
        user_id = payload.get('sub')
        
        if not user_id:
            logger.warning(f"Connection rejected: no user_id in token (sid={sid})")
            return False
        
        # Сохраняем подключение
        if user_id not in active_connections:
            active_connections[user_id] = set()
        
        active_connections[user_id].add(sid)
        
        # Присоединяем к комнате пользователя
        await sio.enter_room(sid, f"user_{user_id}")
        
        logger.info(f"User {user_id} connected (sid={sid})")
        
        # Отправляем подтверждение
        await sio.emit('connected', {'status': 'ok', 'user_id': user_id}, to=sid)
        
        return True
    
    except Exception as e:
        logger.error(f"Error in connect handler: {str(e)}")
        return False


@sio.event
async def disconnect(sid):
    """Клиент отключается."""
    try:
        # Находим пользователя и удаляем подключение
        for user_id, sessions in list(active_connections.items()):
            if sid in sessions:
                sessions.remove(sid)
                
                if not sessions:
                    del active_connections[user_id]
                
                logger.info(f"User {user_id} disconnected (sid={sid})")
                break
    
    except Exception as e:
        logger.error(f"Error in disconnect handler: {str(e)}")


@sio.event
async def ping(sid, data):
    """Heartbeat для поддержания соединения."""
    await sio.emit('pong', {'timestamp': data.get('timestamp')}, to=sid)


async def send_notification_to_user(user_id: str, notification: dict):
    """
    Отправляет уведомление конкретному пользователю.
    
    Args:
        user_id (str): ID пользователя
        notification (dict): Данные уведомления
    """
    try:
        room = f"user_{user_id}"
        await sio.emit('notification', notification, room=room)
        logger.info(f"Notification sent to user {user_id}: {notification.get('type')}")
    
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")


async def broadcast_notification(notification: dict):
    """Отправляет уведомление всем подключённым пользователям."""
    try:
        await sio.emit('notification', notification)
        logger.info(f"Broadcast notification sent: {notification.get('type')}")
    
    except Exception as e:
        logger.error(f"Error broadcasting notification: {str(e)}")


def get_active_users() -> list:
    """Возвращает список активных пользователей."""
    return list(active_connections.keys())


def is_user_online(user_id: str) -> bool:
    """Проверяет, онлайн ли пользователь."""
    return user_id in active_connections and len(active_connections[user_id]) > 0

