import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import {
  Typography,
  Box,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import AddIcon from '@mui/icons-material/Add';
import GavelIcon from '@mui/icons-material/Gavel';
import DescriptionIcon from '@mui/icons-material/Description';
import { format } from 'date-fns';
import { pl } from 'date-fns/locale';

const Dashboard = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cases, setCases] = useState([]);
  const [recentDocuments, setRecentDocuments] = useState([]);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching cases...');
        // Pobieranie listy spraw
        const casesResponse = await api.get('/cases');
        console.log('Cases response:', casesResponse.data);
        setCases(Array.isArray(casesResponse.data) ? casesResponse.data : []);
        
        // Tutaj moglibyśmy pobierać najnowsze dokumenty, ale dla uproszczenia
        // użyjemy przykładowych danych
        setRecentDocuments([
          {
            id: 1,
            filename: 'pozew.pdf',
            document_type: 'pozew',
            created_at: new Date(),
            case_id: casesResponse.data?.[0]?.id || 1
          },
          {
            id: 2,
            filename: 'odpowiedz_na_pozew.pdf',
            document_type: 'odpowiedź na pozew',
            created_at: new Date(),
            case_id: casesResponse.data?.[0]?.id || 1
          }
        ]);
        
        setLoading(false);
      } catch (err) {
        console.error('Błąd pobierania danych:', err);
        setError('Wystąpił błąd podczas pobierania danych. Spróbuj ponownie później.');
        setCases([]);
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Panel główny
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Witaj, {currentUser.full_name}!
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Podsumowanie spraw */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Moje sprawy
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {!Array.isArray(cases) || cases.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="body1" gutterBottom>
                  Nie masz jeszcze żadnych spraw.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  component={RouterLink}
                  to="/cases/new"
                  sx={{ mt: 1 }}
                >
                  Utwórz nową sprawę
                </Button>
              </Box>
            ) : (
              <>
                <List>
                  {cases.slice(0, 5).map((caseItem) => (
                    <ListItem
                      key={caseItem.id}
                      button
                      component={RouterLink}
                      to={`/cases/${caseItem.id}`}
                    >
                      <ListItemIcon>
                        <FolderIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary={caseItem.title}
                        secondary={`Utworzono: ${format(new Date(caseItem.created_at), 'Pp', { locale: pl })}`}
                      />
                    </ListItem>
                  ))}
                </List>
                
                <Box sx={{ textAlign: 'center', mt: 2 }}>
                  <Button
                    variant="outlined"
                    component={RouterLink}
                    to="/cases"
                  >
                    Zobacz wszystkie sprawy
                  </Button>
                </Box>
              </>
            )}
          </Paper>
        </Grid>
        
        {/* Najnowsze dokumenty */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Ostatnio dodane dokumenty
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {recentDocuments.length === 0 ? (
              <Typography variant="body1" sx={{ py: 2, textAlign: 'center' }}>
                Brak dokumentów
              </Typography>
            ) : (
              <List>
                {recentDocuments.map((doc) => (
                  <ListItem key={doc.id}>
                    <ListItemIcon>
                      <DescriptionIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary={doc.filename}
                      secondary={`${doc.document_type} • ${format(new Date(doc.created_at), 'Pp', { locale: pl })}`}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        
        {/* Podpowiedzi */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Szybkie akcje
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" component="div">
                      Utwórz nową sprawę
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Rozpocznij nową sprawę i zarządzaj jej dokumentami
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<AddIcon />}
                      component={RouterLink}
                      to="/cases/new"
                    >
                      Utwórz sprawę
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" component="div">
                      Przeglądaj sprawy
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Zobacz listę wszystkich Twoich spraw
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<FolderIcon />}
                      component={RouterLink}
                      to="/cases"
                    >
                      Zobacz sprawy
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" component="div">
                      Generuj dokumenty
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Twórz dokumenty prawne na podstawie szablonów
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<GavelIcon />}
                      component={RouterLink}
                      to="/documents/new"
                    >
                      Generuj dokument
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
