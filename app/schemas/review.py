"""
app/schemas/review.py
Pydantic модели для отзывов и рейтингов.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal


class ReviewCreate(BaseModel):
    """Схема для создания отзыва."""
    campaign_id: str = Field(..., description="ID заявки")
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    title: Optional[str] = Field(None, max_length=255, description="Заголовок отзыва")
    comment: str = Field(..., min_length=10, max_length=2000, description="Текст отзыва")
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "423e4567-e89b-12d3-a456-426614174000",
                "rating": 5,
                "title": "Отличное размещение!",
                "comment": "Владелец канала выполнил всё вовремя, аудитория качественная. Результат превзошёл ожидания!"
            }
        }


class ReviewResponse(BaseModel):
    """Ответ с информацией об отзыве."""
    id: str
    campaign_id: str
    seller_id: str
    channel_id: str
    
    rating: int
    title: Optional[str] = None
    comment: str
    
    ad_format: Optional[str] = None
    budget: Optional[Decimal] = None
    
    moderated: bool = False
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "523e4567-e89b-12d3-a456-426614174000",
                "campaign_id": "423e4567-e89b-12d3-a456-426614174000",
                "rating": 5,
                "title": "Отличное размещение!",
                "comment": "Владелец качественно разместил рекламу",
                "created_at": "2025-11-15T11:00:00Z"
            }
        }


class ChannelRatingResponse(BaseModel):
    """Агрегированный рейтинг канала."""
    channel_id: str
    channel_name: str
    
    average_rating: Decimal
    total_reviews: int
    rating_distribution: Dict[int, int]  # {1: 0, 2: 1, 3: 5, 4: 20, 5: 74}
    
    recent_reviews: List[ReviewResponse]


class SellerRatingResponse(BaseModel):
    """Рейтинг продавца."""
    seller_id: str
    shop_name: str
    
    average_rating: Decimal
    total_reviews: int
    positive_reviews_percent: Decimal

