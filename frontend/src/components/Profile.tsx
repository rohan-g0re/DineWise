import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useWishlist, useMyReviews, useRemoveFromWishlist, useDeleteReview } from '../lib/queries';
import api from '../lib/api';
import ErrorBanner from './ErrorBanner';

type Tab = 'wishlist' | 'reviews';

function Profile() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('wishlist');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const { data: wishlistData, isLoading: wishlistLoading, error: wishlistError, refetch: refetchWishlist } = useWishlist();
  const { data: reviewsData, isLoading: reviewsLoading, error: reviewsError } = useMyReviews();
  
  const removeFromWishlist = useRemoveFromWishlist();
  const deleteReview = useDeleteReview();

  const wishlist = wishlistData?.wishlist || [];
  const reviews = reviewsData?.reviews || [];
  
  // Count how many wishlist items are missing details
  const missingDetailsCount = wishlist.filter((item: any) => !item.restaurant).length;

  const handleRemoveFromWishlist = async (yelpId: string, restaurantName: string) => {
    if (confirm(`Remove ${restaurantName} from your wishlist?`)) {
      await removeFromWishlist.mutateAsync(yelpId);
    }
  };

  const handleDeleteReview = async (reviewId: number, restaurantName: string) => {
    if (confirm(`Delete your review for ${restaurantName}?`)) {
      await deleteReview.mutateAsync(reviewId);
    }
  };
  
  const handleRefreshDetails = async () => {
    setIsRefreshing(true);
    try {
      const response = await api.post('/wishlist/refresh-details');
      console.log('Refresh result:', response.data);
      alert(`Successfully refreshed ${response.data.updated} restaurant details!`);
      // Refetch wishlist to show updated data
      await refetchWishlist();
    } catch (error: any) {
      console.error('Failed to refresh details:', error);
      alert(`Failed to refresh details: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
            {user?.displayName?.[0] || user?.email?.[0].toUpperCase()}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {user?.displayName || 'User'}
            </h1>
            <p className="text-gray-600">{user?.email}</p>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-3xl font-bold text-blue-600">{wishlist.length}</div>
            <div className="text-sm text-gray-600 mt-1">Saved Restaurants</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-3xl font-bold text-green-600">{reviews.length}</div>
            <div className="text-sm text-gray-600 mt-1">Reviews Written</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <div className="flex">
            <button
              onClick={() => setActiveTab('wishlist')}
              className={`flex-1 px-6 py-4 text-center font-medium transition ${
                activeTab === 'wishlist'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              My Wishlist ({wishlist.length})
            </button>
            <button
              onClick={() => setActiveTab('reviews')}
              className={`flex-1 px-6 py-4 text-center font-medium transition ${
                activeTab === 'reviews'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              My Reviews ({reviews.length})
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'wishlist' && (
            <div>
              {wishlistError && (
                <ErrorBanner message="Failed to load wishlist. Please try again." />
              )}
              
              {/* Refresh Details Button - show if there are missing details */}
              {missingDetailsCount > 0 && !wishlistLoading && (
                <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-yellow-800">
                        {missingDetailsCount} restaurant{missingDetailsCount > 1 ? 's' : ''} missing details
                      </p>
                      <p className="text-xs text-yellow-700 mt-1">
                        Click refresh to fetch missing restaurant information from Yelp
                      </p>
                    </div>
                    <button
                      onClick={handleRefreshDetails}
                      disabled={isRefreshing}
                      className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                    >
                      {isRefreshing ? 'Refreshing...' : '🔄 Refresh Details'}
                    </button>
                  </div>
                </div>
              )}

              {wishlistLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
              ) : wishlist.length > 0 ? (
                <div className="space-y-4">
                  {wishlist.map((item: any) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition"
                    >
                      {/* Restaurant Info */}
                      <div className="flex-1">
                        {item.restaurant ? (
                          <>
                            <Link
                              to={`/restaurant/${item.yelp_id}`}
                              className="text-lg font-semibold text-gray-900 hover:text-blue-600"
                            >
                              {item.restaurant.name}
                            </Link>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-yellow-500">★</span>
                              <span className="text-gray-700">
                                {item.restaurant.rating.toFixed(1)}
                              </span>
                              {item.restaurant.price && (
                                <span className="text-gray-600 ml-2">
                                  {item.restaurant.price}
                                </span>
                              )}
                            </div>
                            {item.restaurant.address && (
                              <p className="text-sm text-gray-600 mt-1">
                                📍 {item.restaurant.address}
                              </p>
                            )}
                          </>
                        ) : (
                          <div>
                            <p className="text-lg font-semibold text-gray-900">
                              Restaurant (ID: {item.yelp_id})
                            </p>
                            <p className="text-sm text-gray-500">Details not available</p>
                          </div>
                        )}
                        <p className="text-xs text-gray-500 mt-2">
                          Added {new Date(item.created_at).toLocaleDateString()}
                        </p>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <Link
                          to={`/restaurant/${item.yelp_id}`}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                        >
                          View
                        </Link>
                        <button
                          onClick={() =>
                            handleRemoveFromWishlist(
                              item.yelp_id,
                              item.restaurant?.name || 'this restaurant'
                            )
                          }
                          disabled={removeFromWishlist.isPending}
                          className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm font-medium disabled:opacity-50"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🍽️</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Your wishlist is empty
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Start saving restaurants you want to try!
                  </p>
                  <Link
                    to="/"
                    className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                  >
                    Explore Restaurants
                  </Link>
                </div>
              )}
            </div>
          )}

          {activeTab === 'reviews' && (
            <div>
              {reviewsError && (
                <ErrorBanner message="Failed to load reviews. Please try again." />
              )}

              {reviewsLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
              ) : reviews.length > 0 ? (
                <div className="space-y-6">
                  {reviews.map((review: any) => (
                    <div
                      key={review.id}
                      className="p-4 border border-gray-200 rounded-lg"
                    >
                      {/* Review Header */}
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          {review.restaurant ? (
                            <Link
                              to={`/restaurant/${review.yelp_id}`}
                              className="text-lg font-semibold text-gray-900 hover:text-blue-600"
                            >
                              {review.restaurant.name}
                            </Link>
                          ) : (
                            <p className="text-lg font-semibold text-gray-900">
                              Restaurant (ID: {review.yelp_id})
                            </p>
                          )}
                          <div className="flex items-center mt-1">
                            <span className="text-yellow-500 text-xl">
                              {'★'.repeat(review.rating)}
                              {'☆'.repeat(5 - review.rating)}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() =>
                            handleDeleteReview(
                              review.id,
                              review.restaurant?.name || 'this restaurant'
                            )
                          }
                          disabled={deleteReview.isPending}
                          className="text-red-600 hover:text-red-800 text-sm font-medium disabled:opacity-50"
                        >
                          Delete
                        </button>
                      </div>

                      {/* Review Text */}
                      <p className="text-gray-700 mb-3">{review.text}</p>

                      {/* Review Meta */}
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>
                          Posted {new Date(review.created_at).toLocaleDateString()}
                        </span>
                        {review.restaurant && (
                          <Link
                            to={`/restaurant/${review.yelp_id}`}
                            className="text-blue-600 hover:underline"
                          >
                            View Restaurant
                          </Link>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">✍️</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    No reviews yet
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Share your dining experiences with the community!
                  </p>
                  <Link
                    to="/"
                    className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                  >
                    Find Restaurants
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Profile;
