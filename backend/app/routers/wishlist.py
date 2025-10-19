"""
Wishlist router - allows users to save favorite restaurants.
All endpoints require authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_db
from app.models import User, Wishlist, RestaurantCache
from app.schemas import WishlistCreate, WishlistResponse
from app.auth.deps import get_current_user
from app.clients.yelp import yelp_client, YelpAPIError
from typing import List, Dict, Any
from datetime import datetime, timezone

router = APIRouter()


@router.post("/wishlist", status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    wishlist_data: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add a restaurant to user's wishlist.
    Uses upsert pattern - won't fail if already exists.
    Also caches restaurant details from Yelp for profile display.
    """
    
    # Check if already in wishlist
    existing = db.exec(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.yelp_id == wishlist_data.yelp_id
        )
    ).first()
    
    if existing:
        return {
            "status": "success",
            "message": "Restaurant already in wishlist",
            "wishlist_item": {
                "id": existing.id,
                "yelp_id": existing.yelp_id,
                "created_at": existing.created_at
            }
        }
    
    # Try to cache restaurant details if not already cached
    cached_restaurant = db.exec(
        select(RestaurantCache).where(RestaurantCache.yelp_id == wishlist_data.yelp_id)
    ).first()
    
    if not cached_restaurant:
        try:
            print(f"📥 Fetching restaurant details from Yelp for {wishlist_data.yelp_id}")
            restaurant_detail = await yelp_client.get_business_clean(wishlist_data.yelp_id)
            
            # Cache the restaurant details
            cached_restaurant = RestaurantCache(
                yelp_id=restaurant_detail.id,
                name=restaurant_detail.name,
                rating=restaurant_detail.rating,
                price=restaurant_detail.price,
                categories=restaurant_detail.categories,
                review_count=restaurant_detail.review_count,
                address=restaurant_detail.address,
                phone=restaurant_detail.phone,
                lat=restaurant_detail.coordinates.get("latitude") if restaurant_detail.coordinates else None,
                lng=restaurant_detail.coordinates.get("longitude") if restaurant_detail.coordinates else None,
                location_code="WISHLIST",  # Mark as from wishlist
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(cached_restaurant)
            db.commit()
            print(f"✅ Cached restaurant details for {restaurant_detail.name}")
        except YelpAPIError as e:
            print(f"⚠️ Could not fetch restaurant details from Yelp: {e}")
            # Continue anyway - wishlist still added, just no cached details
    
    # Create new wishlist item
    new_wishlist_item = Wishlist(
        user_id=current_user.id,
        yelp_id=wishlist_data.yelp_id
    )
    
    db.add(new_wishlist_item)
    db.commit()
    db.refresh(new_wishlist_item)
    
    return {
        "status": "success",
        "message": "Restaurant added to wishlist",
        "wishlist_item": {
            "id": new_wishlist_item.id,
            "yelp_id": new_wishlist_item.yelp_id,
            "created_at": new_wishlist_item.created_at
        }
    }


@router.get("/wishlist")
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user's wishlist with restaurant details.
    Joins with RestaurantCache to provide basic info.
    """
    
    # Get all wishlist items for user
    wishlist_items = db.exec(
        select(Wishlist).where(Wishlist.user_id == current_user.id)
    ).all()
    
    # Enrich with restaurant data from cache
    enriched_items = []
    for item in wishlist_items:
        # Try to get restaurant from cache
        cached_restaurant = db.exec(
            select(RestaurantCache).where(RestaurantCache.yelp_id == item.yelp_id)
        ).first()
        
        item_data = {
            "id": item.id,
            "yelp_id": item.yelp_id,
            "created_at": item.created_at,
            "restaurant": None
        }
        
        if cached_restaurant:
            item_data["restaurant"] = {
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
                }
            }
        
        enriched_items.append(item_data)
    
    return {
        "status": "success",
        "total": len(enriched_items),
        "wishlist": enriched_items
    }


@router.delete("/wishlist/{yelp_id}", status_code=status.HTTP_200_OK)
async def remove_from_wishlist(
    yelp_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Remove a restaurant from user's wishlist.
    """
    
    # Find the wishlist item
    wishlist_item = db.exec(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.yelp_id == yelp_id
        )
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Restaurant not found in wishlist",
                "code": "NOT_IN_WISHLIST"
            }
        )
    
    # Delete the item
    db.delete(wishlist_item)
    db.commit()
    
    return {
        "status": "success",
        "message": "Restaurant removed from wishlist",
        "yelp_id": yelp_id
    }


@router.get("/wishlist/check/{yelp_id}")
async def check_wishlist_status(
    yelp_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check if a restaurant is in user's wishlist.
    Useful for UI to show wishlist button state.
    """
    
    exists = db.exec(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.yelp_id == yelp_id
        )
    ).first() is not None
    
    return {
        "yelp_id": yelp_id,
        "in_wishlist": exists
    }


@router.post("/wishlist/refresh-details")
async def refresh_wishlist_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Backfill restaurant details for wishlist items that don't have cached data.
    This is useful for fixing existing wishlist items.
    """
    # Get all wishlist items for user
    wishlist_items = db.exec(
        select(Wishlist).where(Wishlist.user_id == current_user.id)
    ).all()
    
    updated_count = 0
    failed_count = 0
    
    for item in wishlist_items:
        # Check if already cached
        cached = db.exec(
            select(RestaurantCache).where(RestaurantCache.yelp_id == item.yelp_id)
        ).first()
        
        if not cached:
            try:
                print(f"📥 Fetching details for {item.yelp_id}")
                restaurant_detail = await yelp_client.get_business_clean(item.yelp_id)
                
                # Cache the restaurant details
                cached_restaurant = RestaurantCache(
                    yelp_id=restaurant_detail.id,
                    name=restaurant_detail.name,
                    rating=restaurant_detail.rating,
                    price=restaurant_detail.price,
                    categories=restaurant_detail.categories,
                    review_count=restaurant_detail.review_count,
                    address=restaurant_detail.address,
                    phone=restaurant_detail.phone,
                    lat=restaurant_detail.coordinates.get("latitude") if restaurant_detail.coordinates else None,
                    lng=restaurant_detail.coordinates.get("longitude") if restaurant_detail.coordinates else None,
                    location_code="WISHLIST",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(cached_restaurant)
                db.commit()
                updated_count += 1
                print(f"✅ Cached details for {restaurant_detail.name}")
            except YelpAPIError as e:
                print(f"⚠️ Failed to fetch {item.yelp_id}: {e}")
                failed_count += 1
    
    return {
        "status": "success",
        "message": f"Refreshed {updated_count} restaurant details",
        "updated": updated_count,
        "failed": failed_count,
        "total": len(wishlist_items)
    }


