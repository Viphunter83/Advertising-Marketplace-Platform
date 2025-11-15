"""
Pydantic схемы для продавцов.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class SellerResponse(BaseModel):
    """Схема ответа с данными продавца."""
    id: str
    user_id: str
    shop_name: Optional[str] = None
    shop_url: Optional[str] = None
    category: Optional[str] = None
    balance: float = Field(default=0.0, ge=0)
    total_spent: float = Field(default=0.0, ge=0)
    created_at: datetime
    
    class Config:
        from_attributes = True

