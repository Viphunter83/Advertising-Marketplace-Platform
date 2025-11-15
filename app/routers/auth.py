"""
app/routers/auth.py
API endpoints для аутентификации.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from app.services.user_service import UserService
from app.core.dependencies import get_current_user
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    responses={
        201: {"description": "Пользователь успешно зарегистрирован"},
        400: {"description": "Некорректные данные или пользователь уже существует"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def register(user_data: UserRegister) -> TokenResponse:
    """
    Регистрирует нового пользователя (продавец или владелец канала).
    
    **Параметры**:
    - **email**: Email пользователя (уникальный)
    - **password**: Пароль (минимум 8 символов)
    - **full_name**: ФИО пользователя
    - **phone**: Телефон (опционально)
    - **user_type**: Тип пользователя ("seller" или "channel_owner")
    
    **Возвращает**:
    - **access_token**: JWT токен для использования в Protected endpoints
    - **refresh_token**: Токен для обновления access токена
    - **token_type**: "bearer"
    """
    try:
        # Регистрируем пользователя
        user = await UserService.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            user_type=user_data.user_type
        )
        
        # Создаём токены
        tokens = UserService.create_user_tokens(
            user_id=user["id"],
            email=user["email"],
            user_type=user["user_type"]
        )
        
        logger.info(f"User registered successfully: {user_data.email}")
        return TokenResponse(**tokens)
    
    except ValueError as e:
        logger.warning(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Вход в систему",
    responses={
        200: {"description": "Успешный вход"},
        401: {"description": "Неверные учётные данные"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def login(credentials: UserLogin) -> TokenResponse:
    """
    Вход пользователя в систему.
    
    **Параметры**:
    - **email**: Email пользователя
    - **password**: Пароль
    
    **Возвращает**:
    - **access_token**: JWT токен для использования в защищённых endpoints
    - **refresh_token**: Токен для обновления access токена
    - **token_type**: "bearer"
    
    **Примеры использования токена**:
    ```
    curl -H "Authorization: Bearer {access_token}" http://localhost:8000/auth/me
    ```
    """
    try:
        # Проверяем учётные данные
        user = await UserService.authenticate_user(
            email=credentials.email,
            password=credentials.password
        )
        
        if not user:
            logger.warning(f"Failed login attempt for: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Создаём токены
        tokens = UserService.create_user_tokens(
            user_id=user["id"],
            email=user["email"],
            user_type=user["user_type"]
        )
        
        logger.info(f"User logged in: {credentials.email}")
        return TokenResponse(**tokens)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging in"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление access токена",
    responses={
        200: {"description": "Access токен обновлен"},
        400: {"description": "Невалидный refresh token"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """
    Обновляет access token используя refresh token.
    
    **Параметры**:
    - **refresh_token**: Refresh token, полученный при логине
    
    **Возвращает**:
    - Новую пару токенов (access_token и refresh_token)
    """
    try:
        tokens = await UserService.refresh_access_token(request.refresh_token)
        logger.debug(f"Token refreshed")
        return TokenResponse(**tokens)
    
    except ValueError as e:
        logger.warning(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить текущего пользователя",
    responses={
        200: {"description": "Данные пользователя"},
        401: {"description": "Не авторизован"},
        404: {"description": "Пользователь не найден"}
    }
)
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Получает информацию о текущем авторизованном пользователе.
    
    **Требует**: Authorization заголовок с Bearer токеном
    
    **Пример**:
    ```
    curl -H "Authorization: Bearer {access_token}" http://localhost:8000/auth/me
    ```
    
    **Возвращает**:
    - **id**: UUID пользователя
    - **email**: Email пользователя
    - **full_name**: ФИО
    - **phone**: Телефон
    - **user_type**: Тип пользователя
    - **kyc_status**: Статус верификации
    - **is_active**: Активен ли аккаунт
    - **created_at**: Дата регистрации
    """
    try:
        user = await UserService.get_user_by_id(current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Преобразуем datetime в строку для ответа (если нужно)
        if isinstance(user.get("created_at"), str):
            user["created_at"] = user["created_at"]
        elif hasattr(user.get("created_at"), "isoformat"):
            user["created_at"] = user["created_at"].isoformat()
        else:
            user["created_at"] = str(user.get("created_at", ""))
        
        return UserResponse(**user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Выход из системы",
    responses={
        200: {"description": "Успешный выход"}
    }
)
async def logout(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Выход пользователя из системы (клиент должен удалить токены).
    
    **Требует**: Authorization заголовок с Bearer токеном
    
    **Примечание**: В простом JWT-based решении logout происходит на клиенте
    (удаление токенов из localStorage/cookies). На production нужна blacklist токенов.
    
    **Возвращает**:
    ```json
    {"message": "Successfully logged out"}
    ```
    """
    logger.info(f"User logged out: {current_user['email']}")
    return {"message": "Successfully logged out"}
