"""
Модель уведомления (notifications таблица).
"""
from datetime import datetime
from typing import Optional
import uuid


class Notification:
    """
    Модель уведомления пользователя.
    Соответствует таблице notifications в Supabase.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: Optional[str] = None,
        type: Optional[str] = None,
        title: Optional[str] = None,
        message: Optional[str] = None,
        read: Optional[bool] = False,
        created_at: Optional[datetime] = None,
        **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.type = type
        self.title = title
        self.message = message
        self.read = read or False
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для работы с Supabase."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "read": self.read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """Создает модель из словаря (из Supabase)."""
        return cls(**data)

