import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  Divider,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  IconButton,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  TextField,
  Tooltip
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Gavel as GavelIcon,
  Forum as ForumIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  Search as SearchIcon,
  QuestionAnswer as QuestionAnswerIcon,
  AttachFile as AttachFileIcon,
  InsertDriveFile as FileIcon,
  PictureAsPdf as PdfIcon,
  Image as ImageIcon
} from '@mui/icons-material';

// Adres API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Komponent TabPanel
const TabPanel = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`case-tabpanel-${index}`}
      aria-labelledby={`case-tab-${index}`}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const CaseDetails = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Stan dla zakładek
  const [tabValue, setTabValue] = useState(0);
  
  // Stan dla uploadu dokumentu
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [fileToUpload, setFileToUpload] = useState(null);
  const [documentTitle, setDocumentTitle] = useState('');
  const [documentDescription, setDocumentDescription] = useState('');
  const [uploadLoading, setUploadLoading] = useState(false);
  
  // Stan dla dialogu usuwania
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  const [deleteType, setDeleteType] = useState('');
  
  // Stan dla dialogu zadawania pytań
  const [questionDialogOpen, setQuestionDialogOpen] = useState(false);
  const [question, setQuestion] = useState('');
  
  // Pobieranie danych sprawy
  useEffect(() => {
    const fetchCaseData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/cases/${caseId}`);
        setCaseData(response.data);
      } catch (error) {
        console.error('Błąd pobierania szczegółów sprawy:', error);
        setError('Wystąpił błąd podczas pobierania szczegółów sprawy. Spróbuj ponownie później.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchCaseData();
  }, [caseId]);
  
  // Obsługa zmiany zakładki
  const handleChangeTab = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Obsługa uploadu dokumentu
  const handleUploadDocument = async () => {
    if (!fileToUpload || !documentTitle) {
      setError('Wybierz plik i podaj tytuł dokumentu');
      return;
    }
    
    try {
      setUploadLoading(true);
      
      const formData = new FormData();
      formData.append('title', documentTitle);
      formData.append('description', documentDescription);
      formData.append('file', fileToUpload);
      
      const response = await axios.post(
        `${API_URL}/cases/${caseId}/documents/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      // Aktualizacja listy dokumentów
      setCaseData({
        ...caseData,
        documents: [...(caseData.documents || []), response.data],
      });
      
      // Zamknięcie dialogu
      setUploadDialogOpen(false);
      setFileToUpload(null);
      setDocumentTitle('');
      setDocumentDescription('');
      
      // Przełączenie na zakładkę dokumentów
      setTabValue(0);
    } catch (error) {
      console.error('Błąd uploadu dokumentu:', error);
      setError('Wystąpił błąd podczas uploadu dokumentu. Spróbuj ponownie później.');
    } finally {
      setUploadLoading(false);
    }
  };
  
  // Obsługa usuwania
  const handleDelete = (item, type) => {
    setItemToDelete(item);
    setDeleteType(type);
    setDeleteDialogOpen(true);
  };
  
  // Potwierdzenie usuwania
  const handleDeleteConfirm = async () => {
    try {
      let endpoint = '';
      
      switch (deleteType) {
        case 'document':
          endpoint = `${API_URL}/documents/${itemToDelete.id}`;
          break;
        case 'legal_act':
          endpoint = `${API_URL}/legal_acts/${itemToDelete.id}`;
          break;
        case 'judgment':
          endpoint = `${API_URL}/judgments/${itemToDelete.id}`;
          break;
        case 'question':
          endpoint = `${API_URL}/questions/${itemToDelete.id}`;
          break;
        default:
          throw new Error('Nieznany typ elementu do usunięcia');
      }
      
      await axios.delete(endpoint);
      
      // Aktualizacja danych
      if (deleteType === 'document') {
        setCaseData({
          ...caseData,
          documents: caseData.documents.filter((d) => d.id !== itemToDelete.id),
        });
      } else if (deleteType === 'legal_act') {
        setCaseData({
          ...caseData,
          legal_acts: caseData.legal_acts.filter((a) => a.id !== itemToDelete.id),
        });
      } else if (deleteType === 'judgment') {
        setCaseData({
          ...caseData,
          judgments: caseData.judgments.filter((j) => j.id !== itemToDelete.id),
        });
      } else if (deleteType === 'question') {
        setCaseData({
          ...caseData,
          questions: caseData.questions.filter((q) => q.id !== itemToDelete.id),
        });
      }
      
      setDeleteDialogOpen(false);
    } catch (error) {
      console.error('Błąd usuwania elementu:', error);
      setError(`Wystąpił błąd podczas usuwania ${deleteType}. Spróbuj ponownie później.`);
    }
  };
  
  // Obsługa zadawania pytań
  const handleAskQuestion = async () => {
    if (!question) {
      setError('Podaj treść pytania');
      return;
    }
    
    try {
      const response = await axios.post(`${API_URL}/cases/${caseId}/questions`, {
        question_text: question,
        case_id: parseInt(caseId)
      });
      
      // Aktualizacja listy pytań
      setCaseData({
        ...caseData,
        questions: [...(caseData.questions || []), response.data],
      });
      
      // Zamknięcie dialogu
      setQuestionDialogOpen(false);
      setQuestion('