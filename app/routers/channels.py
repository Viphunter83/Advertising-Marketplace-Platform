"""
app/routers/channels.py
API endpoints для управления профилями каналов.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from app.schemas.channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelFilter,
    ChannelStatsResponse,
    PlatformEnum
)
from app.services.channel_service import ChannelService
from app.core.dependencies import get_current_user, get_channel_owner_user
from decimal import Decimal

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/channels",
    tags=["Channels"]
)


def normalize_channel_data(channel: dict) -> dict:
    """Нормализует данные канала перед возвратом (обрабатывает tags и другие поля)."""
    # Обрабатываем tags - если None, заменяем на пустой список
    if channel.get("tags") is None:
        channel["tags"] = []
    # Убеждаемся, что все Optional поля имеют значения (если None, оставляем None - Pydantic обработает)
    return channel


@router.post(
    "/profile",
    response_model=ChannelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать профиль канала"
)
async def create_channel_profile(
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_channel_owner_user)
) -> ChannelResponse:
    """
    Создаёт профиль канала для текущего пользователя.
    
    **Требует**: Пользователь типа 'channel_owner'
    """
    try:
        channel = await ChannelService.create_channel_profile(
            user_id=current_user["user_id"],
            channel_data=channel_data
        )
        return ChannelResponse(**normalize_channel_data(channel))
    
    except ValueError as e:
        logger.warning(f"Channel profile creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating channel profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating profile"
        )


@router.get(
    "/profile",
    response_model=ChannelResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить свой профиль канала"
)
async def get_channel_profile(
    current_user: dict = Depends(get_channel_owner_user)
) -> ChannelResponse:
    """
    Получает профиль канала текущего пользователя.
    """
    try:
        channel = await ChannelService.get_channel_by_user_id(current_user["user_id"])
        
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel profile not found. Create one first."
            )
        
        return ChannelResponse(**normalize_channel_data(channel))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving profile"
        )


@router.put(
    "/profile",
    response_model=ChannelResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить профиль канала"
)
async def update_channel_profile(
    update_data: ChannelUpdate,
    current_user: dict = Depends(get_channel_owner_user)
) -> ChannelResponse:
    """
    Обновляет профиль канала (статистику, цены и т.д.).
    """
    try:
        channel = await ChannelService.update_channel_profile(
            user_id=current_user["user_id"],
            update_data=update_data
        )
        return ChannelResponse(**normalize_channel_data(channel))
    
    except Exception as e:
        logger.error(f"Error updating channel profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.get(
    "/",
    response_model=List[ChannelResponse],
    status_code=status.HTTP_200_OK,
    summary="Поиск каналов по фильтрам"
)
async def search_channels(
    platforms: List[PlatformEnum] = Query(None),
    categories: List[str] = Query(None),
    min_subscribers: int = Query(None),
    max_subscribers: int = Query(None),
    min_engagement_rate: Decimal = Query(None),
    max_engagement_rate: Decimal = Query(None),
    min_price: Decimal = Query(None),
    max_price: Decimal = Query(None),
    geo: List[str] = Query(None),
    min_rating: Decimal = Query(None),
    verified_only: bool = Query(False),
    sort_by: str = Query(None, description="price, rating, subscribers, engagement_rate"),
    sort_order: str = Query("asc", description="asc или desc")
) -> List[ChannelResponse]:
    """
    Ищет каналы по критериям (используется продавцами).
    
    **Параметры**:
    - **platforms**: Список платформ (vk, telegram, pinterest, instagram, tiktok)
    - **categories**: Список категорий
    - **min_subscribers**: Минимум подписчиков
    - **max_subscribers**: Максимум подписчиков
    - **min_engagement_rate**: Минимальный ER
    - **min_price**: Минимальная цена
    - **max_price**: Максимальная цена
    - **verified_only**: Только проверенные каналы
    - **sort_by**: Сортировка по (price, rating, subscribers, engagement_rate)
    
    **Примеры**:
    ```
    GET /channels/?platforms=vk&platforms=telegram&categories=Мода&min_subscribers=10000&max_price=5000
    ```
    """
    try:
        filters = ChannelFilter(
            platform=platforms,
            category=categories,
            min_subscribers=min_subscribers,
            max_subscribers=max_subscribers,
            min_engagement_rate=min_engagement_rate,
            max_engagement_rate=max_engagement_rate,
            min_price=min_price,
            max_price=max_price,
            geo=geo,
            min_rating=min_rating,
            verified_only=verified_only,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        channels = await ChannelService.search_channels(filters)
        return [ChannelResponse(**normalize_channel_data(channel)) for channel in channels]
    
    except Exception as e:
        logger.error(f"Error searching channels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching channels"
        )


@router.get(
    "/stats",
    response_model=ChannelStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить статистику своего канала"
)
async def get_channel_stats(
    current_user: dict = Depends(get_channel_owner_user)
) -> ChannelStatsResponse:
    """
    Получает статистику канала владельца (доход, заказы и т.д.).
    """
    try:
        channel = await ChannelService.get_channel_by_user_id(current_user["user_id"])
        
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        completion_rate = (
            Decimal(str(channel["completed_orders"])) / Decimal(str(channel["total_orders"]))
            if channel["total_orders"] > 0
            else Decimal(0)
        )
        
        avg_price = (
            Decimal(str(channel["total_earned"])) / Decimal(str(channel["total_orders"]))
            if channel["total_orders"] > 0
            else None
        )
        
        return ChannelStatsResponse(
            total_earned=Decimal(str(channel["total_earned"])),
            total_orders=channel["total_orders"],
            completed_orders=channel["completed_orders"],
            completion_rate=completion_rate,
            average_price=avg_price,
            rating=Decimal(str(channel["rating"])),
            balance=Decimal(str(channel.get("balance", 0)))
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@router.get(
    "/{channel_id}",
    response_model=ChannelResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить профиль канала (публичный)"
)
async def get_public_channel_profile(channel_id: str) -> ChannelResponse:
    """
    Получает публичный профиль канала по ID (без токена).
    """
    try:
        channel = await ChannelService.get_channel_by_id(channel_id)
        
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        return ChannelResponse(**normalize_channel_data(channel))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting public channel profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving profile"
        )

