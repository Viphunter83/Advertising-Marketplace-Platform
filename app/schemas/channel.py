"""
app/schemas/channel.py
Pydantic модели для профилей каналов.
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


class PlatformEnum(str, Enum):
    """Поддерживаемые платформы."""
    VK = "vk"
    TELEGRAM = "telegram"
    PINTEREST = "pinterest"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"


class ChannelCreate(BaseModel):
    """Схема для создания профиля канала."""
    platform: PlatformEnum = Field(...)
    channel_url: str = Field(..., min_length=5, max_length=500)
    channel_name: str = Field(..., min_length=2, max_length=255)
    channel_description: Optional[str] = Field(None, max_length=1000)
    
    category: str = Field(..., description="Тематика канала")
    tags: Optional[List[str]] = Field(None, max_items=10)
    
    subscribers_count: int = Field(..., gt=0)
    avg_reach: int = Field(..., ge=0)
    engagement_rate: Decimal = Field(..., ge=0, le=100)
    
    audience_geo: Optional[str] = None
    audience_age_group: Optional[str] = None
    audience_gender: Optional[str] = Field(None, description="M, F или All")
    
    price_per_post: Decimal = Field(..., gt=0)
    price_per_story: Optional[Decimal] = Field(None, gt=0)
    price_per_video: Optional[Decimal] = Field(None, gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "vk",
                "channel_url": "https://vk.com/mychannel",
                "channel_name": "Мой канал о моде",
                "channel_description": "Тренды в моде и стиль жизни",
                "category": "Мода",
                "tags": ["lifestyle", "fashion", "shopping"],
                "subscribers_count": 50000,
                "avg_reach": 15000,
                "engagement_rate": 4.5,
                "audience_geo": "Москва",
                "audience_age_group": "18-25",
                "audience_gender": "F",
                "price_per_post": 5000.00,
                "price_per_story": 2000.00,
                "price_per_video": 10000.00
            }
        }


class ChannelUpdate(BaseModel):
    """Схема для обновления профиля канала."""
    channel_description: Optional[str] = None
    subscribers_count: Optional[int] = None
    avg_reach: Optional[int] = None
    engagement_rate: Optional[Decimal] = None
    
    price_per_post: Optional[Decimal] = None
    price_per_story: Optional[Decimal] = None
    price_per_video: Optional[Decimal] = None
    
    audience_geo: Optional[str] = None
    audience_age_group: Optional[str] = None
    audience_gender: Optional[str] = None
    
    auto_accept_campaigns: Optional[bool] = None
    max_campaigns_per_month: Optional[int] = None


class ChannelResponse(BaseModel):
    """Полный ответ с данными канала."""
    id: str
    user_id: str
    
    platform: str
    channel_url: str
    channel_name: str
    channel_description: Optional[str] = None
    channel_avatar_url: Optional[str] = None
    
    category: str
    tags: Optional[List[str]] = None
    
    subscribers_count: int
    avg_reach: int
    engagement_rate: Decimal
    audience_geo: Optional[str] = None
    audience_age_group: Optional[str] = None
    audience_gender: Optional[str] = None
    
    price_per_post: Decimal
    price_per_story: Optional[Decimal] = None
    price_per_video: Optional[Decimal] = None
    
    rating: Decimal
    total_orders: int
    completed_orders: int
    total_earned: Decimal
    
    verified: bool
    verification_date: Optional[str] = None
    is_active: bool
    
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "323e4567-e89b-12d3-a456-426614174000",
                "platform": "vk",
                "channel_name": "Мой канал о моде",
                "category": "Мода",
                "subscribers_count": 50000,
                "engagement_rate": 4.5,
                "rating": 4.8,
                "total_orders": 25,
                "completed_orders": 24,
                "total_earned": 125000.00,
                "verified": True,
                "is_active": True,
                "created_at": "2025-11-15T09:30:00Z"
            }
        }


class ChannelFilter(BaseModel):
    """Фильтры для поиска каналов."""
    platform: Optional[List[PlatformEnum]] = None
    category: Optional[List[str]] = None
    
    min_subscribers: Optional[int] = None
    max_subscribers: Optional[int] = None
    
    min_engagement_rate: Optional[Decimal] = None
    max_engagement_rate: Optional[Decimal] = None
    
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    
    geo: Optional[List[str]] = None
    age_group: Optional[List[str]] = None
    gender: Optional[str] = None
    
    min_rating: Optional[Decimal] = None
    verified_only: Optional[bool] = False
    
    sort_by: Optional[str] = Field(None, description="price, rating, subscribers, engagement_rate")
    sort_order: Optional[str] = Field(None, description="asc или desc")


class ChannelStatsResponse(BaseModel):
    """Статистика канала."""
    total_earned: Decimal
    total_orders: int
    completed_orders: int
    completion_rate: Decimal
    average_price: Optional[Decimal]
    rating: Decimal
    balance: Decimal
