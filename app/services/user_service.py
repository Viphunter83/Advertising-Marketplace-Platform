"""
app/services/user_service.py
Сервис для работы с пользователями: регистрация, вход, обновление профиля.
"""
import logging
import uuid
from datetime import timedelta, datetime, timezone
from typing import Optional, Tuple
from app.core.security import (
    hash_password,
    verify_password,
    create_tokens,
    decode_token
)
from app.core.database import get_supabase_client
from app.config import settings

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для управления пользователями."""
    
    @staticmethod
    async def register_user(
        email: str,
        password: str,
        full_name: str,
        phone: Optional[str],
        user_type: str
    ) -> dict:
        """
        Регистрирует нового пользователя.
        
        Args:
            email (str): Email пользователя
            password (str): Пароль
            full_name (str): ФИО
            phone (Optional[str]): Телефон
            user_type (str): Тип (seller или channel_owner)
        
        Returns:
            dict: Данные созданного пользователя
        
        Raises:
            ValueError: Если пользователь с таким email уже существует
        """
        supabase = get_supabase_client()
        
        # Проверяем, существует ли уже пользователь с таким email
        existing_user = supabase.table("users").select("*").eq("email", email).execute()
        
        if existing_user.data:
            logger.warning(f"User with email {email} already exists")
            raise ValueError(f"User with email {email} already exists")
        
        # Создаём новый пользователь
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        
        try:
            new_user = supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "password_hash": hashed_password,
                "phone": phone,
                "full_name": full_name,
                "user_type": user_type,
                "kyc_status": "not_verified",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            logger.info(f"User {email} registered successfully")
            return new_user.data[0] if new_user.data else {}
        
        except Exception as e:
            logger.error(f"Error registering user {email}: {str(e)}")
            raise ValueError(f"Error registering user: {str(e)}")
    
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[dict]:
        """
        Проверяет учётные данные пользователя.
        
        Args:
            email (str): Email пользователя
            password (str): Пароль
        
        Returns:
            Optional[dict]: Данные пользователя если аутентификация успешна, иначе None
        """
        supabase = get_supabase_client()
        
        # Ищем пользователя по email
        result = supabase.table("users").select("*").eq("email", email).execute()
        
        if not result.data:
            logger.warning(f"User not found: {email}")
            return None
        
        user = result.data[0]
        
        # Проверяем пароль
        if not verify_password(password, user["password_hash"]):
            logger.warning(f"Invalid password for user: {email}")
            return None
        
        if not user.get("is_active"):
            logger.warning(f"Inactive user login attempt: {email}")
            return None
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[dict]:
        """
        Получает пользователя по ID.
        
        Args:
            user_id (str): ID пользователя
        
        Returns:
            Optional[dict]: Данные пользователя или None
        """
        supabase = get_supabase_client()
        
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    
    @staticmethod
    async def update_user_profile(
        user_id: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> dict:
        """
        Обновляет профиль пользователя.
        
        Args:
            user_id (str): ID пользователя
            full_name (Optional[str]): Новое ФИО
            phone (Optional[str]): Новый телефон
        
        Returns:
            dict: Обновлённые данные пользователя
        """
        supabase = get_supabase_client()
        
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if full_name:
            update_data["full_name"] = full_name
        if phone:
            update_data["phone"] = phone
        
        try:
            result = supabase.table("users").update(update_data).eq("id", user_id).execute()
            logger.info(f"User {user_id} profile updated")
            return result.data[0] if result.data else {}
        
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise ValueError(f"Error updating profile: {str(e)}")
    
    
    @staticmethod
    async def change_password(
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Меняет пароль пользователя.
        
        Args:
            user_id (str): ID пользователя
            old_password (str): Старый пароль
            new_password (str): Новый пароль
        
        Returns:
            bool: True если пароль изменён
        
        Raises:
            ValueError: Если старый пароль неверен
        """
        supabase = get_supabase_client()
        
        # Получаем пользователя
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Проверяем старый пароль
        if not verify_password(old_password, user["password_hash"]):
            logger.warning(f"Invalid old password for user: {user_id}")
            raise ValueError("Invalid old password")
        
        # Хешируем новый пароль
        new_hashed = hash_password(new_password)
        
        try:
            supabase.table("users").update({
                "password_hash": new_hashed,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", user_id).execute()
            
            logger.info(f"Password changed for user: {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise ValueError(f"Error changing password: {str(e)}")
    
    
    @staticmethod
    def create_user_tokens(user_id: str, email: str, user_type: str) -> dict:
        """
        Создаёт пару токенов для пользователя.
        
        Args:
            user_id (str): ID пользователя
            email (str): Email пользователя
            user_type (str): Тип пользователя
        
        Returns:
            dict: {"access_token": str, "refresh_token": str, "token_type": "bearer"}
        """
        access_expires = timedelta(hours=settings.jwt_expiration_hours)
        refresh_expires = timedelta(days=7)
        
        tokens = create_tokens(
            user_id=user_id,
            email=email,
            user_type=user_type,
            secret_key=settings.jwt_secret_key,
            access_expires_delta=access_expires,
            refresh_expires_delta=refresh_expires
        )
        
        return tokens
    
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> dict:
        """
        Обновляет access token используя refresh token.
        
        Args:
            refresh_token (str): Refresh token
        
        Returns:
            dict: {"access_token": str, "refresh_token": str}
        
        Raises:
            ValueError: Если refresh token невалиден
        """
        # Декодируем refresh token
        payload = decode_token(refresh_token, settings.jwt_secret_key)
        
        if not payload or payload.get("type") != "refresh":
            logger.warning("Invalid refresh token")
            raise ValueError("Invalid refresh token")
        
        # Получаем данные пользователя из токена
        user_id = payload.get("sub")
        email = payload.get("email")
        user_type = payload.get("user_type")
        
        if not user_id or not email:
            raise ValueError("Invalid token data")
        
        # Создаём новые токены
        return UserService.create_user_tokens(user_id, email, user_type)

