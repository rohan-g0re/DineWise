# DineWise API Contract

## Authentication

### Authorization Header
All protected endpoints require an `Authorization` header with a Firebase ID token:

```
Authorization: Bearer <firebase_id_token>
```

### Example
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Endpoints

### Authentication Endpoints

#### GET /auth/me
**Description:** Get current authenticated user information

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Response (200):**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "firebase_uid": "abc123def456",
  "created_at": "2024-01-01T00:00:00"
}
```

**Response (401):**
```json
{
  "detail": "Invalid authentication token"
}
```

#### GET /auth/test
**Description:** Test authentication system status (public endpoint)

**Headers:** None required

**Response (200):**
```json
{
  "message": "Authentication system is running",
  "status": "ok",
  "endpoints": {
    "protected": "/auth/me (requires Authorization header)",
    "public": "/auth/test (no auth required)"
  }
}
```

### Health Endpoints

#### GET /health/
**Description:** Basic health check endpoint

**Response (200):**
```json
{
  "status": "ok"
}
```

#### GET /health/detailed
**Description:** Detailed health check with system information

**Response (200):**
```json
{
  "status": "ok",
  "service": "DineWise API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Search Endpoints

#### GET /search/search
**Description:** Search for restaurants using cached NYC borough data or live Yelp API

**Query Parameters:**
- `q` (optional): Search query (e.g., 'pizza', 'ramen')
- `location` (optional): Location (MAN/BK/QN/BX/SI or custom)
- `cuisine` (optional): Cuisine type filter
- `price` (optional): Price range (comma-separated: $,$$,$$$,$$$$)
- `rating_min` (optional): Minimum rating (1.0-5.0)
- `limit` (optional): Number of results (1-50, default: 20)
- `offset` (optional): Offset for pagination (default: 0)

**Response (200):**
```json
{
  "status": "success",
  "source": "cache|yelp_api",
  "total": 25,
  "restaurants": [
    {
      "id": "yelp_business_id",
      "name": "Restaurant Name",
      "rating": 4.5,
      "price": "$$",
      "categories": ["Italian", "Pizza"],
      "image_url": "https://...",
      "distance": 500.0,
      "is_open": true,
      "review_count": 150,
      "address": "123 Main St",
      "phone": "+1234567890",
      "yelp_url": "https://www.yelp.com/biz/...",
      "coordinates": {
        "latitude": 40.7580,
        "longitude": -73.9855
      }
    }
  ]
}
```

#### GET /search/nearby
**Description:** Search for restaurants near a specific location

**Query Parameters:**
- `latitude` (required): User latitude coordinate
- `longitude` (required): User longitude coordinate
- `radius` (optional): Search radius in meters (100-40000, default: 5000)
- `limit` (optional): Number of results (1-50, default: 20)

**Response (200):**
```json
{
  "status": "success",
  "source": "yelp_api",
  "total": 15,
  "restaurants": [
    {
      "id": "yelp_business_id",
      "name": "Restaurant Name",
      "rating": 4.2,
      "price": "$$$",
      "categories": ["Japanese", "Sushi"],
      "distance": 250.0,
      "is_open": true,
      "review_count": 89,
      "address": "456 Oak Ave",
      "phone": "+1234567890",
      "coordinates": {
        "latitude": 40.7580,
        "longitude": -73.9855
      }
    }
  ]
}
```

#### GET /search/test
**Description:** Test endpoint to verify search functionality

**Response (200):**
```json
{
  "message": "Search endpoints are working!",
  "available_endpoints": [
    "GET /search - Main search endpoint",
    "GET /search/nearby - Nearby restaurants",
    "GET /search/test - This test endpoint"
  ],
  "nyc_boroughs": ["MAN", "BK", "QN", "BX", "SI"],
  "example_requests": [
    "/search?q=pizza&location=MAN&limit=5",
    "/search?q=ramen&location=Brooklyn, NY&rating_min=4.0"
  ]
}
```

### Restaurant Endpoints

#### GET /restaurants/{yelp_id}
**Description:** Get detailed information about a restaurant

**Path Parameters:**
- `yelp_id` (required): Yelp business ID

**Response (200):**
```json
{
  "status": "success",
  "source": "yelp_api|cache",
  "restaurant": {
    "id": "yelp_business_id",
    "name": "Restaurant Name",
    "rating": 4.5,
    "price": "$$",
    "categories": ["Italian", "Pizza"],
    "image_url": "https://...",
    "photos": ["https://...", "https://..."],
    "is_open": true,
    "review_count": 150,
    "address": "123 Main St",
    "phone": "+1234567890",
    "yelp_url": "https://www.yelp.com/biz/...",
    "coordinates": {
      "latitude": 40.7580,
      "longitude": -73.9855
    },
    "hours": {
      "monday": "11:00-22:00",
      "tuesday": "11:00-22:00"
    },
    "transactions": ["delivery", "pickup"]
  },
  "yelp_reviews": [
    {
      "id": "review_id",
      "rating": 5,
      "text": "Great food!",
      "time_created": "2024-01-01T00:00:00",
      "user": {
        "name": "John D.",
        "image_url": "https://..."
      },
      "url": "https://www.yelp.com/..."
    }
  ]
}
```

#### GET /restaurants/{yelp_id}/reviews
**Description:** Get Yelp reviews for a restaurant

**Path Parameters:**
- `yelp_id` (required): Yelp business ID

**Response (200):**
```json
{
  "status": "success",
  "yelp_id": "yelp_business_id",
  "reviews": [
    {
      "id": "review_id",
      "rating": 5,
      "text": "Amazing experience!",
      "time_created": "2024-01-01T00:00:00",
      "user": {
        "name": "Jane S.",
        "image_url": "https://..."
      }
    }
  ],
  "total": 3
}
```

### Wishlist Endpoints (Authentication Required)

#### POST /wishlist
**Description:** Add a restaurant to user's wishlist

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Request Body:**
```json
{
  "yelp_id": "yelp_business_id"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Restaurant added to wishlist",
  "wishlist_item": {
    "id": 1,
    "yelp_id": "yelp_business_id",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### GET /wishlist
**Description:** Get user's wishlist with restaurant details

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Response (200):**
```json
{
  "status": "success",
  "total": 5,
  "wishlist": [
    {
      "id": 1,
      "yelp_id": "yelp_business_id",
      "created_at": "2024-01-01T00:00:00",
      "restaurant": {
        "id": "yelp_business_id",
        "name": "Restaurant Name",
        "rating": 4.5,
        "price": "$$",
        "categories": ["Italian", "Pizza"],
        "review_count": 150,
        "address": "123 Main St",
        "phone": "+1234567890",
        "coordinates": {
          "latitude": 40.7580,
          "longitude": -73.9855
        }
      }
    }
  ]
}
```

#### DELETE /wishlist/{yelp_id}
**Description:** Remove a restaurant from user's wishlist

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Path Parameters:**
- `yelp_id` (required): Yelp business ID

**Response (200):**
```json
{
  "status": "success",
  "message": "Restaurant removed from wishlist",
  "yelp_id": "yelp_business_id"
}
```

#### GET /wishlist/check/{yelp_id}
**Description:** Check if a restaurant is in user's wishlist

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Path Parameters:**
- `yelp_id` (required): Yelp business ID

**Response (200):**
```json
{
  "yelp_id": "yelp_business_id",
  "in_wishlist": true
}
```

#### POST /wishlist/refresh-details
**Description:** Backfill restaurant details for wishlist items

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Response (200):**
```json
{
  "status": "success",
  "message": "Refreshed 3 restaurant details",
  "updated": 3,
  "failed": 0,
  "total": 5
}
```

### Review Endpoints

#### POST /reviews
**Description:** Create a new review for a restaurant

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Request Body:**
```json
{
  "yelp_id": "yelp_business_id",
  "rating": 5,
  "text": "Great food and service!"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Review created successfully",
  "review": {
    "id": 1,
    "yelp_id": "yelp_business_id",
    "rating": 5,
    "text": "Great food and service!",
    "created_at": "2024-01-01T00:00:00",
    "user": {
      "id": 1,
      "full_name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

#### GET /reviews
**Description:** Get community reviews for restaurants

**Query Parameters:**
- `yelp_id` (optional): Filter reviews by restaurant

**Response (200):**
```json
{
  "status": "success",
  "total": 10,
  "reviews": [
    {
      "id": 1,
      "yelp_id": "yelp_business_id",
      "rating": 5,
      "text": "Great food and service!",
      "created_at": "2024-01-01T00:00:00",
      "user": {
        "id": 1,
        "full_name": "John Doe"
      },
      "restaurant": {
        "name": "Restaurant Name",
        "address": "123 Main St"
      }
    }
  ]
}
```

#### GET /users/me/reviews
**Description:** Get all reviews by the current user

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Response (200):**
```json
{
  "status": "success",
  "total": 3,
  "reviews": [
    {
      "id": 1,
      "yelp_id": "yelp_business_id",
      "rating": 5,
      "text": "Great food and service!",
      "created_at": "2024-01-01T00:00:00",
      "restaurant": {
        "name": "Restaurant Name",
        "address": "123 Main St",
        "rating": 4.5
      }
    }
  ]
}
```

#### PATCH /reviews/{review_id}
**Description:** Update a review

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Path Parameters:**
- `review_id` (required): Review ID

**Request Body:**
```json
{
  "rating": 4,
  "text": "Updated review text"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Review updated successfully",
  "review": {
    "id": 1,
    "yelp_id": "yelp_business_id",
    "rating": 4,
    "text": "Updated review text",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### DELETE /reviews/{review_id}
**Description:** Delete a review

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Path Parameters:**
- `review_id` (required): Review ID

**Response (200):**
```json
{
  "status": "success",
  "message": "Review deleted successfully",
  "review_id": 1
}
```

### User Flags Endpoints (Authentication Required)

#### PUT /flags/{yelp_id}
**Description:** Create or update flags for a restaurant

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Path Parameters:**
- `yelp_id` (required): Yelp business ID

**Request Body:**
```json
{
  "visited": true,
  "promo_opt_in": false
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Flags updated successfully",
  "flags": {
    "id": 1,
    "yelp_id": "yelp_business_id",
    "visited": true,
    "promo_opt_in": false,
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

#### GET /flags
**Description:** Get all flags for the current user

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Response (200):**
```json
{
  "status": "success",
  "total": 3,
  "flags": [
    {
      "id": 1,
      "yelp_id": "yelp_business_id",
      "visited": true,
      "promo_opt_in": false,
      "updated_at": "2024-01-01T00:00:00",
      "restaurant": {
        "name": "Restaurant Name",
        "address": "123 Main St",
        "rating": 4.5,
        "price": "$$"
      }
    }
  ]
}
```

#### GET /flags/{yelp_id}
**Description:** Get flags for a specific restaurant

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Path Parameters:**
- `yelp_id` (required): Yelp business ID

**Response (200):**
```json
{
  "status": "success",
  "flags": {
    "id": 1,
    "yelp_id": "yelp_business_id",
    "visited": true,
    "promo_opt_in": false,
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

#### DELETE /flags/{yelp_id}
**Description:** Delete flags for a restaurant

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Path Parameters:**
- `yelp_id` (required): Yelp business ID

**Response (200):**
```json
{
  "status": "success",
  "message": "Flags deleted successfully",
  "yelp_id": "yelp_business_id"
}
```

### Root Endpoint

#### GET /
**Description:** API information and available endpoints

**Response (200):**
```json
{
  "message": "Welcome to DineWise API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health/",
  "auth": "/auth/"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Invalid authentication token"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Authentication Flow

1. **User logs in** with Firebase (frontend)
2. **Firebase returns** ID token
3. **Frontend sends** token in Authorization header
4. **Backend verifies** token with Firebase
5. **Backend creates/updates** user in database
6. **Backend returns** user information

## Token Format

Firebase ID tokens are JWT (JSON Web Token) format:
- **Header:** Contains algorithm and token type
- **Payload:** Contains user information and claims
- **Signature:** Verifies token authenticity

Example token structure:
```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vZGlud2lzZS1hcGkiLCJhdWQiOiJkaW53aXNlLWFwaSIsImF1dGhfdGltZSI6MTYzNDU2Nzg5MCwidXNlcl9pZCI6InRlc3QtdXNlci0xMjMiLCJzdWIiOiJ0ZXN0LXVzZXItMTIzIiwiaWF0IjoxNjM0NTY3ODkwLCJleHAiOjE2MzQ1NzE0OTAsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJ0ZXN0QGV4YW1wbGUuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.signature_here
```

## Development Notes

- **Base URL:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)
- **Firebase Project ID:** `serene-boulder-458623-n3`
- **CORS Origins:** `http://localhost:5173`, `http://localhost:3000`