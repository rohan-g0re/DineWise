"""
API schemas for request/response models.
These define what data is sent between frontend and backend.
Separate from database models to control API interface.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: str = Field(max_length=255)

class UserCreate(UserBase):
    """Schema for creating a new user."""
    firebase_uid: str = Field(max_length=255)

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = Field(None, max_length=255)

class UserResponse(UserBase):
    """Schema for user API responses."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLModel objects

# =============================================================================
# RESTAURANT SCHEMAS
# =============================================================================

class RestaurantBase(BaseModel):
    """Base restaurant schema."""
    name: str = Field(max_length=255)
    location_code: str = Field(max_length=10)
    lat: float
    lng: float
    price: Optional[str] = Field(None, max_length=10)
    rating: float = Field(ge=1.0, le=5.0)
    review_count: int = Field(ge=0)
    categories: List[str] = Field(default_factory=list)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)

class RestaurantCreate(RestaurantBase):
    """Schema for creating restaurant cache entry."""
    yelp_id: str = Field(max_length=255)

class RestaurantUpdate(BaseModel):
    """Schema for updating restaurant information."""
    name: Optional[str] = Field(None, max_length=255)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    review_count: Optional[int] = Field(None, ge=0)
    categories: Optional[List[str]] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)

class RestaurantResponse(RestaurantBase):
    """Schema for restaurant API responses."""
    id: int
    yelp_id: str
    provider: str
    last_fetched_at: datetime
    
    class Config:
        from_attributes = True

# =============================================================================
# WISHLIST SCHEMAS
# =============================================================================

class WishlistCreate(BaseModel):
    """Schema for adding restaurant to wishlist."""
    yelp_id: str = Field(max_length=255)

class WishlistResponse(BaseModel):
    """Schema for wishlist API responses."""
    id: int
    yelp_id: str
    created_at: datetime
    restaurant: Optional[RestaurantResponse] = None  # Include restaurant details if available
    
    class Config:
        from_attributes = True

# =============================================================================
# REVIEW SCHEMAS
# =============================================================================

class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    yelp_id: str = Field(max_length=255)
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    text: str = Field(max_length=1000, description="Review text")

class ReviewUpdate(BaseModel):
    """Schema for updating a review."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    text: Optional[str] = Field(None, max_length=1000)

class ReviewResponse(BaseModel):
    """Schema for review API responses."""
    id: int
    yelp_id: str
    rating: int
    text: str
    created_at: datetime
    user: Optional[UserResponse] = None  # Include user details if available
    restaurant: Optional[RestaurantResponse] = None  # Include restaurant details if available
    
    class Config:
        from_attributes = True

# =============================================================================
# USER RESTAURANT FLAGS SCHEMAS
# =============================================================================

class UserRestaurantFlagsCreate(BaseModel):
    """Schema for creating user restaurant flags."""
    yelp_id: str = Field(max_length=255)
    visited: bool = Field(default=False)
    promo_opt_in: bool = Field(default=False)

class UserRestaurantFlagsUpdate(BaseModel):
    """Schema for updating user restaurant flags."""
    visited: Optional[bool] = None
    promo_opt_in: Optional[bool] = None

class UserRestaurantFlagsResponse(BaseModel):
    """Schema for user restaurant flags API responses."""
    id: int
    yelp_id: str
    visited: bool
    promo_opt_in: bool
    updated_at: datetime
    restaurant: Optional[RestaurantResponse] = None  # Include restaurant details if available
    
    class Config:
        from_attributes = True

# =============================================================================
# SEARCH SCHEMAS
# =============================================================================

class SearchRequest(BaseModel):
    """Schema for restaurant search requests."""
    query: Optional[str] = Field(None, max_length=255, description="Search term (e.g., 'pizza', 'ramen')")
    location: Optional[str] = Field(None, max_length=255, description="Location to search in")
    cuisine: Optional[str] = Field(None, max_length=100, description="Cuisine type filter")
    price: Optional[List[str]] = Field(None, description="Price range filters ($, $$, $$$, $$$$)")
    rating_min: Optional[float] = Field(None, ge=1.0, le=5.0, description="Minimum rating filter")
    limit: int = Field(default=20, ge=1, le=50, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")

class SearchResponse(BaseModel):
    """Schema for search API responses."""
    restaurants: List[RestaurantResponse]
    total_count: int
    has_more: bool
    next_offset: Optional[int] = None

# =============================================================================
# HEALTH CHECK SCHEMAS
# =============================================================================

class HealthResponse(BaseModel):
    """Schema for health check responses."""
    status: str
    service: str = "DineWise API"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# =============================================================================
# ERROR SCHEMAS
# =============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# YELP API SCHEMAS (Complete the existing section)
# =============================================================================

class RestaurantSummary(BaseModel):
    """Clean, simplified restaurant data for search results."""
    id: str = Field(description="Yelp business ID")
    name: str = Field(description="Restaurant name")
    rating: float = Field(ge=1.0, le=5.0, description="Star rating (1-5)")
    price: Optional[str] = Field(None, description="Price range ($, $$, $$$, $$$$)")
    categories: List[str] = Field(default_factory=list, description="Cuisine categories")
    image_url: Optional[str] = Field(None, description="Restaurant photo URL")
    distance: Optional[float] = Field(None, description="Distance in meters")
    is_open: bool = Field(description="Whether restaurant is currently open")
    review_count: int = Field(ge=0, description="Number of reviews")
    address: Optional[str] = Field(None, description="Full address string")
    phone: Optional[str] = Field(None, description="Phone number")
    yelp_url: Optional[str] = Field(None, description="Link to Yelp page")
    coordinates: Optional[dict] = Field(None, description="Latitude and longitude")  # ← ADD THIS LINE

class RestaurantDetail(BaseModel):
    """Detailed restaurant information for individual pages."""
    id: str = Field(description="Yelp business ID")
    name: str = Field(description="Restaurant name")
    rating: float = Field(ge=1.0, le=5.0, description="Star rating (1-5)")
    price: Optional[str] = Field(None, description="Price range ($, $$, $$$, $$$$)")
    categories: List[str] = Field(default_factory=list, description="Cuisine categories")
    image_url: Optional[str] = Field(None, description="Restaurant photo URL")
    photos: List[str] = Field(default_factory=list, description="Additional photo URLs")
    is_open: bool = Field(description="Whether restaurant is currently open")
    review_count: int = Field(ge=0, description="Number of reviews")
    address: Optional[str] = Field(None, description="Full address string")
    phone: Optional[str] = Field(None, description="Phone number")
    yelp_url: Optional[str] = Field(None, description="Link to Yelp page")
    coordinates: Optional[dict] = Field(None, description="Latitude and longitude")
    hours: Optional[dict] = Field(None, description="Business hours information")
    transactions: List[str] = Field(default_factory=list, description="Available services (delivery, pickup, etc.)")
    

class YelpReview(BaseModel):
    """Individual review from Yelp."""
    id: str = Field(description="Review ID")
    rating: int = Field(ge=1, le=5, description="Star rating (1-5)")
    text: str = Field(description="Review text")
    time_created: str = Field(description="When review was created")
    user: dict = Field(description="Reviewer information")
    url: Optional[str] = Field(None, description="Link to full review")

class YelpSearchResponse(BaseModel):
    """Response from Yelp search API."""
    businesses: List[RestaurantSummary] = Field(default_factory=list)
    total: int = Field(ge=0, description="Total number of results")
    region: Optional[dict] = Field(None, description="Search region information")

class YelpBusinessResponse(BaseModel):
    """Response from Yelp business details API."""
    business: RestaurantDetail
    reviews: List[YelpReview] = Field(default_factory=list)