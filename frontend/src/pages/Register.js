import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Avatar,
  Button,
  TextField,
  Link,
  Grid,
  Box,
  Typography,
  Alert
} from '@mui/material';
import { PersonAddOutlined as PersonAddOutlinedIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Walidacja formularza
    if (!username || !email || !password || !confirmPassword) {
      setError('Proszę wypełnić wszystkie pola');
      return;
    }
    
    if (!validateEmail(email)) {
      setError('Proszę podać prawidłowy adres email');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Hasła nie są zgodne');
      return;
    }
    
    if (password.length < 8) {
      setError('Hasło musi zawierać co najmniej 8 znaków');
      return;
    }
    
    try {
      setError('');
      setLoading(true);
      
      const success = await register(username, email, password);
      
      if (success) {
        // Przekierowanie do strony logowania
        navigate('/login', { state: { message: 'Rejestracja zakończona pomyślnie. Możesz się teraz zalogować.' } });
      } else {
        setError('Nie udało się zarejestrować. Spróbuj ponownie później.');
      }
    } catch (error) {
      console.error('Błąd rejestracji:', error);
      setError('Wystąpił błąd podczas rejestracji. Spróbuj ponownie później.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
      }}
    >
      <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
        <PersonAddOutlinedIcon />
      </Avatar>
      
      <Typography component="h1" variant="h5">
        Rejestracja
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
          {error}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1, width: '100%' }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="username"
          label="Nazwa użytkownika"
          name="username"
          autoComplete="username"
          autoFocus
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        
        <TextField
          margin="normal"
          required
          fullWidth
          id="email"
          label="Adres email"
          name="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        
        <TextField
          margin="normal"
          required
          fullWidth
          name="confirmPassword"
          label="Potwierdź hasło"
          type="password"
          id="confirmPassword"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading}
        >
          {loading ? 'Rejestracja...' : 'Zarejestruj się'}
        </Button>
        
        <Grid container justifyContent="flex-end">
          <Grid item>
            <Link component={RouterLink} to="/login" variant="body2">
              Masz już konto? Zaloguj się
            </Link>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Register;
