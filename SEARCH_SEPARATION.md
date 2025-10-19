# Search Functionality Separation

## Overview

The application now has **TWO separate search systems** for different use cases:

1. **Homepage Search** - General restaurant search with text-based filters
2. **Store Locator** - Location-based search with strict radius enforcement

## Why Separate Endpoints?

Previously, I mistakenly tried to merge both functionalities into one endpoint. This was wrong because:

- ❌ Different parameters (text location vs lat/lng + radius)
- ❌ Different behaviors (general search vs strict proximity)
- ❌ Different user expectations (flexible vs precise)
- ❌ Code became confusing and hard to maintain

## Architecture

### 1. Homepage Search (`/search`)

**Purpose:** General restaurant search with text-based location and filters

**Endpoint:** `GET /api/search`

**Parameters:**
- `q` - Search query (e.g., "pizza", "ramen")
- `location` - Text location (e.g., "New York, NY", "MAN", "BK")
- `cuisine` - Cuisine type filter
- `price` - Price range (comma-separated: "$,$$")
- `rating_min` - Minimum rating (1.0-5.0)
- `limit` - Results limit
- `offset` - Pagination offset

**Features:**
- ✅ Supports NYC borough codes (MAN, BK, QN, BX, SI) with cached database search
- ✅ Falls back to Yelp API for other locations
- ✅ Price filtering via Yelp API parameter
- ✅ Rating filtering via server-side post-processing (Yelp doesn't support it)
- ✅ Text-based location matching

**Used by:** `Home.tsx` component

**Query Hook:** `useSearchRestaurants(params)`

**Example:**
```javascript
useSearchRestaurants({
  query: "pizza",
  location: "New York, NY",
  price: ["$", "$$"],
  rating_min: 4.0
})
```

---

### 2. Store Locator (`/search/nearby`)

**Purpose:** Find restaurants near user's GPS location with strict radius filtering

**Endpoint:** `GET /api/search/nearby`

**Parameters:**
- `latitude` - User's latitude (required)
- `longitude` - User's longitude (required)
- `radius` - Search radius in meters (100-40000)
- `limit` - Results limit

**Features:**
- ✅ GPS coordinate-based search
- ✅ **Strict server-side radius filtering** (Yelp doesn't enforce it strictly)
- ✅ Filters out restaurants beyond specified radius
- ✅ Real-time updates when radius slider changes
- ✅ Distance information for each restaurant

**Used by:** `Locator.tsx` component

**Query Hook:** `useNearbyRestaurants(params)`

**Example:**
```javascript
useNearbyRestaurants({
  latitude: 40.7580,
  longitude: -73.9855,
  radius: 1000, // 1km in meters
  limit: 20
})
```

---

## The Radius Problem & Solution

### The Problem

When you selected 1km radius, you were seeing restaurants 5km away. Why?

**According to testing and Yelp API behavior:**
- Yelp API accepts the `radius` parameter but **doesn't strictly enforce it**
- Yelp treats radius as a "suggestion" or "preference"
- Yelp may return businesses beyond the specified radius
- This is by design - Yelp wants to ensure users see results even in sparse areas

### The Solution

**Server-Side Strict Filtering** in `/search/nearby` endpoint:

```python
# Call Yelp API with radius
raw_result = await yelp_client.search_nearby(
    latitude=latitude,
    longitude=longitude,
    radius=radius,  # e.g., 1000m
    categories="restaurants",
    limit=limit
)

# Transform results
results = [transform(business) for business in raw_result["businesses"]]

# CRITICAL: Filter out restaurants beyond specified radius
# Yelp returns distance in meters for each restaurant
results = [r for r in results if r.distance is not None and r.distance <= radius]
```

**How it works:**
1. Yelp API is called with `radius=1000` (1km)
2. Yelp returns ~20 restaurants, some might be 1.5km, 2km, 5km away
3. Backend checks `restaurant.distance` field (provided by Yelp)
4. Backend filters out any restaurant where `distance > 1000m`
5. Frontend receives only restaurants within 1km

**Debug logs:**
```
🔍 Nearby Search: lat=40.7580, lng=-73.9855, radius=1000m
⚠️ Filtered out 8 restaurants beyond 1000m radius
✅ Returning 12 restaurants within 1000m
```

---

## File Structure

### Backend

```
backend/app/routers/search.py
├── search_restaurants()        # Homepage search (line 21)
│   ├── NYC borough search (cached)
│   └── Yelp API search with rating filter
│
├── search_nearby_restaurants() # Store locator (line 201)
│   ├── Yelp API nearby search
│   └── Strict radius filtering
│
└── _search_cached_restaurants() # Helper for NYC boroughs
```

### Frontend

```
frontend/src/lib/queries.ts
├── useSearchRestaurants()      # For homepage
│   └── Calls: GET /api/search
│
└── useNearbyRestaurants()      # For locator
    └── Calls: GET /api/search/nearby
```

```
frontend/src/components/
├── Home.tsx                    # Uses useSearchRestaurants()
└── Locator.tsx                 # Uses useNearbyRestaurants()
```

---

## Testing

### Test Homepage Search
1. Go to homepage
2. Search: "pizza" in "New York, NY"
3. Select price filters, rating filters
4. Should see filtered results based on ALL criteria
5. ✅ No radius filtering here

### Test Store Locator
1. Go to `/locator`
2. Allow location access
3. Set radius to **1 km** using slider
4. Check console logs: `🔍 Locator Search: radius=1000m`
5. **All restaurants should be ≤ 1.0 km away**
6. Change radius to **5 km**
7. Check console: `🔍 Locator Search: radius=5000m`
8. **Should see more restaurants, all ≤ 5.0 km away**

### Verify Strict Filtering
1. Open browser DevTools → Network tab
2. Go to locator, set radius to 1km
3. Find the `/search/nearby?radius=1000` request
4. Check backend logs for:
   ```
   ⚠️ Filtered out X restaurants beyond 1000m radius
   ✅ Returning Y restaurants within 1000m
   ```
5. Verify each restaurant's distance in the response

---

## Console Debugging

### Frontend (Browser Console)
When you adjust the slider, you'll see:
```
🔍 Locator Search: radius=1000m (1.0km), location=(40.7580, -73.9855)
📊 Results: 12 restaurants found
```

### Backend (Terminal/Logs)
When the search is processed:
```
🔍 Nearby Search: lat=40.7580, lng=-73.9855, radius=1000m
⚠️ Filtered out 8 restaurants beyond 1000m radius
✅ Returning 12 restaurants within 1000m
```

---

## API Examples

### Homepage Search
```bash
GET /api/search?q=pizza&location=New York, NY&price=$,$$&rating_min=4.0&limit=20
```

Response:
```json
{
  "status": "success",
  "method": "yelp_api",
  "total": 15,
  "restaurants": [...]
}
```

### Store Locator Search
```bash
GET /api/search/nearby?latitude=40.7580&longitude=-73.9855&radius=1000&limit=20
```

Response:
```json
{
  "status": "success",
  "method": "yelp_nearby_strict",
  "total": 12,
  "radius_meters": 1000,
  "location": {
    "latitude": 40.7580,
    "longitude": -73.9855
  },
  "restaurants": [
    {
      "id": "abc123",
      "name": "Joe's Pizza",
      "distance": 450,  // meters
      "rating": 4.5,
      ...
    }
  ]
}
```

---

## Summary

| Feature | Homepage Search | Store Locator |
|---------|----------------|---------------|
| **Endpoint** | `/search` | `/search/nearby` |
| **Location Type** | Text (NYC, Brooklyn, etc.) | GPS (lat/lng) |
| **Radius** | No radius filtering | Strict radius enforcement |
| **Filters** | Query, price, rating, cuisine | Only radius |
| **Use Case** | Browse restaurants by area | Find nearby restaurants |
| **Component** | `Home.tsx` | `Locator.tsx` |
| **Hook** | `useSearchRestaurants()` | `useNearbyRestaurants()` |

**Key Takeaway:** Two different user needs = Two different endpoints = Clean separation of concerns! 🎯

