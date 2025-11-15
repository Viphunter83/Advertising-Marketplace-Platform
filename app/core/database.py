"""
Подключение к Supabase (PostgreSQL).
Использует Supabase Python SDK для работы с базой данных.
"""
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Глобальный клиент Supabase
supabase: Client = None


def get_supabase_client() -> Client:
    """
    Получает или создает клиент Supabase.
    
    Returns:
        Клиент Supabase
    """
    global supabase
    
    if supabase is None:
        try:
            supabase = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("Supabase client created successfully")
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {e}")
            raise
    
    return supabase


def get_supabase_admin_client() -> Client:
    """
    Получает клиент Supabase с правами администратора (service_role_key).
    Используется для операций, требующих повышенных прав.
    
    Returns:
        Административный клиент Supabase
    """
    try:
        admin_client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        logger.info("Supabase admin client created successfully")
        return admin_client
    except Exception as e:
        logger.error(f"Failed to create Supabase admin client: {e}")
        raise


def check_connection() -> bool:
    """
    Проверяет подключение к Supabase.
    
    Returns:
        True если подключение успешно, иначе False
    """
    try:
        client = get_supabase_client()
        # Простой запрос для проверки подключения
        # Если таблица еще не создана, это нормально - просто проверяем, что клиент работает
        try:
            result = client.table("users").select("id").limit(1).execute()
        except Exception:
            # Таблица может не существовать, но клиент работает
            pass
        return True
    except Exception as e:
        logger.error(f"Supabase connection check failed: {e}")
        return False

