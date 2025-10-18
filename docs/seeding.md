# Restaurant Data Seeding Guide

This document explains how to seed the DineWise database with restaurant data from the Yelp API.

## Overview

The seeding system pre-populates the database with restaurant data for NYC boroughs, enabling fast local queries instead of slow API calls to Yelp.

## What Gets Seeded

### Data Source
- **API**: Yelp Fusion API
- **Locations**: 5 NYC Boroughs (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
- **Data Type**: Restaurant information including ratings, reviews, locations, and contact details

### Database Storage
All seeded data is stored in the `restaurant_cache` table in Supabase PostgreSQL with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key (auto-generated) |
| `yelp_id` | String | Unique Yelp business ID |
| `name` | String | Restaurant name |
| `location_code` | String | Borough code (MAN, BK, QN, BX, SI) |
| `lat` | Float | Latitude coordinate |
| `lng` | Float | Longitude coordinate |
| `price` | String | Price range ($, $$, $$$, $$$$) |
| `rating` | Float | Star rating (1.0-5.0) |
| `review_count` | Integer | Number of reviews |
| `categories` | JSON | Cuisine categories array |
| `phone` | String | Phone number |
| `address` | String | Full address |
| `provider` | String | Data source ("yelp") |
| `last_fetched_at` | Timestamp | When data was last updated |

## How to Run Seeding

### Prerequisites
1. **Environment Setup**: Ensure your `.env` file contains:
   - `YELP_API_KEY`: Your Yelp Fusion API key
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string

2. **Dependencies**: All required packages should be installed:
   ```bash
   pip install -r requirements.txt
   ```

### Command Line Usage

#### Seed All Boroughs
```bash
cd backend
python -m app.seed.boroughs --limit 100
```

#### Seed Specific Borough
```bash
python -m app.seed.boroughs --borough MAN --limit 50
```

#### Available Options
- `--limit`: Number of restaurants per borough (default: 100, max: 50 per API call)
- `--borough`: Specific borough to seed (MAN, BK, QN, BX, SI)

### Example Commands

```bash
# Seed 10 restaurants per borough (50 total)
python -m app.seed.boroughs --limit 10

# Seed only Manhattan with 25 restaurants
python -m app.seed.boroughs --borough MAN --limit 25

# Full production seeding (500 restaurants total)
python -m app.seed.boroughs --limit 100
```

## Borough Codes

| Code | Borough | Yelp Location String |
|------|---------|---------------------|
| MAN | Manhattan | "Manhattan, NY" |
| BK | Brooklyn | "Brooklyn, NY" |
| QN | Queens | "Queens, NY" |
| BX | Bronx | "Bronx, NY" |
| SI | Staten Island | "Staten Island, NY" |

## Seeding Process

### 1. Data Fetching
- Calls Yelp Fusion API for each borough
- Fetches restaurant data with search term "restaurants"
- Transforms raw Yelp data into clean DTOs

### 2. Data Transformation
- Converts Yelp API response to `RestaurantSummary` objects
- Extracts and cleans nested data (categories, addresses, coordinates)
- Validates data types and required fields

### 3. Database Storage
- **Upsert Logic**: Updates existing records or creates new ones
- **Duplicate Prevention**: Uses `yelp_id` as unique identifier
- **Timestamp Tracking**: Updates `last_fetched_at` on each operation

### 4. Error Handling
- **API Errors**: Logs errors and continues with next borough
- **Database Errors**: Rolls back transactions and logs issues
- **Network Issues**: Handles timeouts and connection problems

## Monitoring and Statistics

The seeding process provides real-time feedback:

```
🔍 Fetching 100 restaurants for MAN (Manhattan, NY)...
✅ Fetched 100 restaurants for MAN
➕ Added: Restaurant Name 1
🔄 Updated: Restaurant Name 2
...
✅ Completed seeding MAN

📈 SEEDING COMPLETE!
✅ Boroughs processed: 5
📥 Total fetched: 500
💾 Total upserted: 500
❌ Errors: 0
```

## Performance Considerations

### API Rate Limits
- **Yelp Limit**: 500 requests per day (free tier)
- **Seeding Strategy**: 1-second delay between boroughs
- **Batch Size**: 50 restaurants per API call (Yelp maximum)

### Database Performance
- **Indexes**: `yelp_id` and `location_code` are indexed for fast queries
- **Upsert Efficiency**: Uses database-level upsert operations
- **Connection Pooling**: Reuses database connections

## Troubleshooting

### Common Issues

#### 1. API Key Errors
```
❌ Error fetching restaurants for MAN: Invalid API key
```
**Solution**: Verify `YELP_API_KEY` in your `.env` file

#### 2. Database Connection Issues
```
❌ Database error: connection refused
```
**Solution**: Check `DATABASE_URL` and ensure Supabase is accessible

#### 3. Rate Limit Exceeded
```
❌ Yelp API rate limit exceeded
```
**Solution**: Wait 24 hours or upgrade to paid Yelp API plan

#### 4. Missing Coordinates
```
❌ Unexpected error: 'RestaurantSummary' object has no attribute 'coordinates'
```
**Solution**: Ensure `coordinates` field is included in `RestaurantSummary` schema

### Debug Mode
Enable debug logging by setting `DEBUG=True` in your `.env` file to see detailed SQL queries and API responses.

## Data Maintenance

### Refreshing Data
Run seeding periodically to keep restaurant data current:
```bash
# Refresh all data
python -m app.seed.boroughs --limit 100

# Refresh specific borough
python -m app.seed.boroughs --borough MAN --limit 100
```

### Data Cleanup
To clear all seeded data:
```sql
DELETE FROM restaurant_cache WHERE provider = 'yelp';
```

## Integration with Frontend

The seeded data enables:
- **Fast Search**: Instant results for NYC locations
- **Map Display**: Coordinates for restaurant markers
- **Offline Capability**: App works without Yelp API access
- **Cost Savings**: Reduces API calls and associated costs

## Next Steps

After seeding:
1. **Test Search Endpoints**: Verify data is accessible via API
2. **Frontend Integration**: Connect React app to seeded data
3. **Performance Monitoring**: Track query response times
4. **Data Updates**: Schedule regular re-seeding for fresh data

---

For questions or issues, refer to the main project documentation or check the seeding script logs for detailed error information.
