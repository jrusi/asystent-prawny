import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Divider,
  CircularProgress,
  Alert,
  Avatar
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';

const Profile = () => {
  const { currentUser, logout } = useAuth();
  
  const [formData, setFormData] = useState({
    fullName: currentUser?.full_name || '',
    email: currentUser?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Walidacja
    if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
      setError('Nowe hasła nie są identyczne');
      return;
    }
    
    if (formData.newPassword && !formData.currentPassword) {
      setError('Aby zmienić hasło, musisz podać aktualne hasło');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // W rzeczywistej aplikacji tutaj byłoby żądanie do endpointu aktualizacji profilu
      // np. PUT /users/me/ z danymi formularza
      
      // Symulacja żądania API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Profil został zaktualizowany pomyślnie');
      
      // Czyszczenie pól hasła
      setFormData(prevState => ({
        ...prevState,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));
    } catch (err) {
      console.error('Błąd aktualizacji profilu:', err);
      setError('Wystąpił błąd podczas aktualizacji profilu. Spróbuj ponownie później.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Profil użytkownika
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Avatar
            sx={{ width: 80, height: 80, bgcolor: 'primary.main', mr: 2 }}
          >
            <PersonIcon sx={{ fontSize: 40 }} />
          </Avatar>
          <Box>
            <Typography variant="h5">
              {currentUser?.full_name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {currentUser?.email}
            </Typography>
          </Box>
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Dane podstawowe
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Imię i nazwisko"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Adres e-mail"
                name="email"
                value={formData.email}
                onChange={handleChange}
                variant="outlined"
                disabled // Zazwyczaj nie pozwalamy na zmianę e-maila, bo służy jako login
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Zmiana hasła
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="password"
                label="Aktualne hasło"
                name="currentPassword"
                value={formData.currentPassword}
                onChange={handleChange}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="password"
                label="Nowe hasło"
                name="newPassword"
                value={formData.newPassword}
                onChange={handleChange}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="password"
                label="Potwierdź nowe hasło"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Zapisz zmiany'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
      
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Działania konta
        </Typography>
        
        <Box sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            color="error"
            onClick={logout}
          >
            Wyloguj się
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Profile;
