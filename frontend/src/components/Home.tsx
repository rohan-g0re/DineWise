import { useState } from 'react';
import { useSearchRestaurants } from '../lib/queries';
import RestaurantCard from './RestaurantCard';
import { RestaurantGridSkeleton } from './LoadingSkeleton';
import ErrorBanner from './ErrorBanner';

function Home() {
  const [searchParams, setSearchParams] = useState({
    query: '',
    location: 'New York, NY',
    cuisine: '',
    price: [] as string[],
    rating_min: undefined as number | undefined,
  });
  
  const [activeSearch, setActiveSearch] = useState<typeof searchParams | null>(null);

  const { data, isLoading, error, refetch } = useSearchRestaurants(
    activeSearch || { query: '', location: '' }
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveSearch(searchParams);
  };

  const handlePriceToggle = (price: string) => {
    setSearchParams(prev => ({
      ...prev,
      price: prev.price.includes(price)
        ? prev.price.filter(p => p !== price)
        : [...prev.price, price]
    }));
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center bg-white rounded-lg shadow-md p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Discover Your Next Favorite Restaurant
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Search thousands of restaurants in New York City
        </p>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="max-w-4xl mx-auto space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Query Input */}
            <input
              type="text"
              placeholder="What are you craving? (e.g., pizza, sushi)"
              value={searchParams.query}
              onChange={(e) => setSearchParams({ ...searchParams, query: e.target.value })}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />

            {/* Location Input */}
            <input
              type="text"
              placeholder="Location (e.g., Manhattan, Brooklyn)"
              value={searchParams.location}
              onChange={(e) => setSearchParams({ ...searchParams, location: e.target.value })}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filters Row */}
          <div className="flex flex-wrap gap-4 items-center justify-center">
            {/* Cuisine Input */}
            <input
              type="text"
              placeholder="Cuisine type (optional)"
              value={searchParams.cuisine}
              onChange={(e) => setSearchParams({ ...searchParams, cuisine: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />

            {/* Price Filter */}
            <div className="flex gap-2">
              {['$', '$$', '$$$', '$$$$'].map((price) => (
                <button
                  key={price}
                  type="button"
                  onClick={() => handlePriceToggle(price)}
                  className={`px-3 py-2 rounded-lg font-medium transition ${
                    searchParams.price.includes(price)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {price}
                </button>
              ))}
            </div>

            {/* Rating Filter */}
            <select
              value={searchParams.rating_min || ''}
              onChange={(e) => setSearchParams({ 
                ...searchParams, 
                rating_min: e.target.value ? parseFloat(e.target.value) : undefined 
              })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Any Rating</option>
              <option value="4.5">4.5+ Stars</option>
              <option value="4.0">4.0+ Stars</option>
              <option value="3.5">3.5+ Stars</option>
              <option value="3.0">3.0+ Stars</option>
            </select>
          </div>

          {/* Search Button */}
          <button
            type="submit"
            className="w-full md:w-auto px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition shadow-md"
          >
            Search Restaurants
          </button>
        </form>
      </div>

      {/* Results Section */}
      {activeSearch && (
        <div>
          {/* Error State */}
          {error && (
            <ErrorBanner
              message="Failed to load restaurants. Please try again."
              onRetry={() => refetch()}
            />
          )}

          {/* Loading State */}
          {isLoading && <RestaurantGridSkeleton count={6} />}

          {/* Results */}
          {!isLoading && data && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Search Results
                </h2>
                <p className="text-gray-600">
                  Found {data.restaurants?.length || 0} restaurants
                </p>
              </div>

              {data.restaurants && data.restaurants.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {data.restaurants.map((restaurant: any) => (
                    <RestaurantCard key={restaurant.id} restaurant={restaurant} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-white rounded-lg shadow-md">
                  <p className="text-gray-600 text-lg">
                    No restaurants found. Try adjusting your search criteria.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Welcome Message (when no search has been performed) */}
      {!activeSearch && (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <div className="text-6xl mb-4">🍽️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Ready to explore?
          </h2>
          <p className="text-gray-600">
            Enter your search criteria above to discover amazing restaurants
          </p>
        </div>
      )}
    </div>
  );
}

export default Home;