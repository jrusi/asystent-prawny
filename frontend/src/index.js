// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Komponenty stron
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CaseView from './pages/CaseView';
import CaseList from './pages/CaseList';
import DocumentView from './pages/DocumentView';
import DocumentList from './pages/DocumentList';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';
import PasswordReset from './pages/PasswordReset';

// Komponenty layoutu
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Kontekst autoryzacji
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Prywatna ścieżka, która wymaga zalogowania
const PrivateRoute = ({ element }) => {
  const { isAuthenticated } = useAuth();
  
  return isAuthenticated ? element : <Navigate to="/login" />;
};

// Motyw aplikacji
const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Ścieżki autoryzacji */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/password-reset" element={<PasswordReset />} />
            </Route>
            
            {/* Ścieżki wymagające zalogowania */}
            <Route element={<MainLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" />} />
              <Route path="/dashboard" element={<PrivateRoute element={<Dashboard />} />} />
              <Route path="/cases" element={<PrivateRoute element={<CaseList />} />} />
              <Route path="/cases/:caseId" element={<PrivateRoute element={<CaseView />} />} />
              <Route path="/documents" element={<PrivateRoute element={<DocumentList />} />} />
              <Route path="/documents/:documentId" element={<PrivateRoute element={<DocumentView />} />} />
              <Route path="/profile" element={<PrivateRoute element={<Profile />} />} />
            </Route>
            
            {/* Strona 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
