// API Configuration
// In production, use the same host as the page (via reverse proxy)
// In development, use localhost
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

const API_HOST = import.meta.env.VITE_API_HOST || (isProduction ? window.location.hostname : 'localhost');
const API_PORT = import.meta.env.VITE_API_PORT || (isProduction ? '' : '8080');
const API_PROTOCOL = isProduction ? 'https' : 'http';
const WS_PROTOCOL = isProduction ? 'wss' : 'ws';

// In production with nginx proxy, we don't need a port (nginx handles it)
export const API_BASE = API_PORT ? `${API_PROTOCOL}://${API_HOST}:${API_PORT}` : `${API_PROTOCOL}://${API_HOST}`;
export const WS_BASE = API_PORT ? `${WS_PROTOCOL}://${API_HOST}:${API_PORT}` : `${WS_PROTOCOL}://${API_HOST}`;
