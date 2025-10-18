import { useParams } from 'react-router-dom'

function RestaurantDetails() {
  const { id } = useParams()

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">Restaurant Details</h1>
          <p className="text-gray-600">Restaurant ID: {id}</p>
          <p className="text-gray-600">Yelp API integration coming soon!</p>
        </div>
      </div>
    </div>
  )
}

export default RestaurantDetails