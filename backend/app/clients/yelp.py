"""
Yelp Fusion API client for restaurant search and details.
Handles authentication, rate limiting, and data mapping.
"""
import httpx
from app.core.config import settings
from typing import Dict, Any, List
from app.schemas import RestaurantSummary, RestaurantDetail, YelpReview



class YelpAPIError(Exception):
    """Base exception for Yelp API errors."""
    pass


class YelpRateLimitError(YelpAPIError):
    """Raised when Yelp API rate limit is exceeded."""
    pass


class YelpBadRequestError(YelpAPIError):
    """Raised when request parameters are invalid."""
    pass


class YelpClient:
    """
    Async client for Yelp Fusion API.
    
    This class handles:
    - Authentication with Yelp API
    - Making HTTP requests
    - Error handling and rate limiting
    - Data transformation
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Yelp client.
        
        Args:
            api_key: Yelp API key. If None, uses settings.yelp_api_key
        """
        self.api_key = api_key or settings.yelp_api_key
        self.base_url = "https://api.yelp.com/v3"
        
        # Headers that will be sent with every request
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to Yelp API.
        
        This is a private method (starts with _) that handles:
        - Making the actual HTTP call
        - Error handling
        - Response parsing
        
        Args:
            endpoint: API endpoint (e.g., "/businesses/search")
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            YelpRateLimitError: When rate limit exceeded
            YelpBadRequestError: When request is invalid
            YelpAPIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        # Use httpx.AsyncClient for async requests
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                
                # Handle different HTTP status codes
                if response.status_code == 429:
                    raise YelpRateLimitError("Yelp API rate limit exceeded. Please try again later.")
                elif response.status_code == 400:
                    raise YelpBadRequestError(f"Invalid request: {response.text}")
                elif response.status_code != 200:
                    raise YelpAPIError(f"Yelp API error: {response.status_code} - {response.text}")
                
                return response.json()
                
            except httpx.RequestError as e:
                raise YelpAPIError(f"Network error connecting to Yelp API: {str(e)}")
        
    async def search_businesses(
        self,
        term: str = "restaurants",
        location: str = None,
        latitude: float = None,
        longitude: float = None,
        price: str = None,
        rating: float = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for businesses using Yelp's search API.
        
        Args:
            term: Search term (e.g., "pizza", "restaurants")
            location: Location string (e.g., "New York, NY")
            latitude: Latitude for location-based search
            longitude: Longitude for location-based search
            price: Price range (1-4, comma-separated: "1,2,3")
            rating: Minimum rating (1.0-5.0)
            limit: Number of results (max 50)
            offset: Number of results to skip (for pagination)
            
        Returns:
            Yelp API response with businesses list
        """
        # Build query parameters
        params = {
            "term": term,
            "limit": min(limit, 50),  # Yelp max is 50
            "offset": offset
        }
        
        # Add location (either string or lat/lng)
        if location:
            params["location"] = location
        elif latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude
        else:
            raise YelpBadRequestError("Either location or latitude/longitude must be provided")
        
        # Add optional filters
        if price:
            params["price"] = price
        if rating:
            params["rating"] = rating
        
        return await self._make_request("/businesses/search", params)
    
    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius: int = 1000,
        categories: str = None,
        price: str = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for businesses near a specific location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in meters (max 40000)
            categories: Business categories (comma-separated)
            price: Price range (1-4, comma-separated)
            limit: Number of results (max 50)
            
        Returns:
            Yelp API response with nearby businesses
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": min(radius, 40000),  # Yelp max is 40km
            "limit": min(limit, 50)
        }
        
        if categories:
            params["categories"] = categories
        if price:
            params["price"] = price
        
        return await self._make_request("/businesses/search", params)
    
    async def get_business(self, business_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific business.
        
        Args:
            business_id: Yelp business ID
            
        Returns:
            Detailed business information
        """
        return await self._make_request(f"/businesses/{business_id}")
    
    async def get_reviews(self, business_id: str) -> Dict[str, Any]:
        """
        Get reviews for a specific business.
        
        Args:
            business_id: Yelp business ID
            
        Returns:
            Business reviews
        """
        return await self._make_request(f"/businesses/{business_id}/reviews")



    # Add these imports at the top of your yelp.py file
    # Add these transformation functions to your YelpClient class
    
    def _transform_business_to_summary(self, yelp_data: Dict[str, Any]) -> RestaurantSummary:
        """
        Transform raw Yelp business data into clean RestaurantSummary DTO.
        
        This method handles the messy Yelp API response and converts it to
        a clean, predictable structure for your frontend.
        
        Args:
            yelp_data: Raw business data from Yelp API
            
        Returns:
            Clean RestaurantSummary object
        """
        # Extract categories (Yelp returns [{"alias": "pizza", "title": "Pizza"}])
        categories = [cat["title"] for cat in yelp_data.get("categories", [])]
        
        # Extract address (Yelp returns nested location object)
        location = yelp_data.get("location", {})
        address_parts = [
            location.get("address1"),
            location.get("city"),
            location.get("state")
        ]
        address = ", ".join(filter(None, address_parts)) if any(address_parts) else None
        
        return RestaurantSummary(
            id=yelp_data["id"],
            name=yelp_data["name"],
            rating=yelp_data["rating"],
            price=yelp_data.get("price"),
            categories=categories,
            image_url=yelp_data.get("image_url"),
            distance=yelp_data.get("distance"),
            is_open=not yelp_data.get("is_closed", True),
            review_count=yelp_data.get("review_count", 0),
            address=address,
            phone=yelp_data.get("display_phone"),
            yelp_url=yelp_data.get("url"),
            coordinates=yelp_data.get("coordinates")
        )
    
    def _transform_business_to_detail(self, yelp_data: Dict[str, Any]) -> RestaurantDetail:
        """
        Transform raw Yelp business data into detailed RestaurantDetail DTO.
        
        Args:
            yelp_data: Raw business data from Yelp API
            
        Returns:
            Clean RestaurantDetail object
        """
        # Extract categories
        categories = [cat["title"] for cat in yelp_data.get("categories", [])]
        
        # Extract address
        location = yelp_data.get("location", {})
        address_parts = [
            location.get("address1"),
            location.get("city"),
            location.get("state")
        ]
        address = ", ".join(filter(None, address_parts)) if any(address_parts) else None
        
        # Extract photos (Yelp returns list of photo URLs)
        photos = yelp_data.get("photos", [])
        
        # Extract coordinates
        coordinates = yelp_data.get("coordinates", {})
        
        # Extract business hours
        hours = yelp_data.get("business_hours", [])
        
        # Extract transactions (delivery, pickup, etc.)
        transactions = yelp_data.get("transactions", [])
        
        return RestaurantDetail(
            id=yelp_data["id"],
            name=yelp_data["name"],
            rating=yelp_data["rating"],
            price=yelp_data.get("price"),
            categories=categories,
            image_url=yelp_data.get("image_url"),
            photos=photos,
            is_open=not yelp_data.get("is_closed", True),
            review_count=yelp_data.get("review_count", 0),
            address=address,
            phone=yelp_data.get("display_phone"),
            yelp_url=yelp_data.get("url"),
            coordinates=coordinates,
            hours=hours[0] if hours else None,  # Take first hours entry
            transactions=transactions
        )
    
    def _transform_review(self, yelp_review_data: Dict[str, Any]) -> YelpReview:
        """
        Transform raw Yelp review data into clean YelpReview DTO.
        
        Args:
            yelp_review_data: Raw review data from Yelp API
            
        Returns:
            Clean YelpReview object
        """
        return YelpReview(
            id=yelp_review_data["id"],
            rating=yelp_review_data["rating"],
            text=yelp_review_data["text"],
            time_created=yelp_review_data["time_created"],
            user=yelp_review_data["user"],
            url=yelp_review_data.get("url")
        )
    
    # Update your existing methods to use transformations
    async def search_businesses_clean(
        self,
        term: str = "restaurants",
        location: str = None,
        latitude: float = None,
        longitude: float = None,
        price: str = None,
        rating: float = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[RestaurantSummary]:
        """
        Search for businesses and return clean DTOs.
        
        This is a wrapper around search_businesses that automatically
        transforms the raw Yelp data into clean RestaurantSummary objects.
        """
        # Get raw data from Yelp
        raw_result = await self.search_businesses(
            term=term,
            location=location,
            latitude=latitude,
            longitude=longitude,
            price=price,
            rating=rating,
            limit=limit,
            offset=offset
        )
        
        # Transform each business to clean DTO
        clean_businesses = []
        for business in raw_result.get("businesses", []):
            clean_businesses.append(self._transform_business_to_summary(business))
        
        return clean_businesses
    
    async def get_business_clean(self, business_id: str) -> RestaurantDetail:
        """
        Get detailed business information and return clean DTO.
        """
        raw_result = await self.get_business(business_id)
        return self._transform_business_to_detail(raw_result)
    
    async def get_reviews_clean(self, business_id: str) -> List[YelpReview]:
        """
        Get business reviews and return clean DTOs.
        """
        raw_result = await self.get_reviews(business_id)
        clean_reviews = []
        for review in raw_result.get("reviews", []):
            clean_reviews.append(self._transform_review(review))
        return clean_reviews



# Create a single instance of the Yelp client
# This follows the singleton pattern - one client for the entire app
yelp_client = YelpClient()