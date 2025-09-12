import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003';

const meepApi = axios.create({
  baseURL: `${API_BASE}/api/meep`,
  headers: {
    'Content-Type': 'application/json',
  },
});

meepApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface MEEPEvento {
  id: number;
  meep_id: string;
  nome: string;
  data_inicio: string;
  data_fim: string;
  local?: string;
  cidade?: string;
  estado?: string;
  total_inscritos: number;
  total_presentes: number;
  total_vendas: number;
  taxa_conversao: number;
  sincronizado: boolean;
  ultima_sincronizacao: string;
}

export const meepService = {
  async getEventos() {
    const response = await meepApi.get<MEEPEvento[]>('/eventos');
    return response.data;
  },

  async sincronizar() {
    const response = await meepApi.post('/sync', { force: false });
    return response.data;
  },

  async getSyncStatus() {
    const response = await meepApi.get('/sync/status');
    return response.data;
  }
};
