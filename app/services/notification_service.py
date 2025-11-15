"""
app/services/notification_service.py
Сервис для отправки уведомлений (Email + WebSocket).
"""
import logging
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone
from app.core.websocket import send_notification_to_user
from app.services.email_service import EmailService
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис уведомлений."""
    
    @staticmethod
    async def send_new_campaign_notification(
        channel_owner_user_id: str,
        channel_owner_email: Optional[str] = None,
        channel_owner_name: Optional[str] = None,
        campaign_id: str = None,
        seller_shop_name: str = None,
        budget: Decimal = None
    ) -> None:
        """Уведомление о новой заявке."""
        try:
            # Получаем данные пользователя, если не переданы
            if not channel_owner_email or not channel_owner_name:
                supabase = get_supabase_client()
                user = supabase.table("users").select("email, full_name").eq("id", channel_owner_user_id).execute()
                if user.data:
                    channel_owner_email = channel_owner_email or user.data[0].get("email")
                    channel_owner_name = channel_owner_name or user.data[0].get("full_name")
            
            # WebSocket уведомление (real-time)
            await send_notification_to_user(
                user_id=channel_owner_user_id,
                notification={
                    "type": "new_campaign",
                    "title": "Новая заявка на размещение",
                    "message": f"Продавец {seller_shop_name} создал заявку на {budget} RUB",
                    "campaign_id": campaign_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Email уведомление (для тех, кто offline)
            if channel_owner_email and channel_owner_name and seller_shop_name and campaign_id and budget:
                await EmailService.send_new_campaign_email(
                    channel_owner_email=channel_owner_email,
                    channel_owner_name=channel_owner_name,
                    seller_name=seller_shop_name,
                    campaign_id=campaign_id,
                    budget=float(budget)
                )
            
            logger.info(f"[NOTIFICATION] New campaign notification sent to {channel_owner_user_id}")
        except Exception as e:
            logger.error(f"Error sending new campaign notification: {str(e)}")
    
    
    @staticmethod
    async def send_campaign_accepted_notification(
        seller_user_id: str,
        seller_email: Optional[str] = None,
        seller_name: Optional[str] = None,
        campaign_id: str = None,
        channel_name: Optional[str] = None
    ) -> None:
        """Уведомление о принятии заявки."""
        try:
            # Получаем данные пользователя, если не переданы
            if not seller_email or not seller_name:
                supabase = get_supabase_client()
                user = supabase.table("users").select("email, full_name").eq("id", seller_user_id).execute()
                if user.data:
                    seller_email = seller_email or user.data[0].get("email")
                    seller_name = seller_name or user.data[0].get("full_name")
            
            # WebSocket
            await send_notification_to_user(
                user_id=seller_user_id,
                notification={
                    "type": "campaign_accepted",
                    "title": "Заявка принята!",
                    "message": f"Канал {channel_name} принял вашу заявку",
                    "campaign_id": campaign_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Email
            if seller_email and seller_name and channel_name and campaign_id:
                await EmailService.send_campaign_accepted_email(
                    seller_email=seller_email,
                    seller_name=seller_name,
                    channel_name=channel_name,
                    campaign_id=campaign_id
                )
            
            logger.info(f"[NOTIFICATION] Campaign accepted notification sent to {seller_user_id}")
        except Exception as e:
            logger.error(f"Error sending campaign accepted notification: {str(e)}")
    
    
    @staticmethod
    async def send_campaign_rejected_notification(
        seller_user_id: str,
        campaign_id: str,
        reason: str
    ) -> None:
        """Уведомление об отклонении заявки."""
        logger.info(
            f"[NOTIFICATION] Campaign rejected for seller {seller_user_id}: "
            f"{campaign_id}, Reason: {reason}"
        )
    
    
    @staticmethod
    async def send_campaign_submitted_notification(
        seller_user_id: str,
        campaign_id: str
    ) -> None:
        """Уведомление о подтверждении размещения."""
        logger.info(
            f"[NOTIFICATION] Campaign submitted for seller {seller_user_id}: {campaign_id}"
        )
    
    
    @staticmethod
    async def send_campaign_completed_notification(
        channel_owner_user_id: str,
        channel_owner_email: Optional[str] = None,
        channel_owner_name: Optional[str] = None,
        campaign_id: str = None,
        payment_amount: Decimal = None
    ) -> None:
        """Уведомление о завершении и выплате."""
        try:
            # Получаем данные пользователя, если не переданы
            if not channel_owner_email or not channel_owner_name:
                supabase = get_supabase_client()
                user = supabase.table("users").select("email, full_name").eq("id", channel_owner_user_id).execute()
                if user.data:
                    channel_owner_email = channel_owner_email or user.data[0].get("email")
                    channel_owner_name = channel_owner_name or user.data[0].get("full_name")
            
            # WebSocket
            await send_notification_to_user(
                user_id=channel_owner_user_id,
                notification={
                    "type": "campaign_completed",
                    "title": "Выплата получена!",
                    "message": f"Вам зачислено {payment_amount} RUB за размещение",
                    "campaign_id": campaign_id,
                    "amount": float(payment_amount) if payment_amount else None,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Email
            if channel_owner_email and channel_owner_name and payment_amount and campaign_id:
                await EmailService.send_campaign_completed_email(
                    channel_owner_email=channel_owner_email,
                    channel_owner_name=channel_owner_name,
                    payment_amount=float(payment_amount),
                    campaign_id=campaign_id
                )
            
            logger.info(f"[NOTIFICATION] Campaign completed notification sent to {channel_owner_user_id}")
        except Exception as e:
            logger.error(f"Error sending campaign completed notification: {str(e)}")

