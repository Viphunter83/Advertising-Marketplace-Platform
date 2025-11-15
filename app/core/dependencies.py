"""
app/core/dependencies.py
Зависимости для использования в защищённых маршрутах (Dependency Injection).
"""
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.core.security import decode_token
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)

# Схема для извлечения Bearer токена из заголовка Authorization
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Зависимость для получения текущего пользователя из JWT токена.
    Используется в защищённых endpoints.
    
    Args:
        credentials (HTTPAuthorizationCredentials): Credentials из заголовка Authorization
    
    Returns:
        dict: Данные пользователя из токена {user_id, email, user_type}
    
    Raises:
        HTTPException: 401 Unauthorized если токен невалиден или истёк
    """
    token = credentials.credentials
    
    # Декодируем токен
    payload = decode_token(token, settings.jwt_secret_key)
    
    if payload is None:
        logger.warning(f"Invalid or expired token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем тип токена
    token_type = payload.get("type")
    if token_type != "access":
        logger.warning(f"Wrong token type: {token_type}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type, expected 'access' token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    email = payload.get("email")
    user_type = payload.get("user_type")
    
    if not user_id or not email:
        logger.warning(f"Token missing required fields")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required fields",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": user_id,
        "email": email,
        "user_type": user_type
    }


async def get_seller_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Зависимость для проверки, что пользователь — ПРОДАВЕЦ.
    Используется только в endpoints для продавцов.
    """
    if current_user["user_type"] != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available for sellers"
        )
    return current_user


async def get_channel_owner_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Зависимость для проверки, что пользователь — ВЛАДЕЛЕЦ КАНАЛА.
    """
    if current_user["user_type"] != "channel_owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available for channel owners"
        )
    return current_user


async def get_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Зависимость для проверки, что пользователь — АДМИНИСТРАТОР.
    """
    if current_user["user_type"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available for administrators"
        )
    return current_user
