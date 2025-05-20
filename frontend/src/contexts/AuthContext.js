import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Adres API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Utworzenie kontekstu
const AuthContext = createContext();

// Hook do używania kontekstu
export function useAuth() {
  return useContext(AuthContext);
}

// Provider kontekstu
export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Funkcja do logowania
  const login = async (email, password) => {
    try {
      // Przygotowanie danych do formularza
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      // Wysłanie żądania
      const response = await axios.post(`${API_URL}/token`, formData);
      
      // Zapisanie tokenu w localStorage
      localStorage.setItem('token', response.data.access_token);
      
      // Pobranie danych użytkownika
      await getUserProfile();
      
      return true;
    } catch (error) {
      console.error('Błąd logowania:', error);
      setError(error.response?.data?.detail || 'Nieprawidłowy email lub hasło');
      return false;
    }
  };

  // Funkcja do rejestracji
  const register = async (username, email, password) => {
    try {
      await axios.post(`${API_URL}/users/`, {
        username,
        email,
        password
      });
      
      return true;
    } catch (error) {
      console.error('Błąd rejestracji:', error);
      setError(error.response?.data?.detail || 'Nie udało się zarejestrować');
      return false;
    }
  };

  // Funkcja do wylogowywania
  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  // Funkcja do pobierania profilu użytkownika
  const getUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setIsAuthenticated(false);
        setCurrentUser(null);
        setLoading(false);
        return;
      }
      
      const response = await axios.get(`${API_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setCurrentUser(response.data);
      setIsAuthenticated(true);
      setError(null);
    } catch (error) {
      console.error('Błąd pobierania profilu:', error);
      setCurrentUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  // Konfiguracja interceptora dla żądań
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
    
    return () => {
      axios.interceptors.request.eject(interceptor);
    };
  }, []);

  // Pobranie danych użytkownika przy pierwszym renderowaniu
  useEffect(() => {
    getUserProfile();
  }, []);

  // Wartości kontekstu
  const value = {
    currentUser,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    getUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
