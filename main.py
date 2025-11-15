"""
Точка входа приложения Advertising Marketplace Platform.
FastAPI приложение с базовыми эндпоинтами.
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import get_supabase_client, check_connection
from app.routers import auth, sellers, channels, campaigns

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    description="MVP платформы для размещения рекламы маркетплейсов",
    version="0.1.0",
    debug=settings.fastapi_debug
)

# CORS middleware (для работы с фронтендом)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(sellers.router)
app.include_router(channels.router)
app.include_router(campaigns.router)


@app.get("/", tags=["root"])
async def root():
    """
    Корневой эндпоинт. Проверка работоспособности API.
    
    Returns:
        Приветственное сообщение
    """
    return {
        "message": "Hello, API is running!",
        "app_name": settings.app_name,
        "version": "0.1.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Проверка статуса приложения и подключения к Supabase.
    
    Returns:
        Статус приложения и подключения к БД
    """
    db_status = check_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "app_name": settings.app_name
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} on {settings.fastapi_host}:{settings.fastapi_port}")
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_debug
    )

