"""
Зависимости для маршрутов FastAPI.
Например, get_current_user для получения текущего авторизованного пользователя.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.core.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Получает текущего авторизованного пользователя из JWT токена.
    
    Args:
        credentials: HTTP Bearer токен из заголовка Authorization
        
    Returns:
        Данные пользователя из токена
        
    Raises:
        HTTPException: Если токен невалиден или пользователь не найден
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем пользователя из БД
    supabase = get_supabase_client()
    try:
        result = supabase.table("users").select("*").eq("id", user_id).single().execute()
        user = result.data
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user data"
        )

