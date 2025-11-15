"""
Модель транзакции (transactions таблица).
"""
from datetime import datetime
from typing import Optional
import uuid
import enum


class TransactionStatus(str, enum.Enum):
    """Статус транзакции."""
    PENDING = "pending"
    HELD = "held"
    RELEASED = "released"
    REFUNDED = "refunded"


class Transaction:
    """
    Модель транзакции (платежа).
    Соответствует таблице transactions в Supabase.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        seller_id: Optional[str] = None,
        channel_owner_id: Optional[str] = None,
        amount: Optional[float] = 0.0,
        commission: Optional[float] = 0.0,
        final_amount: Optional[float] = 0.0,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        created_at: Optional[datetime] = None,
        released_at: Optional[datetime] = None,
        **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.campaign_id = campaign_id
        self.seller_id = seller_id
        self.channel_owner_id = channel_owner_id
        self.amount = float(amount) if amount is not None else 0.0
        self.commission = float(commission) if commission is not None else 0.0
        self.final_amount = float(final_amount) if final_amount is not None else 0.0
        self.status = status or TransactionStatus.PENDING.value
        self.payment_method = payment_method
        self.created_at = created_at or datetime.utcnow()
        self.released_at = released_at
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для работы с Supabase."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "seller_id": self.seller_id,
            "channel_owner_id": self.channel_owner_id,
            "amount": self.amount,
            "commission": self.commission,
            "final_amount": self.final_amount,
            "status": self.status,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "released_at": self.released_at.isoformat() if self.released_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Создает модель из словаря (из Supabase)."""
        return cls(**data)

