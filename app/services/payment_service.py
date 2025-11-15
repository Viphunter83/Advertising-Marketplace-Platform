"""
app/services/payment_service.py
Сервис для работы с платежами и финансами.
"""
import logging
from typing import Optional, List, Tuple
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4
from app.core.database import get_supabase_client
from app.config import settings

logger = logging.getLogger(__name__)


class PaymentService:
    """Сервис управления платежами."""
    
    @staticmethod
    async def create_deposit_transaction(
        seller_id: str,
        user_id: str,
        amount: Decimal,
        payment_method: str
    ) -> dict:
        """
        Создаёт транзакцию пополнения баланса.
        
        Args:
            seller_id (str): ID профиля продавца
            user_id (str): ID пользователя
            amount (Decimal): Сумма в RUB
            payment_method (str): Метод оплаты
        
        Returns:
            dict: Созданная транзакция с payment_url (если нужна)
        """
        supabase = get_supabase_client()
        
        # Валидация суммы
        if amount < Decimal(str(settings.min_deposit_amount)) or amount > Decimal(str(settings.max_deposit_amount)):
            raise ValueError(f"Invalid deposit amount: {amount}")
        
        try:
            transaction_id = str(uuid4())
            payment_url = None
            provider_id = None
            
            # Генерируем платёжную ссылку в зависимости от метода
            if payment_method == "yoomoney":
                payment_url, provider_id = await PaymentService._generate_yoomoney_link(
                    transaction_id=transaction_id,
                    amount=amount
                )
            
            elif payment_method == "sbp":
                payment_url, provider_id = await PaymentService._generate_sbp_link(
                    transaction_id=transaction_id,
                    amount=amount
                )
            
            # Создаём транзакцию в БД
            transaction = supabase.table("transactions").insert({
                "id": transaction_id,
                "seller_id": seller_id,
                "transaction_type": "deposit",
                "status": "pending",
                "amount": float(amount),
                "commission": 0,
                "net_amount": float(amount),
                "payment_method": payment_method,
                "payment_provider_id": provider_id,
                "payment_url": payment_url,
                "description": f"Deposit via {payment_method}",
                "metadata": {
                    "user_id": user_id,
                    "payment_method": payment_method
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            logger.info(f"Deposit transaction created: {transaction_id}, Amount: {amount}, Method: {payment_method}")
            if transaction.data:
                return transaction.data[0]
            return {}
        
        except Exception as e:
            logger.error(f"Error creating deposit transaction: {str(e)}")
            raise ValueError(f"Error creating deposit: {str(e)}")
    
    
    @staticmethod
    async def complete_deposit_transaction(
        transaction_id: str,
        seller_id: str
    ) -> bool:
        """
        Завершает транзакцию пополнения и добавляет средства на баланс.
        
        **Вызывается из webhook платёжного провайдера!**
        """
        supabase = get_supabase_client()
        
        try:
            # Получаем транзакцию
            trans_result = supabase.table("transactions").select("*").eq("id", transaction_id).execute()
            if not trans_result.data:
                logger.warning(f"Transaction not found: {transaction_id}")
                raise ValueError("Transaction not found")
            
            transaction = trans_result.data[0]
            
            if transaction["status"] != "pending":
                logger.warning(f"Transaction already processed: {transaction_id}")
                return False
            
            # Добавляем средства на баланс продавца
            from app.services.seller_service import SellerService
            
            seller = await SellerService.get_seller_by_id(seller_id)
            if not seller:
                raise ValueError("Seller not found")
            
            amount = Decimal(str(transaction["amount"]))
            await SellerService.add_balance(
                user_id=seller["user_id"],
                amount=amount
            )
            
            # Обновляем статус транзакции
            supabase.table("transactions").update({
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", transaction_id).execute()
            
            logger.info(f"Deposit transaction completed: {transaction_id}, Amount: {amount}")
            return True
        
        except Exception as e:
            logger.error(f"Error completing deposit: {str(e)}")
            raise ValueError(f"Error completing deposit: {str(e)}")
    
    
    @staticmethod
    async def create_withdrawal_request(
        user_id: str,
        channel_id: str,
        amount: Decimal,
        method: str,
        account: str
    ) -> dict:
        """
        Создаёт запрос на вывод средств.
        
        **ВАЖНО**: Администратор должен проверить и одобрить!
        """
        supabase = get_supabase_client()
        
        # Валидация суммы
        if amount < Decimal(str(settings.min_withdrawal_amount)) or amount > Decimal(str(settings.max_withdrawal_amount)):
            raise ValueError(f"Invalid withdrawal amount: {amount}")
        
        # Проверяем баланс
        from app.services.channel_service import ChannelService
        
        channel = await ChannelService.get_channel_by_user_id(user_id)
        if not channel:
            raise ValueError("Channel not found")
        
        available_balance = Decimal(str(channel.get("total_earned", 0)))
        
        if available_balance < amount:
            raise ValueError(f"Insufficient balance. Available: {available_balance}")
        
        try:
            withdrawal_id = str(uuid4())
            
            # Маскируем номер счёта
            account_masked = PaymentService._mask_account(account)
            
            withdrawal = supabase.table("withdrawal_requests").insert({
                "id": withdrawal_id,
                "user_id": user_id,
                "channel_id": channel_id,
                "amount": float(amount),
                "method": method,
                "account_details": account_masked,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            logger.info(f"Withdrawal request created: {withdrawal_id}, Amount: {amount}, Method: {method}")
            if withdrawal.data:
                return withdrawal.data[0]
            return {}
        
        except Exception as e:
            logger.error(f"Error creating withdrawal request: {str(e)}")
            raise ValueError(f"Error creating withdrawal: {str(e)}")
    
    
    @staticmethod
    async def process_withdrawal(
        withdrawal_id: str,
        approved: bool = True,
        admin_notes: Optional[str] = None
    ) -> dict:
        """
        Администратор обрабатывает запрос на вывод.
        """
        supabase = get_supabase_client()
        
        try:
            withdrawal = supabase.table("withdrawal_requests").select("*").eq("id", withdrawal_id).execute()
            
            if not withdrawal.data:
                raise ValueError("Withdrawal request not found")
            
            withdrawal_req = withdrawal.data[0]
            
            if withdrawal_req["status"] != "pending":
                raise ValueError(f"Withdrawal already processed: {withdrawal_req['status']}")
            
            if approved:
                new_status = "completed"
                reason = None
            else:
                new_status = "rejected"
                reason = admin_notes or "Request rejected by administrator"
            
            # Обновляем статус
            result = supabase.table("withdrawal_requests").update({
                "status": new_status,
                "reason_if_rejected": reason,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", withdrawal_id).execute()
            
            if approved:
                # ОТПРАВЛЯЕМ СРЕДСТВА (в реальности интегрируемся с провайдером)
                # На MVP просто отмечаем как выполненное
                logger.info(f"Withdrawal {withdrawal_id} approved and processed")
            else:
                # Возвращаем средства на баланс канала
                from app.services.channel_service import ChannelService
                
                channel = await ChannelService.get_channel_by_user_id(withdrawal_req["user_id"])
                if channel:
                    # Средства уже на счёте, просто логируем отклонение
                    logger.info(f"Withdrawal {withdrawal_id} rejected")
            
            if result.data:
                return result.data[0]
            return {}
        
        except Exception as e:
            logger.error(f"Error processing withdrawal: {str(e)}")
            raise ValueError(f"Error processing withdrawal: {str(e)}")
    
    
    @staticmethod
    async def get_user_balance(user_id: str, user_type: str) -> dict:
        """
        Получает текущий баланс пользователя.
        
        Args:
            user_id (str): ID пользователя
            user_type (str): Тип пользователя (seller или channel_owner)
        
        Returns:
            dict: {"balance": Decimal, "pending": Decimal, "available": Decimal}
        """
        from app.services.seller_service import SellerService
        from app.services.channel_service import ChannelService
        
        try:
            if user_type == "seller":
                seller = await SellerService.get_seller_by_user_id(user_id)
                if not seller:
                    raise ValueError("Seller not found")
                
                balance = Decimal(str(seller.get("balance", 0)))
                
                return {
                    "balance": balance,
                    "pending_withdrawals": Decimal(0),
                    "available_balance": balance,
                    "currency": "RUB"
                }
            
            elif user_type == "channel_owner":
                channel = await ChannelService.get_channel_by_user_id(user_id)
                if not channel:
                    raise ValueError("Channel not found")
                
                total_earned = Decimal(str(channel.get("total_earned", 0)))
                
                # Считаем pending withdrawals
                supabase = get_supabase_client()
                pending = supabase.table("withdrawal_requests").select("amount").eq("user_id", user_id).eq("status", "pending").execute()
                
                pending_sum = sum(
                    Decimal(str(w["amount"])) for w in pending.data
                ) if pending.data else Decimal(0)
                
                available = total_earned - pending_sum
                
                return {
                    "balance": total_earned,
                    "pending_withdrawals": pending_sum,
                    "available_balance": available,
                    "currency": "RUB"
                }
            
            else:
                raise ValueError(f"Unknown user type: {user_type}")
        
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            raise ValueError(f"Error getting balance: {str(e)}")
    
    
    @staticmethod
    async def get_transaction_history(
        user_id: str,
        user_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[dict], int]:
        """
        Получает историю транзакций пользователя.
        """
        from app.services.seller_service import SellerService
        from app.services.channel_service import ChannelService
        
        supabase = get_supabase_client()
        
        try:
            if user_type == "seller":
                seller = await SellerService.get_seller_by_user_id(user_id)
                if not seller:
                    raise ValueError("Seller not found")
                
                # Получаем все транзакции продавца
                query = supabase.table("transactions").select("*").eq("seller_id", seller["id"])
            
            elif user_type == "channel_owner":
                channel = await ChannelService.get_channel_by_user_id(user_id)
                if not channel:
                    raise ValueError("Channel not found")
                
                # Получаем все транзакции владельца канала
                query = supabase.table("transactions").select("*").eq("channel_owner_id", channel["id"])
            
            else:
                raise ValueError(f"Unknown user type: {user_type}")
            
            # Сортируем по дате (новые сверху)
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            
            result = query.execute()
            transactions = result.data or []
            
            # Получаем общее количество
            count_query = supabase.table("transactions").select("id", count="exact")
            
            if user_type == "seller":
                seller = await SellerService.get_seller_by_user_id(user_id)
                count_query = count_query.eq("seller_id", seller["id"])
            else:
                channel = await ChannelService.get_channel_by_user_id(user_id)
                count_query = count_query.eq("channel_owner_id", channel["id"])
            
            count_result = count_query.execute()
            total_count = count_result.count if hasattr(count_result, 'count') else len(transactions)
            
            return transactions, total_count
        
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            raise ValueError(f"Error retrieving transaction history: {str(e)}")
    
    
    # ==================== ПРИВАТНЫЕ МЕТОДЫ ====================
    
    @staticmethod
    async def _generate_yoomoney_link(
        transaction_id: str,
        amount: Decimal
    ) -> Tuple[str, str]:
        """
        Генерирует платёжную ссылку ЮMoney.
        
        **На MVP используем quickpay (простая ссылка)**
        **На production нужна полная интеграция с API ЮMoney**
        """
        wallet = settings.yoomoney_wallet_number
        
        if not wallet:
            logger.warning("YooMoney wallet not configured, using placeholder")
            wallet = "410012345678901"
        
        payment_url = (
            f"https://yoomoney.ru/quickpay/confirm.xml?"
            f"receiver={wallet}"
            f"&quickpay-form=shop"
            f"&targets=Deposit%20for%20campaign"
            f"&sum={amount}"
            f"&label={transaction_id}"
        )
        
        logger.info(f"Generated YooMoney payment link for transaction {transaction_id}")
        return payment_url, transaction_id
    
    
    @staticmethod
    async def _generate_sbp_link(
        transaction_id: str,
        amount: Decimal
    ) -> Tuple[str, str]:
        """
        Генерирует платёжную ссылку СБП.
        
        **На MVP используем симуляцию**
        **На production интегрируемся с API банка СБП**
        """
        # Симуляция SBP платежа
        sbp_url = (
            f"https://sbp-payment.example.com/pay?"
            f"amount={amount}"
            f"&reference={transaction_id}"
        )
        
        logger.info(f"Generated SBP payment link for transaction {transaction_id}")
        return sbp_url, transaction_id
    
    
    @staticmethod
    def _mask_account(account: str) -> str:
        """
        Маскирует номер счёта/карты для безопасности.
        """
        if len(account) <= 4:
            return "****"
        
        return account[:2] + "****" + account[-4:]

