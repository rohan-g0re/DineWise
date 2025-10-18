"""
Database models using SQLModel.
These models define both database tables and API response schemas.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from sqlalchemy import UniqueConstraint

# Set metadata for Alembic migrations
SQLMODEL_METADATA = SQLModel.metadata

class User(SQLModel, table=True):
    """
    User model - stores user information from Firebase authentication.
    """
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    firebase_uid: str = Field(unique=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    
    # Relationships
    wishlist_items: List["Wishlist"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
    restaurant_flags: List["UserRestaurantFlags"] = Relationship(back_populates="user")







class RestaurantCache(SQLModel, table=True):
    """
    Restaurant cache - stores restaurant data from Yelp API.
    We cache this to avoid hitting Yelp API limits.
    """
    __tablename__ = "restaurant_cache"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    yelp_id: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    location_code: str = Field(max_length=10)  # MAN, BK, QN, BX, SI
    lat: float = Field()  # Latitude
    lng: float = Field()  # Longitude
    price: Optional[str] = Field(default=None, max_length=10)  # $, $$, $$$, $$$$
    rating: float = Field()  # 1.0 to 5.0
    review_count: int = Field(default=0)
    categories: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # ["Italian", "Pizza"]
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None, max_length=500)
    provider: str = Field(default="yelp", max_length=50)  # "yelp" or "manual"
    last_fetched_at: datetime = Field(default_factory=datetime.utcnow)







class Wishlist(SQLModel, table=True):
    """
    Wishlist - stores restaurants that users want to save for later.
    """
    __tablename__ = "wishlist"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    yelp_id: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="wishlist_items")
    
    # Unique constraint: one user can't add the same restaurant twice
    __table_args__ = (
        UniqueConstraint("user_id", "yelp_id"),
    )






class Review(SQLModel, table=True):
    """
    Review - stores user reviews for restaurants.
    """
    __tablename__ = "reviews"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    yelp_id: str = Field(max_length=255)
    rating: int = Field(ge=1, le=5)  # Rating between 1 and 5
    text: str = Field(max_length=1000)  # Review text
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="reviews")





class UserRestaurantFlags(SQLModel, table=True):
    """
    User restaurant flags - stores user preferences for restaurants.
    Used for future notifications and personalization.
    """
    __tablename__ = "user_restaurant_flags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    yelp_id: str = Field(max_length=255)
    visited: bool = Field(default=False)  # Has user visited this restaurant?
    promo_opt_in: bool = Field(default=False)  # Does user want promo notifications?
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="restaurant_flags")
    
    # Unique constraint: one flag record per user-restaurant combination
    __table_args__ = (
        UniqueConstraint("user_id", "yelp_id"),
    )