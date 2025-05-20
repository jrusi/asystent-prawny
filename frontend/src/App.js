import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Komponent layouts
import MainLayout from './layouts/MainLayout';

// Import komponentów stron
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CaseList from './pages/CaseList';
import CaseDetail from './pages/CaseDetail';
import NewCase from './pages/NewCase';
import Profile from './pages/Profile';

// Komponent prywatnej trasy
const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Ładowanie...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Temat aplikacji
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      'Arial',
      'sans-serif'
    ].join(','),
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={
              <PrivateRoute>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </PrivateRoute>
            } />
            <Route path="/cases" element={
              <PrivateRoute>
                <MainLayout>
                  <CaseList />
                </MainLayout>
              </PrivateRoute>
            } />
            <Route path="/cases/new" element={
              <PrivateRoute>
                <MainLayout>
                  <NewCase />
                </MainLayout>
              </PrivateRoute>
            } />
            <Route path="/cases/:caseId" element={
              <PrivateRoute>
                <MainLayout>
                  <CaseDetail />
                </MainLayout>
              </PrivateRoute>
            } />
            <Route path="/profile" element={
              <PrivateRoute>
                <MainLayout>
                  <Profile />
                </MainLayout>
              </PrivateRoute>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
