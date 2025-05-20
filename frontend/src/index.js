import React from 'react';
import ReactDOM from 'react-dom';

// Bardzo prosty komponent bez żadnych zależności
function App() {
  return (
    <div style={{
      textAlign: 'center',
      marginTop: '50px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>Asystent Prawny</h1>
      <p>Aplikacja jest załadowana poprawnie!</p>
      <p style={{ color: 'blue' }}>To jest tekst testowy, który powinien być widoczny.</p>
    </div>
  );
}

// Używamy starszej metody renderowania (kompatybilnej z React 17 i wcześniejszymi)
ReactDOM.render(
  <App />,
  document.getElementById('root')
);