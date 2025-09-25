import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  // StrictMode removido temporariamente para evitar execução dupla em desenvolvimento
  // <React.StrictMode>
    <App />
  // </React.StrictMode>
);