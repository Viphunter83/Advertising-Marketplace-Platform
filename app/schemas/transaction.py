"""
Pydantic схемы для транзакций.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    """Схема ответа с данными транзакции."""
    id: str
    campaign_id: Optional[str] = None
    seller_id: str
    channel_owner_id: Optional[str] = None
    amount: float = Field(ge=0)
    commission: float = Field(ge=0)
    final_amount: float = Field(ge=0)
    status: str
    payment_method: Optional[str] = None
    created_at: datetime
    released_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

