import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  CircularProgress,
  IconButton,
  Tooltip,
  Alert,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Search as SearchIcon
} from '@mui/icons-material';

// Adres API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const CasesList = () => {
  const navigate = useNavigate();
  
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Stan dla paginacji
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Stan dla wyszukiwania
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredCases, setFilteredCases] = useState([]);
  
  // Stan dla dialogu tworzenia/edycji sprawy
  const [openDialog, setOpenDialog] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [currentCase, setCurrentCase] = useState({
    id: null,
    title: '',
    description: '',
    case_number: ''
  });
  
  // Stan dla dialogu usuwania
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [caseToDelete, setCaseToDelete] = useState(null);
  
  // Pobieranie spraw
  useEffect(() => {
    const fetchCases = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/cases/`);
        setCases(response.data);
        setFilteredCases(response.data);
      } catch (error) {
        console.error('Błąd pobierania spraw:', error);
        setError('Wystąpił błąd podczas pobierania spraw. Spróbuj ponownie później.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchCases();
  }, []);
  
  // Filtrowanie spraw
  useEffect(() => {
    if (searchQuery) {
      const filtered = cases.filter(
        (c) =>
          c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (c.case_number && c.case_number.toLowerCase().includes(searchQuery.toLowerCase())) ||
          (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setFilteredCases(filtered);
    } else {
      setFilteredCases(cases);
    }
    
    setPage(0);
  }, [searchQuery, cases]);
  
  // Obsługa zmiany strony
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  // Obsługa zmiany liczby wierszy na stronę
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Obsługa otwierania dialogu tworzenia sprawy
  const handleCreateCase = () => {
    setCurrentCase({
      id: null,
      title: '',
      description: '',
      case_number: ''
    });
    setIsEditMode(false);
    setOpenDialog(true);
  };
  
  // Obsługa otwierania dialogu edycji sprawy
  const handleEditCase = (c) => {
    setCurrentCase({
      id: c.id,
      title: c.title,
      description: c.description || '',
      case_number: c.case_number || ''
    });
    setIsEditMode(true);
    setOpenDialog(true);
  };
  
  // Obsługa zapisywania sprawy
  const handleSaveCase = async () => {
    try {
      if (!currentCase.title) {
        setError('Tytuł sprawy jest wymagany');
        return;
      }
      
      if (isEditMode) {
        // Aktualizacja istniejącej sprawy
        await axios.put(`${API_URL}/cases/${currentCase.id}`, currentCase);
        
        // Aktualizacja listy
        setCases(
          cases.map((c) => (c.id === currentCase.id ? { ...c, ...currentCase } : c))
        );
      } else {
        // Tworzenie nowej sprawy
        const response = await axios.post(`${API_URL}/cases/`, currentCase);
        
        // Aktualizacja listy
        setCases([...cases, response.data]);
      }
      
      setOpenDialog(false);
    } catch (error) {
      console.error('Błąd zapisywania sprawy:', error);
      setError('Wystąpił błąd podczas zapisywania sprawy. Spróbuj ponownie później.');
    }
  };
  
  // Obsługa otwierania dialogu usuwania
  const handleDeleteClick = (c) => {
    setCaseToDelete(c);
    setOpenDeleteDialog(true);
  };
  
  // Obsługa usuwania sprawy
  const handleDeleteConfirm = async () => {
    try {
      await axios.delete(`${API_URL}/cases/${caseToDelete.id}`);
      
      // Aktualizacja listy
      setCases(cases.filter((c) => c.id !== caseToDelete.id));
      
      setOpenDeleteDialog(false);
    } catch (error) {
      console.error('Błąd usuwania sprawy:', error);
      setError('Wystąpił błąd podczas usuwania sprawy. Spróbuj ponownie później.');
    }
  };
  
  // Obsługa przejścia do szczegółów sprawy
  const handleViewCase = (caseId) => {
    navigate(`/cases/${caseId}`);
  };
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Sprawy
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {/* Pasek narzędziowy */}
      <Grid container spacing={2} alignItems="center" mb={2}>
        <Grid item xs={12} sm={6} md={4}>
          <TextField
            fullWidth
            variant="outlined"
            label="Wyszukaj sprawy"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              endAdornment: <SearchIcon color="action" />,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={8} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateCase}
          >
            Nowa sprawa
          </Button>
        </Grid>
      </Grid>
      
      {/* Tabela spraw */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Tytuł</TableCell>
              <TableCell>Sygnatura</TableCell>
              <TableCell>Opis</TableCell>
              <TableCell>Data utworzenia</TableCell>
              <TableCell align="right">Akcje</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : filteredCases.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  Nie znaleziono żadnych spraw
                </TableCell>
              </TableRow>
            ) : (
              filteredCases
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((c) => (
                  <TableRow key={c.id}>
                    <TableCell>{c.title}</TableCell>
                    <TableCell>{c.case_number || '-'}</TableCell>
                    <TableCell>
                      {c.description
                        ? c.description.length > 100
                          ? `${c.description.substring(0, 100)}...`
                          : c.description
                        : '-'}
                    </TableCell>
                    <TableCell>
                      {new Date(c.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Zobacz szczegóły">
                        <IconButton
                          color="primary"
                          onClick={() => handleViewCase(c.id)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edytuj">
                        <IconButton
                          color="primary"
                          onClick={() => handleEditCase(c)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Usuń">
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteClick(c)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
            )}
          </TableBody>
        </Table>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredCases.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Wierszy na stronę:"
          labelDisplayedRows={({ from, to, count }) =>
            `${from}-${to} z ${count}`
          }
        />
      </TableContainer>
      
      {/* Dialog tworzenia/edycji sprawy */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {isEditMode ? 'Edytuj sprawę' : 'Nowa sprawa'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Tytuł sprawy"
            fullWidth
            required
            value={currentCase.title}
            onChange={(e) =>
              setCurrentCase({ ...currentCase, title: e.target.value })
            }
          />
          <TextField
            margin="dense"
            label="Sygnatura sprawy"
            fullWidth
            value={currentCase.case_number}
            onChange={(e) =>
              setCurrentCase({ ...currentCase, case_number: e.target.value })
            }
          />
          <TextField
            margin="dense"
            label="Opis sprawy"
            fullWidth
            multiline
            rows={4}
            value={currentCase.description}
            onChange={(e) =>
              setCurrentCase({ ...currentCase, description: e.target.value })
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Anuluj</Button>
          <Button onClick={handleSaveCase} variant="contained">
            {isEditMode ? 'Zapisz zmiany' : 'Utwórz sprawę'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog usuwania */}
      <Dialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
      >
        <DialogTitle>Potwierdź usunięcie</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Czy na pewno chcesz usunąć sprawę "
            {caseToDelete?.title}"? Tej operacji nie można cofnąć.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Anuluj</Button>
          <Button onClick={handleDeleteConfirm} color="error">
            Usuń
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CasesList;
