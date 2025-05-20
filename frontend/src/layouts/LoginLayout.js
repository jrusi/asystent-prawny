import React from 'react';
import { Box, Container, Paper, Typography } from '@mui/material';

const LoginLayout = ({ children }) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={6}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h4" gutterBottom>
            Asystent Prawny
          </Typography>
          
          {children}
        </Paper>
      </Container>
    </Box>
  );
};

export default LoginLayout;
