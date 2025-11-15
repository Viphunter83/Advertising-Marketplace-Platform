"""
app/schemas/campaign.py
Pydantic модели для заявок на размещение.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import date
from enum import Enum


class CampaignStatus(str, Enum):
    """Статусы заявки."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class AdFormat(str, Enum):
    """Форматы рекламы."""
    POST = "post"
    STORY = "story"
    VIDEO = "video"
    INTEGRATION = "integration"


class PlacementProofType(str, Enum):
    """Типы подтверждения размещения."""
    SCREENSHOT = "screenshot"
    POST_LINK = "post_link"
    OTHER = "other"


class CampaignCreate(BaseModel):
    """Схема для создания заявки."""
    channel_id: str = Field(..., description="ID канала для размещения")
    
    # Даты
    start_date: date = Field(..., description="Дата начала размещения")
    end_date: date = Field(..., description="Дата окончания размещения")
    
    # Финансы
    budget: Decimal = Field(..., gt=0, description="Бюджет размещения (RUB)")
    
    # Размещение
    ad_format: AdFormat = Field(..., description="Формат рекламы")
    creative_text: str = Field(..., min_length=10, max_length=5000, description="Текст объявления")
    creative_images: Optional[List[str]] = Field(None, max_items=10, description="URLs изображений")
    creative_video_url: Optional[str] = Field(None, description="URL видео (если есть)")
    ad_url: Optional[str] = Field(None, description="URL для отслеживания кликов")
    
    # Примечания
    seller_notes: Optional[str] = Field(None, max_length=1000, description="Примечания продавца")
    
    @validator("end_date")
    def end_date_must_be_after_start(cls, v, values):
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel_id": "323e4567-e89b-12d3-a456-426614174000",
                "start_date": "2025-11-20",
                "end_date": "2025-11-22",
                "budget": 5000.00,
                "ad_format": "post",
                "creative_text": "Проверьте нашу новую коллекцию товаров!",
                "creative_images": ["https://example.com/img1.jpg"],
                "ad_url": "https://myshop.com/campaign123",
                "seller_notes": "Предпочитаю размещение в понедельник утром"
            }
        }


class CampaignUpdate(BaseModel):
    """Схема для обновления заявки (может менять только создатель до принятия)."""
    ad_format: Optional[AdFormat] = None
    creative_text: Optional[str] = Field(None, min_length=10, max_length=5000)
    creative_images: Optional[List[str]] = None
    creative_video_url: Optional[str] = None
    ad_url: Optional[str] = None
    seller_notes: Optional[str] = Field(None, max_length=1000)


class CampaignResponse(BaseModel):
    """Полный ответ с данными заявки."""
    id: str
    seller_id: str
    channel_id: str
    
    status: str
    budget: Decimal
    platform_commission_percent: Decimal
    
    start_date: str
    end_date: str
    actual_completion_date: Optional[str] = None
    
    ad_format: str
    creative_text: str
    creative_images: Optional[List[str]] = None
    creative_video_url: Optional[str] = None
    ad_url: Optional[str] = None
    
    placement_proof_url: Optional[str] = None
    placement_proof_type: Optional[str] = None
    
    owner_submitted_at: Optional[str] = None
    seller_confirmed_at: Optional[str] = None
    
    seller_notes: Optional[str] = None
    owner_notes: Optional[str] = None
    
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "423e4567-e89b-12d3-a456-426614174000",
                "seller_id": "123e4567-e89b-12d3-a456-426614174000",
                "channel_id": "323e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "budget": 5000.00,
                "platform_commission_percent": 10.00,
                "start_date": "2025-11-20",
                "end_date": "2025-11-22",
                "ad_format": "post",
                "creative_text": "Проверьте нашу новую коллекцию!",
                "created_at": "2025-11-15T10:00:00Z"
            }
        }


class CampaignAccept(BaseModel):
    """Схема для принятия заявки владельцем канала."""
    owner_notes: Optional[str] = Field(None, max_length=1000, description="Примечания владельца канала")


class CampaignReject(BaseModel):
    """Схема для отклонения заявки."""
    reason: str = Field(..., min_length=10, max_length=1000, description="Причина отклонения")


class CampaignSubmit(BaseModel):
    """Схема для отправки подтверждения размещения."""
    placement_proof_url: str = Field(..., description="URL скриншота или ссылка на пост")
    placement_proof_type: PlacementProofType = Field(..., description="Тип подтверждения")
    owner_notes: Optional[str] = Field(None, max_length=1000, description="Примечания о размещении")


class CampaignConfirm(BaseModel):
    """Схема для подтверждения размещения продавцом."""
    confirmed: bool = Field(..., description="True если размещение хорошее, False если спор")
    dispute_reason: Optional[str] = Field(None, max_length=1000, description="Причина спора (если confirmed=False)")


class CampaignStats(BaseModel):
    """Статистика по кампаниям."""
    total_campaigns: int
    active_campaigns: int
    completed_campaigns: int
    pending_campaigns: int
    total_spent: Optional[Decimal] = None  # Для продавцов
    total_earned: Optional[Decimal] = None  # Для владельцев каналов
