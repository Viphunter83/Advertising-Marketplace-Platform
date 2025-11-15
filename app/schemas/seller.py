"""
app/schemas/seller.py
Pydantic модели для профилей продавцов.
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal


class SellerCreate(BaseModel):
    """Схема для создания профиля продавца."""
    shop_name: str = Field(..., min_length=2, max_length=255)
    shop_url: Optional[str] = Field(None, max_length=500)
    shop_description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., description="Мода, Техника, Красота и т.д.")
    notification_email: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "shop_name": "Интернет-магазин 'TechStore'",
                "shop_url": "https://wildberries.ru/seller/techstore",
                "shop_description": "Продаём качественную электронику по низким ценам",
                "category": "Техника",
                "notification_email": "seller@techstore.com"
            }
        }


class SellerUpdate(BaseModel):
    """Схема для обновления профиля продавца."""
    shop_name: Optional[str] = Field(None, min_length=2, max_length=255)
    shop_description: Optional[str] = Field(None, max_length=1000)
    notification_email: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    payment_method: Optional[str] = None


class PaymentDetails(BaseModel):
    """Детали платёжного реквизита."""
    account: str = Field(..., description="Номер счёта, кошелька или телефона")
    holder_name: str = Field(..., description="ФИО владельца счёта")
    bank_name: Optional[str] = None


class SellerPaymentUpdate(BaseModel):
    """Схема для обновления платёжных реквизитов."""
    payment_method: str = Field(..., description="yoomoney, sbp, bank_transfer")
    payment_details: PaymentDetails


class SellerResponse(BaseModel):
    """Полный ответ с данными продавца."""
    id: str
    user_id: str
    shop_name: str
    shop_url: Optional[str] = None
    shop_description: Optional[str] = None
    category: str
    logo_url: Optional[str] = None
    
    balance: Decimal
    total_spent: Decimal
    total_campaigns: int
    
    payment_method: Optional[str] = None
    notifications_enabled: bool = True
    notification_email: Optional[str] = None
    
    kyc_status: str
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "223e4567-e89b-12d3-a456-426614174000",
                "shop_name": "TechStore",
                "shop_url": "https://wildberries.ru/seller/techstore",
                "category": "Техника",
                "balance": 150000.50,
                "total_spent": 5000.00,
                "total_campaigns": 12,
                "kyc_status": "not_verified",
                "is_active": True,
                "created_at": "2025-11-15T09:30:00Z"
            }
        }


class SellerStatsResponse(BaseModel):
    """Статистика продавца."""
    total_spent: Decimal
    total_campaigns: int
    active_campaigns: int
    completed_campaigns: int
    average_roi: Optional[Decimal]
    balance: Decimal
