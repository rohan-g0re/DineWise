import { useState } from 'react'

function Home() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">DineWise Home</h1>
          <p className="text-gray-600 mb-6">Search for restaurants in your area</p>
          <button 
            onClick={() => setCount((count) => count + 1)}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors"
          >
            Test Counter: {count}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Home