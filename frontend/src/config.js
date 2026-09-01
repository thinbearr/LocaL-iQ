// LocaL-iQ Centralized API Configuration
// Reads VITE_API_URL from environment variables in production (e.g. https://local-iq.onrender.com)
// Defaults to http://127.0.0.1:5000 for local desktop development

export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000').replace(/\/$/, '');
