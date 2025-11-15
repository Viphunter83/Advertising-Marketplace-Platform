"""
app/routers/admin.py
API endpoints для администраторов.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.schemas.admin import (
    PlatformStatsResponse,
    DisputeResponse,
    UserBlockRequest,
    DisputeResolutionRequest,
    WithdrawalApprovalRequest
)
from app.services.review_service import AdminService
from app.core.dependencies import get_admin_user
from app.core.database import get_supabase_client
from decimal import Decimal

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get(
    "/stats",
    response_model=PlatformStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Статистика платформы"
)
async def get_platform_stats(
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD"),
    current_user: dict = Depends(get_admin_user)
) -> PlatformStatsResponse:
    """
    Получает статистику платформы за конкретную дату.
    
    **Требует**: Admin
    """
    try:
        stats = await AdminService.get_platform_stats(date)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stats not found"
            )
        
        # Считаем процент завершения
        total_campaigns = stats.get("total_campaigns", 0)
        completed_campaigns = stats.get("completed_campaigns", 0)
        completion_rate = (
            Decimal(completed_campaigns) / Decimal(total_campaigns)
            if total_campaigns > 0
            else Decimal(0)
        )
        
        # Считаем среднюю транзакцию
        gmv = Decimal(str(stats.get("gmv", 0)))
        total_campaigns_decimal = Decimal(total_campaigns) if total_campaigns > 0 else Decimal(1)
        average_transaction = gmv / total_campaigns_decimal if total_campaigns > 0 else None
        
        stats["completion_rate"] = completion_rate
        stats["average_transaction"] = average_transaction
        
        return PlatformStatsResponse(**stats)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting platform stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@router.get(
    "/disputes",
    response_model=List[DisputeResponse],
    status_code=status.HTTP_200_OK,
    summary="Список открытых споров"
)
async def get_disputes(
    status_filter: Optional[str] = Query(None, description="open, pending_admin, resolved"),
    current_user: dict = Depends(get_admin_user)
) -> List[DisputeResponse]:
    """Получает список споров для администратора."""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("campaign_disputes").select("*")
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        query = query.order("created_at", desc=True)
        result = query.execute()
        
        disputes = []
        if result.data:
            for d in result.data:
                disputes.append(DisputeResponse(**d))
        
        return disputes
    
    except Exception as e:
        logger.error(f"Error getting disputes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving disputes"
        )


@router.post(
    "/disputes/{dispute_id}/resolve",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Разрешить спор"
)
async def resolve_dispute(
    dispute_id: str,
    resolution: DisputeResolutionRequest,
    current_user: dict = Depends(get_admin_user)
) -> dict:
    """
    Администратор разрешает спор.
    
    **Требует**: Admin
    
    **Решения**:
    - `refund`: Вернуть все деньги продавцу
    - `release_payment`: Выплатить владельцу канала полностью
    - `partial_refund`: Разделить между продавцом и владельцем
    """
    try:
        success = await AdminService.resolve_dispute(
            dispute_id=dispute_id,
            decision=resolution.decision,
            notes=resolution.notes,
            admin_id=current_user["user_id"],
            refund_amount=resolution.refund_amount
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not resolve dispute"
            )
        
        return {"status": "ok", "message": "Dispute resolved"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving dispute: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error resolving dispute"
        )


@router.post(
    "/users/{user_id}/block",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Заблокировать пользователя"
)
async def block_user(
    user_id: str,
    block_request: UserBlockRequest,
    current_user: dict = Depends(get_admin_user)
) -> dict:
    """Блокирует пользователя на платформе."""
    try:
        success = await AdminService.block_user(
            user_id=user_id,
            reason=block_request.reason,
            admin_id=current_user["user_id"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not block user"
            )
        
        return {"status": "ok", "message": f"User {user_id} blocked"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error blocking user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error blocking user"
        )


@router.get(
    "/withdrawals",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Список запросов на вывод"
)
async def get_withdrawals(
    status_filter: Optional[str] = Query("pending", description="pending, processing, completed, rejected"),
    current_user: dict = Depends(get_admin_user)
) -> List[dict]:
    """Получает список запросов на вывод для администратора."""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("withdrawal_requests").select("*").eq("status", status_filter)
        query = query.order("created_at", desc=True)
        
        result = query.execute()
        return result.data or []
    
    except Exception as e:
        logger.error(f"Error getting withdrawals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving withdrawals"
        )


@router.post(
    "/withdrawals/{withdrawal_id}/approve",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Одобрить вывод"
)
async def approve_withdrawal(
    withdrawal_id: str,
    approval: WithdrawalApprovalRequest,
    current_user: dict = Depends(get_admin_user)
) -> dict:
    """Одобряет запрос на вывод средств."""
    try:
        if not approval.approved:
            return {"status": "error", "message": "Use /reject endpoint to reject"}
        
        success = await AdminService.approve_withdrawal(
            withdrawal_id=withdrawal_id,
            admin_id=current_user["user_id"],
            notes=approval.notes
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not approve withdrawal"
            )
        
        return {"status": "ok", "message": "Withdrawal approved"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving withdrawal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error approving withdrawal"
        )


@router.post(
    "/withdrawals/{withdrawal_id}/reject",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Отклонить вывод"
)
async def reject_withdrawal(
    withdrawal_id: str,
    rejection: WithdrawalApprovalRequest,
    current_user: dict = Depends(get_admin_user)
) -> dict:
    """Отклоняет запрос на вывод средств."""
    try:
        success = await AdminService.reject_withdrawal(
            withdrawal_id=withdrawal_id,
            admin_id=current_user["user_id"],
            reason=rejection.notes or "Rejected by administrator"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not reject withdrawal"
            )
        
        return {"status": "ok", "message": "Withdrawal rejected"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting withdrawal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error rejecting withdrawal"
        )

