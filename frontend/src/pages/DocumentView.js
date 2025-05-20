import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Divider,
  Card,
  CardContent,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Description as DescriptionIcon,
  Gavel as GavelIcon,
  Download as DownloadIcon,
  ContentCopy as ContentCopyIcon,
  Search as SearchIcon
} from '@mui/icons-material';

// Adres API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const DocumentView = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();
  
  const [document, setDocument] = useState(null);
  const [documentContent, setDocumentContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [contentLoading, setContentLoading] = useState(true);
  const [error, setError] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);
  
  // Pobieranie danych dokumentu
  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/documents/${documentId}`);
        setDocument(response.data);
      } catch (error) {
        console.error('Błąd pobierania dokumentu:', error);
        setError('Wystąpił błąd podczas pobierania dokumentu. Spróbuj ponownie później.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDocument();
  }, [documentId]);
  
  // Pobieranie treści dokumentu
  useEffect(() => {
    if (document) {
      const fetchDocumentContent = async () => {
        try {
          setContentLoading(true);
          const response = await axios.get(`${API_URL}/documents/${documentId}/content`);
          setDocumentContent(response.data.content_text || '');
        } catch (error) {
          console.error('Błąd pobierania treści dokumentu:', error);
          setError('Wystąpił błąd podczas pobierania treści dokumentu.');
        } finally {
          setContentLoading(false);
        }
      };
      
      fetchDocumentContent();
    }
  }, [document, documentId]);
  
  // Obsługa pobierania dokumentu
  const handleDownload = async () => {
    try {
      // Implementacja pobierania dokumentu
      // To jest uproszczona wersja - w rzeczywistości należałoby pobrać plik z MinIO
      // i udostępnić go użytkownikowi do pobrania
      
      // Tworzy dokument tekstowy z treścią
      const blob = new Blob([documentContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${document.title}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Błąd pobierania dokumentu:', error);
      setError('Wystąpił błąd podczas pobierania dokumentu.');
    }
  };
  
  // Obsługa kopiowania treści
  const handleCopyContent = () => {
    navigator.clipboard.writeText(documentContent)
      .then(() => {
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      })
      .catch(() => {
        setError('Nie udało się skopiować treści do schowka.');
      });
  };
  
  // Formatowanie daty
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };
  
  // Powrót do szczegółów sprawy
  const handleBack = () => {
    if (document && document.case_id) {
      navigate(`/cases/${document.case_id}`);
    } else {
      navigate('/cases');
    }
  };
  
  // Obsługa analizy dokumentu
  const handleAnalyzeDocument = async () => {
    if (!document || !document.case_id) return;
    
    try {
      await axios.post(`${API_URL}/cases/${document.case_id}/analyze-document/${documentId}`);
      navigate(`/cases/${document.case_id}`);
    } catch (error) {
      console.error('Błąd analizy dokumentu:', error);
      setError('Wystąpił błąd podczas analizy dokumentu.');
    }
  };
  
  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="300px"
      >
        <CircularProgress />
      </Box>
    );
  }
  
  if (error && !document) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }
  
  if (!document) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Nie znaleziono dokumentu o podanym ID
      </Alert>
    );
  }
  
  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {copySuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Skopiowano treść do schowka
        </Alert>
      )}
      
      {/* Nagłówek */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container>
          <Grid item xs={12} sm={8}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={handleBack}
              sx={{ mb: 2 }}
            >
              Powrót
            </Button>
            <Typography variant="h4" gutterBottom>
              {document.title}
            </Typography>
            {document.description && (
              <Typography variant="body1" paragraph>
                {document.description}
              </Typography>
            )}
            <Typography variant="body2" color="text.secondary">
              Dodano: {formatDate(document.created_at)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={4} sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'flex-start' }}>
            <Tooltip title="Analizuj dokument">
              <Button
                variant="outlined"
                startIcon={<SearchIcon />}
                onClick={handleAnalyzeDocument}
                sx={{ mr: 1 }}
              >
                Analizuj
              </Button>
            </Tooltip>
            <Tooltip title="Pobierz dokument">
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={handleDownload}
              >
                Pobierz
              </Button>
            </Tooltip>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Treść dokumentu */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            <DescriptionIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            Treść dokumentu
          </Typography>
          <Tooltip title="Kopiuj treść">
            <IconButton onClick={handleCopyContent}>
              <ContentCopyIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        {contentLoading ? (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight="200px"
          >
            <CircularProgress />
          </Box>
        ) : documentContent ? (
          <Card variant="outlined" sx={{ bgcolor: 'background.default' }}>
            <CardContent>
              <Typography
                variant="body1"
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                  overflowX: 'auto',
                }}
              >
                {documentContent}
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Typography variant="body1" color="text.secondary" align="center">
            Brak treści dokumentu
          </Typography>
        )}
      </Paper>
      
      {/* Informacje o dokumencie */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Informacje o dokumencie
        </Typography>
        
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2">
              <strong>Tytuł:</strong> {document.title}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2">
              <strong>ID dokumentu:</strong> {document.id}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2">
              <strong>Data utworzenia:</strong> {formatDate(document.created_at)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2">
              <strong>Typ pliku:</strong> {document.file_type || 'Nieznany'}
            </Typography>
          </Grid>
          {document.description && (
            <Grid item xs={12}>
              <Typography variant="body2">
                <strong>Opis:</strong> {document.description}
              </Typography>
            </Grid>
          )}
          <Grid item xs={12}>
            <Typography variant="body2">
              <strong>Ścieżka pliku:</strong> {document.file_path}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default DocumentView;
