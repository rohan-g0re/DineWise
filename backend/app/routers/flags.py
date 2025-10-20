"""
User restaurant flags router - for visited status and promo preferences.
Future-proofing for event notifications and personalization.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_db
from app.models import User, UserRestaurantFlags, RestaurantCache
from app.schemas import UserRestaurantFlagsCreate, UserRestaurantFlagsUpdate
from app.auth.deps import get_current_user
from typing import Dict, Any
from datetime import datetime

router = APIRouter()


@router.put("/flags/{yelp_id}")
async def upsert_flags(
    yelp_id: str,
    flags_data: UserRestaurantFlagsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create or update flags for a restaurant.
    Uses upsert pattern - creates if doesn't exist, updates if it does.
    """
    
    # Check if flags already exist
    existing_flags = db.exec(
        select(UserRestaurantFlags).where(
            UserRestaurantFlags.user_id == current_user.id,
            UserRestaurantFlags.yelp_id == yelp_id
        )
    ).first()
    
    if existing_flags:
        # Update existing flags
        if flags_data.visited is not None:
            existing_flags.visited = flags_data.visited
        if flags_data.promo_opt_in is not None:
            existing_flags.promo_opt_in = flags_data.promo_opt_in
        existing_flags.updated_at = datetime.utcnow()
        
        db.add(existing_flags)
        db.commit()
        db.refresh(existing_flags)
        
        return {
            "status": "success",
            "message": "Flags updated successfully",
            "flags": {
                "id": existing_flags.id,
                "yelp_id": existing_flags.yelp_id,
                "visited": existing_flags.visited,
                "promo_opt_in": existing_flags.promo_opt_in,
                "updated_at": existing_flags.updated_at
            }
        }
    else:
        # Create new flags
        new_flags = UserRestaurantFlags(
            user_id=current_user.id,
            yelp_id=yelp_id,
            visited=flags_data.visited if flags_data.visited is not None else False,
            promo_opt_in=flags_data.promo_opt_in if flags_data.promo_opt_in is not None else False
        )
        
        db.add(new_flags)
        db.commit()
        db.refresh(new_flags)
        
        return {
            "status": "success",
            "message": "Flags created successfully",
            "flags": {
                "id": new_flags.id,
                "yelp_id": new_flags.yelp_id,
                "visited": new_flags.visited,
                "promo_opt_in": new_flags.promo_opt_in,
                "updated_at": new_flags.updated_at
            }
        }


@router.get("/flags")
async def get_all_flags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all flags for the current user.
    Enriched with restaurant data from cache.
    """
    
    flags = db.exec(
        select(UserRestaurantFlags).where(UserRestaurantFlags.user_id == current_user.id)
    ).all()
    
    # Enrich with restaurant data
    enriched_flags = []
    for flag in flags:
        restaurant = db.exec(
            select(RestaurantCache).where(RestaurantCache.yelp_id == flag.yelp_id)
        ).first()
        
        flag_data = {
            "id": flag.id,
            "yelp_id": flag.yelp_id,
            "visited": flag.visited,
            "promo_opt_in": flag.promo_opt_in,
            "updated_at": flag.updated_at,
            "restaurant": {
                "name": restaurant.name,
                "address": restaurant.address,
                "rating": restaurant.rating,
                "price": restaurant.price
            } if restaurant else None
        }
        
        enriched_flags.append(flag_data)
    
    return {
        "status": "success",
        "total": len(enriched_flags),
        "flags": enriched_flags
    }


@router.get("/flags/{yelp_id}")
async def get_flags_for_restaurant(
    yelp_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get flags for a specific restaurant.
    Returns default values if no flags exist yet.
    """
    
    flags = db.exec(
        select(UserRestaurantFlags).where(
            UserRestaurantFlags.user_id == current_user.id,
            UserRestaurantFlags.yelp_id == yelp_id
        )
    ).first()
    
    if flags:
        return {
            "status": "success",
            "flags": {
                "id": flags.id,
                "yelp_id": flags.yelp_id,
                "visited": flags.visited,
                "promo_opt_in": flags.promo_opt_in,
                "updated_at": flags.updated_at
            }
        }
    else:
        # Return default values
        return {
            "status": "success",
            "flags": {
                "yelp_id": yelp_id,
                "visited": False,
                "promo_opt_in": False,
                "exists": False
            }
        }


@router.delete("/flags/{yelp_id}")
async def delete_flags(
    yelp_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete flags for a restaurant.
    """
    
    flags = db.exec(
        select(UserRestaurantFlags).where(
            UserRestaurantFlags.user_id == current_user.id,
            UserRestaurantFlags.yelp_id == yelp_id
        )
    ).first()
    
    if not flags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Flags not found", "code": "FLAGS_NOT_FOUND"}
        )
    
    db.delete(flags)
    db.commit()
    
    return {
        "status": "success",
        "message": "Flags deleted successfully",
        "yelp_id": yelp_id
    }



