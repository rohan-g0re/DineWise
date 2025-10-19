"""
Search router - handles restaurant search functionality.
Provides both cached NYC borough searches and live Yelp API searches.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from sqlmodel import Session, select, or_
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB
from app.db import get_db
from app.models import RestaurantCache
from app.clients.yelp import yelp_client, YelpAPIError
from app.schemas import RestaurantSummary

# Create router instance
router = APIRouter()

# NYC borough codes we have cached data for
NYC_BOROUGHS = {"MAN", "BK", "QN", "BX", "SI"}

@router.get("/search")
async def search_restaurants(
    q: Optional[str] = Query(None, description="Search query (e.g., 'pizza', 'ramen')"),
    location: Optional[str] = Query(None, description="Location (MAN/BK/QN/BX/SI or custom)"),
    cuisine: Optional[str] = Query(None, description="Cuisine type"),
    price: Optional[str] = Query(None, description="Price range (comma-separated: $,$$,$$$,$$$$)"),
    rating_min: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum rating"),
    limit: int = Query(20, ge=1, le=50, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Search for restaurants using either cached NYC borough data or Yelp API.
    """
    
    # STEP 1: Normalize parameters
    query = q.strip() if q else ""
    location_code = location.upper() if location else None
    
    # Parse price ranges
    price_ranges = []
    if price:
        price_ranges = [p.strip() for p in price.split(",") if p.strip()]
    
    # Clamp rating_min
    if rating_min is not None:
        rating_min = max(1.0, min(5.0, rating_min))
    
    # STEP 2: Route to appropriate search method
    if location_code in NYC_BOROUGHS:
        # Use cached database search for NYC boroughs
        results = await _search_cached_restaurants(
            db=db,
            query=query,
            location_code=location_code,
            cuisine=cuisine,
            price_ranges=price_ranges,
            rating_min=rating_min,
            limit=limit,
            offset=offset
        )
        search_method = "cached_db"
    else:
        # REUSE the existing Yelp function! 🎯
        try:
            # Convert price ranges to Yelp format (1-4)
            yelp_price = None
            if price_ranges:
                price_mapping = {"$": "1", "$$": "2", "$$$": "3", "$$$$": "4"}
                yelp_prices = [price_mapping.get(p) for p in price_ranges if p in price_mapping]
                if yelp_prices:
                    yelp_price = ",".join(yelp_prices)
            
            # Build search term
            search_term = query if query else "restaurants"
            if cuisine:
                search_term = f"{search_term} {cuisine}"
            
            # REUSE the existing function from yelp.py!
            # NOTE: Yelp API does NOT support rating filtering
            results = await yelp_client.search_businesses_clean(
                term=search_term,
                location=location,
                price=yelp_price,
                rating=None,  # Yelp API doesn't support rating parameter
                limit=limit,
                offset=offset
            )
            
            # Filter out businesses with no reviews (Yelp API rejects them)
            results = [r for r in results if r.review_count > 0]
            
            # Apply rating filter manually (Yelp API doesn't support this)
            if rating_min is not None:
                results = [r for r in results if r.rating >= rating_min]
            
            # Cache search results for fallback when details API fails
            _cache_search_results(db, results)
            
            search_method = "yelp_api"
            
        except YelpAPIError as e:
            raise HTTPException(
                status_code=429 if "rate limit" in str(e).lower() else 400,
                detail={
                    "message": str(e),
                    "code": "YELP_API_ERROR"
                }
            )
    
    # STEP 3: Return standardized response
    return {
        "status": "success",
        "method": search_method,
        "total": len(results),
        "limit": limit,
        "offset":offset,
        "restaurants": results
    }


async def _search_cached_restaurants(
    db: Session,
    query: str,
    location_code: str,
    cuisine: Optional[str],
    price_ranges: List[str],
    rating_min: Optional[float],
    limit: int,
    offset: int
) -> List[RestaurantSummary]:
    """
    Search cached restaurants in our database.
    """
    
    # Start building the query
    sql_query = select(RestaurantCache).where(
        RestaurantCache.location_code == location_code,
        RestaurantCache.review_count > 0  # Filter out zero-review restaurants
    )
    
    # Add text search filter - Search in name and lowercase categories
    if query:
        query_lower = query.lower()
        sql_query = sql_query.where(
            or_(
                RestaurantCache.name.ilike(f"%{query}%"),
                # Categories are stored in lowercase, so search with lowercase query
                cast(RestaurantCache.categories, JSONB).contains([query_lower])
            )
        )
    
    # Add cuisine filter - Search in lowercase categories
    if cuisine:
        cuisine_lower = cuisine.lower()
        sql_query = sql_query.where(
            cast(RestaurantCache.categories, JSONB).contains([cuisine_lower])
        )
    
    # Add price filter
    if price_ranges:
        sql_query = sql_query.where(
            RestaurantCache.price.in_(price_ranges)
        )
    
    # Add rating filter
    if rating_min is not None:
        sql_query = sql_query.where(
            RestaurantCache.rating >= rating_min
        )
    
    # Add ordering, limit, and offset
    sql_query = sql_query.order_by(
        RestaurantCache.rating.desc(),
        RestaurantCache.review_count.desc()
    ).offset(offset).limit(limit)
    
    # Execute query
    cached_restaurants = db.execute(sql_query).scalars().all()
    
    # Convert to RestaurantSummary objects (same format as Yelp results)
    results = []
    for restaurant in cached_restaurants:
        results.append(RestaurantSummary(
            id=restaurant.yelp_id,
            name=restaurant.name,
            rating=restaurant.rating,
            price=restaurant.price,
            categories=restaurant.categories,
            image_url=None,  # We don't store images in cache
            distance=None,   # We don't store distance in cache
            is_open=True,    # Assume open
            review_count=restaurant.review_count,
            address=restaurant.address,
            phone=restaurant.phone,
            yelp_url=None,   # We don't store Yelp URL in cache
            coordinates={
                "latitude": restaurant.lat,
                "longitude": restaurant.lng
            }
        ))
    
    return results
    

@router.get("/nearby")
async def search_nearby_restaurants(
    latitude: float = Query(..., description="User latitude coordinate"),
    longitude: float = Query(..., description="User longitude coordinate"),
    radius: int = Query(5000, ge=100, le=40000, description="Search radius in meters (max 40km)"),
    limit: int = Query(20, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Search for restaurants near a specific location with strict radius filtering.
    This endpoint is specifically for the Store Locator feature.
    
    Unlike the general search endpoint, this enforces strict radius filtering
    because Yelp API doesn't always respect the radius parameter.
    """
    try:
        print(f"🔍 Nearby Search: lat={latitude}, lng={longitude}, radius={radius}m")
        
        # Call Yelp API with radius parameter
        raw_result = await yelp_client.search_nearby(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            categories="restaurants",
            limit=limit
        )
        
        # Transform results
        results = []
        for business in raw_result.get("businesses", []):
            results.append(yelp_client._transform_business_to_summary(business))
        
        # CRITICAL: Yelp API doesn't strictly enforce radius parameter
        # It treats it more as a "suggestion", so we filter server-side
        initial_count = len(results)
        results = [r for r in results if r.distance is not None and r.distance <= radius]
        filtered_count = initial_count - len(results)
        
        if filtered_count > 0:
            print(f"⚠️ Filtered out {filtered_count} restaurants beyond {radius}m radius")
        print(f"✅ Returning {len(results)} restaurants within {radius}m")
        
        # Filter out businesses with no reviews
        results = [r for r in results if r.review_count > 0]
        
        # Cache for fallback
        _cache_search_results(db, results)
        
        return {
            "status": "success",
            "method": "yelp_nearby_strict",
            "total": len(results),
            "radius_meters": radius,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "restaurants": results
        }
        
    except YelpAPIError as e:
        raise HTTPException(
            status_code=429 if "rate limit" in str(e).lower() else 400,
            detail={
                "message": str(e),
                "code": "YELP_API_ERROR"
            }
        )


@router.get("/test")
async def test_search_endpoints():
    """
    Test endpoint to verify search functionality.
    """
    return {
        "message": "Search endpoints are working!",
        "available_endpoints": [
            "GET /search - Main search endpoint",
            "GET /search/nearby - Nearby restaurants with strict radius filtering (for locator)",
            "GET /search/test - This test endpoint"
        ],
        "nyc_boroughs": list(NYC_BOROUGHS),
        "example_requests": [
            "/search?q=pizza&location=MAN&limit=5",
            "/search?q=ramen&location=Brooklyn, NY&rating_min=4.0",
            "/search?cuisine=italian&price=$,$$&location=BK",
            "/search/nearby?latitude=40.7580&longitude=-73.9855&radius=1000"
        ]
    }


def _cache_search_results(db: Session, results: List[RestaurantSummary]):
    """
    Cache search results so they can be used as fallback when Yelp details API fails.
    This helps handle Yelp's inconsistent API behavior.
    """
    try:
        from datetime import datetime, timezone
        
        for restaurant in results:
            # Check if already exists
            existing = db.exec(
                select(RestaurantCache).where(RestaurantCache.yelp_id == restaurant.id)
            ).first()
            
            if existing:
                # Update existing cache
                existing.name = restaurant.name
                existing.rating = restaurant.rating
                existing.price = restaurant.price
                existing.categories = restaurant.categories
                existing.review_count = restaurant.review_count
                existing.address = restaurant.address
                existing.phone = restaurant.phone
                existing.updated_at = datetime.now(timezone.utc)
                
                if restaurant.coordinates:
                    existing.lat = restaurant.coordinates.get("latitude")
                    existing.lng = restaurant.coordinates.get("longitude")
            else:
                # Create new cache entry
                lat = restaurant.coordinates.get("latitude") if restaurant.coordinates else None
                lng = restaurant.coordinates.get("longitude") if restaurant.coordinates else None
                
                new_cache = RestaurantCache(
                    yelp_id=restaurant.id,
                    name=restaurant.name,
                    rating=restaurant.rating,
                    price=restaurant.price,
                    categories=restaurant.categories,
                    review_count=restaurant.review_count,
                    address=restaurant.address,
                    phone=restaurant.phone,
                    lat=lat,
                    lng=lng,
                    location_code="SEARCH",  # Mark as from search, not NYC borough
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(new_cache)
        
        db.commit()
        
    except Exception as e:
        print(f"⚠️ Error caching search results: {e}")
        db.rollback()
        # Don't raise - caching failure shouldn't break search