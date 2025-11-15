"""
Модель продавца (sellers таблица).
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
import uuid


class Seller:
    """
    Модель продавца.
    Соответствует таблице sellers в Supabase.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: Optional[str] = None,
        shop_name: Optional[str] = None,
        shop_url: Optional[str] = None,
        category: Optional[str] = None,
        balance: Optional[float] = 0.0,
        total_spent: Optional[float] = 0.0,
        created_at: Optional[datetime] = None,
        **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.shop_name = shop_name
        self.shop_url = shop_url
        self.category = category
        self.balance = float(balance) if balance is not None else 0.0
        self.total_spent = float(total_spent) if total_spent is not None else 0.0
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для работы с Supabase."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "shop_name": self.shop_name,
            "shop_url": self.shop_url,
            "category": self.category,
            "balance": self.balance,
            "total_spent": self.total_spent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Seller":
        """Создает модель из словаря (из Supabase)."""
        return cls(**data)

