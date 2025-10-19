import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import {
  useRestaurantDetails,
  useRestaurantReviews,
  useCheckWishlistStatus,
  useAddToWishlist,
  useRemoveFromWishlist,
  useCreateReview,
  useDeleteReview,
  useRestaurantFlags,
  useUpdateFlags,
} from '../lib/queries';
import ErrorBanner from './ErrorBanner';

function RestaurantDetails() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewText, setReviewText] = useState('');
  const [showReviewForm, setShowReviewForm] = useState(false);

  // Fetch data
  const { data: restaurantData, isLoading: restaurantLoading, error: restaurantError } = useRestaurantDetails(id);
  const { data: reviewsData, isLoading: reviewsLoading } = useRestaurantReviews(id);
  const { data: wishlistStatus } = useCheckWishlistStatus(id);
  const { data: flagsData } = useRestaurantFlags(id);

  // Mutations
  const addToWishlist = useAddToWishlist();
  const removeFromWishlist = useRemoveFromWishlist();
  const createReview = useCreateReview();
  const deleteReview = useDeleteReview();
  const updateFlags = useUpdateFlags();

  if (restaurantLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (restaurantError || !restaurantData) {
    return (
      <div className="space-y-6">
        <Link to="/" className="text-blue-600 hover:underline flex items-center gap-2">
          ← Back to search
        </Link>
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg">
          <div className="flex items-start gap-3">
            <svg className="h-6 w-6 text-yellow-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">
                Restaurant Details Unavailable
              </h3>
              <p className="text-yellow-700 mb-4">
                This restaurant's details couldn't be loaded. This usually happens when:
              </p>
              <ul className="list-disc list-inside text-yellow-700 space-y-1 mb-4">
                <li>The business has closed or moved</li>
                <li>Yelp has updated their information</li>
                <li>The restaurant ID is no longer valid</li>
              </ul>
              <div className="flex gap-3">
                <Link
                  to="/"
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 font-medium"
                >
                  Try Another Restaurant
                </Link>
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-white text-yellow-800 border border-yellow-300 rounded-lg hover:bg-yellow-50 font-medium"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const restaurant = restaurantData.restaurant;
  const yelpReviews = restaurantData.yelp_reviews || [];
  const communityReviews = reviewsData?.reviews || [];
  const isInWishlist = wishlistStatus?.in_wishlist || false;
  const flags = flagsData?.flags || { visited: false, promo_opt_in: false };

  const handleWishlistToggle = () => {
    if (!user) {
      alert('Please sign in to add restaurants to your wishlist');
      return;
    }
    
    const errorHandler = {
      onError: (error: any) => {
        alert(`Failed to update wishlist: ${error.response?.data?.detail?.message || error.message || 'Unknown error'}`);
      },
    };
    
    if (isInWishlist) {
      removeFromWishlist.mutate(id!, errorHandler);
    } else {
      addToWishlist.mutate(id!, errorHandler);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      alert('Please sign in to leave a review');
      return;
    }

    try {
      await createReview.mutateAsync({
        yelp_id: id!,
        rating: reviewRating,
        text: reviewText,
      });
      setReviewText('');
      setReviewRating(5);
      setShowReviewForm(false);
    } catch (error) {
      alert('Failed to submit review');
    }
  };

  const handleDeleteReview = async (reviewId: number) => {
    if (confirm('Are you sure you want to delete this review?')) {
      await deleteReview.mutateAsync(reviewId);
    }
  };

  const handleFlagToggle = (field: 'visited' | 'promo_opt_in') => {
    if (!user) {
      alert('Please sign in to mark preferences');
      return;
    }

    updateFlags.mutate(
      {
        yelpId: id!,
        [field]: !flags[field],
      },
      {
        onError: (error: any) => {
          alert(`Failed to update: ${error.response?.data?.detail?.message || error.message || 'Unknown error'}`);
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link to="/" className="text-blue-600 hover:underline flex items-center gap-2">
        ← Back to search
      </Link>

      {/* Restaurant Header */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {/* Image Gallery */}
        {restaurant.image_url && (
          <div className="h-64 md:h-96 bg-gray-200">
            <img
              src={restaurant.image_url}
              alt={restaurant.name}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        <div className="p-6">
          {/* Name and Actions */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{restaurant.name}</h1>
              <div className="flex items-center gap-4">
                <div className="flex items-center">
                  <span className="text-yellow-500 text-xl mr-1">★</span>
                  <span className="text-xl font-semibold">{restaurant.rating.toFixed(1)}</span>
                  <span className="text-gray-600 ml-2">({restaurant.review_count} reviews)</span>
                </div>
                {restaurant.price && (
                  <span className="text-gray-700 font-medium">{restaurant.price}</span>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleWishlistToggle}
                disabled={!user}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  isInWishlist
                    ? 'bg-red-500 text-white hover:bg-red-600'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                }`}
              >
                {isInWishlist ? '❤️ Saved' : '🤍 Save'}
              </button>
            </div>
          </div>

          {/* Categories */}
          <div className="flex flex-wrap gap-2 mb-4">
            {restaurant.categories.map((category: string, index: number) => (
              <span
                key={index}
                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
              >
                {category}
              </span>
            ))}
          </div>

          {/* Info Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {restaurant.address && (
              <div>
                <h3 className="font-semibold text-gray-700 mb-1">Address</h3>
                <p className="text-gray-600">📍 {restaurant.address}</p>
              </div>
            )}
            {restaurant.phone && (
              <div>
                <h3 className="font-semibold text-gray-700 mb-1">Phone</h3>
                <p className="text-gray-600">📞 {restaurant.phone}</p>
              </div>
            )}
          </div>

          {/* Status Badge */}
          <span
            className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
              restaurant.is_open
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {restaurant.is_open ? 'Open Now' : 'Closed'}
          </span>

          {/* User Flags (if logged in) */}
          {user && (
            <div className="mt-4 pt-4 border-t">
              <h3 className="font-semibold text-gray-700 mb-2">My Preferences</h3>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={flags.visited}
                    onChange={() => handleFlagToggle('visited')}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">I've visited here</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={flags.promo_opt_in}
                    onChange={() => handleFlagToggle('promo_opt_in')}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">Get promo notifications</span>
                </label>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Yelp Reviews */}
      {yelpReviews.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Yelp Reviews</h2>
          <div className="space-y-4">
            {yelpReviews.map((review: any) => (
              <div key={review.id} className="border-b pb-4 last:border-b-0">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {review.user.image_url && (
                      <img
                        src={review.user.image_url}
                        alt={review.user.name}
                        className="w-12 h-12 rounded-full"
                      />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold">{review.user.name}</span>
                      <span className="text-yellow-500">{'★'.repeat(review.rating)}</span>
                    </div>
                    <p className="text-gray-700 mb-2">{review.text}</p>
                    <span className="text-sm text-gray-500">{review.time_created}</span>
        </div>
      </div>
    </div>
            ))}
          </div>
        </div>
      )}

      {/* Community Reviews */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Community Reviews</h2>
          {user && !showReviewForm && (
            <button
              onClick={() => setShowReviewForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Write a Review
            </button>
          )}
        </div>

        {/* Review Form */}
        {showReviewForm && (
          <form onSubmit={handleReviewSubmit} className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Rating
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setReviewRating(star)}
                    className={`text-3xl ${
                      star <= reviewRating ? 'text-yellow-500' : 'text-gray-300'
                    }`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Review
              </label>
              <textarea
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                rows={4}
                maxLength={1000}
                required
                placeholder="Share your experience..."
              />
              <p className="text-sm text-gray-500 mt-1">
                {reviewText.length}/1000 characters
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={createReview.isPending}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                {createReview.isPending ? 'Submitting...' : 'Submit Review'}
              </button>
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* Reviews List */}
        {reviewsLoading ? (
          <p className="text-gray-600">Loading community reviews...</p>
        ) : communityReviews.length > 0 ? (
          <div className="space-y-4">
            {communityReviews.map((review: any) => (
              <div key={review.id} className="border-b pb-4 last:border-b-0">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="font-semibold">{review.user?.full_name || 'Anonymous'}</span>
                    <span className="text-yellow-500 ml-2">{'★'.repeat(review.rating)}</span>
                  </div>
                  {user && review.user?.id === user.uid && (
                    <button
                      onClick={() => handleDeleteReview(review.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  )}
                </div>
                <p className="text-gray-700 mb-2">{review.text}</p>
                <span className="text-sm text-gray-500">
                  {new Date(review.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600 text-center py-8">
            No community reviews yet. Be the first to review!
          </p>
        )}
      </div>
    </div>
  );
}

export default RestaurantDetails;
