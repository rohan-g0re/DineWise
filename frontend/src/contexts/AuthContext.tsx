/**
 * Authentication Context
 * Manages user authentication state and provides auth methods throughout the app
 */

import { createContext, useEffect, useState, ReactNode } from 'react';
import { type User as FirebaseUser, onAuthStateChanged } from 'firebase/auth';
import { auth, isFirebaseConfigured } from '../lib/firebase';
import { useRegisterUser } from '../lib/queries';

interface AuthContextType {
  user: FirebaseUser | null;
  loading: boolean;
  error: string | null;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  error: null,
});

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const registerUserMutation = useRegisterUser();

  useEffect(() => {
    // If Firebase is not configured, set loading to false immediately
    if (!isFirebaseConfigured) {
      setLoading(false);
      setError('Firebase not configured. Please add credentials to .env.local');
      return;
    }

    // Subscribe to auth state changes
    const unsubscribe = onAuthStateChanged(
      auth,
      async (firebaseUser) => {
        setUser(firebaseUser);
        setLoading(false);
        
        // If user just signed up, register them in backend
        if (firebaseUser) {
          try {
            // Check if this is a new user by attempting to register
            // Backend will handle duplicate user gracefully
            await registerUserMutation.mutateAsync({
              email: firebaseUser.email!,
              full_name: firebaseUser.displayName || firebaseUser.email!.split('@')[0],
              firebase_uid: firebaseUser.uid,
            });
          } catch (err) {
            // Ignore errors - user might already exist in backend
            console.log('User registration check completed');
          }
        }
      },
      (err) => {
        console.error('Auth state change error:', err);
        setError(err.message);
        setLoading(false);
      }
    );

    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

