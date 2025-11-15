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
    
    # ==================== PHASE 2: Redis ====================
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db: int = Field(0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(None, alias="REDIS_PASSWORD")
    
    # ==================== PHASE 2: WebSocket ====================
    websocket_cors_origins: list = Field(
        default=["*"],
        alias="WEBSOCKET_CORS_ORIGINS"
    )
    
    # ==================== PHASE 2: Email (SendGrid) ====================
    sendgrid_api_key: Optional[str] = Field(None, alias="SENDGRID_API_KEY")
    sendgrid_from_email: str = Field("noreply@advertising-marketplace.com", alias="SENDGRID_FROM_EMAIL")
    sendgrid_from_name: str = Field("Advertising Marketplace", alias="SENDGRID_FROM_NAME")
    
    # Альтернатива: SMTP (уже есть выше, но добавим use_tls)
    smtp_use_tls: bool = Field(True, alias="SMTP_USE_TLS")
    
    # ==================== PHASE 2: VK API ====================
    vk_service_key: Optional[str] = Field(None, alias="VK_SERVICE_KEY")
    
    # ==================== PHASE 2: Telegram ====================
    telegram_bot_token: Optional[str] = Field(None, alias="TELEGRAM_BOT_TOKEN")
    
    # ==================== PHASE 2: Background Tasks ====================
    enable_background_tasks: bool = Field(True, alias="ENABLE_BACKGROUND_TASKS")
    
    # Frontend URL для email ссылок
    frontend_url: str = Field("http://localhost:3000", alias="FRONTEND_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name == "WEBSOCKET_CORS_ORIGINS":
                return [origin.strip() for origin in raw_val.split(",")] if raw_val else ["*"]
            try:
                return cls.json_loads(raw_val)
            except:
                return raw_val


# Глобальный экземпляр настроек
settings = Settings()

