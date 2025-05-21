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
    username: '', // Dodane pole username
    email: '',
    full_name: '',
    password: '',
    confirmPassword: ''
  });
  const [formError, setFormError] = useState('');
  const { register, error } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Walidacja
    if (!formData.username || !formData.email || !formData.full_name || !formData.password || !formData.confirmPassword) {
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
    
    setFormError('');
    const success = await register({
      username: formData.username, // Dodane pole username
      email: formData.email,
      full_name: formData.full_name,
      password: formData.password
    });
    
    if (success) {
      navigate('/login');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
      <Typography component="h1" variant="h5" align="center" gutterBottom>
        Rejestracja
      </Typography>
      
      {(formError || error) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {formError || error}
        </Alert>
      )}
      
      <TextField
        margin="normal"
        required
        fullWidth
        id="username"
        label="Nazwa użytkownika"
        name="username"
        autoComplete="username"
        autoFocus
        value={formData.username}
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
        id="email"
        label="Adres e-mail"
        name="email"
        autoComplete="email"
        value={formData.email}
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
        sx={{ mt: 3, mb: 2 }}
      >
        Zarejestruj się
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