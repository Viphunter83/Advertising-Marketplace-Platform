"""
app/services/notification_service.py
Сервис для отправки уведомлений.

(На MVP — только логирование, позже добавим email и WebSocket)
"""
import logging
from typing import Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис уведомлений."""
    
    @staticmethod
    async def send_new_campaign_notification(
        channel_owner_user_id: str,
        campaign_id: str,
        seller_shop_name: str,
        budget: Decimal
    ) -> None:
        """Уведомление о новой заявке."""
        logger.info(
            f"[NOTIFICATION] New campaign for channel owner {channel_owner_user_id}: "
            f"Campaign {campaign_id}, Seller: {seller_shop_name}, Budget: {budget}"
        )
        # TODO: Добавить отправку email и WebSocket уведомлений
    
    
    @staticmethod
    async def send_campaign_accepted_notification(
        seller_user_id: str,
        campaign_id: str
    ) -> None:
        """Уведомление о принятии заявки."""
        logger.info(
            f"[NOTIFICATION] Campaign accepted for seller {seller_user_id}: {campaign_id}"
        )
    
    
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
        campaign_id: str,
        payment_amount: Decimal
    ) -> None:
        """Уведомление о завершении и выплате."""
        logger.info(
            f"[NOTIFICATION] Campaign completed for channel owner {channel_owner_user_id}: "
            f"{campaign_id}, Payment: {payment_amount}"
        )

