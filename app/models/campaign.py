"""
Модель заявки на размещение (campaigns таблица).
"""
from datetime import datetime, date
from typing import Optional, List
import uuid
import enum


class CampaignStatus(str, enum.Enum):
    """Статус заявки."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class Campaign:
    """
    Модель заявки на размещение рекламы.
    Соответствует таблице campaigns в Supabase.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        seller_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        status: Optional[str] = None,
        budget: Optional[float] = 0.0,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        ad_format: Optional[str] = None,
        creative_text: Optional[str] = None,
        creative_images: Optional[List[str]] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.seller_id = seller_id
        self.channel_id = channel_id
        self.status = status or CampaignStatus.PENDING.value
        self.budget = float(budget) if budget is not None else 0.0
        self.start_date = start_date
        self.end_date = end_date
        self.ad_format = ad_format
        self.creative_text = creative_text
        self.creative_images = creative_images or []
        self.notes = notes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для работы с Supabase."""
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "channel_id": self.channel_id,
            "status": self.status,
            "budget": self.budget,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "ad_format": self.ad_format,
            "creative_text": self.creative_text,
            "creative_images": self.creative_images,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        """Создает модель из словаря (из Supabase)."""
        # Преобразуем строки дат обратно в date объекты
        if "start_date" in data and data["start_date"]:
            data["start_date"] = datetime.fromisoformat(data["start_date"]).date()
        if "end_date" in data and data["end_date"]:
            data["end_date"] = datetime.fromisoformat(data["end_date"]).date()
        return cls(**data)

