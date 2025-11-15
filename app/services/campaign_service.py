"""
app/services/campaign_service.py
Сервис для управления заявками на размещение.
"""
import logging
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4
from app.core.database import get_supabase_client
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.services.seller_service import SellerService
from app.services.channel_service import ChannelService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class CampaignService:
    """Сервис управления кампаниями (заявками)."""
    
    @staticmethod
    async def create_campaign(
        seller_id: str,
        campaign_data: CampaignCreate,
        platform_commission_percent: Decimal = Decimal(10)
    ) -> dict:
        """
        Создаёт новую заявку на размещение.
        
        **ВАЖНО**: Средства продавца БЛОКИРУЮТСЯ на escrow-счёте!
        
        Args:
            seller_id (str): ID профиля продавца
            campaign_data (CampaignCreate): Данные заявки
            platform_commission_percent (Decimal): % комиссии платформы
        
        Returns:
            dict: Созданная заявка
        
        Raises:
            ValueError: Если нет баланса, канал не найден и т.д.
        """
        supabase = get_supabase_client()
        
        # Проверяем, существует ли канал
        channel = await ChannelService.get_channel_by_id(campaign_data.channel_id)
        if not channel:
            logger.warning(f"Channel not found: {campaign_data.channel_id}")
            raise ValueError("Channel not found")
        
        # Проверяем баланс продавца (для блокировки средств нужны реальные деньги)
        seller = await SellerService.get_seller_by_id(seller_id)
        if not seller:
            logger.warning(f"Seller not found: {seller_id}")
            raise ValueError("Seller not found")
        
        budget = campaign_data.budget
        current_balance = Decimal(str(seller.get("balance", 0)))
        
        if current_balance < budget:
            logger.warning(f"Insufficient balance for seller {seller_id}: {current_balance} < {budget}")
            raise ValueError("Insufficient balance for this campaign")
        
        try:
            # Создаём заявку
            campaign_id = str(uuid4())
            
            new_campaign = supabase.table("campaigns").insert({
                "id": campaign_id,
                "seller_id": seller_id,
                "channel_id": campaign_data.channel_id,
                "status": "pending",
                "budget": float(budget),
                "platform_commission_percent": float(platform_commission_percent),
                "start_date": campaign_data.start_date.isoformat(),
                "end_date": campaign_data.end_date.isoformat(),
                "ad_format": campaign_data.ad_format.value if hasattr(campaign_data.ad_format, 'value') else campaign_data.ad_format,
                "creative_text": campaign_data.creative_text,
                "creative_images": campaign_data.creative_images or [],
                "creative_video_url": campaign_data.creative_video_url,
                "ad_url": campaign_data.ad_url,
                "seller_notes": campaign_data.seller_notes,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            # БЛОКИРУЕМ средства на escrow (вычитаем из баланса продавца)
            await SellerService.deduct_balance(seller["user_id"], budget)
            
            # Логируем действие
            await CampaignService._log_activity(
                campaign_id=campaign_id,
                user_id=seller["user_id"],
                action_type="created",
                description=f"Campaign created for channel {campaign_data.channel_id}"
            )
            
            # Отправляем уведомление владельцу канала
            await NotificationService.send_new_campaign_notification(
                channel_owner_user_id=channel["user_id"],
                campaign_id=campaign_id,
                seller_shop_name=seller.get("shop_name", "Неизвестный продавец"),
                budget=budget
            )
            
            logger.info(f"Campaign created: {campaign_id}, Budget: {budget}, Seller: {seller_id}")
            return new_campaign.data[0] if new_campaign.data else {}
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise ValueError(f"Error creating campaign: {str(e)}")
    
    
    @staticmethod
    async def get_campaign(campaign_id: str) -> Optional[dict]:
        """Получает заявку по ID."""
        supabase = get_supabase_client()
        result = supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    
    @staticmethod
    async def list_seller_campaigns(seller_id: str, status: Optional[str] = None) -> List[dict]:
        """Список заявок продавца."""
        supabase = get_supabase_client()
        
        query = supabase.table("campaigns").select("*").eq("seller_id", seller_id)
        
        if status:
            query = query.eq("status", status)
        
        query = query.order("created_at", desc=True)
        result = query.execute()
        
        return result.data or []
    
    
    @staticmethod
    async def list_channel_campaigns(channel_id: str, status: Optional[str] = None) -> List[dict]:
        """Список заявок для владельца канала."""
        supabase = get_supabase_client()
        
        query = supabase.table("campaigns").select("*").eq("channel_id", channel_id)
        
        if status:
            query = query.eq("status", status)
        
        query = query.order("created_at", desc=True)
        result = query.execute()
        
        return result.data or []
    
    
    @staticmethod
    async def update_campaign(
        campaign_id: str,
        update_data: CampaignUpdate,
        user_id: str
    ) -> dict:
        """
        Обновляет заявку (может только создатель до принятия).
        """
        supabase = get_supabase_client()
        
        campaign = await CampaignService.get_campaign(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        # Только создатель может редактировать и только в статусе PENDING
        if campaign["status"] != "pending":
            raise ValueError(f"Can only update campaign in pending status, current: {campaign['status']}")
        
        update_dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        for key, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                if key == "ad_format" and hasattr(value, 'value'):
                    update_dict[key] = value.value
                else:
                    update_dict[key] = value
        
        try:
            result = supabase.table("campaigns").update(update_dict).eq("id", campaign_id).execute()
            
            logger.info(f"Campaign {campaign_id} updated")
            if result.data and len(result.data) > 0:
                return result.data[0]
            return await CampaignService.get_campaign(campaign_id) or {}
        
        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            raise ValueError(f"Error updating campaign: {str(e)}")
    
    
    @staticmethod
    async def accept_campaign(
        campaign_id: str,
        channel_owner_user_id: str,
        owner_notes: Optional[str] = None
    ) -> dict:
        """
        Владелец канала принимает заявку.
        """
        supabase = get_supabase_client()
        
        campaign = await CampaignService.get_campaign(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign["status"] != "pending":
            raise ValueError(f"Can only accept pending campaigns, current: {campaign['status']}")
        
        try:
            result = supabase.table("campaigns").update({
                "status": "accepted",
                "owner_notes": owner_notes,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", campaign_id).execute()
            
            # Логируем
            await CampaignService._log_activity(
                campaign_id=campaign_id,
                user_id=channel_owner_user_id,
                action_type="accepted",
                description="Campaign accepted by channel owner"
            )
            
            # Уведомляем продавца
            seller = supabase.table("sellers").select("user_id").eq("id", campaign["seller_id"]).execute()
            if seller.data:
                await NotificationService.send_campaign_accepted_notification(
                    seller_user_id=seller.data[0]["user_id"],
                    campaign_id=campaign_id
                )
            
            logger.info(f"Campaign {campaign_id} accepted by channel owner")
            if result.data and len(result.data) > 0:
                return result.data[0]
            return await CampaignService.get_campaign(campaign_id) or {}
        
        except Exception as e:
            logger.error(f"Error accepting campaign: {str(e)}")
            raise ValueError(f"Error accepting campaign: {str(e)}")
    
    
    @staticmethod
    async def reject_campaign(
        campaign_id: str,
        channel_owner_user_id: str,
        reason: str
    ) -> dict:
        """
        Владелец канала отклоняет заявку.
        **ВАЖНО**: Блокированные средства возвращаются продавцу!
        """
        supabase = get_supabase_client()
        
        campaign = await CampaignService.get_campaign(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign["status"] != "pending":
            raise ValueError(f"Can only reject pending campaigns")
        
        try:
            # ВОЗВРАЩАЕМ средства продавцу
            seller = supabase.table("sellers").select("*").eq("id", campaign["seller_id"]).execute()
            if seller.data:
                await SellerService.add_balance(
                    user_id=seller.data[0]["user_id"],
                    amount=Decimal(str(campaign["budget"]))
                )
            
            # Обновляем статус
            result = supabase.table("campaigns").update({
                "status": "rejected",
                "owner_notes": f"Rejected: {reason}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", campaign_id).execute()
            
            # Логируем
            await CampaignService._log_activity(
                campaign_id=campaign_id,
                user_id=channel_owner_user_id,
                action_type="rejected",
                description=f"Campaign rejected: {reason}"
            )
            
            # Уведомляем продавца
            if seller.data:
                await NotificationService.send_campaign_rejected_notification(
                    seller_user_id=seller.data[0]["user_id"],
                    campaign_id=campaign_id,
                    reason=reason
                )
            
            logger.info(f"Campaign {campaign_id} rejected, funds returned to seller")
            if result.data and len(result.data) > 0:
                return result.data[0]
            return await CampaignService.get_campaign(campaign_id) or {}
        
        except Exception as e:
            logger.error(f"Error rejecting campaign: {str(e)}")
            raise ValueError(f"Error rejecting campaign: {str(e)}")
    
    
    @staticmethod
    async def submit_campaign(
        campaign_id: str,
        channel_owner_user_id: str,
        placement_proof_url: str,
        placement_proof_type: str,
        owner_notes: Optional[str] = None
    ) -> dict:
        """
        Владелец канала отмечает размещение как выполненное.
        """
        supabase = get_supabase_client()
        
        campaign = await CampaignService.get_campaign(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign["status"] != "accepted":
            raise ValueError(f"Can only submit accepted campaigns, current: {campaign['status']}")
        
        try:
            result = supabase.table("campaigns").update({
                "status": "in_progress",
                "placement_proof_url": placement_proof_url,
                "placement_proof_type": placement_proof_type,
                "owner_notes": owner_notes,
                "owner_submitted_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", campaign_id).execute()
            
            # Логируем
            await CampaignService._log_activity(
                campaign_id=campaign_id,
                user_id=channel_owner_user_id,
                action_type="submitted",
                description="Placement proof submitted"
            )
            
            # Уведомляем продавца
            seller = supabase.table("sellers").select("user_id").eq("id", campaign["seller_id"]).execute()
            if seller.data:
                await NotificationService.send_campaign_submitted_notification(
                    seller_user_id=seller.data[0]["user_id"],
                    campaign_id=campaign_id
                )
            
            logger.info(f"Campaign {campaign_id} marked as in_progress, awaiting seller confirmation")
            if result.data and len(result.data) > 0:
                return result.data[0]
            return await CampaignService.get_campaign(campaign_id) or {}
        
        except Exception as e:
            logger.error(f"Error submitting campaign: {str(e)}")
            raise ValueError(f"Error submitting campaign: {str(e)}")
    
    
    @staticmethod
    async def confirm_campaign(
        campaign_id: str,
        seller_user_id: str,
        confirmed: bool,
        dispute_reason: Optional[str] = None
    ) -> dict:
        """
        Продавец подтверждает размещение или открывает спор.
        
        **Если confirmed=True**:
        - Статус → COMPLETED
        - Средства с ESCROW переводятся владельцу канала
        
        **Если confirmed=False**:
        - Статус → DISPUTED
        - Открывается спор, администратор разбирается
        """
        supabase = get_supabase_client()
        
        campaign = await CampaignService.get_campaign(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign["status"] != "in_progress":
            raise ValueError(f"Can only confirm in_progress campaigns, current: {campaign['status']}")
        
        try:
            if confirmed:
                # ВЫПЛАЧИВАЕМ владельцу канала
                channel = supabase.table("channels").select("*").eq("id", campaign["channel_id"]).execute()
                
                if channel.data:
                    budget = Decimal(str(campaign["budget"]))
                    commission_percent = Decimal(str(campaign["platform_commission_percent"]))
                    commission = budget * commission_percent / 100
                    payment_to_owner = budget - commission
                    
                    # Создаём транзакцию комиссии платформы
                    commission_transaction_id = str(uuid4())
                    supabase.table("transactions").insert({
                        "id": commission_transaction_id,
                        "campaign_id": campaign_id,
                        "seller_id": campaign["seller_id"],
                        "transaction_type": "commission",
                        "status": "completed",
                        "amount": float(commission),  # Исправлено: amount = commission, а не budget
                        "commission": float(commission),
                        "net_amount": float(commission),
                        "description": f"Platform commission for campaign {campaign_id}",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }).execute()
                    
                    # Создаём транзакцию выплаты владельцу канала
                    payment_transaction_id = str(uuid4())
                    supabase.table("transactions").insert({
                        "id": payment_transaction_id,
                        "campaign_id": campaign_id,
                        "channel_owner_id": campaign["channel_id"],
                        "transaction_type": "payment",
                        "status": "completed",
                        "amount": float(payment_to_owner),  # Исправлено: amount = payment_to_owner, а не budget
                        "commission": float(commission),
                        "net_amount": float(payment_to_owner),
                        "description": f"Payment for completed campaign {campaign_id}",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }).execute()
                    
                    # Добавляем заработок на счёт владельца
                    await ChannelService.add_earnings(
                        user_id=channel.data[0]["user_id"],
                        amount=payment_to_owner
                    )
                    
                    # Обновляем статистику канала
                    await ChannelService.update_channel_stats(
                        channel_id=campaign["channel_id"],
                        completed_order=True
                    )
                    
                    # Обновляем статус заявки (внутри блока if channel.data для атомарности)
                    result = supabase.table("campaigns").update({
                        "status": "completed",
                        "seller_confirmed_at": datetime.now(timezone.utc).isoformat(),
                        "actual_completion_date": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }).eq("id", campaign_id).execute()
                    
                    # Логируем
                    await CampaignService._log_activity(
                        campaign_id=campaign_id,
                        user_id=seller_user_id,
                        action_type="confirmed",
                        description="Campaign confirmed, payment released to channel owner"
                    )
                    
                    # Уведомляем владельца канала
                    await NotificationService.send_campaign_completed_notification(
                        channel_owner_user_id=channel.data[0]["user_id"],
                        campaign_id=campaign_id,
                        payment_amount=payment_to_owner
                    )
                    
                    logger.info(f"Campaign {campaign_id} confirmed, funds released to channel owner")
                else:
                    # Если канал не найден, не обновляем статус
                    logger.error(f"Channel not found for campaign {campaign_id}, cannot complete payment")
                    raise ValueError("Channel not found, cannot complete payment")
            
            else:
                # ОТКРЫВАЕМ СПОР
                dispute_id = str(uuid4())
                
                supabase.table("campaign_disputes").insert({
                    "id": dispute_id,
                    "campaign_id": campaign_id,
                    "initiated_by_user_id": seller_user_id,
                    "reason": dispute_reason or "Placement quality issue",
                    "status": "open",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }).execute()
                
                # Обновляем статус заявки
                result = supabase.table("campaigns").update({
                    "status": "disputed",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", campaign_id).execute()
                
                # Логируем
                await CampaignService._log_activity(
                    campaign_id=campaign_id,
                    user_id=seller_user_id,
                    action_type="disputed",
                    description=f"Dispute opened: {dispute_reason}"
                )
                
                logger.info(f"Campaign {campaign_id} disputed, admin will review")
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return await CampaignService.get_campaign(campaign_id) or {}
        
        except Exception as e:
            logger.error(f"Error confirming campaign: {str(e)}")
            raise ValueError(f"Error confirming campaign: {str(e)}")
    
    
    @staticmethod
    async def cancel_campaign(
        campaign_id: str,
        user_id: str,
        reason: str
    ) -> dict:
        """
        Отменяет заявку и возвращает средства продавцу.
        (может отменить только в статусе PENDING)
        """
        supabase = get_supabase_client()
        
        campaign = await CampaignService.get_campaign(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign["status"] != "pending":
            raise ValueError(f"Can only cancel pending campaigns, current: {campaign['status']}")
        
        try:
            # Возвращаем средства
            seller = supabase.table("sellers").select("*").eq("id", campaign["seller_id"]).execute()
            if seller.data:
                await SellerService.add_balance(
                    user_id=seller.data[0]["user_id"],
                    amount=Decimal(str(campaign["budget"]))
                )
            
            result = supabase.table("campaigns").update({
                "status": "cancelled",
                "owner_notes": f"Cancelled: {reason}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", campaign_id).execute()
            
            await CampaignService._log_activity(
                campaign_id=campaign_id,
                user_id=user_id,
                action_type="cancelled",
                description=reason
            )
            
            logger.info(f"Campaign {campaign_id} cancelled")
            if result.data and len(result.data) > 0:
                return result.data[0]
            return await CampaignService.get_campaign(campaign_id) or {}
        
        except Exception as e:
            logger.error(f"Error cancelling campaign: {str(e)}")
            raise ValueError(f"Error cancelling campaign: {str(e)}")
    
    
    @staticmethod
    async def _log_activity(
        campaign_id: str,
        user_id: str,
        action_type: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """Логирует действие по заявке."""
        supabase = get_supabase_client()
        
        try:
            supabase.table("campaign_activities").insert({
                "campaign_id": campaign_id,
                "user_id": user_id,
                "action_type": action_type,
                "description": description,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")

