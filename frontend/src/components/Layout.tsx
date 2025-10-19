import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { logOut } from '../lib/auth';

function Layout() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logOut();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header Navigation */}
      <nav className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo Section */}
            <div className="flex items-center">
              <Link 
                to="/" 
                className="text-2xl font-bold text-gray-900 hover:text-blue-600 transition-colors duration-200"
              >
                🍽️ DineWise
              </Link>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <Link 
                to="/" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              >
                Home
              </Link>
              <Link 
                to="/locator" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              >
                Locator
              </Link>
              
              {!loading && (
                <>
                  {user ? (
                    <>
                      <Link 
                        to="/profile" 
                        className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                      >
                        My Profile
                      </Link>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-600">
                          {user.displayName || user.email}
                        </span>
                        <button
                          onClick={handleLogout}
                          className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
                        >
                          Sign Out
                        </button>
                      </div>
                    </>
                  ) : (
                    <Link 
                      to="/login" 
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 shadow-sm"
                    >
                      Sign In
                    </Link>
                  )}
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button 
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-700 hover:text-blue-600 p-2"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-4">
              <div className="flex flex-col space-y-2">
                <Link 
                  to="/" 
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Home
                </Link>
                <Link 
                  to="/locator" 
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Locator
                </Link>
                {!loading && (
                  <>
                    {user ? (
                      <>
                        <Link 
                          to="/profile" 
                          onClick={() => setMobileMenuOpen(false)}
                          className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                        >
                          My Profile
                        </Link>
                        <button
                          onClick={() => {
                            handleLogout();
                            setMobileMenuOpen(false);
                          }}
                          className="text-left text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                        >
                          Sign Out
                        </button>
                      </>
                    ) : (
                      <Link 
                        to="/login" 
                        onClick={() => setMobileMenuOpen(false)}
                        className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                      >
                        Sign In
                      </Link>
                    )}
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content Area with Responsive Container */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600 text-sm">
            <p>&copy; 2024 DineWise. Built with React + FastAPI + Firebase.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Layout;