// frontend/src/pages/Login.js
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

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');
  const { login, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      setFormError('Proszę wypełnić wszystkie pola');
      return;
    }
    
    setFormError('');
    const success = await login(email, password);
    
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
      <Typography component="h1" variant="h5" align="center" gutterBottom>
        Logowanie
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
        id="email"
        label="Adres e-mail"
        name="email"
        autoComplete="email"
        autoFocus
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
        autoComplete="current-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Zaloguj się
      </Button>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Link component={RouterLink} to="/password-reset" variant="body2">
          Zapomniałeś hasła?
        </Link>
        <Link component={RouterLink} to="/register" variant="body2">
          Nie masz konta? Zarejestruj się
        </Link>
      </Box>
    </Box>
  );
};

export default Login;

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
    name: '',
    email: '',
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
    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
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
      name: formData.name,
      email: formData.email,
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
        id="name"
        label="Imię i nazwisko"
        name="name"
        autoComplete="name"
        autoFocus
        value={formData.name}
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

// frontend/src/pages/Dashboard.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Divider
} from '@mui/material';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Dane przykładowe
  const recentCases = [
    { id: 1, title: 'Sprawa #1234', status: 'W toku', lastUpdated: '2025-05-18' },
    { id: 2, title: 'Sprawa #5678', status: 'Zakończona', lastUpdated: '2025-05-15' }
  ];

  const recentDocuments = [
    { id: 1, title: 'Umowa sprzedaży.pdf', addedDate: '2025-05-18' },
    { id: 2, title: 'Akt notarialny.pdf', addedDate: '2025-05-15' }
  ];

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4 }}>
        Dashboard
      </Typography>

      <Typography variant="h6" sx={{ mb: 2 }}>
        Witaj, {user?.name || 'Użytkowniku'}!
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">Ostatnie sprawy</Typography>
              <Divider sx={{ my: 2 }} />
              {recentCases.length > 0 ? (
                recentCases.map((caseItem) => (
                  <Box key={caseItem.id} sx={{ mb: 2 }}>
                    <Typography variant="subtitle1">{caseItem.title}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Status: {caseItem.status} | Ostatnia aktualizacja: {caseItem.lastUpdated}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography>Brak spraw</Typography>
              )}
            </CardContent>
            <CardActions>
              <Button size="small" onClick={() => navigate('/cases')}>
                Zobacz wszystkie sprawy
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">Ostatnie dokumenty</Typography>
              <Divider sx={{ my: 2 }} />
              {recentDocuments.length > 0 ? (
                recentDocuments.map((document) => (
                  <Box key={document.id} sx={{ mb: 2 }}>
                    <Typography variant="subtitle1">{document.title}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Dodano: {document.addedDate}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography>Brak dokumentów</Typography>
              )}
            </CardContent>
            <CardActions>
              <Button size="small" onClick={() => navigate('/documents')}>
                Zobacz wszystkie dokumenty
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6">Szybkie akcje</Typography>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button variant="contained" onClick={() => navigate('/cases')}>
                  Nowa sprawa
                </Button>
                <Button variant="outlined" onClick={() => navigate('/documents')}>
                  Dodaj dokument
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;

// frontend/src/pages/NotFound.js
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Button, Typography, Container } from '@mui/material';

const NotFound = () => {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          textAlign: 'center'
        }}
      >
        <Typography variant="h1" component="h1" gutterBottom>
          404
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom>
          Strona nie została znaleziona
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Przepraszamy, strona której szukasz nie istnieje lub została przeniesiona.
        </Typography>
        <Button
          variant="contained"
          component={RouterLink}
          to="/"
          sx={{ mt: 2 }}
        >
          Wróć do strony głównej
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound;
