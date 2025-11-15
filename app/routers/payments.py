"""
app/routers/payments.py
API endpoints для платежей и финансов.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import List
from app.schemas.payment import (
    DepositRequest,
    DepositResponse,
    WithdrawalRequest,
    WithdrawalResponse,
    TransactionResponse,
    BalanceResponse,
    TransactionHistoryResponse,
    PaymentMethod as PaymentMethodEnum
)
from app.services.payment_service import PaymentService
from app.services.seller_service import SellerService
from app.services.channel_service import ChannelService
from app.core.dependencies import get_current_user, get_seller_user, get_channel_owner_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post(
    "/deposit",
    response_model=DepositResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Пополнить баланс (создать платёж)"
)
async def create_deposit(
    deposit_data: DepositRequest,
    current_user: dict = Depends(get_seller_user)
) -> DepositResponse:
    """
    Создаёт запрос на пополнение баланса продавца.
    
    **Требует**: Пользователь типа 'seller'
    
    **Процесс**:
    1. Система создаёт платёжную ссылку у провайдера
    2. Возвращает URL для оплаты
    3. Пользователь переходит по ссылке и платит
    4. Провайдер отправляет webhook
    5. Средства добавляются на баланс
    
    **Поддерживаемые методы**: yoomoney, sbp
    """
    try:
        # Получаем профиль продавца
        seller = await SellerService.get_seller_by_user_id(current_user["user_id"])
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seller profile not found. Create one first."
            )
        
        # Создаём транзакцию
        transaction = await PaymentService.create_deposit_transaction(
            seller_id=seller["id"],
            user_id=current_user["user_id"],
            amount=deposit_data.amount,
            payment_method=deposit_data.payment_method.value
        )
        
        return DepositResponse(
            transaction_id=transaction["id"],
            payment_url=transaction.get("payment_url"),
            amount=deposit_data.amount,
            status=transaction["status"],
            message="Click the link to complete payment"
        )
    
    except ValueError as e:
        logger.warning(f"Deposit creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating deposit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating deposit"
        )


@router.post(
    "/withdrawal",
    response_model=WithdrawalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Запросить вывод средств"
)
async def create_withdrawal(
    withdrawal_data: WithdrawalRequest,
    current_user: dict = Depends(get_channel_owner_user)
) -> WithdrawalResponse:
    """
    Создаёт запрос на вывод средств владельца канала.
    
    **Требует**: Пользователь типа 'channel_owner'
    
    **ВАЖНО**: Администратор должен проверить и одобрить запрос!
    
    **Процесс**:
    1. Владелец канала создаёт запрос на вывод
    2. Указывает сумму и метод вывода
    3. Администратор проверяет и одобряет
    4. Средства переводятся на указанный счёт
    """
    try:
        channel = await ChannelService.get_channel_by_user_id(current_user["user_id"])
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Channel profile not found"
            )
        
        withdrawal = await PaymentService.create_withdrawal_request(
            user_id=current_user["user_id"],
            channel_id=channel["id"],
            amount=withdrawal_data.amount,
            method=withdrawal_data.method.value,
            account=withdrawal_data.account
        )
        
        return WithdrawalResponse(
            withdrawal_id=withdrawal["id"],
            amount=withdrawal_data.amount,
            status=withdrawal["status"],
            method=withdrawal_data.method.value,
            message="Withdrawal request created, admin will process within 24 hours"
        )
    
    except ValueError as e:
        logger.warning(f"Withdrawal creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating withdrawal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating withdrawal"
        )


@router.get(
    "/balance",
    response_model=BalanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить текущий баланс"
)
async def get_balance(
    current_user: dict = Depends(get_current_user)
) -> BalanceResponse:
    """
    Получает текущий баланс пользователя.
    
    **Для продавца**: Баланс для создания заявок
    **Для владельца канала**: Заработанные средства (доступные для вывода)
    """
    try:
        balance_info = await PaymentService.get_user_balance(
            user_id=current_user["user_id"],
            user_type=current_user["user_type"]
        )
        
        return BalanceResponse(**balance_info)
    
    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving balance"
        )


@router.get(
    "/history",
    response_model=TransactionHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="История транзакций"
)
async def get_transaction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
) -> TransactionHistoryResponse:
    """
    Получает историю финансовых операций пользователя.
    
    **Параметры**:
    - **page**: Номер страницы (начиная с 1)
    - **limit**: Количество записей на странице (максимум 100)
    """
    try:
        offset = (page - 1) * limit
        
        transactions, total_count = await PaymentService.get_transaction_history(
            user_id=current_user["user_id"],
            user_type=current_user["user_type"],
            limit=limit,
            offset=offset
        )
        
        return TransactionHistoryResponse(
            transactions=[TransactionResponse(**t) for t in transactions],
            total_count=total_count,
            page=page,
            page_size=limit
        )
    
    except Exception as e:
        logger.error(f"Error getting transaction history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving transaction history"
        )


# ==================== WEBHOOKS (для платёжных провайдеров) ====================

@router.post(
    "/yoomoney/callback",
    status_code=status.HTTP_200_OK,
    summary="YooMoney webhook"
)
async def yoomoney_callback(request: Request):
    """
    Webhook от YooMoney о завершении платежа.
    
    **ВАЖНО**: Проверяем signature для безопасности!
    """
    try:
        body = await request.json()
        
        # На MVP просто логируем (нужна реальная реализация webhook)
        logger.info(f"YooMoney callback received: {body}")
        
        # В продакшене:
        # 1. Проверяем signature
        # 2. Получаем transaction_id и статус платежа
        # 3. Вызываем PaymentService.complete_deposit_transaction()
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error processing YooMoney callback: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.post(
    "/sbp/callback",
    status_code=status.HTTP_200_OK,
    summary="SBP webhook"
)
async def sbp_callback(request: Request):
    """
    Webhook от СБП о завершении платежа.
    """
    try:
        body = await request.json()
        
        logger.info(f"SBP callback received: {body}")
        
        # На MVP просто логируем
        # На production - полная реализация
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error processing SBP callback: {str(e)}")
        return {"status": "error", "message": str(e)}

