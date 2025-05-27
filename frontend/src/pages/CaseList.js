import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import api from '../utils/api';  // Import our configured api instance
import {
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Avatar,
  IconButton,
  Button,
  Divider,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import { format } from 'date-fns';
import { pl } from 'date-fns/locale';

const CaseList = () => {
  const [cases, setCases] = useState([]);
  const [filteredCases, setFilteredCases] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [caseToDelete, setCaseToDelete] = useState(null);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const response = await api.get('/cases');
        console.log('Cases response:', response);
        // Ensure we have a valid array of cases with required fields
        const casesData = Array.isArray(response.data) ? response.data.map(caseItem => ({
          ...caseItem,
          documents: Array.isArray(caseItem.documents) ? caseItem.documents : [],
          title: caseItem.title || 'Untitled Case',
          description: caseItem.description || '',
          created_at: caseItem.created_at || new Date().toISOString()
        })) : [];
        setCases(casesData);
        setFilteredCases(casesData);
        setLoading(false);
      } catch (err) {
        console.error('Błąd pobierania spraw:', err);
        setError('Nie udało się pobrać listy spraw. Spróbuj ponownie później.');
        setCases([]);
        setFilteredCases([]);
        setLoading(false);
      }
    };

    fetchCases();
  }, []);

  useEffect(() => {
    // Filtrowanie spraw na podstawie wyszukiwanego terminu
    if (!Array.isArray(cases)) {
      setFilteredCases([]);
      return;
    }
    
    if (searchTerm.trim() === '') {
      setFilteredCases(cases);
    } else {
      const filtered = cases.filter(caseItem => 
        caseItem?.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        caseItem?.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredCases(filtered);
    }
  }, [searchTerm, cases]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleDeleteClick = (e, caseItem) => {
    e.preventDefault(); // Prevent navigation to case details
    e.stopPropagation(); // Prevent event bubbling
    setCaseToDelete(caseItem);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!caseToDelete) return;
    
    try {
      await api.delete(`/cases/${caseToDelete.id}`);
      setCases(prevCases => prevCases.filter(c => c.id !== caseToDelete.id));
      setFilteredCases(prevCases => prevCases.filter(c => c.id !== caseToDelete.id));
      setDeleteDialogOpen(false);
      setCaseToDelete(null);
    } catch (err) {
      console.error('Błąd podczas usuwania sprawy:', err);
      setError('Nie udało się usunąć sprawy. Spróbuj ponownie później.');
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setCaseToDelete(null);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Moje sprawy
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          component={RouterLink}
          to="/cases/new"
        >
          Nowa sprawa
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Szukaj sprawy..."
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      <Paper elevation={3}>
        <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
          {!Array.isArray(filteredCases) || filteredCases.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                {!Array.isArray(cases) || cases.length === 0 
                  ? "Nie masz jeszcze żadnych spraw. Utwórz nową sprawę, aby rozpocząć."
                  : "Nie znaleziono spraw pasujących do kryteriów wyszukiwania."}
              </Typography>
              {(!Array.isArray(cases) || cases.length === 0) && (
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  component={RouterLink}
                  to="/cases/new"
                  sx={{ mt: 2 }}
                >
                  Utwórz nową sprawę
                </Button>
              )}
            </Box>
          ) : (
            filteredCases.map((caseItem, index) => (
              <React.Fragment key={caseItem?.id || index}>
                {index > 0 && <Divider variant="inset" component="li" />}
                <ListItem 
                  alignItems="flex-start"
                  button
                  component={RouterLink}
                  to={`/cases/${caseItem.id}`}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      <FolderIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={caseItem.title}
                    secondary={
                      <>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.primary"
                          sx={{ display: 'block', mb: 0.5 }}
                        >
                          {caseItem.description}
                        </Typography>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.secondary"
                        >
                          {`Utworzono: ${format(new Date(caseItem.created_at), 'd MMMM yyyy', { locale: pl })}`}
                        </Typography>
                      </>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Chip 
                      label={`Dokumenty: ${Array.isArray(caseItem?.documents) ? caseItem.documents.length : 0}`} 
                      size="small" 
                      sx={{ mr: 1 }}
                    />
                    <IconButton 
                      edge="end" 
                      aria-label="delete"
                      onClick={(e) => handleDeleteClick(e, caseItem)}
                      sx={{ 
                        color: 'error.main',
                        '&:hover': {
                          backgroundColor: 'error.light',
                          color: 'error.dark',
                        }
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              </React.Fragment>
            ))
          )}
        </List>
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"Czy na pewno chcesz usunąć tę sprawę?"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Ta operacja jest nieodwracalna. Wszystkie dokumenty i dane związane z tą sprawą zostaną usunięte.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Anuluj
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            Usuń
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CaseList;
