"""
Borough seeding module for NYC restaurant data.
Fetches restaurant data from Yelp API and stores in local database.
"""
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import RestaurantCache
from app.clients.yelp import yelp_client, YelpAPIError
from app.schemas import RestaurantSummary


class BoroughSeeder:
    """
    Handles seeding restaurant data for NYC boroughs.
    
    This class manages:
    - Fetching data from Yelp API
    - Transforming data to database format
    - Upserting records in database
    - Error handling and logging
    """
    
    # NYC Boroughs mapping
    BOROUGHS = {
        "MAN": "Manhattan, NY",
        "BK": "Brooklyn, NY", 
        "QN": "Queens, NY",
        "BX": "Bronx, NY",
        "SI": "Staten Island, NY"
    }
    
    def __init__(self, db_session: Session = None):
        """
        Initialize the seeder.
        
        Args:
            db_session: Database session. If None, creates a new one.
        """
        self.db = db_session or SessionLocal()
        self.stats = {
            "total_fetched": 0,
            "total_upserted": 0,
            "errors": 0,
            "boroughs_processed": 0
        }
    
    async def fetch_restaurants_for_borough(
        self, 
        borough_code: str, 
        limit: int = 100
    ) -> List[RestaurantSummary]:
        """
        Fetch restaurants for a specific borough from Yelp API.
        
        Args:
            borough_code: Borough code (MAN, BK, QN, BX, SI)
            limit: Number of restaurants to fetch
            
        Returns:
            List of clean RestaurantSummary objects
            
        Raises:
            YelpAPIError: If Yelp API call fails
        """
        if borough_code not in self.BOROUGHS:
            raise ValueError(f"Invalid borough code: {borough_code}")
        
        location = self.BOROUGHS[borough_code]
        
        print(f"🔍 Fetching {limit} restaurants for {borough_code} ({location})...")
        
        try:
            # Use our clean Yelp client method
            restaurants = await yelp_client.search_businesses_clean(
                term="restaurants",
                location=location,
                limit=limit
            )
            
            print(f"✅ Fetched {len(restaurants)} restaurants for {borough_code}")
            self.stats["total_fetched"] += len(restaurants)
            
            return restaurants
            
        except YelpAPIError as e:
            print(f"❌ Error fetching restaurants for {borough_code}: {e}")
            self.stats["errors"] += 1
            raise
    
    def transform_to_db_model(
        self, 
        restaurant: RestaurantSummary, 
        borough_code: str
    ) -> RestaurantCache:
        """
        Transform RestaurantSummary DTO to RestaurantCache database model.
        
        Args:
            restaurant: Clean restaurant data from Yelp
            borough_code: Borough code for this restaurant
            
        Returns:
            RestaurantCache database model ready for insertion
        """
        # Convert all categories to lowercase for case-insensitive search
        lowercase_categories = [cat.lower() for cat in restaurant.categories] if restaurant.categories else []
        
        return RestaurantCache(
            yelp_id=restaurant.id,
            name=restaurant.name,
            location_code=borough_code,
            lat=restaurant.coordinates.get("latitude") if restaurant.coordinates else 0.0,
            lng=restaurant.coordinates.get("longitude") if restaurant.coordinates else 0.0,
            price=restaurant.price,
            rating=restaurant.rating,
            review_count=restaurant.review_count,
            categories=lowercase_categories,
            phone=restaurant.phone,
            address=restaurant.address,
            provider="yelp",
            last_fetched_at=datetime.utcnow()
        )
    
    def upsert_restaurant(self, restaurant: RestaurantSummary, borough_code: str) -> bool:
        """
        Insert or update restaurant in database.
        
        Args:
            restaurant: Restaurant data to upsert
            borough_code: Borough code for this restaurant
            
        Returns:
            True if successful, False if error
        """
        try:
            # Check if restaurant already exists
            existing = self.db.query(RestaurantCache).filter(
                RestaurantCache.yelp_id == restaurant.id
            ).first()
            
            if existing:
                # Update existing record
                # Convert categories to lowercase for consistency
                lowercase_categories = [cat.lower() for cat in restaurant.categories] if restaurant.categories else []
                
                existing.name = restaurant.name
                existing.rating = restaurant.rating
                existing.review_count = restaurant.review_count
                existing.categories = lowercase_categories
                existing.phone = restaurant.phone
                existing.address = restaurant.address
                existing.last_fetched_at = datetime.utcnow()
                
                print(f"🔄 Updated: {restaurant.name}")
            else:
                # Create new record
                new_restaurant = self.transform_to_db_model(restaurant, borough_code)
                self.db.add(new_restaurant)
                
                print(f"➕ Added: {restaurant.name}")
            
            self.db.commit()
            self.stats["total_upserted"] += 1
            return True
            
        except IntegrityError as e:
            print(f"❌ Database error for {restaurant.name}: {e}")
            self.db.rollback()
            self.stats["errors"] += 1
            return False
        except Exception as e:
            print(f"❌ Unexpected error for {restaurant.name}: {e}")
            self.db.rollback()
            self.stats["errors"] += 1
            return False
    
    async def seed_borough(self, borough_code: str, limit: int = 100) -> bool:
        """
        Seed restaurants for a single borough.
        
        Args:
            borough_code: Borough code to seed
            limit: Number of restaurants to fetch
            
        Returns:
            True if successful, False if error
        """
        try:
            # Fetch restaurants from Yelp
            restaurants = await self.fetch_restaurants_for_borough(borough_code, limit)
            
            # Upsert each restaurant
            for restaurant in restaurants:
                self.upsert_restaurant(restaurant, borough_code)
            
            self.stats["boroughs_processed"] += 1
            print(f"✅ Completed seeding {borough_code}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to seed {borough_code}: {e}")
            return False
    
    async def seed_all_boroughs(self, limit: int = 100) -> Dict[str, Any]:
        """
        Seed restaurants for all NYC boroughs.
        
        Args:
            limit: Number of restaurants per borough
            
        Returns:
            Statistics about the seeding process
        """
        print(f"🚀 Starting seeding process for all boroughs (limit: {limit} per borough)")
        print(f"📊 Total expected restaurants: {len(self.BOROUGHS) * limit}")
        
        # Process each borough
        for borough_code in self.BOROUGHS.keys():
            await self.seed_borough(borough_code, limit)
            
            # Small delay to be nice to Yelp API
            await asyncio.sleep(1)
        
        # Print final statistics
        print("\n📈 SEEDING COMPLETE!")
        print(f"✅ Boroughs processed: {self.stats['boroughs_processed']}")
        print(f"📥 Total fetched: {self.stats['total_fetched']}")
        print(f"💾 Total upserted: {self.stats['total_upserted']}")
        print(f"❌ Errors: {self.stats['errors']}")
        
        return self.stats
    
    def close(self):
        """Close database session."""
        if self.db:
            self.db.close()


async def main():
    """
    Main function for CLI usage.
    """
    parser = argparse.ArgumentParser(description="Seed NYC boroughs with restaurant data")
    parser.add_argument(
        "--limit", 
        type=int, 
        default=100, 
        help="Number of restaurants to fetch per borough (default: 100)"
    )
    parser.add_argument(
        "--borough",
        type=str,
        choices=["MAN", "BK", "QN", "BX", "SI"],
        help="Seed only specific borough (optional)"
    )
    
    args = parser.parse_args()
    
    seeder = BoroughSeeder()
    
    try:
        if args.borough:
            # Seed single borough
            await seeder.seed_borough(args.borough, args.limit)
        else:
            # Seed all boroughs
            await seeder.seed_all_boroughs(args.limit)
            
    except KeyboardInterrupt:
        print("\n⏹️ Seeding interrupted by user")
    except Exception as e:
        print(f"\n💥 Seeding failed: {e}")
    finally:
        seeder.close()


if __name__ == "__main__":
    asyncio.run(main())