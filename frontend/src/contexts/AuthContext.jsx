import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axiosConfig';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        
        // Set token in axios headers
        api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        
        // Verify token is still valid by fetching user info
        api.get('/api/auth/me')
          .then(response => {
            // Token is valid, update user data
            const userData = response.data;
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
          })
          .catch(error => {
            // Token is invalid, clear auth data
            console.error('Token verification failed:', error);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setToken(null);
            setUser(null);
            delete api.defaults.headers.common['Authorization'];
          })
          .finally(() => {
            setIsLoading(false);
          });
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        // Clear invalid data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login', {
        email,
        password
      });

      const { token: newToken, user: userData } = response.data;

      // Store in localStorage
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(userData));

      // Update state
      setToken(newToken);
      setUser(userData);

      // Set token in axios headers
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;

      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      // Extract error message from response
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      throw new Error(errorMessage);
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await api.post('/api/auth/signup', {
        name,
        email,
        password
      });

      const { token: newToken, user: userData } = response.data;

      // Store in localStorage
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(userData));

      // Update state
      setToken(newToken);
      setUser(userData);

      // Set token in axios headers
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;

      return { success: true, user: userData };
    } catch (error) {
      console.error('Registration error:', error);
      // Extract error message from response
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
      throw new Error(errorMessage);
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Clear state
    setToken(null);
    setUser(null);

    // Remove token from axios headers
    delete api.defaults.headers.common['Authorization'];
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const isAuthenticated = () => {
    return !!token && !!user;
  };

  const value = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
