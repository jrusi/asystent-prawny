import React, { createContext, useState, useContext, useEffect } from 'react';
import jwtDecode from 'jwt-decode';
import api from '../utils/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  console.log('AuthProvider rendering, token:', token ? 'exists' : 'none');

  const fetchUserData = async (authToken) => {
    console.log('Fetching user data...');
    try {
      const response = await api.get('/users/me');
      console.log('User data received:', response.data);
      setCurrentUser(response.data);
      return true;
    } catch (error) {
      console.error('Error fetching user data:', error);
      return false;
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      console.log('Initializing authentication...');
      if (token) {
        try {
          // Sprawdzenie ważności tokenu
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          
          if (decodedToken.exp < currentTime) {
            console.log('Token expired');
            logout();
          } else {
            console.log('Token valid, fetching user data');
            const success = await fetchUserData(token);
            if (!success) {
              console.log('Failed to fetch user data, logging out');
              logout();
            }
          }
        } catch (error) {
          console.error('Error during auth initialization:', error);
          logout();
        }
      } else {
        console.log('No token found');
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email, password) => {
    console.log('Attempting login...');
    try {
      const response = await api.post('/token', {
        username: email,
        password: password
      });

      const { access_token } = response.data;
      console.log('Login successful, token received');
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      const success = await fetchUserData(access_token);
      if (!success) {
        throw new Error('Failed to fetch user data after login');
      }
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email, password, fullName) => {
    console.log('Attempting registration...');
    try {
      const response = await api.post('/users', {
        email: email,
        password: password,
        full_name: fullName
      });

      console.log('Registration successful:', response.data);
      return await login(email, password);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    console.log('Logging out...');
    localStorage.removeItem('token');
    setToken(null);
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    isAuthenticated: !!currentUser,
    loading,
    login,
    register,
    logout
  };

  console.log('AuthContext state:', { 
    hasCurrentUser: !!currentUser, 
    isLoading: loading 
  });

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
