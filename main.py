"""
Точка входа приложения Advertising Marketplace Platform.
FastAPI приложение с WebSocket и Background Tasks (Phase 2).
"""
import logging
import socketio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import get_supabase_client, check_connection
from app.routers import auth, sellers, channels, campaigns, payments, reviews, admin
from app.core.websocket import sio
from app.core.scheduler import start_scheduler, stop_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    description="Advertising Marketplace API with Real-time WebSocket (Phase 2)",
    version="0.2.0-phase2",
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
app.include_router(payments.router)
app.include_router(reviews.router)
app.include_router(admin.router)

# ==================== WEBSOCKET ИНТЕГРАЦИЯ ====================
# Создаём ASGI приложение с Socket.io
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
    socketio_path='/socket.io'
)

# ==================== LIFECYCLE EVENTS ====================
@app.on_event("startup")
async def startup_event():
    """При запуске приложения."""
    logger.info("🚀 Application starting up...")
    
    # Запускаем планировщик фоновых задач
    start_scheduler()
    
    logger.info("✅ Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """При остановке приложения."""
    logger.info("🛑 Application shutting down...")
    
    # Останавливаем планировщик
    stop_scheduler()
    
    logger.info("✅ Application shut down successfully")


@app.get("/", tags=["root"])
async def root():
    """
    Корневой эндпоинт. Проверка работоспособности API.
    
    Returns:
        Приветственное сообщение
    """
    return {
        "message": "Advertising Marketplace API (Phase 2)",
        "app_name": settings.app_name,
        "version": "0.2.0-phase2",
        "websocket": "Enabled",
        "features": ["Real-time notifications", "Email alerts", "Background tasks"]
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Проверка статуса приложения и подключения к Supabase.
    
    Returns:
        Статус приложения и подключения к БД
    """
    from app.core.websocket import get_active_users
    
    db_status = check_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "app_name": settings.app_name,
        "version": "0.2.0-phase2",
        "websocket_active_users": len(get_active_users())
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} on {settings.fastapi_host}:{settings.fastapi_port}")
    # Запускаем с socket_app вместо app для поддержки WebSocket
    uvicorn.run(
        socket_app,  # ИЗМЕНЕНО для поддержки WebSocket
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_debug
    )

