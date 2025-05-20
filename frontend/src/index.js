import React from 'react';
import ReactDOM from 'react-dom';

// Prosty komponent bez zależności od React Router czy Material UI
const App = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Asystent Prawny</h1>
      <p>Aplikacja została prawidłowo załadowana!</p>
    </div>
  );
};

// Użyj tradycyjnej metody renderowania, która jest bardziej kompatybilna
ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);