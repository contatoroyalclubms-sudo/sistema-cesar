import axios from 'axios';

// Configuração da URL da API baseada no ambiente
const getApiBaseUrl = () => {
  // Detectar se está em produção
  const isProd = import.meta.env.PROD || window.location.hostname.includes('railway.app');
  
  if (isProd) {
    // Em produção, usar URL completa do backend
    const backendUrl = import.meta.env.VITE_API_URL || 
                      'https://backend-painel-universal-production.up.railway.app';
    console.log('🚀 Modo produção - URL Backend:', backendUrl);
    return backendUrl;
  } else {
    // Em desenvolvimento, usar proxy local
    console.log('🔧 Modo desenvolvimento - usando proxy local');
    return '';
  }
};

const API_BASE_URL = getApiBaseUrl();

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 segundos timeout
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      message: error.message
    });

    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// Interfaces
export interface LoginRequest {
  cpf: string;
  senha: string;
  codigo_verificacao?: string;
}

export interface Usuario {
  id?: number;
  cpf: string;
  nome: string;
  email: string;
  telefone?: string;
  tipo: 'admin' | 'promoter' | 'cliente';
  empresa_id: number;
  ativo?: boolean;
  criado_em?: string;
  ultimo_login?: string;
  empresa?: {
    id: number;
    nome: string;
  };
}

export interface Token {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export interface Empresa {
  id?: number;
  nome: string;
  cnpj: string;
  email: string;
  telefone?: string;
  endereco?: string;
  ativa?: boolean;
}

export interface Evento {
  id?: number;
  nome: string;
  descricao?: string;
  data_evento: string;
  local: string;
  endereco?: string;
  limite_idade?: number;
  capacidade_maxima?: number;
  status?: string;
  empresa_id: number;
  criador_id?: number;
}

// Serviços de autenticação
export const authService = {
  async login(data: LoginRequest): Promise<Token> {
    const response = await api.post('/api/auth/login', data);
    return response.data;
  },

  async register(data: {
    cpf: string;
    nome: string;
    email: string;
    telefone?: string;
    senha: string;
    tipo?: 'admin' | 'promoter' | 'cliente';
    empresa_id?: number;
  }): Promise<Usuario> {
    const userData = {
      ...data,
      tipo: data.tipo || 'cliente',
      empresa_id: data.empresa_id || 1
    };
    const response = await api.post('/api/usuarios/', userData);
    return response.data;
  },

  async getProfile(): Promise<Usuario> {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
  }
};

// Serviços de usuários
export const usuarioService = {
  async getAll(): Promise<Usuario[]> {
    const response = await api.get('/api/usuarios/');
    return response.data;
  },

  async getById(id: number): Promise<Usuario> {
    const response = await api.get(`/api/usuarios/${id}`);
    return response.data;
  },

  async create(usuarioData: any): Promise<Usuario> {
    const response = await api.post('/api/usuarios/', usuarioData);
    return response.data;
  },

  async update(id: number, usuarioData: any): Promise<Usuario> {
    const response = await api.put(`/api/usuarios/${id}`, usuarioData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/usuarios/${id}`);
  },

  async toggleStatus(id: number, ativo: boolean): Promise<Usuario> {
    const response = await api.patch(`/api/usuarios/${id}/status`, { ativo });
    return response.data;
  }
};

// Serviços de empresas
export const empresaService = {
  async getAll(): Promise<Empresa[]> {
    const response = await api.get('/api/empresas/');
    return response.data;
  },

  async getById(id: number): Promise<Empresa> {
    const response = await api.get(`/api/empresas/${id}`);
    return response.data;
  },

  async create(empresaData: Empresa): Promise<Empresa> {
    const response = await api.post('/api/empresas/', empresaData);
    return response.data;
  },

  async update(id: number, empresaData: Empresa): Promise<Empresa> {
    const response = await api.put(`/api/empresas/${id}`, empresaData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/empresas/${id}`);
  }
};

// Serviços de eventos
export const eventoService = {
  async getAll(): Promise<Evento[]> {
    const response = await api.get('/api/eventos/');
    return response.data;
  },

  async getById(id: number): Promise<Evento> {
    const response = await api.get(`/api/eventos/${id}`);
    return response.data;
  },

  async create(eventoData: Evento): Promise<Evento> {
    const response = await api.post('/api/eventos/', eventoData);
    return response.data;
  },

  async update(id: number, eventoData: Evento): Promise<Evento> {
    const response = await api.put(`/api/eventos/${id}`, eventoData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/eventos/${id}`);
  }
};

// Serviços de dashboard
export const dashboardService = {
  async getStats(): Promise<any> {
    const response = await api.get('/api/dashboard/avancado');
    return response.data;
  },

  async getEventosProximos(): Promise<any[]> {
    const response = await api.get('/api/eventos/');
    return response.data;
  },

  async getResumoFinanceiro(): Promise<any> {
    const response = await api.get('/api/dashboard/avancado');
    return response.data;
  }
};

// Serviços de checkin
export const checkinService = {
  async checkinCPF(cpf: string, eventoId: number, validacaoCpf?: string): Promise<any> {
    const response = await api.post('/api/checkins/', {
      cpf: cpf.replace(/\D/g, ''),
      evento_id: eventoId,
      validacao_cpf: validacaoCpf
    });
    return response.data;
  },

  async getCheckins(eventoId: number): Promise<any[]> {
    const response = await api.get(`/api/checkins/evento/${eventoId}`);
    return response.data;
  }
};

// Serviços de listas
export const listaService = {
  async getAll(eventoId?: number): Promise<any[]> {
    const params = eventoId ? { evento_id: eventoId } : {};
    const response = await api.get('/api/listas/', { params });
    return response.data;
  },

  async create(listaData: any): Promise<any> {
    const response = await api.post('/api/listas/', listaData);
    return response.data;
  },

  async update(id: number, listaData: any): Promise<any> {
    const response = await api.put(`/api/listas/${id}`, listaData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/listas/${id}`);
  },

  async importarConvidados(listaId: number, convidados: any[]): Promise<any> {
    const response = await api.post(`/api/listas/${listaId}/convidados/import`, { convidados });
    return response.data;
  }
};

// Serviços de gamificação
export const gamificacaoService = {
  async obterRanking(filtros?: any): Promise<any[]> {
    const response = await api.get('/api/gamificacao/ranking', { params: filtros });
    return response.data;
  },

  async obterDashboard(eventoId?: number): Promise<any> {
    const response = await api.get('/api/gamificacao/dashboard', { 
      params: eventoId ? { evento_id: eventoId } : {} 
    });
    return response.data;
  },

  async criarConquista(conquista: any): Promise<any> {
    const response = await api.post('/api/gamificacao/conquistas', conquista);
    return response.data;
  },

  async verificarConquistas(promoterId: number): Promise<any> {
    const response = await api.post(`/api/gamificacao/verificar-conquistas/${promoterId}`);
    return response.data;
  }
};

// Serviços de financeiro
export const financeiroService = {
  async obterDashboard(eventoId?: number): Promise<any> {
    const params = eventoId ? { evento_id: eventoId } : {};
    const response = await api.get('/api/financeiro/dashboard', { params });
    return response.data;
  },

  async criarMovimentacao(movimentacao: any): Promise<any> {
    const response = await api.post('/api/financeiro/movimentacoes', movimentacao);
    return response.data;
  },

  async obterMovimentacoes(eventoId?: number): Promise<any[]> {
    const params = eventoId ? { evento_id: eventoId } : {};
    const response = await api.get('/api/financeiro/movimentacoes', { params });
    return response.data;
  }
};

// Setup inicial do sistema
export const setupInicial = async (): Promise<any> => {
  const response = await api.post('/setup-inicial');
  return response.data;
};

export default api;
