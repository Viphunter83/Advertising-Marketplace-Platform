"""
app/services/channel_service.py
Сервис для работы с профилями каналов.
"""
import logging
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, timezone
from app.core.database import get_supabase_client
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelFilter

logger = logging.getLogger(__name__)


class ChannelService:
    """Сервис управления профилями каналов."""
    
    @staticmethod
    async def create_channel_profile(
        user_id: str,
        channel_data: ChannelCreate
    ) -> dict:
        """
        Создаёт профиль канала.
        
        Args:
            user_id (str): ID пользователя (владелец канала)
            channel_data (ChannelCreate): Данные профиля канала
        
        Returns:
            dict: Созданный профиль
        """
        supabase = get_supabase_client()
        
        # Проверяем, не существует ли уже профиль
        existing = supabase.table("channels").select("*").eq("user_id", user_id).execute()
        if existing.data:
            logger.warning(f"Channel profile already exists for user {user_id}")
            raise ValueError("Channel profile already exists")
        
        try:
            new_channel = supabase.table("channels").insert({
                "user_id": user_id,
                "platform": channel_data.platform.value if hasattr(channel_data.platform, 'value') else channel_data.platform,
                "channel_url": channel_data.channel_url,
                "channel_name": channel_data.channel_name,
                "channel_description": channel_data.channel_description,
                "category": channel_data.category,
                "tags": channel_data.tags or [],
                "subscribers_count": channel_data.subscribers_count,
                "avg_reach": channel_data.avg_reach,
                "engagement_rate": float(channel_data.engagement_rate),
                "audience_geo": channel_data.audience_geo,
                "audience_age_group": channel_data.audience_age_group,
                "audience_gender": channel_data.audience_gender,
                "price_per_post": float(channel_data.price_per_post),
                "price_per_story": float(channel_data.price_per_story) if channel_data.price_per_story else None,
                "price_per_video": float(channel_data.price_per_video) if channel_data.price_per_video else None,
                "rating": 0,
                "total_orders": 0,
                "completed_orders": 0,
                "total_earned": 0,
                "verified": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            logger.info(f"Channel profile created for user {user_id}")
            return new_channel.data[0] if new_channel.data else {}
        
        except Exception as e:
            logger.error(f"Error creating channel profile: {str(e)}")
            raise ValueError(f"Error creating profile: {str(e)}")
    
    
    @staticmethod
    async def get_channel_by_user_id(user_id: str) -> Optional[dict]:
        """
        Получает профиль канала по ID пользователя.
        
        Args:
            user_id (str): ID пользователя (владельца)
        
        Returns:
            Optional[dict]: Профиль канала или None
        """
        supabase = get_supabase_client()
        
        result = supabase.table("channels").select("*").eq("user_id", user_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    
    @staticmethod
    async def get_channel_by_id(channel_id: str) -> Optional[dict]:
        """
        Получает профиль канала по ID.
        
        Args:
            channel_id (str): ID канала
        
        Returns:
            Optional[dict]: Профиль канала или None
        """
        supabase = get_supabase_client()
        
        result = supabase.table("channels").select("*").eq("id", channel_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    
    @staticmethod
    async def update_channel_profile(
        user_id: str,
        update_data: ChannelUpdate
    ) -> dict:
        """
        Обновляет профиль канала.
        
        Args:
            user_id (str): ID пользователя
            update_data (ChannelUpdate): Данные для обновления
        
        Returns:
            dict: Обновлённый профиль
        """
        supabase = get_supabase_client()
        
        update_dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        for key, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                if isinstance(value, Decimal):
                    update_dict[key] = float(value)
                else:
                    update_dict[key] = value
        
        try:
            result = supabase.table("channels").update(update_dict).eq("user_id", user_id).execute()
            logger.info(f"Channel profile updated for user {user_id}")
            if result.data and len(result.data) > 0:
                return result.data[0]
            # Если обновление не вернуло данные, получаем обновлённый профиль
            return await ChannelService.get_channel_by_user_id(user_id) or {}
        
        except Exception as e:
            logger.error(f"Error updating channel profile: {str(e)}")
            raise ValueError(f"Error updating profile: {str(e)}")
    
    
    @staticmethod
    async def search_channels(filters: ChannelFilter) -> List[dict]:
        """
        Ищет каналы по фильтрам.
        
        Args:
            filters (ChannelFilter): Фильтры поиска
        
        Returns:
            List[dict]: Список каналов, соответствующих критериям
        """
        supabase = get_supabase_client()
        
        # Начинаем с базового запроса
        query = supabase.table("channels").select("*")
        
        # Применяем фильтры
        if filters.platform:
            platform_values = [p.value if hasattr(p, 'value') else p for p in filters.platform]
            query = query.in_("platform", platform_values)
        
        if filters.category:
            query = query.in_("category", filters.category)
        
        if filters.min_subscribers:
            query = query.gte("subscribers_count", filters.min_subscribers)
        
        if filters.max_subscribers:
            query = query.lte("subscribers_count", filters.max_subscribers)
        
        if filters.min_engagement_rate:
            query = query.gte("engagement_rate", float(filters.min_engagement_rate))
        
        if filters.max_engagement_rate:
            query = query.lte("engagement_rate", float(filters.max_engagement_rate))
        
        if filters.min_price:
            query = query.gte("price_per_post", float(filters.min_price))
        
        if filters.max_price:
            query = query.lte("price_per_post", float(filters.max_price))
        
        if filters.geo:
            query = query.in_("audience_geo", filters.geo)
        
        if filters.age_group:
            query = query.in_("audience_age_group", filters.age_group)
        
        if filters.gender:
            query = query.eq("audience_gender", filters.gender)
        
        if filters.min_rating:
            query = query.gte("rating", float(filters.min_rating))
        
        if filters.verified_only:
            query = query.eq("verified", True)
        
        # Фильтруем только активные каналы
        query = query.eq("is_active", True)
        
        # Сортировка
        if filters.sort_by:
            order = filters.sort_order == "desc" if filters.sort_order else False
            query = query.order(filters.sort_by, desc=order)
        else:
            query = query.order("created_at", desc=True)
        
        try:
            result = query.execute()
            logger.info(f"Found {len(result.data)} channels matching filters")
            return result.data
        
        except Exception as e:
            logger.error(f"Error searching channels: {str(e)}")
            raise ValueError(f"Error searching channels: {str(e)}")
    
    
    @staticmethod
    async def add_earnings(
        user_id: str,
        amount: Decimal
    ) -> dict:
        """
        Добавляет заработок на счёт владельца канала.
        
        Args:
            user_id (str): ID владельца канала
            amount (Decimal): Сумма заработка
        
        Returns:
            dict: Обновлённый профиль
        """
        supabase = get_supabase_client()
        
        channel = await ChannelService.get_channel_by_user_id(user_id)
        
        if not channel:
            raise ValueError("Channel not found")
        
        new_earned = Decimal(str(channel["total_earned"])) + amount
        
        try:
            result = supabase.table("channels").update({
                "total_earned": float(new_earned),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Earnings added for channel owner {user_id}: {amount}")
            if result.data and len(result.data) > 0:
                return result.data[0]
            # Если обновление не вернуло данные, получаем обновлённый профиль
            return await ChannelService.get_channel_by_user_id(user_id) or {}
        
        except Exception as e:
            logger.error(f"Error adding earnings: {str(e)}")
            raise ValueError(f"Error adding earnings: {str(e)}")
    
    
    @staticmethod
    async def update_channel_stats(
        channel_id: str,
        subscribers: Optional[int] = None,
        engagement_rate: Optional[Decimal] = None,
        completed_order: bool = False
    ) -> dict:
        """
        Обновляет статистику канала.
        
        Args:
            channel_id (str): ID канала
            subscribers (Optional[int]): Новое количество подписчиков
            engagement_rate (Optional[Decimal]): Новый ER
            completed_order (bool): Добавить завершённый заказ
        
        Returns:
            dict: Обновлённый профиль
        """
        supabase = get_supabase_client()
        
        channel = await ChannelService.get_channel_by_id(channel_id)
        
        if not channel:
            raise ValueError("Channel not found")
        
        update_dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if subscribers is not None:
            update_dict["subscribers_count"] = subscribers
        
        if engagement_rate is not None:
            update_dict["engagement_rate"] = float(engagement_rate)
        
        if completed_order:
            update_dict["completed_orders"] = channel["completed_orders"] + 1
        
        try:
            result = supabase.table("channels").update(update_dict).eq("id", channel_id).execute()
            logger.info(f"Channel stats updated: {channel_id}")
            if result.data and len(result.data) > 0:
                return result.data[0]
            # Если обновление не вернуло данные, получаем обновлённый профиль
            return await ChannelService.get_channel_by_id(channel_id) or {}
        
        except Exception as e:
            logger.error(f"Error updating channel stats: {str(e)}")
            raise ValueError(f"Error updating stats: {str(e)}")

