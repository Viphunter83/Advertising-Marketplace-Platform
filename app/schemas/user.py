"""
app/schemas/user.py
Pydantic модели для аутентификации и работы с пользователями.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional


class UserRegister(BaseModel):
    """Схема для регистрации нового пользователя."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    user_type: Literal["seller", "channel_owner"] = Field(
        ..., 
        description="Тип пользователя: seller (продавец) или channel_owner (владелец канала)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "seller@example.com",
                "password": "secure_password_123",
                "full_name": "Иван Петров",
                "phone": "+7 (999) 123-45-67",
                "user_type": "seller"
            }
        }


class UserLogin(BaseModel):
    """Схема для входа пользователя."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "seller@example.com",
                "password": "secure_password_123"
            }
        }


class TokenResponse(BaseModel):
    """Схема для ответа с токенами."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Схема для обновления access токена."""
    refresh_token: str


class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя."""
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    user_type: str
    kyc_status: str
    is_active: bool
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "seller@example.com",
                "full_name": "Иван Петров",
                "phone": "+7 (999) 123-45-67",
                "user_type": "seller",
                "kyc_status": "not_verified",
                "is_active": True,
                "created_at": "2025-11-15T09:30:00Z"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Схема для смены пароля."""
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "old_password_123",
                "new_password": "new_secure_password_456"
            }
        }
