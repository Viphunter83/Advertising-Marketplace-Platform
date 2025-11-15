"""
Конфигурация приложения.
Загружает переменные окружения из .env файла.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    
    # Supabase
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_service_role_key: str = Field(..., alias="SUPABASE_SERVICE_ROLE_KEY")
    
    # ProxyAPI для ChatGPT
    proxyapi_key: Optional[str] = Field(None, alias="PROXYAPI_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")
    
    # FastAPI
    fastapi_env: str = Field("development", alias="FASTAPI_ENV")
    fastapi_debug: bool = Field(True, alias="FASTAPI_DEBUG")
    fastapi_host: str = Field("0.0.0.0", alias="FASTAPI_HOST")
    fastapi_port: int = Field(8000, alias="FASTAPI_PORT")
    
    # JWT
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(24, alias="JWT_EXPIRATION_HOURS")
    
    # Email
    smtp_server: Optional[str] = Field(None, alias="SMTP_SERVER")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(None, alias="SMTP_USER")
    smtp_password: Optional[str] = Field(None, alias="SMTP_PASSWORD")
    sender_email: str = Field("noreply@advertising-marketplace.com", alias="SENDER_EMAIL")
    
    # Приложение
    app_name: str = Field("Advertising Marketplace MVP", alias="APP_NAME")
    platform_commission_percent: float = Field(10.0, alias="PLATFORM_COMMISSION_PERCENT")
    
    # Платёжные системы
    yoomoney_wallet_number: Optional[str] = Field(None, alias="YOOMONEY_WALLET_NUMBER")
    yoomoney_api_key: Optional[str] = Field(None, alias="YOOMONEY_API_KEY")
    yoomoney_redirect_url: str = Field("http://localhost:8000/payments/yoomoney/callback", alias="YOOMONEY_REDIRECT_URL")
    
    sbp_bank_id: Optional[str] = Field(None, alias="SBP_BANK_ID")
    sbp_merchant_id: Optional[str] = Field(None, alias="SBP_MERCHANT_ID")
    sbp_api_key: Optional[str] = Field(None, alias="SBP_API_KEY")
    
    # Финансовые параметры
    min_deposit_amount: float = Field(100.0, alias="MIN_DEPOSIT_AMOUNT")
    max_deposit_amount: float = Field(500000.0, alias="MAX_DEPOSIT_AMOUNT")
    min_withdrawal_amount: float = Field(100.0, alias="MIN_WITHDRAWAL_AMOUNT")
    max_withdrawal_amount: float = Field(500000.0, alias="MAX_WITHDRAWAL_AMOUNT")
    
    # Webhooks
    webhook_secret: str = Field("your-super-secret-webhook-key", alias="WEBHOOK_SECRET")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()

