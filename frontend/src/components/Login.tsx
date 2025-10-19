import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { signIn, signUp, resetPassword } from '../lib/auth';
import { isFirebaseConfigured } from '../lib/firebase';

type AuthMode = 'login' | 'signup' | 'reset';

function Login() {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { error: authError } = await signIn(email, password);
    
    if (authError) {
      setError(authError);
      setLoading(false);
    } else {
      // User state will update via AuthContext, triggering redirect
      navigate('/');
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!fullName.trim()) {
      setError('Please enter your full name');
      setLoading(false);
      return;
    }

    const { error: authError } = await signUp(email, password, fullName);
    
    if (authError) {
      setError(authError);
      setLoading(false);
    } else {
      // User state will update via AuthContext, triggering redirect
      navigate('/');
    }
  };

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    const { error: resetError } = await resetPassword(email);
    
    if (resetError) {
      setError(resetError);
    } else {
      setSuccess('Password reset email sent! Check your inbox.');
    }
    setLoading(false);
  };

  const renderForm = () => {
    switch (mode) {
      case 'signup':
        return (
          <form onSubmit={handleSignup} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="John Doe"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
                minLength={6}
              />
              <p className="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>
        );
      
      case 'reset':
        return (
          <form onSubmit={handleReset} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="you@example.com"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Sending...' : 'Send Reset Email'}
            </button>
          </form>
        );
      
      default: // login
        return (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>
            <button
              type="button"
              onClick={() => setMode('reset')}
              className="text-sm text-blue-600 hover:underline"
            >
              Forgot password?
            </button>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        {/* Firebase Configuration Warning */}
        {!isFirebaseConfigured && (
          <div className="mb-6 p-4 bg-yellow-50 border-l-4 border-yellow-400">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Firebase Not Configured
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>Please set up Firebase to enable authentication:</p>
                  <ol className="list-decimal list-inside mt-2 space-y-1">
                    <li>Copy <code className="bg-yellow-100 px-1 rounded">.env.local.template</code> to <code className="bg-yellow-100 px-1 rounded">.env.local</code></li>
                    <li>Add your Firebase credentials</li>
                    <li>Restart the dev server</li>
                  </ol>
                  <p className="mt-2">
                    <a href="https://console.firebase.google.com/" target="_blank" rel="noopener noreferrer" className="font-medium underline">
                      Get Firebase credentials →
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            {mode === 'signup' ? 'Create Account' : mode === 'reset' ? 'Reset Password' : 'Welcome Back'}
          </h1>
          <p className="text-gray-600">
            {mode === 'signup' 
              ? 'Sign up to start discovering restaurants' 
              : mode === 'reset'
              ? 'Enter your email to receive a reset link'
              : 'Sign in to your DineWise account'}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            {success}
          </div>
        )}

        {/* Form */}
        {renderForm()}

        {/* Mode Toggle */}
        <div className="mt-6 text-center text-sm">
          {mode === 'login' && (
            <p className="text-gray-600">
              Don't have an account?{' '}
              <button
                onClick={() => setMode('signup')}
                className="text-blue-600 hover:underline font-medium"
              >
                Sign up
              </button>
            </p>
          )}
          {(mode === 'signup' || mode === 'reset') && (
            <p className="text-gray-600">
              Already have an account?{' '}
              <button
                onClick={() => {
                  setMode('login');
                  setError(null);
                  setSuccess(null);
                }}
                className="text-blue-600 hover:underline font-medium"
              >
                Sign in
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;