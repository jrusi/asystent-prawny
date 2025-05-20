import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Komponenty układu
import MainLayout from './layouts/MainLayout';
import LoginLayout from './layouts/LoginLayout';

// Strony
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CasesList from './pages/CasesList';
import CaseDetails from './pages/CaseDetails';
import DocumentView from './pages/DocumentView';

// Utworzenie tematu
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
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});

// Komponent zabezpieczający ścieżki
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Ładowanie...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
};

// Główny komponent aplikacji
function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Strony publiczne */}
            <Route path="/login" element={<LoginLayout><Login /></LoginLayout>} />
            <Route path="/register" element={<LoginLayout><Register /></LoginLayout>} />
            
            {/* Strony chronione */}
            <Route path="/" element={<ProtectedRoute><MainLayout><Dashboard /></MainLayout></ProtectedRoute>} />
            <Route path="/cases" element={<ProtectedRoute><MainLayout><CasesList /></MainLayout></ProtectedRoute>} />
            <Route path="/cases/:caseId" element={<ProtectedRoute><MainLayout><CaseDetails /></MainLayout></ProtectedRoute>} />
            <Route path="/documents/:documentId" element={<ProtectedRoute><MainLayout><DocumentView /></MainLayout></ProtectedRoute>} />
            
            {/* Przekierowanie dla nieznanych ścieżek */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
