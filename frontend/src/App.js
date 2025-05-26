import React, { useState } from 'react';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div style={{ 
      padding: '20px', 
      maxWidth: '800px', 
      margin: '0 auto',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>Asystent Prawny</h1>
      <div style={{ marginTop: '20px' }}>
        <p>Aplikacja jest w trakcie ładowania...</p>
        <p>Sprawdzanie połączenia z serwerem: <span style={{ color: count > 0 ? 'green' : 'orange' }}>{count > 0 ? 'OK' : 'Oczekiwanie...'}</span></p>
        <button 
          onClick={() => setCount(count + 1)}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#2196f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test połączenia
        </button>
      </div>
    </div>
  );
}

export default App;
