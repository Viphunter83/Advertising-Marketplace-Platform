"""
Pydantic схемы для заявок на размещение.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    """Схема для создания заявки на размещение."""
    channel_id: str
    budget: float = Field(..., gt=0, description="Бюджет размещения")
    start_date: date
    end_date: date
    ad_format: Optional[str] = None
    creative_text: Optional[str] = None
    creative_images: Optional[List[str]] = None
    notes: Optional[str] = None


class CampaignUpdate(BaseModel):
    """Схема для обновления заявки."""
    status: Optional[str] = Field(None, pattern="^(pending|accepted|rejected|in_progress|completed|disputed|cancelled)$")
    notes: Optional[str] = None


class CampaignResponse(BaseModel):
    """Схема ответа с данными заявки."""
    id: str
    seller_id: str
    channel_id: str
    status: str
    budget: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    ad_format: Optional[str] = None
    creative_text: Optional[str] = None
    creative_images: Optional[List[str]] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

