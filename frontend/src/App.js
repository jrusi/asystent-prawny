import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, CircularProgress } from '@mui/material';

// Komponenty stron
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CaseDetail from './pages/CaseDetail';
import CaseList from './pages/CaseList';
import NewCase from './pages/NewCase';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';
import PasswordReset from './pages/PasswordReset';

// Komponenty layoutu
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Kontekst autoryzacji
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Prywatna ścieżka, która wymaga zalogowania
const PrivateRoute = () => {
  const { isAuthenticated, loading, currentUser } = useAuth();
  
  console.log('PrivateRoute:', { isAuthenticated, loading, hasUser: !!currentUser });
  
  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

// Publiczna ścieżka, która przekierowuje zalogowanych użytkowników
const PublicRoute = () => {
  const { isAuthenticated, loading } = useAuth();
  
  console.log('PublicRoute:', { isAuthenticated, loading });
  
  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return isAuthenticated ? <Navigate to="/dashboard" /> : <Outlet />;
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
            <Route element={<PublicRoute />}>
              <Route element={<AuthLayout />}>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/password-reset" element={<PasswordReset />} />
              </Route>
            </Route>
            
            {/* Ścieżki wymagające zalogowania */}
            <Route element={<PrivateRoute />}>
              <Route element={<MainLayout />}>
                <Route path="/" element={<Navigate to="/dashboard" />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/cases" element={<CaseList />} />
                <Route path="/cases/new" element={<NewCase />} />
                <Route path="/cases/:caseId" element={<CaseDetail />} />
                <Route path="/profile" element={<Profile />} />
              </Route>
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
