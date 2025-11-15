"""
Маршруты для аутентификации: регистрация, вход, обновление токена.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.database import get_supabase_client
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Регистрация нового пользователя.
    
    Args:
        user_data: Данные для регистрации (email, password, full_name, user_type)
        
    Returns:
        Данные созданного пользователя
        
    Raises:
        HTTPException: Если пользователь с таким email уже существует
    """
    supabase = get_supabase_client()
    
    # Проверяем, существует ли пользователь с таким email
    try:
        existing_user = supabase.table("users").select("id").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking existing user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during registration"
        )
    
    # Хешируем пароль
    password_hash = get_password_hash(user_data.password)
    
    # Создаем модель пользователя
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        phone=user_data.phone,
        full_name=user_data.full_name,
        user_type=user_data.user_type
    )
    
    # Сохраняем в БД
    try:
        result = supabase.table("users").insert(user.to_dict()).execute()
        created_user = result.data[0] if result.data else None
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Убираем password_hash из ответа
        created_user.pop("password_hash", None)
        
        logger.info(f"User registered: {user_data.email}")
        return UserResponse(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during registration"
        )


@router.post("/login", response_model=dict)
async def login(credentials: UserLogin):
    """
    Вход пользователя. Возвращает JWT токен.
    
    Args:
        credentials: Email и пароль
        
    Returns:
        Словарь с access_token и user данными
        
    Raises:
        HTTPException: Если email или пароль неверны
    """
    supabase = get_supabase_client()
    
    try:
        # Ищем пользователя по email
        result = supabase.table("users").select("*").eq("email", credentials.email).execute()
        user_data = None
        
        if result.data and len(result.data) > 0:
            user_data = result.data[0]
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Проверяем пароль
        if not verify_password(credentials.password, user_data.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Проверяем, активен ли пользователь
        if not user_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Создаем JWT токен
        access_token = create_access_token(
            data={"sub": user_data["id"], "email": user_data["email"]}
        )
        
        # Убираем password_hash из ответа
        user_data.pop("password_hash", None)
        
        logger.info(f"User logged in: {credentials.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

