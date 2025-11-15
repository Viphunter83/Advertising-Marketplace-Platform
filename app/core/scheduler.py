"""
app/core/scheduler.py
Планировщик фоновых задач.
"""
import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def update_platform_stats():
    """Обновляет ежедневную статистику платформы."""
    from app.services.review_service import AdminService
    
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        stats = await AdminService.get_platform_stats(date=today)
        
        logger.info(f"Platform stats updated for {today}: GMV={stats.get('gmv', 0)}")
    
    except Exception as e:
        logger.error(f"Error updating platform stats: {str(e)}")


async def cleanup_old_notifications():
    """Удаляет старые уведомления (>30 дней)."""
    from app.core.database import get_supabase_client
    
    try:
        supabase = get_supabase_client()
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        
        result = supabase.table("notifications").delete().lt("created_at", cutoff_date).execute()
        
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Deleted {deleted_count} old notifications")
    
    except Exception as e:
        logger.error(f"Error cleaning up notifications: {str(e)}")


async def send_pending_withdrawal_reminders():
    """Напоминание админам о необработанных выводах."""
    from app.core.database import get_supabase_client
    
    try:
        supabase = get_supabase_client()
        
        # Находим выводы, ожидающие более 24 часов
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        
        pending = supabase.table("withdrawal_requests").select("*").eq("status", "pending").lt("created_at", cutoff).execute()
        
        if pending.data:
            logger.warning(f"{len(pending.data)} withdrawal requests pending for >24h")
            # TODO: Отправить уведомление администраторам
    
    except Exception as e:
        logger.error(f"Error checking pending withdrawals: {str(e)}")


def start_scheduler():
    """Запускает планировщик задач."""
    if not settings.enable_background_tasks:
        logger.info("Background tasks disabled")
        return
    
    # Ежедневная статистика (в 00:00 UTC)
    scheduler.add_job(
        update_platform_stats,
        CronTrigger(hour=0, minute=0),
        id="update_platform_stats",
        replace_existing=True
    )
    
    # Очистка уведомлений (раз в неделю)
    scheduler.add_job(
        cleanup_old_notifications,
        CronTrigger(day_of_week='sun', hour=2, minute=0),
        id="cleanup_notifications",
        replace_existing=True
    )
    
    # Проверка выводов (каждые 6 часов)
    scheduler.add_job(
        send_pending_withdrawal_reminders,
        IntervalTrigger(hours=6),
        id="check_pending_withdrawals",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background tasks scheduler started")


def stop_scheduler():
    """Останавливает планировщик."""
    scheduler.shutdown()
    logger.info("Background tasks scheduler stopped")

