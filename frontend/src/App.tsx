import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './components/Home'
import Login from './components/Login'
import RestaurantDetails from './components/RestaurantDetails'
import Locator from './components/Locator'
import Profile from './components/Profile'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="restaurant/:id" element={<RestaurantDetails />} />
        <Route path="locator" element={<Locator />} />
        <Route 
          path="profile" 
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } 
        />
      </Route>
    </Routes>
  )
}

export default App