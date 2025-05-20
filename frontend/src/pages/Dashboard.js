import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar
} from '@mui/material';
import {
  Folder as FolderIcon,
  Description as DescriptionIcon,
  Gavel as GavelIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

// Adres API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCases: 0,
    totalDocuments: 0,
    totalLegalActs: 0,
    totalJudgments: 0
  });
  const [recentCases, setRecentCases] = useState([]);
  
  // Pobieranie danych
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Pobieranie spraw
        const casesResponse = await axios.get(`${API_URL}/cases/`);
        const cases = casesResponse.data || [];
        
        // Obliczanie statystyk
        let documents = 0;
        let legalActs = 0;
        let judgments = 0;
        
        cases.forEach(c => {
          documents += c.documents ? c.documents.length : 0;
          legalActs += c.legal_acts ? c.legal_acts.length : 0;
          judgments += c.judgments ? c.judgments.length : 0;
        });
        
        setStats({
          totalCases: cases.length,
          totalDocuments: documents,
          totalLegalActs: legalActs,
          totalJudgments: judgments
        });
        
        // Pobieranie najnowszych spraw (maksymalnie 5)
        setRecentCases(cases.slice(0, 5));
      } catch (error) {
        console.error('Błąd pobierania danych:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // Obsługa tworzenia nowej sprawy
  const handleCreateCase = () => {
    navigate('/cases/new');
  };
  
  // Obsługa przejścia do sprawy
  const handleCaseClick = (caseId) => {
    navigate(`/cases/${caseId}`);
  };
  
  return (
    <Box>
      {/* Powitanie */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Witaj, {currentUser?.username || 'Użytkowniku'}!
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Oto przegląd Twoich spraw prawnych i dokumentów.
        </Typography>
      </Box>
      
      {/* Statystyki */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'primary.light',
              color: 'white',
            }}
          >
            <Avatar sx={{ bgcolor: 'primary.dark', width: 56, height: 56, mb: 1 }}>
              <FolderIcon fontSize="large" />
            </Avatar>
            <Typography component="h2" variant="h5">
              {stats.totalCases}
            </Typography>
            <Typography variant="body2">Sprawy</Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'secondary.light',
              color: 'white',
            }}
          >
            <Avatar sx={{ bgcolor: 'secondary.dark', width: 56, height: 56, mb: 1 }}>
              <DescriptionIcon fontSize="large" />
            </Avatar>
            <Typography component="h2" variant="h5">
              {stats.totalDocuments}
            </Typography>
            <Typography variant="body2">Dokumenty</Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'success.light',
              color: 'white',
            }}
          >
            <Avatar sx={{ bgcolor: 'success.dark', width: 56, height: 56, mb: 1 }}>
              <GavelIcon fontSize="large" />
            </Avatar>
            <Typography component="h2" variant="h5">
              {stats.totalLegalActs}
            </Typography>
            <Typography variant="body2">Akty prawne</Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'info.light',
              color: 'white',
            }}
          >
            <Avatar sx={{ bgcolor: 'info.dark', width: 56, height: 56, mb: 1 }}>
              <GavelIcon fontSize="large" />
            </Avatar>
            <Typography component="h2" variant="h5">
              {stats.totalJudgments}
            </Typography>
            <Typography variant="body2">Orzeczenia</Typography>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Ostatnie sprawy */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Ostatnie sprawy</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateCase}
          >
            Nowa sprawa
          </Button>
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        {loading ? (
          <Typography>Ładowanie...</Typography>
        ) : recentCases.length > 0 ? (
          <List>
            {recentCases.map((c) => (
              <ListItem
                key={c.id}
                button
                onClick={() => handleCaseClick(c.id)}
                divider
              >
                <ListItemAvatar>
                  <Avatar>
                    <FolderIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={c.title}
                  secondary={
                    <>
                      {c.case_number && (
                        <Typography
                          component="span"
                          variant="body2"
                          color="textPrimary"
                        >
                          {c.case_number} - 
                        </Typography>
                      )}
                      {" "}
                      {c.description
                        ? c.description.length > 100
                          ? `${c.description.substring(0, 100)}...`
                          : c.description
                        : "Brak opisu"}
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography>Nie masz jeszcze żadnych spraw</Typography>
        )}
        
        {recentCases.length > 0 && (
          <Box mt={2} display="flex" justifyContent="flex-end">
            <Button onClick={() => navigate('/cases')}>
              Zobacz wszystkie sprawy
            </Button>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default Dashboard;
