/**
 * Loading Skeleton Component
 * Provides visual feedback during data loading
 */

const LoadingSkeleton = () => {
  return (
    <div className="animate-pulse">
      <div className="bg-gray-200 h-48 rounded-t-lg"></div>
      <div className="p-4 space-y-3">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        <div className="h-3 bg-gray-200 rounded w-5/6"></div>
      </div>
    </div>
  );
};

export const RestaurantCardSkeleton = () => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <LoadingSkeleton />
    </div>
  );
};

export const RestaurantGridSkeleton = ({ count = 6 }: { count?: number }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, index) => (
        <RestaurantCardSkeleton key={index} />
      ))}
    </div>
  );
};

export default LoadingSkeleton;


