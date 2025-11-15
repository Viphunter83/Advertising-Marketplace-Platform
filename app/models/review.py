"""
Модель отзыва (reviews таблица).
"""
from datetime import datetime
from typing import Optional
import uuid


class Review:
    """
    Модель отзыва на канал.
    Соответствует таблице reviews в Supabase.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        seller_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        rating: Optional[int] = 0,
        comment: Optional[str] = None,
        created_at: Optional[datetime] = None,
        **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.campaign_id = campaign_id
        self.seller_id = seller_id
        self.channel_id = channel_id
        self.rating = rating or 0
        self.comment = comment
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для работы с Supabase."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "seller_id": self.seller_id,
            "channel_id": self.channel_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Review":
        """Создает модель из словаря (из Supabase)."""
        return cls(**data)

