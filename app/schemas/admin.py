"""
app/schemas/admin.py
Pydantic модели для админ-панели.
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class PlatformStatsResponse(BaseModel):
    """Общая статистика платформы."""
    date: str
    
    total_users: int
    active_sellers: int
    active_channels: int
    
    total_campaigns: int
    completed_campaigns: int
    completion_rate: Decimal
    
    gmv: Decimal
    platform_revenue: Decimal
    average_transaction: Optional[Decimal] = None
    
    new_users_today: int


class DisputeResponse(BaseModel):
    """Информация о споре для админа."""
    id: str
    campaign_id: str
    initiated_by_user_id: str
    
    reason: str
    description: Optional[str] = None
    
    status: str
    created_at: str
    
    admin_notes: Optional[str] = None
    admin_decision: Optional[str] = None


class UserReviewResponse(BaseModel):
    """Обзор пользователя для администратора."""
    user_id: str
    email: str
    user_type: str
    
    created_at: str
    is_active: bool
    
    kyc_status: str
    
    total_campaigns: int
    completed_campaigns: int
    
    total_spent_or_earned: Decimal
    
    complaints_count: int
    avg_rating: Optional[Decimal] = None
    
    notes: Optional[str] = None


class UserBlockRequest(BaseModel):
    """Запрос на блокировку пользователя."""
    reason: str = Field(..., min_length=10, max_length=500)
    send_notification: bool = Field(True, description="Отправить уведомление пользователю")


class DisputeResolutionRequest(BaseModel):
    """Запрос на разрешение спора."""
    decision: str = Field(..., description="refund, release_payment, или partial_refund")
    refund_amount: Optional[Decimal] = None
    notes: str = Field(..., min_length=10, max_length=1000)


class WithdrawalApprovalRequest(BaseModel):
    """Запрос на одобрение вывода средств."""
    approved: bool = Field(...)
    notes: Optional[str] = None

