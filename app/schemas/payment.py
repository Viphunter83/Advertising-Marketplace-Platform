"""
app/schemas/payment.py
Pydantic модели для платежей и финансов.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from enum import Enum


class PaymentMethod(str, Enum):
    """Методы оплаты."""
    YOOMONEY = "yoomoney"
    SBP = "sbp"
    CARD_MIR = "card_mir"
    QIWI = "qiwi"
    BANK_TRANSFER = "bank_transfer"


class TransactionType(str, Enum):
    """Типы транзакций."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    COMMISSION = "commission"
    PAYMENT = "payment"


class TransactionStatus(str, Enum):
    """Статусы транзакций."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DepositRequest(BaseModel):
    """Запрос на пополнение баланса."""
    amount: Decimal = Field(..., gt=0, description="Сумма в RUB")
    payment_method: PaymentMethod = Field(..., description="Метод оплаты")
    
    @validator("amount")
    def validate_amount(cls, v):
        from app.config import settings
        if v < Decimal(str(settings.min_deposit_amount)):
            raise ValueError(f"Minimum deposit: {settings.min_deposit_amount} RUB")
        if v > Decimal(str(settings.max_deposit_amount)):
            raise ValueError(f"Maximum deposit: {settings.max_deposit_amount} RUB")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 5000,
                "payment_method": "yoomoney"
            }
        }


class DepositResponse(BaseModel):
    """Ответ при создании депозита."""
    transaction_id: str
    payment_url: Optional[str] = Field(None, description="URL для оплаты")
    amount: Decimal
    status: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "payment_url": "https://yoomoney.ru/quickpay/...",
                "amount": 5000,
                "status": "pending",
                "message": "Click the link to complete payment"
            }
        }


class WithdrawalRequest(BaseModel):
    """Запрос на вывод средств."""
    amount: Decimal = Field(..., gt=0, description="Сумма в RUB")
    method: PaymentMethod = Field(..., description="Метод вывода")
    account: str = Field(..., min_length=5, max_length=255, description="Номер счёта/кошелька/телефона")
    
    @validator("amount")
    def validate_amount(cls, v):
        from app.config import settings
        if v < Decimal(str(settings.min_withdrawal_amount)):
            raise ValueError(f"Minimum withdrawal: {settings.min_withdrawal_amount} RUB")
        if v > Decimal(str(settings.max_withdrawal_amount)):
            raise ValueError(f"Maximum withdrawal: {settings.max_withdrawal_amount} RUB")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 10000,
                "method": "yoomoney",
                "account": "79991234567"
            }
        }


class WithdrawalResponse(BaseModel):
    """Ответ на запрос вывода."""
    withdrawal_id: str
    amount: Decimal
    status: str
    method: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "withdrawal_id": "223e4567-e89b-12d3-a456-426614174000",
                "amount": 10000,
                "status": "pending",
                "method": "yoomoney",
                "message": "Withdrawal request created, admin will process within 24 hours"
            }
        }


class TransactionResponse(BaseModel):
    """Ответ с информацией о транзакции."""
    id: str
    transaction_type: str
    status: str
    amount: Decimal
    commission: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    
    payment_method: Optional[str] = None
    description: Optional[str] = None
    
    created_at: str
    completed_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "transaction_type": "deposit",
                "status": "completed",
                "amount": 5000,
                "commission": 0,
                "net_amount": 5000,
                "payment_method": "yoomoney",
                "description": "Deposit to campaign budget",
                "created_at": "2025-11-15T10:30:00Z",
                "completed_at": "2025-11-15T10:35:00Z"
            }
        }


class BalanceResponse(BaseModel):
    """Текущий баланс пользователя."""
    balance: Decimal
    pending_withdrawals: Optional[Decimal] = None
    available_balance: Optional[Decimal] = None
    currency: str = "RUB"
    
    class Config:
        json_schema_extra = {
            "example": {
                "balance": 50000,
                "pending_withdrawals": 0,
                "available_balance": 50000,
                "currency": "RUB"
            }
        }


class TransactionHistoryResponse(BaseModel):
    """История транзакций."""
    transactions: List[TransactionResponse]
    total_count: int
    page: int
    page_size: int


class PaymentMethodResponse(BaseModel):
    """Сохранённый метод оплаты."""
    id: str
    user_id: str
    primary_method: Optional[str] = None
    primary_account_masked: Optional[str] = None
    verified: bool
    created_at: str

