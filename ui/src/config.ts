// API Configuration
// In production, nginx proxies /api and /ws to backend - no port needed
// In development, connect directly to backend port
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

const API_HOST = import.meta.env.VITE_API_HOST || window.location.hostname;
const API_PORT = import.meta.env.VITE_API_PORT || (isProduction ? '' : '8080');
const API_PROTOCOL = window.location.protocol === 'https:' ? 'https' : 'http';
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss' : 'ws';

// In production, nginx proxies - no port. In dev, include port.
export const API_BASE = API_PORT ? `${API_PROTOCOL}://${API_HOST}:${API_PORT}` : `${API_PROTOCOL}://${API_HOST}`;
export const WS_BASE = API_PORT ? `${WS_PROTOCOL}://${API_HOST}:${API_PORT}` : `${WS_PROTOCOL}://${API_HOST}`;
