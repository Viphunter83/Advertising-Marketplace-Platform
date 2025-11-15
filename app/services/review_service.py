"""
app/services/review_service.py
Сервис для работы с отзывами и рейтингами.
"""
import logging
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)


class ReviewService:
    """Сервис управления отзывами."""
    
    @staticmethod
    async def create_review(
        campaign_id: str,
        seller_id: str,
        channel_id: str,
        rating: int,
        comment: str,
        title: Optional[str] = None
    ) -> dict:
        """
        Создаёт отзыв продавца на канал.
        
        **ВАЖНО**: Может оставить отзыв только после завершения заявки!
        """
        supabase = get_supabase_client()
        
        # Проверяем, что заявка завершена
        campaign = supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
        if not campaign.data or campaign.data[0]["status"] != "completed":
            raise ValueError("Can only review completed campaigns")
        
        # Проверяем, не существует ли уже отзыв
        existing = supabase.table("reviews").select("*").eq("campaign_id", campaign_id).execute()
        if existing.data:
            raise ValueError("Review already exists for this campaign")
        
        try:
            review_id = str(uuid4())
            
            review = supabase.table("reviews").insert({
                "id": review_id,
                "campaign_id": campaign_id,
                "seller_id": seller_id,
                "channel_id": channel_id,
                "rating": rating,
                "title": title,
                "comment": comment,
                "ad_format": campaign.data[0].get("ad_format"),
                "budget": float(campaign.data[0].get("budget", 0)) if campaign.data[0].get("budget") else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            # Обновляем рейтинг канала
            await ReviewService._update_channel_rating(channel_id)
            
            logger.info(f"Review created: {review_id}, Rating: {rating}")
            if review.data:
                return review.data[0]
            return {}
        
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}")
            raise ValueError(f"Error creating review: {str(e)}")
    
    
    @staticmethod
    async def get_channel_reviews(channel_id: str, limit: int = 50) -> List[dict]:
        """Получает отзывы на канал."""
        supabase = get_supabase_client()
        
        result = supabase.table("reviews").select("*").eq("channel_id", channel_id).order("created_at", desc=True).limit(limit).execute()
        
        return result.data or []
    
    
    @staticmethod
    async def get_channel_rating(channel_id: str) -> Dict:
        """
        Получает агрегированный рейтинг канала.
        
        Возвращает:
        - average_rating: средняя оценка (1-5)
        - total_reviews: количество отзывов
        - distribution: распределение оценок {1: 0, 2: 1, 3: 5, 4: 20, 5: 74}
        """
        supabase = get_supabase_client()
        
        reviews = await ReviewService.get_channel_reviews(channel_id, limit=1000)
        
        if not reviews:
            return {
                "average_rating": Decimal(0),
                "total_reviews": 0,
                "distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        # Считаем статистику
        ratings = [r["rating"] for r in reviews]
        avg_rating = Decimal(sum(ratings)) / Decimal(len(ratings))
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            distribution[rating] += 1
        
        return {
            "average_rating": avg_rating,
            "total_reviews": len(reviews),
            "distribution": distribution
        }
    
    
    @staticmethod
    async def _update_channel_rating(channel_id: str) -> None:
        """Обновляет рейтинг канала в таблице channels."""
        supabase = get_supabase_client()
        
        rating_data = await ReviewService.get_channel_rating(channel_id)
        
        try:
            supabase.table("channels").update({
                "rating": float(rating_data["average_rating"]),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", channel_id).execute()
            
            logger.info(f"Channel {channel_id} rating updated: {rating_data['average_rating']}")
        
        except Exception as e:
            logger.error(f"Error updating channel rating: {str(e)}")


class AdminService:
    """Сервис для администраторов."""
    
    @staticmethod
    async def get_platform_stats(date: Optional[str] = None) -> dict:
        """
        Получает статистику платформы за дату.
        
        Args:
            date (Optional[str]): Дата в формате YYYY-MM-DD (по умолчанию сегодня)
        
        Returns:
            dict: Статистика платформы
        """
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        supabase = get_supabase_client()
        
        try:
            # Получаем или создаём запись статистики
            stats_result = supabase.table("platform_stats").select("*").eq("date", date).execute()
            
            if stats_result.data and len(stats_result.data) > 0:
                return stats_result.data[0]
            
            # Если нет, подсчитываем текущую статистику
            
            # Количество пользователей (используем auth.users через Supabase)
            # Для MVP считаем через sellers и channels
            sellers = supabase.table("sellers").select("id", count="exact").execute()
            channels = supabase.table("channels").select("id", count="exact").execute()
            
            total_users = (sellers.count or 0) + (channels.count or 0)
            
            # Активные продавцы
            active_sellers_result = supabase.table("sellers").select("id", count="exact").eq("is_active", True).execute()
            active_sellers = active_sellers_result.count or 0
            
            # Активные каналы
            active_channels_result = supabase.table("channels").select("id", count="exact").eq("is_active", True).execute()
            active_channels = active_channels_result.count or 0
            
            # Кампании
            all_campaigns = supabase.table("campaigns").select("*").execute()
            total_campaigns = len(all_campaigns.data) if all_campaigns.data else 0
            completed = len([c for c in all_campaigns.data if c["status"] == "completed"]) if all_campaigns.data else 0
            
            # GMV и комиссия
            transactions = supabase.table("transactions").select("*").eq("status", "completed").execute()
            gmv = Decimal(0)
            platform_revenue = Decimal(0)
            
            if transactions.data:
                for t in transactions.data:
                    if t["transaction_type"] == "payment":
                        gmv += Decimal(str(t.get("amount", 0)))
                    elif t["transaction_type"] == "commission":
                        platform_revenue += Decimal(str(t.get("amount", 0)))
            
            stats = {
                "date": date,
                "total_users": total_users,
                "active_sellers": active_sellers,
                "active_channels": active_channels,
                "total_campaigns": total_campaigns,
                "completed_campaigns": completed,
                "gmv": float(gmv),
                "platform_revenue": float(platform_revenue),
                "new_users": 0  # TODO: Подсчитать новых за день
            }
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting platform stats: {str(e)}")
            return {}
    
    
    @staticmethod
    async def block_user(user_id: str, reason: str, admin_id: str) -> bool:
        """Блокирует пользователя."""
        supabase = get_supabase_client()
        
        try:
            # Блокируем пользователя (обновляем is_active в sellers/channels)
            # Для MVP блокируем через профили
            seller = supabase.table("sellers").select("*").eq("user_id", user_id).execute()
            if seller.data:
                supabase.table("sellers").update({
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("user_id", user_id).execute()
            
            channel = supabase.table("channels").select("*").eq("user_id", user_id).execute()
            if channel.data:
                supabase.table("channels").update({
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("user_id", user_id).execute()
            
            # Логируем действие админа
            await AdminService._log_admin_action(
                admin_id=admin_id,
                action_type="user_blocked",
                target_type="user",
                target_id=user_id,
                description=reason
            )
            
            logger.info(f"User {user_id} blocked by admin {admin_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error blocking user: {str(e)}")
            return False
    
    
    @staticmethod
    async def resolve_dispute(
        dispute_id: str,
        decision: str,
        notes: str,
        admin_id: str,
        refund_amount: Optional[Decimal] = None
    ) -> bool:
        """
        Администратор разрешает спор по заявке.
        
        Args:
            dispute_id: ID спора
            decision: "refund", "release_payment", или "partial_refund"
            notes: Комментарий администратора
            admin_id: ID администратора
            refund_amount: Сумма возврата (для partial_refund)
        """
        supabase = get_supabase_client()
        
        try:
            # Получаем спор
            dispute = supabase.table("campaign_disputes").select("*").eq("id", dispute_id).execute()
            if not dispute.data:
                raise ValueError("Dispute not found")
            
            disp = dispute.data[0]
            campaign_id = disp["campaign_id"]
            
            # Получаем заявку
            campaign = supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
            if not campaign.data:
                raise ValueError("Campaign not found")
            
            camp = campaign.data[0]
            amount = Decimal(str(camp["budget"]))
            
            # Обновляем спор
            supabase.table("campaign_disputes").update({
                "status": "resolved",
                "admin_decision": decision,
                "admin_notes": notes,
                "admin_decided_at": datetime.now(timezone.utc).isoformat(),
                "decided_by_admin_id": admin_id,
                "resolved_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", dispute_id).execute()
            
            # Обрабатываем решение
            from app.services.seller_service import SellerService
            from app.services.channel_service import ChannelService
            
            seller = supabase.table("sellers").select("*").eq("id", camp["seller_id"]).execute()
            channel = supabase.table("channels").select("*").eq("id", camp["channel_id"]).execute()
            
            if decision == "refund":
                # Возвращаем все средства продавцу
                if seller.data:
                    await SellerService.add_balance(
                        user_id=seller.data[0]["user_id"],
                        amount=amount
                    )
            
            elif decision == "release_payment":
                # Выплачиваем владельцу канала полностью
                if channel.data:
                    commission_percent = Decimal(str(camp.get("platform_commission_percent", 10)))
                    commission = amount * commission_percent / 100
                    payment = amount - commission
                    await ChannelService.add_earnings(
                        user_id=channel.data[0]["user_id"],
                        amount=payment
                    )
            
            elif decision == "partial_refund" and refund_amount:
                # Возвращаем часть продавцу, выплачиваем часть владельцу
                if seller.data:
                    await SellerService.add_balance(
                        user_id=seller.data[0]["user_id"],
                        amount=refund_amount
                    )
                
                if channel.data:
                    payment = amount - refund_amount
                    await ChannelService.add_earnings(
                        user_id=channel.data[0]["user_id"],
                        amount=payment
                    )
            
            # Логируем действие
            await AdminService._log_admin_action(
                admin_id=admin_id,
                action_type="dispute_resolved",
                target_type="dispute",
                target_id=dispute_id,
                description=f"Decision: {decision}"
            )
            
            logger.info(f"Dispute {dispute_id} resolved with decision: {decision}")
            return True
        
        except Exception as e:
            logger.error(f"Error resolving dispute: {str(e)}")
            return False
    
    
    @staticmethod
    async def approve_withdrawal(
        withdrawal_id: str,
        admin_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Одобряет запрос на вывод средств."""
        from app.services.payment_service import PaymentService
        
        return await PaymentService.process_withdrawal(
            withdrawal_id=withdrawal_id,
            approved=True,
            admin_notes=notes
        )
    
    
    @staticmethod
    async def reject_withdrawal(
        withdrawal_id: str,
        admin_id: str,
        reason: str
    ) -> bool:
        """Отклоняет запрос на вывод средств."""
        from app.services.payment_service import PaymentService
        
        return await PaymentService.process_withdrawal(
            withdrawal_id=withdrawal_id,
            approved=False,
            admin_notes=reason
        )
    
    
    @staticmethod
    async def _log_admin_action(
        admin_id: str,
        action_type: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """Логирует действие администратора."""
        supabase = get_supabase_client()
        
        try:
            supabase.table("admin_logs").insert({
                "admin_id": admin_id,
                "action_type": action_type,
                "target_type": target_type,
                "target_id": target_id,
                "description": description,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        
        except Exception as e:
            logger.error(f"Error logging admin action: {str(e)}")

