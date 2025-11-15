"""
Модель канала/паблика (channels таблица).
"""
from datetime import datetime
from typing import Optional
import uuid
import enum


class Platform(str, enum.Enum):
    """Платформа канала."""
    VK = "vk"
    TELEGRAM = "telegram"
    PINTEREST = "pinterest"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"


class AudienceGender(str, enum.Enum):
    """Пол аудитории."""
    M = "M"
    F = "F"
    ALL = "All"


class Channel:
    """
    Модель канала/паблика.
    Соответствует таблице channels в Supabase.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: Optional[str] = None,
        platform: Optional[str] = None,
        channel_url: Optional[str] = None,
        channel_name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        subscribers_count: Optional[int] = 0,
        avg_reach: Optional[int] = 0,
        engagement_rate: Optional[float] = 0.0,
        price_per_post: Optional[float] = 0.0,
        audience_geo: Optional[str] = None,
        audience_age_group: Optional[str] = None,
        audience_gender: Optional[str] = None,
        verified: Optional[bool] = False,
        rating: Optional[float] = 0.0,
        total_orders: Optional[int] = 0,
        total_earned: Optional[float] = 0.0,
        created_at: Optional[datetime] = None,
        **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.platform = platform
        self.channel_url = channel_url
        self.channel_name = channel_name
        self.description = description
        self.category = category
        self.subscribers_count = subscribers_count or 0
        self.avg_reach = avg_reach or 0
        self.engagement_rate = float(engagement_rate) if engagement_rate is not None else 0.0
        self.price_per_post = float(price_per_post) if price_per_post is not None else 0.0
        self.audience_geo = audience_geo
        self.audience_age_group = audience_age_group
        self.audience_gender = audience_gender or AudienceGender.ALL.value
        self.verified = verified or False
        self.rating = float(rating) if rating is not None else 0.0
        self.total_orders = total_orders or 0
        self.total_earned = float(total_earned) if total_earned is not None else 0.0
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для работы с Supabase."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform": self.platform,
            "channel_url": self.channel_url,
            "channel_name": self.channel_name,
            "description": self.description,
            "category": self.category,
            "subscribers_count": self.subscribers_count,
            "avg_reach": self.avg_reach,
            "engagement_rate": self.engagement_rate,
            "price_per_post": self.price_per_post,
            "audience_geo": self.audience_geo,
            "audience_age_group": self.audience_age_group,
            "audience_gender": self.audience_gender,
            "verified": self.verified,
            "rating": self.rating,
            "total_orders": self.total_orders,
            "total_earned": self.total_earned,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Channel":
        """Создает модель из словаря (из Supabase)."""
        return cls(**data)

