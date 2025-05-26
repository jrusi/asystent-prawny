import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper, Container } from '@mui/material';

function CaseView() {
  const { caseId } = useParams();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Szczegóły sprawy
          </Typography>
          <Typography variant="body1">
            ID sprawy: {caseId}
          </Typography>
          {/* More case details will be added here */}
        </Paper>
      </Box>
    </Container>
  );
}

export default CaseView; 