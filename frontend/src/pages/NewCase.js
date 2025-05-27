import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';  // Import our configured api instance
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  CircularProgress,
  Alert
} from '@mui/material';

const NewCase = () => {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    title: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);
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
    
    if (!formData.title.trim()) {
      setError('Tytuł sprawy jest wymagany.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/cases', {  // Use api instance and correct path
        title: formData.title,
        description: formData.description
      });
      
      // Przekierowanie do nowo utworzonej sprawy
      navigate(`/cases/${response.data.id}`);
    } catch (err) {
      console.error('Błąd tworzenia sprawy:', err);
      setError('Wystąpił błąd podczas tworzenia sprawy. Spróbuj ponownie później.');
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Nowa sprawa
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Paper elevation={3} sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Tytuł sprawy"
                name="title"
                value={formData.title}
                onChange={handleChange}
                variant="outlined"
                placeholder="np. Sprawa o odszkodowanie z tytułu wypadku komunikacyjnego"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Opis sprawy"
                name="description"
                value={formData.description}
                onChange={handleChange}
                variant="outlined"
                multiline
                rows={4}
                placeholder="Wprowadź krótki opis sprawy oraz istotne informacje"
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/cases')}
                  disabled={loading}
                >
                  Anuluj
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Utwórz sprawę'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Co dalej?
        </Typography>
        <Typography variant="body1" paragraph>
          Po utworzeniu sprawy będziesz mógł:
        </Typography>
        <ul>
          <li>
            <Typography variant="body1">
              Dodawać dokumenty związane ze sprawą (np. pozew, odpowiedź na pozew, pisma procesowe)
            </Typography>
          </li>
          <li>
            <Typography variant="body1">
              Wyszukiwać akty prawne odpowiednie dla Twojej sprawy
            </Typography>
          </li>
          <li>
            <Typography variant="body1">
              Znajdować orzeczenia sądowe w podobnych sprawach
            </Typography>
          </li>
          <li>
            <Typography variant="body1">
              Zadawać pytania dotyczące sprawy i otrzymywać inteligentne odpowiedzi
            </Typography>
          </li>
        </ul>
      </Box>
    </Box>
  );
};

export default NewCase;
