// frontend/src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sprawdzenie czy użytkownik jest zalogowany przy ładowaniu aplikacji
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        
        if (token) {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const response = await axios.get('/api/auth/me');
          
          if (response.status === 200) {
            setUser(response.data);
            setIsAuthenticated(true);
          } else {
            // Token wygasł lub jest nieprawidłowy
            logout();
          }
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Funkcja logowania
  const login = async (email, password) => {
    setError(null);
    
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      
      if (response.status === 200 && response.data.token) {
        const { token, user } = response.data;
        
        // Zapisz token w localStorage
        localStorage.setItem('auth_token', token);
        
        // Ustaw token w nagłówkach axios
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // Zaktualizuj stan
        setUser(user);
        setIsAuthenticated(true);
        
        return true;
      } else {
        throw new Error(response.data.message || 'Logowanie nie powiodło się');
      }
    } catch (error) {
      setError(error.response?.data?.message || error.message || 'Błąd podczas logowania');
      return false;
    }
  };

  // Funkcja rejestracji
  const register = async (userData) => {
    setError(null);
    
    try {
      const response = await axios.post('/api/auth/register', userData);
      
      if (response.status === 201) {
        return true;
      } else {
        throw new Error(response.data.message || 'Rejestracja nie powiodła się');
      }
    } catch (error) {
      setError(error.response?.data?.message || error.message || 'Błąd podczas rejestracji');
      return false;
    }
  };

  // Funkcja wylogowania
  const logout = () => {
    // Usuń token z localStorage
    localStorage.removeItem('auth_token');
    
    // Usuń token z nagłówków axios
    delete axios.defaults.headers.common['Authorization'];
    
    // Zresetuj stan
    setUser(null);
    setIsAuthenticated(false);
  };

  // Funkcja resetowania hasła
  const resetPassword = async (email) => {
    setError(null);
    
    try {
      const response = await axios.post('/api/auth/reset-password', { email });
      
      if (response.status === 200) {
        return true;
      } else {
        throw new Error(response.data.message || 'Resetowanie hasła nie powiodło się');
      }
    } catch (error) {
      setError(error.response?.data?.message || error.message || 'Błąd podczas resetowania hasła');
      return false;
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    resetPassword
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
