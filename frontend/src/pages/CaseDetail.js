import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Button,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  Avatar,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import GavelIcon from '@mui/icons-material/Gavel';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import SearchIcon from '@mui/icons-material/Search';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import SendIcon from '@mui/icons-material/Send';
import { format } from 'date-fns';
import { pl } from 'date-fns/locale';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`case-tabpanel-${index}`}
      aria-labelledby={`case-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const CaseDetail = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef();
  
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false);
  const [actDialogOpen, setActDialogOpen] = useState(false);
  const [judgmentDialogOpen, setJudgmentDialogOpen] = useState(false);
  
  const [documentForm, setDocumentForm] = useState({
    file: null,
    documentType: '',
    description: ''
  });
  
  const [actForm, setActForm] = useState({
    keywords: ''
  });
  
  const [judgmentForm, setJudgmentForm] = useState({
    keywords: ''
  });
  
  const [question, setQuestion] = useState('');
  const [askingQuestion, setAskingQuestion] = useState(false);
  
  const [documentUploading, setDocumentUploading] = useState(false);
  const [fetchingActs, setFetchingActs] = useState(false);
  const [fetchingJudgments, setFetchingJudgments] = useState(false);

  useEffect(() => {
    const fetchCaseData = async () => {
      try {
        const response = await axios.get(`/cases/${caseId}`);
        // Ensure documents array is initialized
        const caseData = {
          ...response.data,
          documents: Array.isArray(response.data?.documents) ? response.data.documents : [],
          legal_acts: Array.isArray(response.data?.legal_acts) ? response.data.legal_acts : [],
          judgments: Array.isArray(response.data?.judgments) ? response.data.judgments : []
        };
        setCaseData(caseData);
        setLoading(false);
      } catch (err) {
        console.error('Błąd pobierania szczegółów sprawy:', err);
        setError('Nie udało się pobrać szczegółów sprawy. Spróbuj ponownie później.');
        setLoading(false);
      }
    };

    fetchCaseData();
  }, [caseId]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleDocumentDialogOpen = () => {
    setDocumentDialogOpen(true);
  };

  const handleDocumentDialogClose = () => {
    setDocumentDialogOpen(false);
    setDocumentForm({
      file: null,
      documentType: '',
      description: ''
    });
  };

  const handleActDialogOpen = () => {
    setActDialogOpen(true);
  };

  const handleActDialogClose = () => {
    setActDialogOpen(false);
    setActForm({
      keywords: ''
    });
  };

  const handleJudgmentDialogOpen = () => {
    setJudgmentDialogOpen(true);
  };

  const handleJudgmentDialogClose = () => {
    setJudgmentDialogOpen(false);
    setJudgmentForm({
      keywords: ''
    });
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setDocumentForm({
        ...documentForm,
        file: e.target.files[0]
      });
    }
  };

  const handleDocumentFormChange = (e) => {
    const { name, value } = e.target;
    setDocumentForm({
      ...documentForm,
      [name]: value
    });
  };

  const handleActFormChange = (e) => {
    const { name, value } = e.target;
    setActForm({
      ...actForm,
      [name]: value
    });
  };

  const handleJudgmentFormChange = (e) => {
    const { name, value } = e.target;
    setJudgmentForm({
      ...judgmentForm,
      [name]: value
    });
  };

  const handleUploadDocument = async () => {
    if (!documentForm.file || !documentForm.documentType) {
      return;
    }

    setDocumentUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', documentForm.file);
      formData.append('document_type', documentForm.documentType);
      
      if (documentForm.description) {
        formData.append('description', documentForm.description);
      }

      const response = await axios.post(`/cases/${caseId}/documents/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Dodanie nowego dokumentu do stanu
      setCaseData(prevData => ({
        ...prevData,
        documents: [...prevData.documents, response.data]
      }));

      handleDocumentDialogClose();
    } catch (err) {
      console.error('Błąd podczas wgrywania dokumentu:', err);
      setError('Nie udało się wgrać dokumentu. Spróbuj ponownie później.');
    } finally {
      setDocumentUploading(false);
    }
  };

  const handleFetchLegalActs = async () => {
    if (!actForm.keywords.trim()) {
      return;
    }

    setFetchingActs(true);

    try {
      const formData = new FormData();
      // Dla uproszczenia, przyjmujemy słowa kluczowe jako string oddzielony przecinkami
      formData.append('keywords', actForm.keywords.split(',').map(k => k.trim()));

      const response = await axios.post(`/cases/${caseId}/fetch-legal-acts/`, formData);

      // Dodanie nowych aktów prawnych do stanu
      setCaseData(prevData => ({
        ...prevData,
        legal_acts: [...prevData.legal_acts, ...response.data]
      }));

      handleActDialogClose();
    } catch (err) {
      console.error('Błąd podczas pobierania aktów prawnych:', err);
      setError('Nie udało się pobrać aktów prawnych. Spróbuj ponownie później.');
    } finally {
      setFetchingActs(false);
    }
  };

  const handleFetchJudgments = async () => {
    if (!judgmentForm.keywords.trim()) {
      return;
    }

    setFetchingJudgments(true);

    try {
      const formData = new FormData();
      // Dla uproszczenia, przyjmujemy słowa kluczowe jako string oddzielony przecinkami
      formData.append('keywords', judgmentForm.keywords.split(',').map(k => k.trim()));

      const response = await axios.post(`/cases/${caseId}/fetch-judgments/`, formData);

      // Dodanie nowych orzeczeń do stanu
      setCaseData(prevData => ({
        ...prevData,
        judgments: [...prevData.judgments, ...response.data]
      }));

      handleJudgmentDialogClose();
    } catch (err) {
      console.error('Błąd podczas pobierania orzeczeń:', err);
      setError('Nie udało się pobrać orzeczeń. Spróbuj ponownie później.');
    } finally {
      setFetchingJudgments(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setAskingQuestion(true);

    try {
      const formData = new FormData();
      formData.append('question', question);

      const response = await axios.post(`/cases/${caseId}/ask/`, formData);

      // Dodanie nowego pytania do stanu
      setCaseData(prevData => ({
        ...prevData,
        questions: prevData.questions ? [...prevData.questions, response.data] : [response.data]
      }));

      setQuestion('');
    } catch (err) {
      console.error('Błąd podczas zadawania pytania:', err);
      setError('Nie udało się zadać pytania. Spróbuj ponownie później.');
    } finally {
      setAskingQuestion(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!caseData) {
    return (
      <Box sx={{ mt: 4 }}>
        <Alert severity="error">
          Nie udało się załadować szczegółów sprawy.
        </Alert>
        <Button 
          variant="outlined" 
          onClick={() => navigate('/cases')}
          sx={{ mt: 2 }}
        >
          Wróć do listy spraw
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {caseData.title}
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          {caseData.description}
        </Typography>
        <Chip 
          icon={<DescriptionIcon />} 
          label={`Dokumenty: ${caseData.documents.length}`} 
          sx={{ mr: 1 }}
        />
        <Chip 
          icon={<GavelIcon />} 
          label={`Akty prawne: ${caseData.legal_acts.length}`} 
          sx={{ mr: 1 }}
        />
        <Chip 
          icon={<QuestionAnswerIcon />} 
          label={`Pytania: ${caseData.questions?.length || 0}`} 
        />
      </Box>

      <Paper elevation={3} sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Dokumenty" id="case-tab-0" aria-controls="case-tabpanel-0" />
          <Tab label="Akty prawne" id="case-tab-1" aria-controls="case-tabpanel-1" />
          <Tab label="Orzeczenia" id="case-tab-2" aria-controls="case-tabpanel-2" />
          <Tab label="Zadaj pytanie" id="case-tab-3" aria-controls="case-tabpanel-3" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleDocumentDialogOpen}
            >
              Dodaj dokument
            </Button>
          </Box>

          {caseData.documents.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1" gutterBottom>
                Brak dokumentów dla tej sprawy.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleDocumentDialogOpen}
                sx={{ mt: 1 }}
              >
                Dodaj pierwszy dokument
              </Button>
            </Box>
          ) : (
            <List>
              {caseData.documents.map((document, index) => (
                <React.Fragment key={document.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar>
                        <DescriptionIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={document.filename}
                      secondary={
                        <>
                          <Typography
                            component="span"
                            variant="body2"
                            color="text.primary"
                          >
                            {document.document_type}
                          </Typography>
                          {document.description && (
                            <Typography
                              component="span"
                              variant="body2"
                              color="text.secondary"
                              sx={{ display: 'block' }}
                            >
                              {document.description}
                            </Typography>
                          )}
                          <Typography
                            component="span"
                            variant="body2"
                            color="text.secondary"
                          >
                            {`Dodano: ${format(new Date(document.created_at), 'Pp', { locale: pl })}`}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SearchIcon />}
              onClick={handleActDialogOpen}
            >
              Wyszukaj akty prawne
            </Button>
          </Box>

          {caseData.legal_acts.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1" gutterBottom>
                Brak aktów prawnych dla tej sprawy.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<SearchIcon />}
                onClick={handleActDialogOpen}
                sx={{ mt: 1 }}
              >
                Wyszukaj akty prawne
              </Button>
            </Box>
          ) : (
            <div>
              {caseData.legal_acts.map((act) => (
                <Accordion key={act.id}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls={`panel-${act.id}-content`}
                    id={`panel-${act.id}-header`}
                  >
                    <Typography sx={{ fontWeight: 'bold' }}>{act.title}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {`${act.publication}, ${act.year}`}
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {act.content}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </div>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SearchIcon />}
              onClick={handleJudgmentDialogOpen}
            >
              Wyszukaj orzeczenia
            </Button>
          </Box>

          {caseData.judgments.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1" gutterBottom>
                Brak orzeczeń dla tej sprawy.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<SearchIcon />}
                onClick={handleJudgmentDialogOpen}
                sx={{ mt: 1 }}
              >
                Wyszukaj orzeczenia
              </Button>
            </Box>
          ) : (
            <div>
              {caseData.judgments.map((judgment) => (
                <Accordion key={judgment.id}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls={`panel-${judgment.id}-content`}
                    id={`panel-${judgment.id}-header`}
                  >
                    <Typography sx={{ fontWeight: 'bold' }}>
                      {`${judgment.court_name}, ${judgment.case_number}`}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {`Data orzeczenia: ${format(new Date(judgment.judgment_date), 'd MMMM yyyy', { locale: pl })}`}
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {judgment.content}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </div>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Zadaj pytanie dotyczące sprawy
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Zadaj pytanie, a AI przeanalizuje dokumenty, akty prawne i orzeczenia, aby dostarczyć odpowiedź.
            </Typography>
            
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              placeholder="Wpisz swoje pytanie..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              sx={{ mb: 2 }}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                endIcon={<SendIcon />}
                onClick={handleAskQuestion}
                disabled={askingQuestion || !question.trim()}
              >
                {askingQuestion ? 'Analizowanie...' : 'Wyślij pytanie'}
              </Button>
            </Box>
          </Box>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Historia pytań
          </Typography>
          
          {!caseData.questions || caseData.questions.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1">
                Jeszcze nie zadano żadnych pytań.
              </Typography>
            </Box>
          ) : (
            <div>
              {caseData.questions.map((q) => (
                <Card key={q.id} variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary" gutterBottom>
                      {q.question}
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {q.answer}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {`Zapytano: ${format(new Date(q.created_at), 'Pp', { locale: pl })}`}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end' }}>
                    <Button size="small" onClick={() => setQuestion(q.question)}>
                      Zadaj ponownie
                    </Button>
                  </CardActions>
                </Card>
              ))}
            </div>
          )}
        </TabPanel>
      </Paper>

      {/* Dialog dodawania dokumentu */}
      <Dialog open={documentDialogOpen} onClose={handleDocumentDialogClose}>
        <DialogTitle>Dodaj dokument</DialogTitle>
        <DialogContent>
          <Box sx={{ my: 2 }}>
            <Button
              variant="outlined"
              component="label"
              startIcon={<AttachFileIcon />}
              sx={{ mb: 2 }}
            >
              Wybierz plik
              <input
                ref={fileInputRef}
                type="file"
                hidden
                onChange={handleFileChange}
              />
            </Button>
            
            {documentForm.file && (
              <Typography variant="body2" sx={{ mb: 2 }}>
                Wybrany plik: {documentForm.file.name}
              </Typography>
            )}

            <TextField
              fullWidth
              margin="dense"
              label="Typ dokumentu"
              name="documentType"
              value={documentForm.documentType}
              onChange={handleDocumentFormChange}
              required
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              margin="dense"
              label="Opis (opcjonalny)"
              name="description"
              value={documentForm.description}
              onChange={handleDocumentFormChange}
              multiline
              rows={3}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDocumentDialogClose}>Anuluj</Button>
          <Button 
            onClick={handleUploadDocument}
            variant="contained"
            disabled={documentUploading || !documentForm.file || !documentForm.documentType}
          >
            {documentUploading ? 'Wgrywanie...' : 'Dodaj'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog wyszukiwania aktów prawnych */}
      <Dialog open={actDialogOpen} onClose={handleActDialogClose}>
        <DialogTitle>Wyszukaj akty prawne</DialogTitle>
        <DialogContent>
          <Box sx={{ my: 2 }}>
            <Typography variant="body2" paragraph>
              Wprowadź słowa kluczowe oddzielone przecinkami, aby wyszukać odpowiednie akty prawne.
            </Typography>
            <TextField
              fullWidth
              margin="dense"
              label="Słowa kluczowe"
              name="keywords"
              value={actForm.keywords}
              onChange={handleActFormChange}
              placeholder="np. kodeks cywilny, odszkodowanie, wypadek"
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleActDialogClose}>Anuluj</Button>
          <Button 
            onClick={handleFetchLegalActs}
            variant="contained"
            disabled={fetchingActs || !actForm.keywords.trim()}
          >
            {fetchingActs ? 'Wyszukiwanie...' : 'Wyszukaj'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog wyszukiwania orzeczeń */}
      <Dialog open={judgmentDialogOpen} onClose={handleJudgmentDialogClose}>
        <DialogTitle>Wyszukaj orzeczenia</DialogTitle>
        <DialogContent>
          <Box sx={{ my: 2 }}>
            <Typography variant="body2" paragraph>
              Wprowadź słowa kluczowe oddzielone przecinkami, aby wyszukać orzeczenia sądowe.
            </Typography>
            <TextField
              fullWidth
              margin="dense"
              label="Słowa kluczowe"
              name="keywords"
              value={judgmentForm.keywords}
              onChange={handleJudgmentFormChange}
              placeholder="np. wypadek, zadośćuczynienie, art. 445"
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleJudgmentDialogClose}>Anuluj</Button>
          <Button 
            onClick={handleFetchJudgments}
            variant="contained"
            disabled={fetchingJudgments || !judgmentForm.keywords.trim()}
          >
            {fetchingJudgments ? 'Wyszukiwanie...' : 'Wyszukaj'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CaseDetail;
