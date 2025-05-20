// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import axios from 'axios';

// Konfiguracja axios - ustaw bazowy URL dla wszystkich zapytań
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Dodaj interceptor do obsługi błędów autoryzacji
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Usunięcie tokenu, jeśli serwer zwraca błąd autoryzacji
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
