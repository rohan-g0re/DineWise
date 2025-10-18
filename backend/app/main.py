# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import health, auth  # Add auth import

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="DineWise API - Restaurant search and review platform",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)  # Add auth router

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint - API information."""
    return {
        "message": "Welcome to DineWise API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health/",
        "auth": "/auth/"  # Add auth endpoint info
    }



# Add this to your main.py or create a new router
from app.clients.yelp import yelp_client, YelpAPIError
# In your main.py test route:
from app.schemas import RestaurantSummary

@app.get("/test-yelp-clean")
async def test_yelp_clean():
    try:
        # Get raw Yelp data
        clean_restaurants = await yelp_client.search_businesses_clean(
            term="pizza",
            location="New York, NY",
            limit=3
        )
        
        return {
            "status": "success",
            "restaurants": clean_restaurants,
            "total": len(clean_restaurants)
        }
    except YelpAPIError as e:
        return {"status": "error", "message": str(e)}               