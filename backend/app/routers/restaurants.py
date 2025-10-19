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
    
    Flow:
    1. Try Yelp API for fresh details
    2. If Yelp fails, check cache for basic info
    3. Return whatever data we have
    """
    
    # Check if we have cached data as fallback
    cached_restaurant = db.exec(
        select(RestaurantCache).where(RestaurantCache.yelp_id == yelp_id)
    ).first()
    
    try:
        # Try to fetch full details from Yelp (includes hours, photos, etc.)
        print(f"🔍 Fetching details for {yelp_id} from Yelp API...")
        restaurant_detail = await yelp_client.get_business_clean(yelp_id)
        print(f"✅ Got details from Yelp for {yelp_id}")
        
        # Fetch reviews from Yelp (up to 3) - handle failure gracefully
        yelp_reviews = []
        try:
            yelp_reviews = await yelp_client.get_reviews_clean(yelp_id)
            yelp_reviews = yelp_reviews[:3] if yelp_reviews else []
            print(f"✅ Got {len(yelp_reviews)} reviews from Yelp")
        except YelpAPIError as review_error:
            print(f"⚠️ Reviews API failed for {yelp_id}: {str(review_error)}")
            print(f"   Continuing with business details but no reviews")
            # Continue anyway - we have business details
        
        return {
            "status": "success",
            "source": "yelp_api",
            "restaurant": restaurant_detail.model_dump(),
            "yelp_reviews": [review.model_dump() for review in yelp_reviews]
        }
        
    except YelpAPIError as e:
        print(f"❌ Business Details API failed for {yelp_id}: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        
        # Fallback to cached data if available (from search results)
        if cached_restaurant:
            return {
                "status": "success",
                "source": "cache",
                "message": "Showing basic info (full details unavailable from Yelp)",
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
        
        # No cache and Yelp failed - return error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Restaurant details unavailable. The business may have closed or moved.",
                "code": "RESTAURANT_NOT_FOUND"
            }
        )


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


