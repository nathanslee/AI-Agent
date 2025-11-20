import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API functions
export const authAPI = {
  signup: (email: string, password: string) =>
    api.post('/api/auth/signup', { email, password }),

  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),

  getMe: () =>
    api.get('/api/auth/me'),
};

export const databaseAPI = {
  list: () =>
    api.get('/api/databases'),

  create: (description: string) =>
    api.post('/api/databases/create', { description }),

  createWithSchema: (schema: any) =>
    api.post('/api/databases/create-with-schema', { schema }),

  get: (dbId: string) =>
    api.get(`/api/databases/${dbId}`),

  delete: (dbId: string) =>
    api.delete(`/api/databases/${dbId}`),
};

export const dataAPI = {
  getAll: (dbId: string) =>
    api.get(`/api/data/${dbId}`),

  insert: (dbId: string, data: any) =>
    api.post(`/api/data/${dbId}/insert`, { db_id: dbId, data }),

  executeSQL: (dbId: string, sql: string) =>
    api.post('/api/execute/sql', { db_id: dbId, sql }),

  executeNatural: (dbId: string, command: string) =>
    api.post('/api/execute/natural', { db_id: dbId, command }),
};

export const aiAPI = {
  generateSchema: (description: string) =>
    api.post('/api/ai/generate-schema', { description }),

  suggestExpiration: (itemName: string, itemType?: string) =>
    api.post('/api/ai/suggest-expiration', { item_name: itemName, item_type: itemType }),

  categorize: (itemName: string, availableCategories?: string[]) =>
    api.post('/api/ai/categorize', { item_name: itemName, available_categories: availableCategories }),

  getSuggestions: (dbId: string) =>
    api.get(`/api/ai/suggestions/${dbId}`),
};

export const plaidAPI = {
  createLinkToken: () =>
    api.post('/api/plaid/create-link-token'),

  exchangeToken: (publicToken: string) =>
    api.post('/api/plaid/exchange-token', { public_token: publicToken }),

  syncTransactions: (dbId: string, startDate?: string, endDate?: string) =>
    api.post('/api/plaid/sync-transactions', { db_id: dbId, start_date: startDate, end_date: endDate }),
};

export default api;
