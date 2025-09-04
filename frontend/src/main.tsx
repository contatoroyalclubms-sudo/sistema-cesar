import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import { Toaster } from "@/components/ui/toaster"

// Tratamento global de erros JSON
const originalJSONParse = JSON.parse;
JSON.parse = function(text: string, reviver?: any) {
  try {
    return originalJSONParse.call(this, text, reviver);
  } catch (error) {
    console.error('Erro global JSON.parse:', error, 'Text:', text);
    // Retornar um objeto vazio em vez de quebrar a aplicação
    return {};
  }
};

// Tratamento global de erros não capturados
window.addEventListener('error', (event) => {
  if (event.error && event.error.message && event.error.message.includes('JSON')) {
    console.error('Erro JSON global capturado:', event.error);
    event.preventDefault(); // Previne que o erro quebre a aplicação
  }
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
    <Toaster />
  </StrictMode>,
)
