"""
app/routers/sellers.py
API endpoints для управления профилями продавцов.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.seller import (
    SellerCreate,
    SellerUpdate,
    SellerPaymentUpdate,
    SellerResponse,
    SellerStatsResponse
)
from app.services.seller_service import SellerService
from app.core.dependencies import get_current_user, get_seller_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sellers",
    tags=["Sellers"]
)


@router.post(
    "/profile",
    response_model=SellerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать профиль продавца"
)
async def create_seller_profile(
    seller_data: SellerCreate,
    current_user: dict = Depends(get_seller_user)
) -> SellerResponse:
    """
    Создаёт профиль продавца для текущего пользователя.
    
    **Требует**: Пользователь типа 'seller'
    """
    try:
        seller = await SellerService.create_seller_profile(
            user_id=current_user["user_id"],
            seller_data=seller_data
        )
        return SellerResponse(**seller)
    
    except ValueError as e:
        logger.warning(f"Profile creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating seller profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating profile"
        )


@router.get(
    "/profile",
    response_model=SellerResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить свой профиль продавца"
)
async def get_seller_profile(
    current_user: dict = Depends(get_seller_user)
) -> SellerResponse:
    """
    Получает профиль продавца текущего пользователя.
    """
    try:
        seller = await SellerService.get_seller_by_user_id(current_user["user_id"])
        
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller profile not found. Create one first."
            )
        
        return SellerResponse(**seller)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting seller profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving profile"
        )


@router.put(
    "/profile",
    response_model=SellerResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить профиль продавца"
)
async def update_seller_profile(
    update_data: SellerUpdate,
    current_user: dict = Depends(get_seller_user)
) -> SellerResponse:
    """
    Обновляет профиль продавца.
    """
    try:
        seller = await SellerService.update_seller_profile(
            user_id=current_user["user_id"],
            update_data=update_data
        )
        return SellerResponse(**seller)
    
    except Exception as e:
        logger.error(f"Error updating seller profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.post(
    "/payment-details",
    response_model=SellerResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить платёжные реквизиты"
)
async def update_payment_details(
    payment_data: SellerPaymentUpdate,
    current_user: dict = Depends(get_seller_user)
) -> SellerResponse:
    """
    Обновляет платёжные реквизиты продавца.
    """
    try:
        seller = await SellerService.update_payment_details(
            user_id=current_user["user_id"],
            payment_data=payment_data
        )
        return SellerResponse(**seller)
    
    except Exception as e:
        logger.error(f"Error updating payment details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating payment details"
        )


@router.get(
    "/stats",
    response_model=SellerStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить статистику продавца"
)
async def get_seller_stats(
    current_user: dict = Depends(get_seller_user)
) -> SellerStatsResponse:
    """
    Получает статистику продавца (затраты, кампании, баланс).
    """
    try:
        stats = await SellerService.get_seller_stats(current_user["user_id"])
        # Добавляем недостающие поля для ответа
        stats["active_campaigns"] = 0  # TODO: подсчитать из campaigns
        stats["completed_campaigns"] = 0  # TODO: подсчитать из campaigns
        stats["average_roi"] = None  # TODO: рассчитать ROI
        return SellerStatsResponse(**stats)
    
    except Exception as e:
        logger.error(f"Error getting seller stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@router.get(
    "/{seller_id}",
    response_model=SellerResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить профиль продавца (публичный)"
)
async def get_public_seller_profile(seller_id: str) -> SellerResponse:
    """
    Получает публичный профиль продавца по ID (без токена).
    """
    try:
        seller = await SellerService.get_seller_by_id(seller_id)
        
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller not found"
            )
        
        return SellerResponse(**seller)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting public seller profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving profile"
        )

