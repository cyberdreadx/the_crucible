// API Configuration
// In production, this will be set by the build process or environment
const API_HOST = import.meta.env.VITE_API_HOST || 'localhost';
const API_PORT = import.meta.env.VITE_API_PORT || '8080';

export const API_BASE = `http://${API_HOST}:${API_PORT}`;
export const WS_BASE = `ws://${API_HOST}:${API_PORT}`;
