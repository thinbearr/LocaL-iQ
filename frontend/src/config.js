// LocaL-iQ Centralized API Configuration
// Automatically defaults to production backend (https://local-iq.onrender.com) in production builds
// Defaults to http://127.0.0.1:5000 during local development (npm run dev)
// Overrideable by setting VITE_API_URL environment variable during build

const defaultProductionUrl = 'https://local-iq.onrender.com';
const defaultLocalUrl = 'http://127.0.0.1:5000';

const rawUrl = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? defaultLocalUrl : defaultProductionUrl);

export const API_BASE_URL = rawUrl.replace(/\/$/, '');
