import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import jwtDecode from 'jwt-decode';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          // Sprawdzenie ważności tokenu
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          
          if (decodedToken.exp < currentTime) {
            // Token wygasł
            logout();
          } else {
            // Ustawienie tokenu w nagłówkach Axios
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            
            // Pobranie informacji o użytkowniku
            const response = await axios.get('/users/me/');
            setCurrentUser(response.data);
          }
        } catch (error) {
          console.error('Błąd podczas inicjalizacji autoryzacji:', error);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await axios.post('/token', new URLSearchParams({
        username: email,
        password: password
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Ustawienie tokenu w nagłówkach Axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Pobranie informacji o użytkowniku
      const userResponse = await axios.get('/users/me/');
      setCurrentUser(userResponse.data);
      
      return true;
    } catch (error) {
      console.error('Błąd logowania:', error);
      return false;
    }
  };

  const register = async (username, email, password, fullName) => {
    try {
      await axios.post('/users/', {
        username,
        email,
        password,
        full_name: fullName
      });
      
      // Po rejestracji automatycznie logujemy
      return await login(email, password);
    } catch (error) {
      console.error('Błąd rejestracji:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCurrentUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    currentUser,
    isAuthenticated: !!currentUser,
    loading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
