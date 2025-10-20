"""
Reviews router - community reviews for restaurants.
All POST endpoints require authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_db
from app.models import User, Review, RestaurantCache
from app.schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from app.auth.deps import get_current_user
from typing import List, Dict, Any, Optional

router = APIRouter()


@router.post("/reviews", status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new review for a restaurant.
    Validates rating (1-5) and text length (≤1000 chars).
    """
    
    # Validation is already handled by Pydantic schema
    # Create review
    new_review = Review(
        user_id=current_user.id,
        yelp_id=review_data.yelp_id,
        rating=review_data.rating,
        text=review_data.text.strip()
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return {
        "status": "success",
        "message": "Review created successfully",
        "review": {
            "id": new_review.id,
            "yelp_id": new_review.yelp_id,
            "rating": new_review.rating,
            "text": new_review.text,
            "created_at": new_review.created_at,
            "user": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "email": current_user.email
            }
        }
    }


@router.get("/reviews")
async def get_reviews(
    yelp_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get community reviews for a restaurant.
    If yelp_id not provided, returns all reviews (for admin/testing).
    """
    
    # Build query
    query = select(Review)
    if yelp_id:
        query = query.where(Review.yelp_id == yelp_id)
    
    # Order by newest first
    query = query.order_by(Review.created_at.desc())
    
    reviews = db.exec(query).all()
    
    # Enrich with user data
    enriched_reviews = []
    for review in reviews:
        # Get user info
        user = db.get(User, review.user_id)
        
        # Get restaurant info from cache if available
        restaurant = db.exec(
            select(RestaurantCache).where(RestaurantCache.yelp_id == review.yelp_id)
        ).first()
        
        review_data = {
            "id": review.id,
            "yelp_id": review.yelp_id,
            "rating": review.rating,
            "text": review.text,
            "created_at": review.created_at,
            "user": {
                "id": user.id,
                "full_name": user.full_name
            } if user else None,
            "restaurant": {
                "name": restaurant.name,
                "address": restaurant.address
            } if restaurant else None
        }
        
        enriched_reviews.append(review_data)
    
    return {
        "status": "success",
        "total": len(enriched_reviews),
        "reviews": enriched_reviews
    }


@router.get("/users/me/reviews")
async def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all reviews by the current user.
    """
    
    reviews = db.exec(
        select(Review)
        .where(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
    ).all()
    
    # Enrich with restaurant data
    enriched_reviews = []
    for review in reviews:
        restaurant = db.exec(
            select(RestaurantCache).where(RestaurantCache.yelp_id == review.yelp_id)
        ).first()
        
        review_data = {
            "id": review.id,
            "yelp_id": review.yelp_id,
            "rating": review.rating,
            "text": review.text,
            "created_at": review.created_at,
            "restaurant": {
                "name": restaurant.name,
                "address": restaurant.address,
                "rating": restaurant.rating
            } if restaurant else {"name": "Unknown Restaurant"}
        }
        
        enriched_reviews.append(review_data)
    
    return {
        "status": "success",
        "total": len(enriched_reviews),
        "reviews": enriched_reviews
    }


@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete a review. Only the author can delete their review.
    """
    
    review = db.get(Review, review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Review not found", "code": "REVIEW_NOT_FOUND"}
        )
    
    # Check ownership
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "You can only delete your own reviews", "code": "FORBIDDEN"}
        )
    
    db.delete(review)
    db.commit()
    
    return {
        "status": "success",
        "message": "Review deleted successfully",
        "review_id": review_id
    }


@router.patch("/reviews/{review_id}")
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update a review. Only the author can update their review.
    """
    
    review = db.get(Review, review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Review not found", "code": "REVIEW_NOT_FOUND"}
        )
    
    # Check ownership
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "You can only update your own reviews", "code": "FORBIDDEN"}
        )
    
    # Update fields
    if review_update.rating is not None:
        review.rating = review_update.rating
    if review_update.text is not None:
        review.text = review_update.text.strip()
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return {
        "status": "success",
        "message": "Review updated successfully",
        "review": {
            "id": review.id,
            "yelp_id": review.yelp_id,
            "rating": review.rating,
            "text": review.text,
            "created_at": review.created_at
        }
    }



