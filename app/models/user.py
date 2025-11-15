"""
Модель пользователя (users таблица).
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


class UserType(str, enum.Enum):
    """Тип пользователя."""
    SELLER = "seller"
    CHANNEL_OWNER = "channel_owner"
    ADMIN = "admin"


class KYCStatus(str, enum.Enum):
    """Статус верификации пользователя."""
    NOT_VERIFIED = "not_verified"
    PENDING = "pending"
    VERIFIED = "verified"


# SQLAlchemy модель (для миграций и работы с ORM)
# В Supabase мы используем прямые запросы через SDK, но модели помогают структурировать код
class User:
    """
    Модель пользователя.
    Соответствует таблице users в Supabase.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
        phone: Optional[str] = None,
        full_name: Optional[str] = None,
        user_type: Optional[str] = None,
        kyc_status: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_active: Optional[bool] = True,
        **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.full_name = full_name
        self.user_type = user_type or UserType.SELLER.value
        self.kyc_status = kyc_status or KYCStatus.NOT_VERIFIED.value
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.is_active = is_active
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для работы с Supabase."""
        return {
            "id": self.id,
            "email": self.email,
            "password_hash": self.password_hash,
            "phone": self.phone,
            "full_name": self.full_name,
            "user_type": self.user_type,
            "kyc_status": self.kyc_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Создает модель из словаря (из Supabase)."""
        return cls(**data)

