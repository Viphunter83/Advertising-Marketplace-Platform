"""
Pydantic схемы для пользователей.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Схема для создания пользователя."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Пароль должен быть не менее 8 символов")
    phone: Optional[str] = None
    full_name: str = Field(..., min_length=1)
    user_type: str = Field(default="seller", pattern="^(seller|channel_owner|admin)$")


class UserLogin(BaseModel):
    """Схема для входа пользователя."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""
    id: str
    email: str
    phone: Optional[str] = None
    full_name: str
    user_type: str
    kyc_status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

