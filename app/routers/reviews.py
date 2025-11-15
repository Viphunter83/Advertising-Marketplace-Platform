"""
app/routers/reviews.py
API endpoints для отзывов и рейтингов.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.review import ReviewCreate, ReviewResponse, ChannelRatingResponse
from app.services.review_service import ReviewService
from app.services.campaign_service import CampaignService
from app.services.channel_service import ChannelService
from app.services.seller_service import SellerService
from app.core.dependencies import get_current_user, get_seller_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


async def _get_seller_id(user_id: str) -> str:
    """Получает ID профиля продавца по ID пользователя."""
    seller = await SellerService.get_seller_by_user_id(user_id)
    if not seller:
        raise ValueError("Seller profile not found")
    
    return seller["id"]


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Оставить отзыв на канал"
)
async def create_review(
    review_data: ReviewCreate,
    current_user: dict = Depends(get_seller_user)
) -> ReviewResponse:
    """
    Оставляет отзыв на канал после размещения.
    
    **Требует**: Пользователь типа 'seller' и завершённую заявку
    
    **ВАЖНО**: Отзыв можно оставить только один раз за заявку!
    """
    try:
        # Получаем заявку
        campaign = await CampaignService.get_campaign(review_data.campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Проверяем, что это заявка текущего продавца
        seller = await SellerService.get_seller_by_user_id(current_user["user_id"])
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seller profile not found"
            )
        
        if campaign["seller_id"] != seller["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only review your own campaigns"
            )
        
        # Создаём отзыв
        review = await ReviewService.create_review(
            campaign_id=review_data.campaign_id,
            seller_id=seller["id"],
            channel_id=campaign["channel_id"],
            rating=review_data.rating,
            comment=review_data.comment,
            title=review_data.title
        )
        
        return ReviewResponse(**review)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating review"
        )


@router.get(
    "/channel/{channel_id}",
    response_model=List[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить отзывы на канал"
)
async def get_channel_reviews(
    channel_id: str
) -> List[ReviewResponse]:
    """Получает все отзывы на конкретный канал."""
    try:
        reviews = await ReviewService.get_channel_reviews(channel_id)
        return [ReviewResponse(**r) for r in reviews]
    
    except Exception as e:
        logger.error(f"Error getting reviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving reviews"
        )


@router.get(
    "/channel/{channel_id}/rating",
    response_model=ChannelRatingResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить рейтинг канала"
)
async def get_channel_rating(
    channel_id: str
) -> ChannelRatingResponse:
    """Получает агрегированный рейтинг канала."""
    try:
        # Получаем информацию о канале
        channel = await ChannelService.get_channel_by_id(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        # Получаем рейтинг
        rating_data = await ReviewService.get_channel_rating(channel_id)
        reviews = await ReviewService.get_channel_reviews(channel_id, limit=5)
        
        return ChannelRatingResponse(
            channel_id=channel_id,
            channel_name=channel.get("channel_name", "Unknown"),
            average_rating=rating_data["average_rating"],
            total_reviews=rating_data["total_reviews"],
            rating_distribution=rating_data["distribution"],
            recent_reviews=[ReviewResponse(**r) for r in reviews]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel rating: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving rating"
        )

