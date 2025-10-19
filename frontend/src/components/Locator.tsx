import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Link } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useNearbyRestaurants } from '../lib/queries';
import RestaurantCard from './RestaurantCard';
import { RestaurantGridSkeleton } from './LoadingSkeleton';

// Fix Leaflet default marker icon issue with webpack
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

function Locator() {
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [searchRadius, setSearchRadius] = useState(5000); // meters (5km default)
  const [locationError, setLocationError] = useState<string | null>(null);
  const [mapCenter, setMapCenter] = useState<[number, number]>([40.7580, -73.9855]); // NYC default

  // Get user's location on mount
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserLocation({ lat: latitude, lng: longitude });
          setMapCenter([latitude, longitude]);
          setLocationError(null);
        },
        (error) => {
          console.error('Geolocation error:', error);
          setLocationError('Unable to get your location. Showing default NYC area.');
        }
      );
    } else {
      setLocationError('Geolocation is not supported by your browser.');
    }
  }, []);

  // Search nearby restaurants using dedicated nearby endpoint
  const { data, isLoading } = useNearbyRestaurants(
    userLocation
      ? {
          latitude: userLocation.lat,
          longitude: userLocation.lng,
          radius: searchRadius,
          limit: 20,
        }
      : { latitude: 0, longitude: 0, radius: 0 } // Disabled state
  );

  const restaurants = data?.restaurants || [];
  
  // Debug: Log search parameters when they change
  useEffect(() => {
    if (userLocation) {
      console.log(`🔍 Locator Search: radius=${searchRadius}m (${(searchRadius / 1000).toFixed(1)}km), location=(${userLocation.lat}, ${userLocation.lng})`);
      console.log(`📊 Results: ${restaurants.length} restaurants found`);
    }
  }, [searchRadius, userLocation, restaurants.length]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Restaurant Locator</h1>
        <p className="text-gray-600 mb-4">
          Find restaurants near you using your current location
        </p>

        {/* Location Status */}
        {locationError && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
            {locationError}
          </div>
        )}

        {userLocation && (
          <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 p-3 rounded-lg">
            <span>📍</span>
            <span>
              Location found: {userLocation.lat.toFixed(4)}, {userLocation.lng.toFixed(4)}
            </span>
          </div>
        )}

        {/* Search Radius Control */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Radius: {(searchRadius / 1000).toFixed(1)} km
          </label>
          <input
            type="range"
            min="1000"
            max="50000"
            step="1000"
            value={searchRadius}
            onChange={(e) => setSearchRadius(parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Manual Location Button */}
        {!userLocation && (
          <button
            onClick={() => {
              navigator.geolocation.getCurrentPosition(
                (position) => {
                  const { latitude, longitude } = position.coords;
                  setUserLocation({ lat: latitude, lng: longitude });
                  setMapCenter([latitude, longitude]);
                  setLocationError(null);
                },
                () => {
                  setLocationError('Unable to get your location. Please check your browser permissions.');
                }
              );
            }}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Enable Location
          </button>
        )}
      </div>

      {/* Map Section */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="h-96 md:h-[500px]">
          <MapContainer
            center={mapCenter}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              subdomains="abcd"
              maxZoom={20}
            />
            
            {/* User Location Marker */}
            {userLocation && (
              <Marker position={[userLocation.lat, userLocation.lng]}>
                <Popup>
                  <div className="text-center">
                    <strong>You are here</strong>
                  </div>
                </Popup>
              </Marker>
            )}

            {/* Restaurant Markers */}
            {restaurants.map((restaurant: any) => {
              if (restaurant.coordinates) {
                return (
                  <Marker
                    key={restaurant.id}
                    position={[
                      restaurant.coordinates.latitude,
                      restaurant.coordinates.longitude,
                    ]}
                  >
                    <Popup>
                      <div className="text-sm">
                        <Link
                          to={`/restaurant/${restaurant.id}`}
                          className="font-semibold text-blue-600 hover:underline block mb-1"
                        >
                          {restaurant.name}
                        </Link>
                        <div className="flex items-center mb-1">
                          <span className="text-yellow-500 mr-1">★</span>
                          <span>{restaurant.rating.toFixed(1)}</span>
                        </div>
                        {restaurant.price && (
                          <span className="text-gray-600">{restaurant.price}</span>
                        )}
                        {restaurant.distance && (
                          <p className="text-gray-500 mt-1">
                            {(restaurant.distance / 1000).toFixed(1)} km away
                          </p>
                        )}
                      </div>
                    </Popup>
                  </Marker>
                );
              }
              return null;
            })}
          </MapContainer>
        </div>
      </div>

      {/* Results Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Nearby Restaurants</h2>

        {/* Loading State */}
        {isLoading && <RestaurantGridSkeleton count={6} />}

        {/* Results */}
        {!isLoading && (
          <>
            {restaurants.length > 0 ? (
              <>
                <p className="text-gray-600 mb-4">
                  Found {restaurants.length} restaurants nearby
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {restaurants.map((restaurant: any) => (
                    <RestaurantCard key={restaurant.id} restaurant={restaurant} />
                  ))}
                </div>
              </>
            ) : userLocation ? (
              <div className="text-center py-12 bg-white rounded-lg shadow-md">
                <p className="text-gray-600 text-lg">
                  No restaurants found nearby. Try increasing the search radius.
                </p>
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-lg shadow-md">
                <p className="text-gray-600 text-lg">
                  Enable location to find nearby restaurants
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Locator;
