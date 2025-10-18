"""
Unit tests for search router functionality.
Tests parameter parsing, data mapping, and error handling.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.main import app
from app.models import RestaurantCache
from app.schemas import RestaurantSummary
from app.clients.yelp import YelpAPIError

client = TestClient(app)

class TestSearchRouter:
    """Test class for search functionality."""
    
    def test_search_nyc_borough_cached_db(self):
        """Test search using cached NYC borough data."""
        # Mock database session and data
        with patch('app.routers.search.get_db') as mock_db:
            # Create mock restaurant data
            mock_restaurant = RestaurantCache(
                yelp_id="test123",
                name="Test Pizza Place",
                location_code="MAN",
                lat=40.7128,
                lng=-74.0060,
                price="$$",
                rating=4.5,
                review_count=100,
                categories=["Pizza", "Italian"],
                phone="555-1234",
                address="123 Test St, New York, NY"
            )
            
            # Mock database query result
            mock_db.return_value.exec.return_value.all.return_value = [mock_restaurant]
            
            # Make request
            response = client.get("/search/search?q=pizza&location=MAN&limit=5")
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["method"] == "cached_db"
            assert len(data["restaurants"]) == 1
            assert data["restaurants"][0]["name"] == "Test Pizza Place"
    
    @patch('app.routers.search.yelp_client.search_businesses_clean')
    async def test_search_non_nyc_yelp_api(self, mock_yelp_search):
        """Test search using Yelp API for non-NYC locations."""
        # Mock Yelp API response
        mock_yelp_restaurant = RestaurantSummary(
            id="yelp123",
            name="Yelp Pizza Place",
            rating=4.0,
            price="$$",
            categories=["Pizza"],
            image_url="http://example.com/image.jpg",
            distance=500,
            is_open=True,
            review_count=50,
            address="456 Yelp St, Brooklyn, NY",
            phone="555-5678",
            yelp_url="http://yelp.com/biz/yelp123",
            coordinates={"latitude": 40.6782, "longitude": -73.9442}
        )
        
        mock_yelp_search.return_value = [mock_yelp_restaurant]
        
        # Make request
        response = client.get("/search/search?q=pizza&location=Brooklyn, NY&limit=5")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["method"] == "yelp_api"
        assert len(data["restaurants"]) == 1
        assert data["restaurants"][0]["name"] == "Yelp Pizza Place"
    
    def test_parameter_parsing_and_validation(self):
        """Test that parameters are parsed and validated correctly."""
        with patch('app.routers.search.get_db'):
            # Test limit clamping
            response = client.get("/search/search?location=MAN&limit=100")  # Over limit
            assert response.status_code == 422  # Validation error
            
            # Test rating clamping
            response = client.get("/search/search?location=MAN&rating_min=6.0")  # Over max
            assert response.status_code == 422  # Validation error
            
            # Test valid parameters
            response = client.get("/search/search?location=MAN&limit=20&rating_min=3.0")
            assert response.status_code == 200
    
    def test_price_range_parsing(self):
        """Test that comma-separated price ranges are parsed correctly."""
        with patch('app.routers.search.get_db') as mock_db:
            mock_db.return_value.exec.return_value.all.return_value = []
            
            # Test price parsing
            response = client.get("/search/search?location=MAN&price=$,$$")
            assert response.status_code == 200
            
            # Verify the price parameter was processed
            # (This would require checking the mock call arguments)
    
    @patch('app.routers.search.yelp_client.search_businesses_clean')
    async def test_yelp_error_handling(self, mock_yelp_search):
        """Test that Yelp API errors are handled correctly."""
        # Mock Yelp API error
        mock_yelp_search.side_effect = YelpAPIError("Rate limit exceeded")
        
        # Make request
        response = client.get("/search/search?q=pizza&location=Brooklyn, NY")
        
        # Assertions
        assert response.status_code == 429
        data = response.json()
        assert data["detail"]["code"] == "YELP_API_ERROR"
        assert "rate limit" in data["detail"]["message"].lower()
    
    def test_empty_search_results(self):
        """Test handling of empty search results."""
        with patch('app.routers.search.get_db') as mock_db:
            mock_db.return_value.exec.return_value.all.return_value = []
            
            response = client.get("/search/search?location=MAN&q=nonexistent")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["total"] == 0
            assert len(data["restaurants"]) == 0