/**
 * Restaurant Card Component
 * Reusable card for displaying restaurant summary
 */

import { Link } from 'react-router-dom';
import type { Restaurant } from '../types';

interface RestaurantCardProps {
  restaurant: Restaurant;
}

const RestaurantCard = ({ restaurant }: RestaurantCardProps) => {
  return (
    <Link
      to={`/restaurant/${restaurant.id}`}
      className="block bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
    >
      {/* Image */}
      <div className="h-48 bg-gray-200 overflow-hidden">
        {restaurant.image_url ? (
          <img
            src={restaurant.image_url}
            alt={restaurant.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No Image Available
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Name and Price */}
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
            {restaurant.name}
          </h3>
          {restaurant.price && (
            <span className="text-gray-600 font-medium ml-2">{restaurant.price}</span>
          )}
        </div>

        {/* Rating and Reviews */}
        <div className="flex items-center mb-2">
          <div className="flex items-center">
            <span className="text-yellow-500 mr-1">★</span>
            <span className="text-gray-700 font-medium">{restaurant.rating.toFixed(1)}</span>
          </div>
          <span className="text-gray-500 text-sm ml-2">
            ({restaurant.review_count} reviews)
          </span>
        </div>

        {/* Categories */}
        <div className="flex flex-wrap gap-1 mb-2">
          {restaurant.categories.slice(0, 3).map((category, index) => (
            <span
              key={index}
              className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full"
            >
              {category}
            </span>
          ))}
        </div>

        {/* Address */}
        {restaurant.address && (
          <p className="text-sm text-gray-600 line-clamp-1 mb-2">
            📍 {restaurant.address}
          </p>
        )}

        {/* Distance */}
        {restaurant.distance !== undefined && (
          <p className="text-sm text-gray-500">
            {(restaurant.distance / 1000).toFixed(1)} km away
          </p>
        )}

        {/* Status Badge */}
        <div className="mt-2">
          <span
            className={`text-xs px-2 py-1 rounded-full ${
              restaurant.is_open
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {restaurant.is_open ? 'Open Now' : 'Closed'}
          </span>
        </div>
      </div>
    </Link>
  );
};

export default RestaurantCard;

