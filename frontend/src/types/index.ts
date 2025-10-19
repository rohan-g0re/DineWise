/**
 * Shared TypeScript Types
 * Central location for all type definitions
 */

export interface Restaurant {
  id: string;
  name: string;
  rating: number;
  price?: string;
  categories: string[];
  image_url?: string;
  distance?: number;
  is_open: boolean;
  review_count: number;
  address?: string;
  phone?: string;
  yelp_url?: string;
  coordinates?: { latitude: number; longitude: number };
}

export interface RestaurantDetail extends Restaurant {
  photos: string[];
  hours?: any;
  transactions: string[];
}

export interface YelpReview {
  id: string;
  rating: number;
  text: string;
  time_created: string;
  user: { name: string; image_url?: string };
  url?: string;
}

export interface CommunityReview {
  id: number;
  yelp_id: string;
  rating: number;
  text: string;
  created_at: string;
  user?: { id: number; full_name: string };
  restaurant?: { name: string; address: string };
}

export interface WishlistItem {
  id: number;
  yelp_id: string;
  created_at: string;
  restaurant?: Restaurant;
}

export interface UserFlags {
  id?: number;
  yelp_id: string;
  visited: boolean;
  promo_opt_in: boolean;
  updated_at?: string;
  exists?: boolean;
}


