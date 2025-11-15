"""
app/routers/campaigns.py
API endpoints для управления заявками на размещение.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from decimal import Decimal
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignAccept,
    CampaignReject,
    CampaignSubmit,
    CampaignConfirm,
    CampaignStats
)
from app.services.campaign_service import CampaignService
from app.services.seller_service import SellerService
from app.services.channel_service import ChannelService
from app.core.dependencies import get_current_user, get_seller_user, get_channel_owner_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)


@router.post(
    "/",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку на размещение"
)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: dict = Depends(get_seller_user)
) -> CampaignResponse:
    """
    Создаёт новую заявку на размещение рекламы.
    
    **Требует**: Пользователь типа 'seller'
    **ВАЖНО**: Средства продавца БЛОКИРУЮТСЯ на escrow-счёте!
    
    **Процесс**:
    1. Продавец выбирает канал и указывает параметры
    2. Система проверяет баланс продавца
    3. Средства вычитаются с баланса (блокируются на escrow)
    4. Заявка попадает в очередь к владельцу канала
    """
    try:
        # Получаем профиль продавца
        seller = await SellerService.get_seller_by_user_id(current_user["user_id"])
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seller profile not found. Create one first."
            )
        
        # Создаём заявку
        campaign = await CampaignService.create_campaign(
            seller_id=seller["id"],
            campaign_data=campaign_data
        )
        
        return CampaignResponse(**campaign)
    
    except ValueError as e:
        logger.warning(f"Campaign creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating campaign"
        )


@router.get(
    "/my-campaigns",
    response_model=List[CampaignResponse],
    status_code=status.HTTP_200_OK,
    summary="Мои заявки (для продавца или владельца канала)"
)
async def get_my_campaigns(
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),
    current_user: dict = Depends(get_current_user)
) -> List[CampaignResponse]:
    """
    Получает список заявок текущего пользователя.
    
    **Для продавца**: все его заявки
    **Для владельца канала**: все заявки на его каналы
    """
    try:
        if current_user["user_type"] == "seller":
            seller = await SellerService.get_seller_by_user_id(current_user["user_id"])
            if not seller:
                return []
            
            campaigns = await CampaignService.list_seller_campaigns(
                seller_id=seller["id"],
                status=status_filter
            )
        
        elif current_user["user_type"] == "channel_owner":
            channel = await ChannelService.get_channel_by_user_id(current_user["user_id"])
            if not channel:
                return []
            
            campaigns = await CampaignService.list_channel_campaigns(
                channel_id=channel["id"],
                status=status_filter
            )
        
        else:
            return []
        
        return [CampaignResponse(**campaign) for campaign in campaigns]
    
    except Exception as e:
        logger.error(f"Error retrieving campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving campaigns"
        )


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить заявку"
)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
) -> CampaignResponse:
    """Получает информацию о заявке."""
    try:
        campaign = await CampaignService.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse(**campaign)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving campaign"
        )


@router.put(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить заявку"
)
async def update_campaign(
    campaign_id: str,
    update_data: CampaignUpdate,
    current_user: dict = Depends(get_seller_user)
) -> CampaignResponse:
    """
    Обновляет заявку (может только создатель, и только в статусе PENDING).
    """
    try:
        campaign = await CampaignService.update_campaign(
            campaign_id=campaign_id,
            update_data=update_data,
            user_id=current_user["user_id"]
        )
        
        return CampaignResponse(**campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating campaign"
        )


@router.post(
    "/{campaign_id}/accept",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Принять заявку"
)
async def accept_campaign(
    campaign_id: str,
    accept_data: CampaignAccept,
    current_user: dict = Depends(get_channel_owner_user)
) -> CampaignResponse:
    """
    Владелец канала принимает заявку.
    
    **После этого**:
    - Статус: pending → accepted
    - Средства остаются заблокированы на escrow
    - Владелец должен разместить рекламу
    """
    try:
        campaign = await CampaignService.accept_campaign(
            campaign_id=campaign_id,
            channel_owner_user_id=current_user["user_id"],
            owner_notes=accept_data.owner_notes
        )
        
        return CampaignResponse(**campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error accepting campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error accepting campaign"
        )


@router.post(
    "/{campaign_id}/reject",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Отклонить заявку"
)
async def reject_campaign(
    campaign_id: str,
    reject_data: CampaignReject,
    current_user: dict = Depends(get_channel_owner_user)
) -> CampaignResponse:
    """
    Владелец канала отклоняет заявку.
    
    **ВАЖНО**: Блокированные средства возвращаются продавцу!
    """
    try:
        campaign = await CampaignService.reject_campaign(
            campaign_id=campaign_id,
            channel_owner_user_id=current_user["user_id"],
            reason=reject_data.reason
        )
        
        return CampaignResponse(**campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rejecting campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error rejecting campaign"
        )


@router.post(
    "/{campaign_id}/submit",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Отметить размещение выполненным"
)
async def submit_campaign(
    campaign_id: str,
    submit_data: CampaignSubmit,
    current_user: dict = Depends(get_channel_owner_user)
) -> CampaignResponse:
    """
    Владелец канала отмечает, что рекламу разместил.
    
    **После этого**:
    - Статус: accepted → in_progress
    - Ждём подтверждения от продавца
    """
    try:
        campaign = await CampaignService.submit_campaign(
            campaign_id=campaign_id,
            channel_owner_user_id=current_user["user_id"],
            placement_proof_url=submit_data.placement_proof_url,
            placement_proof_type=submit_data.placement_proof_type.value if hasattr(submit_data.placement_proof_type, 'value') else submit_data.placement_proof_type,
            owner_notes=submit_data.owner_notes
        )
        
        return CampaignResponse(**campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting campaign"
        )


@router.post(
    "/{campaign_id}/confirm",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Подтвердить размещение (продавец)"
)
async def confirm_campaign(
    campaign_id: str,
    confirm_data: CampaignConfirm,
    current_user: dict = Depends(get_seller_user)
) -> CampaignResponse:
    """
    Продавец подтверждает, что размещение качественное.
    
    **Если подтверждено (confirmed=True)**:
    - Статус: in_progress → completed
    - Платформа вычитает комиссию (10%)
    - Остаток переходит владельцу канала
    
    **Если спор (confirmed=False)**:
    - Статус: in_progress → disputed
    - Администратор разберётся и примет решение
    """
    try:
        campaign = await CampaignService.confirm_campaign(
            campaign_id=campaign_id,
            seller_user_id=current_user["user_id"],
            confirmed=confirm_data.confirmed,
            dispute_reason=confirm_data.dispute_reason
        )
        
        return CampaignResponse(**campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error confirming campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error confirming campaign"
        )


@router.post(
    "/{campaign_id}/cancel",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Отменить заявку"
)
async def cancel_campaign(
    campaign_id: str,
    reason: str = Query(..., description="Причина отмены"),
    current_user: dict = Depends(get_seller_user)
) -> CampaignResponse:
    """
    Продавец отменяет заявку (может только в статусе PENDING).
    
    **ВАЖНО**: Блокированные средства возвращаются продавцу!
    """
    try:
        campaign = await CampaignService.cancel_campaign(
            campaign_id=campaign_id,
            user_id=current_user["user_id"],
            reason=reason
        )
        
        return CampaignResponse(**campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error cancelling campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling campaign"
        )


@router.get(
    "/stats/my-stats",
    response_model=CampaignStats,
    status_code=status.HTTP_200_OK,
    summary="Статистика по моим заявкам"
)
async def get_campaign_stats(
    current_user: dict = Depends(get_current_user)
) -> CampaignStats:
    """Получает статистику по заявкам пользователя."""
    try:
        if current_user["user_type"] == "seller":
            seller = await SellerService.get_seller_by_user_id(current_user["user_id"])
            if not seller:
                return CampaignStats(
                    total_campaigns=0,
                    active_campaigns=0,
                    completed_campaigns=0,
                    pending_campaigns=0,
                    total_spent=Decimal(0)
                )
            
            all_campaigns = await CampaignService.list_seller_campaigns(seller["id"])
            
            return CampaignStats(
                total_campaigns=len(all_campaigns),
                active_campaigns=len([c for c in all_campaigns if c["status"] in ["pending", "accepted", "in_progress"]]),
                completed_campaigns=len([c for c in all_campaigns if c["status"] == "completed"]),
                pending_campaigns=len([c for c in all_campaigns if c["status"] == "pending"]),
                total_spent=Decimal(str(seller.get("total_spent", 0)))
            )
        
        elif current_user["user_type"] == "channel_owner":
            channel = await ChannelService.get_channel_by_user_id(current_user["user_id"])
            if not channel:
                return CampaignStats(
                    total_campaigns=0,
                    active_campaigns=0,
                    completed_campaigns=0,
                    pending_campaigns=0,
                    total_earned=Decimal(0)
                )
            
            all_campaigns = await CampaignService.list_channel_campaigns(channel["id"])
            
            return CampaignStats(
                total_campaigns=len(all_campaigns),
                active_campaigns=len([c for c in all_campaigns if c["status"] in ["accepted", "in_progress"]]),
                completed_campaigns=len([c for c in all_campaigns if c["status"] == "completed"]),
                pending_campaigns=len([c for c in all_campaigns if c["status"] == "pending"]),
                total_earned=Decimal(str(channel.get("total_earned", 0)))
            )
        
        return CampaignStats(
            total_campaigns=0,
            active_campaigns=0,
            completed_campaigns=0,
            pending_campaigns=0
        )
    
    except Exception as e:
        logger.error(f"Error getting campaign stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )

