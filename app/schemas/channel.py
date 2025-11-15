"""
Pydantic схемы для каналов.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class ChannelCreate(BaseModel):
    """Схема для создания канала."""
    platform: str = Field(..., pattern="^(vk|telegram|pinterest|instagram|tiktok)$")
    channel_url: str = Field(..., min_length=1)
    channel_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: Optional[str] = None
    subscribers_count: int = Field(default=0, ge=0)
    avg_reach: int = Field(default=0, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    price_per_post: float = Field(..., gt=0)
    audience_geo: Optional[str] = None
    audience_age_group: Optional[str] = None
    audience_gender: str = Field(default="All", pattern="^(M|F|All)$")


class ChannelFilter(BaseModel):
    """Схема для фильтрации каналов при поиске."""
    platform: Optional[str] = None
    category: Optional[str] = None
    min_subscribers: Optional[int] = Field(None, ge=0)
    max_subscribers: Optional[int] = Field(None, ge=0)
    min_engagement_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    max_engagement_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    geo: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(M|F|All)$")
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    max_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    sort_by: Optional[str] = Field(None, pattern="^(price|rating|subscribers|engagement_rate)$")


class ChannelResponse(BaseModel):
    """Схема ответа с данными канала."""
    id: str
    user_id: str
    platform: str
    channel_url: str
    channel_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    subscribers_count: int
    avg_reach: int
    engagement_rate: float
    price_per_post: float
    audience_geo: Optional[str] = None
    audience_age_group: Optional[str] = None
    audience_gender: str
    verified: bool
    rating: float
    total_orders: int
    total_earned: float
    created_at: datetime
    
    class Config:
        from_attributes = True

