// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css'; // Upewnij się, że ten plik istnieje

// Najprostszy komponent App
function App() {
  const [count, setCount] = React.useState(0);
  
  return (
    <div style={{ 
      maxWidth: '600px', 
      margin: '0 auto', 
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
      textAlign: 'center'
    }}>
      <h1 style={{ color: '#2196F3' }}>Asystent Prawny</h1>
      <div style={{ 
        border: '1px solid #ccc', 
        borderRadius: '8px', 
        padding: '20px',
        backgroundColor: '#f9f9f9'
      }}>
        <p>React z npm działa! Kliknięcia: {count}</p>
        <button 
          onClick={() => setCount(count + 1)}
          style={{
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Kliknij mnie
        </button>
      </div>
    </div>
  );
}

// Znajdź element root i renderuj do niego
const rootElement = document.getElementById('root');
if (rootElement) {
  console.log('Znaleziono element root, rozpoczynam renderowanie React');
  ReactDOM.render(<App />, rootElement);
  console.log('Zakończono renderowanie React');
} else {
  console.error('Nie znaleziono elementu root!');
}