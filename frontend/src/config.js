// config.js
// La URL del backend se inyecta en tiempo de build con REACT_APP_API_BASE_URL.
// En desarrollo local cae por defecto a localhost:8000.
export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
export const UPLOADS_BASE_URL = `${API_BASE_URL}/uploads`;
