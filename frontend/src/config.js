const getApiUrl = () => {
  // If running in GitHub Codespaces
  if (window.location.hostname.includes('.app.github.dev')) {
    const codespaceUrl = window.location.hostname.replace('3000', '8000');
    return `https://${codespaceUrl}/api`;
  }
  
  // Default development URL
  return process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
};

const config = {
  apiUrl: getApiUrl(),
  // Add other configuration variables here
};

export default config; 