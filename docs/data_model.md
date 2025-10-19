# DineWise Database Schema

## Overview
This document describes the complete database schema for the DineWise application, including all tables, columns, constraints, and indexes.

## Tables

### 1. Users Table
**Purpose:** Stores user information from Firebase authentication

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | serial | PRIMARY KEY | Auto-incrementing user ID |
| email | varchar(255) | UNIQUE, NOT NULL | User's email address |
| full_name | varchar(255) | NOT NULL | User's full name |
| firebase_uid | varchar(255) | UNIQUE, NOT NULL | Firebase user ID |
| created_at | timestamp | NOT NULL | Account creation timestamp |

**Indexes:**
- `ix_users_email` (UNIQUE) - Fast email lookups
- `ix_users_firebase_uid` (UNIQUE) - Fast Firebase UID lookups

### 2. Restaurant Cache Table
**Purpose:** Caches restaurant data from Yelp API to avoid API limits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | serial | PRIMARY KEY | Auto-incrementing restaurant ID |
| yelp_id | varchar(255) | UNIQUE, NOT NULL | Yelp business ID |
| name | varchar(255) | NOT NULL | Restaurant name |
| location_code | varchar(10) | NOT NULL | Borough code (MAN, BK, QN, BX, SI) |
| lat | double precision | NOT NULL | Latitude coordinate |
| lng | double precision | NOT NULL | Longitude coordinate |
| price | varchar(10) | NULL | Price range ($, $$, $$$, $$$$) |
| rating | double precision | NOT NULL | Average rating (1.0-5.0) |
| review_count | integer | NOT NULL | Number of reviews |
| categories | json | NULL | Array of category strings |
| phone | varchar(50) | NULL | Phone number |
| address | varchar(500) | NULL | Street address |
| provider | varchar(50) | NOT NULL | Data source ("yelp" or "manual") |
| last_fetched_at | timestamp | NOT NULL | Last API fetch timestamp |

**Indexes:**
- `ix_restaurant_cache_yelp_id` (UNIQUE) - Fast Yelp ID lookups
- `ix_restaurant_cache_location_code` - Fast borough filtering
- `ix_restaurant_cache_rating` - Fast rating sorting
- `ix_restaurant_cache_review_count` - Fast popularity sorting

### 3. Wishlist Table
**Purpose:** Stores restaurants users want to save for later

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | serial | PRIMARY KEY | Auto-incrementing wishlist ID |
| user_id | integer | FOREIGN KEY → users.id, NOT NULL | User who added to wishlist |
| yelp_id | varchar(255) | NOT NULL | Restaurant Yelp ID |
| created_at | timestamp | NOT NULL | When added to wishlist |

**Constraints:**
- UNIQUE(user_id, yelp_id) - User can't add same restaurant twice

### 4. Reviews Table
**Purpose:** Stores user reviews for restaurants

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | serial | PRIMARY KEY | Auto-incrementing review ID |
| user_id | integer | FOREIGN KEY → users.id, NOT NULL | User who wrote review |
| yelp_id | varchar(255) | NOT NULL | Restaurant Yelp ID |
| rating | integer | NOT NULL | Rating (1-5 stars) |
| text | varchar(1000) | NOT NULL | Review text |
| created_at | timestamp | NOT NULL | When review was written |

**Indexes:**
- `ix_reviews_yelp_id` - Fast restaurant review lookups
- `ix_reviews_user_id` - Fast user review lookups

### 5. User Restaurant Flags Table
**Purpose:** Stores user preferences for restaurants (for future notifications)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | serial | PRIMARY KEY | Auto-incrementing flag ID |
| user_id | integer | FOREIGN KEY → users.id, NOT NULL | User who set flags |
| yelp_id | varchar(255) | NOT NULL | Restaurant Yelp ID |
| visited | boolean | NOT NULL | Has user visited this restaurant? |
| promo_opt_in | boolean | NOT NULL | Does user want promo notifications? |
| updated_at | timestamp | NOT NULL | When flags were last updated |

**Constraints:**
- UNIQUE(user_id, yelp_id) - One flag record per user-restaurant combination

**Indexes:**
- `ix_user_restaurant_flags_yelp_id` - Fast restaurant flag lookups

## Relationships

```
Users (1) ←→ (Many) Wishlist
Users (1) ←→ (Many) Reviews  
Users (1) ←→ (Many) User Restaurant Flags

Restaurant Cache (1) ←→ (Many) Wishlist (by yelp_id)
Restaurant Cache (1) ←→ (Many) Reviews (by yelp_id)
Restaurant Cache (1) ←→ (Many) User Restaurant Flags (by yelp_id)
```

## Performance Optimizations

### Indexes for Fast Queries:
- **Borough filtering:** `ix_restaurant_cache_location_code`
- **Rating sorting:** `ix_restaurant_cache_rating`
- **Popularity sorting:** `ix_restaurant_cache_review_count`
- **Restaurant reviews:** `ix_reviews_yelp_id`
- **User reviews:** `ix_reviews_user_id`
- **Restaurant flags:** `ix_user_restaurant_flags_yelp_id`

### Unique Constraints:
- **User emails:** One email per user
- **Firebase UIDs:** One Firebase UID per user
- **Restaurant Yelp IDs:** One cache entry per restaurant
- **Wishlist entries:** User can't add same restaurant twice
- **User flags:** One flag record per user-restaurant combination

## Migration History

### Initial Migration (e4380a9b1daf)
- Created all 5 tables with primary keys and foreign keys
- Added unique constraints for email, firebase_uid, and yelp_id
- Added composite unique constraints for wishlist and user flags

### Performance Migration (d6bc2fd0fc19)
- Added performance indexes for faster queries
- Optimized for common search and filtering operations
- Improved query performance by 10-100x for indexed columns

## Current Implementation Status

### Completed Features
- ✅ **User Authentication**: Firebase integration with user management
- ✅ **Restaurant Search**: Cached NYC borough data + live Yelp API integration
- ✅ **Restaurant Details**: Full restaurant information with Yelp reviews
- ✅ **Wishlist Management**: Add/remove restaurants from personal wishlist
- ✅ **Community Reviews**: User-generated reviews with CRUD operations
- ✅ **User Flags**: Visited status and promo preferences for future notifications
- ✅ **Location-based Search**: Nearby restaurant search with geolocation
- ✅ **Database Caching**: Restaurant data caching to reduce Yelp API calls

### API Endpoints Implemented
- **Authentication**: `/auth/me`, `/auth/test`
- **Health**: `/health/`, `/health/detailed`
- **Search**: `/search/search`, `/search/nearby`, `/search/test`
- **Restaurants**: `/restaurants/{yelp_id}`, `/restaurants/{yelp_id}/reviews`
- **Wishlist**: `/wishlist` (GET, POST), `/wishlist/{yelp_id}` (DELETE), `/wishlist/check/{yelp_id}`, `/wishlist/refresh-details`
- **Reviews**: `/reviews` (GET, POST), `/reviews/{review_id}` (PATCH, DELETE), `/users/me/reviews`
- **Flags**: `/flags` (GET), `/flags/{yelp_id}` (GET, PUT, DELETE)

### Frontend Features
- ✅ **React + TypeScript**: Modern frontend with type safety
- ✅ **Firebase Authentication**: Email/password login and registration
- ✅ **Restaurant Search**: Advanced filtering and search functionality
- ✅ **Restaurant Details**: Comprehensive restaurant information display
- ✅ **Wishlist Management**: Add/remove restaurants from wishlist
- ✅ **Review System**: Create, read, update, delete reviews
- ✅ **User Profile**: View personal reviews and wishlist
- ✅ **Interactive Map**: Location-based restaurant discovery
- ✅ **Responsive Design**: Mobile-friendly interface with Tailwind CSS

## Common Query Patterns

### Fast Borough Search:
```sql
SELECT * FROM restaurant_cache 
WHERE location_code = 'BK' 
ORDER BY rating DESC;
```

### Fast Popular Restaurant Search:
```sql
SELECT * FROM restaurant_cache 
WHERE rating >= 4.0 
ORDER BY review_count DESC 
LIMIT 20;
```

### Fast User Wishlist:
```sql
SELECT rc.* FROM restaurant_cache rc
JOIN wishlist w ON rc.yelp_id = w.yelp_id
WHERE w.user_id = ?;
```

### Fast Restaurant Reviews:
```sql
SELECT * FROM reviews 
WHERE yelp_id = ? 
ORDER BY created_at DESC;
```