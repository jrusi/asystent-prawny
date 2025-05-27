// frontend/src/pages/Register.js
import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  Button,
  TextField,
  Typography,
  Link,
  Alert
} from '@mui/material';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    confirmPassword: ''
  });
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setFormError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Walidacja
    if (!formData.email || !formData.full_name || !formData.password || !formData.confirmPassword) {
      setFormError('Proszę wypełnić wszystkie pola');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setFormError('Hasła nie są identyczne');
      return;
    }
    
    if (formData.password.length < 8) {
      setFormError('Hasło musi mieć co najmniej 8 znaków');
      return;
    }

    // Walidacja email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setFormError('Proszę podać prawidłowy adres email');
      return;
    }
    
    setFormError('');
    setIsSubmitting(true);

    try {
      await register(
        formData.email,
        formData.password,
        formData.full_name
      );
      // After successful registration, navigate to login
      navigate('/login', { 
        state: { 
          message: 'Rejestracja zakończona sukcesem. Możesz się teraz zalogować.' 
        } 
      });
    } catch (error) {
      console.error('Registration error:', error);
      setFormError(
        error.response?.data?.detail || 
        'Wystąpił błąd podczas rejestracji. Sprawdź czy podany email nie jest już zajęty.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
      <Typography component="h1" variant="h5" align="center" gutterBottom>
        Rejestracja
      </Typography>
      
      {formError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {formError}
        </Alert>
      )}
      
      <TextField
        margin="normal"
        required
        fullWidth
        id="email"
        label="Adres e-mail"
        name="email"
        autoComplete="email"
        autoFocus
        value={formData.email}
        onChange={handleChange}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        id="full_name"
        label="Imię i nazwisko"
        name="full_name"
        autoComplete="name"
        value={formData.full_name}
        onChange={handleChange}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        name="password"
        label="Hasło"
        type="password"
        id="password"
        autoComplete="new-password"
        value={formData.password}
        onChange={handleChange}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        name="confirmPassword"
        label="Powtórz hasło"
        type="password"
        id="confirmPassword"
        value={formData.confirmPassword}
        onChange={handleChange}
      />
      
      <Button
        type="submit"
        fullWidth
        variant="contained"
        disabled={isSubmitting}
        sx={{ mt: 3, mb: 2 }}
      >
        {isSubmitting ? 'Rejestracja...' : 'Zarejestruj się'}
      </Button>
      
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <Link component={RouterLink} to="/login" variant="body2">
          Masz już konto? Zaloguj się
        </Link>
      </Box>
    </Box>
  );
};

export default Register;