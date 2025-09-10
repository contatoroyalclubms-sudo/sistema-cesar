import axios from 'axios';

// API URL configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  login: (cpf: string, senha: string) => 
    api.post('/auth/login', { cpf, senha }),
  
  register: (data: any) => 
    api.post('/auth/register', data),
  
  refreshToken: () => 
    api.post('/auth/refresh'),
  
  verifyToken: () => 
    api.get('/auth/verify-token'),
  
  logout: () => 
    api.post('/auth/logout'),
};

// Eventos endpoints
export const eventosAPI = {
  list: () => api.get('/eventos'),
  get: (id: number) => api.get(`/eventos/${id}`),
  create: (data: any) => api.post('/eventos', data),
  update: (id: number, data: any) => api.put(`/eventos/${id}`, data),
  delete: (id: number) => api.delete(`/eventos/${id}`),
};

// Usuarios endpoints
export const usuariosAPI = {
  list: () => api.get('/usuarios'),
  get: (id: number) => api.get(`/usuarios/${id}`),
  create: (data: any) => api.post('/usuarios', data),
  update: (id: number, data: any) => api.put(`/usuarios/${id}`, data),
  delete: (id: number) => api.delete(`/usuarios/${id}`),
  me: () => api.get('/usuarios/me'),
};

// Produtos endpoints
export const produtosAPI = {
  list: () => api.get('/produtos'),
  get: (id: number) => api.get(`/produtos/${id}`),
  create: (data: any) => api.post('/produtos', data),
  update: (id: number, data: any) => api.put(`/produtos/${id}`, data),
  delete: (id: number) => api.delete(`/produtos/${id}`),
};

// PDV endpoints
export const pdvAPI = {
  createVenda: (data: any) => api.post('/pdv/vendas', data),
  getVendas: () => api.get('/pdv/vendas'),
  getVenda: (id: number) => api.get(`/pdv/vendas/${id}`),
  cancelVenda: (id: number) => api.post(`/pdv/vendas/${id}/cancel`),
};

// Checkin endpoints
export const checkinAPI = {
  check: (data: any) => api.post('/checkin', data),
  list: (eventoId: number) => api.get(`/checkin/evento/${eventoId}`),
  stats: (eventoId: number) => api.get(`/checkin/evento/${eventoId}/stats`),
};

// Dashboard endpoints
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRevenue: () => api.get('/dashboard/revenue'),
  getEvents: () => api.get('/dashboard/events'),
  getRecent: () => api.get('/dashboard/recent'),
};

// Export default
export default api;