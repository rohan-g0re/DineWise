"""
Restaurant details router - provides detailed information about individual restaurants.
Combines cached data with live Yelp API calls.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_db
from app.models import RestaurantCache
from app.clients.yelp import yelp_client, YelpAPIError
from app.schemas import RestaurantDetail, YelpReview
from typing import Optional, List, Dict, Any

router = APIRouter()


@router.get("/restaurants/{yelp_id}")
async def get_restaurant_details(
    yelp_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a restaurant.
    
    This endpoint:
    1. Checks cache for basic info
    2. Fetches full details from Yelp API
    3. Fetches up to 3 reviews from Yelp
    4. Merges everything into a comprehensive response
    """
    
    # Step 1: Check if we have this restaurant in cache
    cached_restaurant = db.exec(
        select(RestaurantCache).where(RestaurantCache.yelp_id == yelp_id)
    ).first()
    
    # Step 2: Fetch full details from Yelp API
    try:
        # REUSE: get_business_clean() method that already exists
        restaurant_detail = await yelp_client.get_business_clean(yelp_id)
        
        # REUSE: get_reviews_clean() method that already exists
        yelp_reviews = await yelp_client.get_reviews_clean(yelp_id)
        
        # Limit to 3 reviews as per task requirements
        yelp_reviews = yelp_reviews[:3] if yelp_reviews else []
        
    except YelpAPIError as e:
        # Log the actual error for debugging
        print(f"Yelp API Error for {yelp_id}: {str(e)}")
        
        # If Yelp fails but we have cache, return cached data
        if cached_restaurant:
            return {
                "status": "success",
                "source": "cache_only",
                "message": "Yelp API unavailable, showing cached data",
                "restaurant": {
                    "id": cached_restaurant.yelp_id,
                    "name": cached_restaurant.name,
                    "rating": cached_restaurant.rating,
                    "price": cached_restaurant.price,
                    "categories": cached_restaurant.categories,
                    "review_count": cached_restaurant.review_count,
                    "address": cached_restaurant.address,
                    "phone": cached_restaurant.phone,
                    "coordinates": {
                        "latitude": cached_restaurant.lat,
                        "longitude": cached_restaurant.lng
                    },
                    "is_open": True,
                    "photos": [],
                    "hours": None,
                    "transactions": [],
                    "yelp_url": f"https://www.yelp.com/biz/{yelp_id}",
                    "image_url": None
                },
                "yelp_reviews": []
            }
        else:
            # No cache and Yelp failed - return error
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": f"Unable to fetch restaurant details. Yelp API error: {str(e)}",
                    "code": "YELP_API_ERROR",
                    "yelp_error": str(e)
                }
            )
    
    # Step 3: Return merged data
    return {
        "status": "success",
        "source": "yelp_api",
        "restaurant": restaurant_detail.model_dump(),
        "yelp_reviews": [review.model_dump() for review in yelp_reviews],
        "cached": cached_restaurant is not None
    }


@router.get("/restaurants/{yelp_id}/reviews")
async def get_restaurant_yelp_reviews(yelp_id: str) -> Dict[str, Any]:
    """
    Get Yelp reviews for a restaurant.
    Separate endpoint if frontend wants to fetch reviews independently.
    """
    try:
        reviews = await yelp_client.get_reviews_clean(yelp_id)
        return {
            "status": "success",
            "yelp_id": yelp_id,
            "reviews": [review.model_dump() for review in reviews[:3]],
            "total": len(reviews)
        }
    except YelpAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": f"Unable to fetch reviews: {str(e)}",
                "code": "YELP_API_ERROR"
            }
        )


