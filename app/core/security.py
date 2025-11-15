"""
app/core/security.py
Модуль для работы с безопасностью: хеширование паролей, JWT токены.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Контекст для хеширования паролей с bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Алгоритм для JWT (должен совпадать с конфигом)
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием bcrypt.
    
    Args:
        password (str): Открытый пароль
    
    Returns:
        str: Хешированный пароль
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли открытый пароль хешированному.
    
    Args:
        plain_password (str): Открытый пароль
        hashed_password (str): Хешированный пароль из БД
    
    Returns:
        bool: True если пароли совпадают, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    secret_key: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создаёт JWT access token.
    
    Args:
        data (dict): Данные для включения в токен (user_id, email и т.д.)
        secret_key (str): Секретный ключ для подписи
        expires_delta (Optional[timedelta]): Время жизни токена
    
    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        logger.debug(f"Access token created for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise


def create_refresh_token(
    data: dict,
    secret_key: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создаёт JWT refresh token (с дольшим сроком жизни).
    
    Args:
        data (dict): Данные для включения в токен
        secret_key (str): Секретный ключ для подписи
        expires_delta (Optional[timedelta]): Время жизни токена
    
    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)  # Refresh на 7 дней
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        logger.debug(f"Refresh token created for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {str(e)}")
        raise


def decode_token(token: str, secret_key: str) -> Optional[dict]:
    """
    Декодирует и проверяет JWT токен.
    
    Args:
        token (str): JWT токен
        secret_key (str): Секретный ключ для проверки подписи
    
    Returns:
        Optional[dict]: Данные токена если валиден, иначе None
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        return None


def create_tokens(
    user_id: str,
    email: str,
    user_type: str,
    secret_key: str,
    access_expires_delta: Optional[timedelta] = None,
    refresh_expires_delta: Optional[timedelta] = None
) -> dict:
    """
    Создаёт пару (access_token, refresh_token).
    
    Args:
        user_id (str): ID пользователя
        email (str): Email пользователя
        user_type (str): Тип пользователя (seller, channel_owner, admin)
        secret_key (str): Секретный ключ
        access_expires_delta (Optional[timedelta]): TTL для access токена
        refresh_expires_delta (Optional[timedelta]): TTL для refresh токена
    
    Returns:
        dict: {"access_token": str, "refresh_token": str, "token_type": "bearer"}
    """
    data = {
        "sub": user_id,  # subject (обычно пользователь ID)
        "email": email,
        "user_type": user_type
    }
    
    access_token = create_access_token(data, secret_key, access_expires_delta)
    refresh_token = create_refresh_token(data, secret_key, refresh_expires_delta)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
