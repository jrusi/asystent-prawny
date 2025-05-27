import React, { useState, useEffect } from 'react';
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
  Avatar,
  Container
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';

const Profile = () => {
  console.log('Profile component rendering');
  const { currentUser, logout } = useAuth();
  console.log('Current user:', currentUser);
  
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('Profile useEffect - currentUser changed:', currentUser);
    if (currentUser) {
      setFormData(prevState => ({
        ...prevState,
        full_name: currentUser.full_name || '',
        email: currentUser.email || ''
      }));
    }
  }, [currentUser]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
    setError('');
    setSuccess('');
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

    if (formData.newPassword && formData.newPassword.length < 8) {
      setError('Nowe hasło musi mieć co najmniej 8 znaków');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Update user profile
      const updateData = {
        full_name: formData.full_name
      };

      // If password change is requested, add password fields
      if (formData.newPassword) {
        updateData.current_password = formData.currentPassword;
        updateData.new_password = formData.newPassword;
      }

      console.log('Sending update request:', updateData);
      await axios.put('/api/users/me', updateData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      setSuccess('Profil został zaktualizowany pomyślnie');
      
      // Clear password fields
      setFormData(prevState => ({
        ...prevState,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));
    } catch (err) {
      console.error('Błąd aktualizacji profilu:', err);
      setError(
        err.response?.data?.detail || 
        'Wystąpił błąd podczas aktualizacji profilu. Spróbuj ponownie później.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Show loading state while waiting for user data
  if (!currentUser) {
    console.log('No current user, showing loading state');
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '80vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ 
      flexGrow: 1,
      p: 3,
      width: '100%',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      <Container maxWidth="md">
        <Box sx={{ py: 4 }}>
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
                  {currentUser.full_name}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {currentUser.email}
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
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    variant="outlined"
                    required
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Adres e-mail"
                    name="email"
                    value={formData.email}
                    variant="outlined"
                    disabled
                    helperText="Email nie może być zmieniony, ponieważ służy jako login"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    Zmiana hasła
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Pozostaw puste, jeśli nie chcesz zmieniać hasła
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
                    helperText="Minimum 8 znaków"
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
      </Container>
    </Box>
  );
};

export default Profile;
