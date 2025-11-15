"""
app/services/seller_service.py
Сервис для работы с профилями продавцов.
"""
import logging
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, timezone
from app.core.database import get_supabase_client
from app.schemas.seller import SellerCreate, SellerUpdate, SellerPaymentUpdate

logger = logging.getLogger(__name__)


class SellerService:
    """Сервис управления профилями продавцов."""
    
    @staticmethod
    async def create_seller_profile(
        user_id: str,
        seller_data: SellerCreate
    ) -> dict:
        """
        Создаёт профиль продавца.
        
        Args:
            user_id (str): ID пользователя
            seller_data (SellerCreate): Данные профиля
        
        Returns:
            dict: Созданный профиль
        """
        supabase = get_supabase_client()
        
        # Проверяем, не существует ли уже профиль
        existing = supabase.table("sellers").select("*").eq("user_id", user_id).execute()
        if existing.data:
            logger.warning(f"Seller profile already exists for user {user_id}")
            raise ValueError("Seller profile already exists")
        
        try:
            new_seller = supabase.table("sellers").insert({
                "user_id": user_id,
                "shop_name": seller_data.shop_name,
                "shop_url": seller_data.shop_url,
                "shop_description": seller_data.shop_description,
                "category": seller_data.category,
                "notification_email": seller_data.notification_email,
                "balance": 0,
                "total_spent": 0,
                "total_campaigns": 0,
                "kyc_status": "not_verified",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            logger.info(f"Seller profile created for user {user_id}")
            return new_seller.data[0] if new_seller.data else {}
        
        except Exception as e:
            logger.error(f"Error creating seller profile: {str(e)}")
            raise ValueError(f"Error creating profile: {str(e)}")
    
    
    @staticmethod
    async def get_seller_by_user_id(user_id: str) -> Optional[dict]:
        """
        Получает профиль продавца по ID пользователя.
        
        Args:
            user_id (str): ID пользователя
        
        Returns:
            Optional[dict]: Профиль продавца или None
        """
        supabase = get_supabase_client()
        
        result = supabase.table("sellers").select("*").eq("user_id", user_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    
    @staticmethod
    async def get_seller_by_id(seller_id: str) -> Optional[dict]:
        """
        Получает профиль продавца по ID.
        
        Args:
            seller_id (str): ID профиля
        
        Returns:
            Optional[dict]: Профиль продавца или None
        """
        supabase = get_supabase_client()
        
        result = supabase.table("sellers").select("*").eq("id", seller_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    
    @staticmethod
    async def update_seller_profile(
        user_id: str,
        update_data: SellerUpdate
    ) -> dict:
        """
        Обновляет профиль продавца.
        
        Args:
            user_id (str): ID пользователя
            update_data (SellerUpdate): Данные для обновления
        
        Returns:
            dict: Обновлённый профиль
        """
        supabase = get_supabase_client()
        
        # Подготавливаем данные для обновления
        update_dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        for key, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                update_dict[key] = value
        
        try:
            result = supabase.table("sellers").update(update_dict).eq("user_id", user_id).execute()
            logger.info(f"Seller profile updated for user {user_id}")
            if result.data and len(result.data) > 0:
                return result.data[0]
            # Если обновление не вернуло данные, получаем обновлённый профиль
            return await SellerService.get_seller_by_user_id(user_id) or {}
        
        except Exception as e:
            logger.error(f"Error updating seller profile: {str(e)}")
            raise ValueError(f"Error updating profile: {str(e)}")
    
    
    @staticmethod
    async def update_payment_details(
        user_id: str,
        payment_data: SellerPaymentUpdate
    ) -> dict:
        """
        Обновляет платёжные реквизиты продавца.
        
        Args:
            user_id (str): ID пользователя
            payment_data (SellerPaymentUpdate): Платёжные реквизиты
        
        Returns:
            dict: Обновлённый профиль
        """
        supabase = get_supabase_client()
        
        try:
            result = supabase.table("sellers").update({
                "payment_method": payment_data.payment_method,
                "payment_details": payment_data.payment_details.dict(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Payment details updated for seller {user_id}")
            if result.data and len(result.data) > 0:
                return result.data[0]
            # Если обновление не вернуло данные, получаем обновлённый профиль
            return await SellerService.get_seller_by_user_id(user_id) or {}
        
        except Exception as e:
            logger.error(f"Error updating payment details: {str(e)}")
            raise ValueError(f"Error updating payment details: {str(e)}")
    
    
    @staticmethod
    async def get_seller_stats(user_id: str) -> dict:
        """
        Получает статистику продавца.
        
        Args:
            user_id (str): ID пользователя
        
        Returns:
            dict: Статистика (затраты, кампании, баланс)
        """
        supabase = get_supabase_client()
        
        seller = await SellerService.get_seller_by_user_id(user_id)
        
        if not seller:
            raise ValueError("Seller not found")
        
        return {
            "total_spent": seller.get("total_spent", 0),
            "total_campaigns": seller.get("total_campaigns", 0),
            "balance": seller.get("balance", 0),
            "kyc_status": seller.get("kyc_status", "not_verified")
        }
    
    
    @staticmethod
    async def deduct_balance(
        user_id: str,
        amount: Decimal
    ) -> bool:
        """
        Вычитает сумму с баланса продавца (для создания заявки).
        
        Args:
            user_id (str): ID пользователя
            amount (Decimal): Сумма для вычитания
        
        Returns:
            bool: True если успешно
        """
        supabase = get_supabase_client()
        
        seller = await SellerService.get_seller_by_user_id(user_id)
        
        if not seller:
            raise ValueError("Seller not found")
        
        if Decimal(str(seller["balance"])) < amount:
            raise ValueError("Insufficient balance")
        
        new_balance = Decimal(str(seller["balance"])) - amount
        new_spent = Decimal(str(seller["total_spent"])) + amount
        
        try:
            supabase.table("sellers").update({
                "balance": float(new_balance),
                "total_spent": float(new_spent),
                "total_campaigns": seller["total_campaigns"] + 1,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Balance deducted for seller {user_id}: {amount}")
            return True
        
        except Exception as e:
            logger.error(f"Error deducting balance: {str(e)}")
            raise ValueError(f"Error deducting balance: {str(e)}")
    
    
    @staticmethod
    async def add_balance(
        user_id: str,
        amount: Decimal
    ) -> dict:
        """
        Добавляет сумму на баланс продавца (пополнение).
        
        Args:
            user_id (str): ID пользователя
            amount (Decimal): Сумма для добавления
        
        Returns:
            dict: Обновлённый профиль
        """
        supabase = get_supabase_client()
        
        seller = await SellerService.get_seller_by_user_id(user_id)
        
        if not seller:
            raise ValueError("Seller not found")
        
        new_balance = Decimal(str(seller["balance"])) + amount
        
        try:
            result = supabase.table("sellers").update({
                "balance": float(new_balance),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Balance added for seller {user_id}: {amount}")
            if result.data and len(result.data) > 0:
                return result.data[0]
            # Если обновление не вернуло данные, получаем обновлённый профиль
            return await SellerService.get_seller_by_user_id(user_id) or {}
        
        except Exception as e:
            logger.error(f"Error adding balance: {str(e)}")
            raise ValueError(f"Error adding balance: {str(e)}")

