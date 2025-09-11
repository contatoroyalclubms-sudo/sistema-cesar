import { api, publicApi } from '@/lib/api';
import type { 
  LoginRequest, 
  Token, 
  Usuario,
  Evento,
  EventoCreate,
  Produto,
  ProdutoFormData,
  Venda,
  VendaCreate,
  Checkin,
  Lista,
  DashboardResumo,
  // CheckinRequest removido
  // PaginatedResponse removido
} from '../types';

// Re-exportar tipos para compatibilidade
export type {
  LoginRequest,
  Token,
  Usuario,
  Evento,
  EventoCreate,
  Produto,
  ProdutoFormData,
  Venda,
  VendaCreate,
  Checkin,
  Lista,
  DashboardResumo,
};

// Função utilitária para detectar formato do input
const detectarTipoInput = (input: string): 'email' | 'cpf' => {
  // Verificar se é email (contém @ e formato básico)
  if (input.includes('@') && input.includes('.')) {
    return 'email';
  }
  
  // Verificar se é CPF (11 dígitos, com ou sem formatação)
  const cpfLimpo = input.replace(/\D/g, '');
  if (cpfLimpo.length === 11) {
    return 'cpf';
  }
  
  // Se não tem formato claro, assumir email se contém @
  return input.includes('@') ? 'email' : 'cpf';
};

// Função para buscar CPF por email
const buscarCpfPorEmail = async (email: string): Promise<string | null> => {
  try {
    console.log('🔍 Buscando CPF para email:', email);
    
    // Tentar buscar usuário por email usando endpoint público
    const response = await publicApi.get('/api/usuarios/buscar-por-email', {
      params: { email }
    });
    
    if (response.data && response.data.cpf) {
      console.log('✅ CPF encontrado para email');
      return response.data.cpf;
    }
    
    return null;
  } catch (error: any) {
    console.warn('⚠️ Não foi possível buscar CPF por email:', error.message);
    
    // Se o endpoint não existe, tentar alguns CPFs de teste conhecidos
    const testUsers: Record<string, string> = {
      'admin@teste.com': '00000000000',
      'admin@admin.com': '00000000000',
      'promoter@teste.com': '11111111111',
      'promoter@promoter.com': '11111111111',
      'cliente@teste.com': '22222222222',
      'cliente@cliente.com': '22222222222'
    };
    
    if (testUsers[email.toLowerCase()]) {
      console.log('✅ CPF encontrado via mapeamento de teste');
      return testUsers[email.toLowerCase()];
    }
    
    return null;
  }
};

// Serviços de Autenticação
export const authService = {
  async login(data: LoginRequest): Promise<Token> {
    console.log('🔐 Iniciando processo de login...');
    
    // Detectar se o input é email ou CPF
    const tipoInput = detectarTipoInput(data.cpf);
    console.log('🔍 Tipo de input detectado:', tipoInput);
    
    let cpfParaLogin = data.cpf;
    
    // Se for email, buscar o CPF correspondente
    if (tipoInput === 'email') {
      console.log('📧 Email detectado, buscando CPF correspondente...');
      const cpfEncontrado = await buscarCpfPorEmail(data.cpf);
      
      if (!cpfEncontrado) {
        throw new Error('Email não encontrado no sistema ou CPF não associado');
      }
      
      cpfParaLogin = cpfEncontrado;
      console.log('✅ CPF obtido para login');
    } else {
      // Se for CPF, limpar formatação
      cpfParaLogin = data.cpf.replace(/\D/g, '');
      console.log('✅ CPF formatado para login');
    }
    
    // Fazer login com CPF
    console.log('🚀 Enviando requisição de login com CPF...');
    const response = await publicApi.post('/api/auth/login', {
      cpf: cpfParaLogin,
      senha: data.senha
    });
    
    console.log('✅ Login bem-sucedido!');
    return response.data;
  },

  async register(data: {
    cpf: string;
    // CheckinRequest removido
    // PaginatedResponse removido
    telefone?: string;
    senha: string;
    tipo?: 'admin' | 'promoter' | 'cliente';
  }): Promise<Usuario> {
    const userData = {
      ...data,
      tipo: data.tipo || 'cliente'
    };
    const response = await publicApi.post('/api/auth/register', userData);
    return response.data;
  },

  async getProfile(): Promise<Usuario> {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
  },

  async healthCheck(): Promise<any> {
    const response = await publicApi.get('/healthz');
    return response.data;
  }
};

// Serviços de Usuários
export const usuarioService = {
  async getAll(): Promise<Usuario[]> {
    const response = await api.get('/api/usuarios/');
    return response.data;
  },

  async getById(id: number): Promise<Usuario> {
    const response = await api.get(`/api/usuarios/${id}`);
    return response.data;
  },

  async create(usuarioData: Partial<Usuario>): Promise<Usuario> {
    const response = await api.post('/api/usuarios/', usuarioData);
    return response.data;
  },

  async update(id: number, usuarioData: Partial<Usuario>): Promise<Usuario> {
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

// Serviços de Eventos
export const eventoService = {
  async getAll(): Promise<Evento[]> {
    const response = await api.get('/api/eventos/');
    return response.data;
  },

  async getById(id: number): Promise<Evento> {
    const response = await api.get(`/api/eventos/${id}`);
    return response.data;
  },

  async create(eventoData: EventoCreate): Promise<Evento> {
    const response = await api.post('/api/eventos/', eventoData);
    return response.data;
  },

  async update(id: number, eventoData: Partial<Evento>): Promise<Evento> {
    const response = await api.put(`/api/eventos/${id}`, eventoData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/eventos/${id}`);
  },

  async getEventosProximos(): Promise<Evento[]> {
    const response = await api.get('/api/eventos/?proximos=true');
    return response.data;
  }
};

// Serviços de Produtos
export const produtoService = {
  async getAll(): Promise<Produto[]> {
    const response = await api.get('/api/produtos/');
    return response.data;
  },

  async getById(id: number): Promise<Produto> {
    const response = await api.get(`/api/produtos/${id}`);
    return response.data;
  },

  async create(produtoData: ProdutoFormData, imageFile?: File): Promise<Produto> {
    let produto: Produto;
    
    // Primeiro, criar o produto
    const response = await api.post('/api/produtos/', {
      nome: produtoData.nome,
      codigo: produtoData.codigo_interno,
      categoria: produtoData.categoria,
      tipo: produtoData.tipo,
      valor: produtoData.preco,
      descricao: produtoData.descricao,
      estoque: produtoData.estoque_atual,
      estoque_minimo: produtoData.estoque_minimo,
      estoque_maximo: produtoData.estoque_maximo,
      controla_estoque: produtoData.controla_estoque,
      status: produtoData.status,
    });
    
    produto = response.data;

    // Se há imagem, fazer upload separado
    if (imageFile && produto.id) {
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const uploadResponse = await api.post(`/api/produtos/${produto.id}/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      produto = uploadResponse.data;
    }

    return produto;
  },

  async update(id: number, produtoData: ProdutoFormData, imageFile?: File): Promise<Produto> {
    let produto: Produto;
    
    // Primeiro, atualizar o produto
    const response = await api.put(`/api/produtos/${id}`, {
      nome: produtoData.nome,
      codigo: produtoData.codigo_interno,
      categoria: produtoData.categoria,
      tipo: produtoData.tipo,
      valor: produtoData.preco,
      descricao: produtoData.descricao,
      estoque: produtoData.estoque_atual,
      estoque_minimo: produtoData.estoque_minimo,
      estoque_maximo: produtoData.estoque_maximo,
      controla_estoque: produtoData.controla_estoque,
      status: produtoData.status,
    });
    
    produto = response.data;

    // Se há nova imagem, fazer upload
    if (imageFile) {
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const uploadResponse = await api.post(`/api/produtos/${id}/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      produto = uploadResponse.data;
    }

    return produto;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/produtos/${id}`);
  },

  async getCategorias(): Promise<string[]> {
    const response = await api.get('/api/produtos/categorias');
    return response.data;
  }
};

// Serviços de Vendas
export const vendaService = {
  async getAll(eventoId?: number): Promise<Venda[]> {
    const params = eventoId ? { evento_id: eventoId } : {};
    const response = await api.get('/api/vendas/', { params });
    return response.data;
  },

  async getById(id: number): Promise<Venda> {
    const response = await api.get(`/api/vendas/${id}`);
    return response.data;
  },

  async create(vendaData: VendaCreate): Promise<Venda> {
    const response = await api.post('/api/vendas/', vendaData);
    return response.data;
  },

  async cancelar(id: number): Promise<Venda> {
    const response = await api.patch(`/api/vendas/${id}/cancelar`);
    return response.data;
  },

  async getRelatorio(eventoId: number, dataInicio?: string, dataFim?: string): Promise<any> {
    const params: any = { evento_id: eventoId };
    if (dataInicio) params.data_inicio = dataInicio;
    if (dataFim) params.data_fim = dataFim;
    
    const response = await api.get('/api/vendas/relatorio', { params });
    return response.data;
  }
};

// Serviços de Check-in
export const checkinService = {
  async checkinCPF(cpf: string, eventoId: number, validacaoCpf?: string): Promise<Checkin> {
    const response = await api.post('/api/checkins/', {
      cpf: cpf.replace(/\D/g, ''),
      evento_id: eventoId,
      validacao_cpf: validacaoCpf
    });
    return response.data;
  },

  async getCheckins(eventoId: number): Promise<Checkin[]> {
    const response = await api.get(`/api/checkins/evento/${eventoId}`);
    return response.data;
  },

  async getRelatorio(eventoId: number): Promise<any> {
    const response = await api.get(`/api/checkins/relatorio/${eventoId}`);
    return response.data;
  }
};

// Serviços de Listas
export const listaService = {
  async getAll(eventoId?: number): Promise<Lista[]> {
    const params = eventoId ? { evento_id: eventoId } : {};
    const response = await api.get('/api/listas/', { params });
    return response.data;
  },

  async create(listaData: Omit<Lista, 'id'>): Promise<Lista> {
    const response = await api.post('/api/listas/', listaData);
    return response.data;
  },

  async update(id: number, listaData: Partial<Lista>): Promise<Lista> {
    const response = await api.put(`/api/listas/${id}`, listaData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/listas/${id}`);
  }
};

// Serviços de Dashboard
export const dashboardService = {
  async getResumo(): Promise<DashboardResumo> {
    const response = await api.get('/api/dashboard/avancado');
    return response.data;
  },

  async getMetricas(eventoId?: number): Promise<any> {
    const params = eventoId ? { evento_id: eventoId } : {};
    const response = await api.get('/api/dashboard/avancado', { params });
    return response.data;
  },

  async getAnalytics(periodo: string = '30d'): Promise<any> {
    const response = await api.get('/api/dashboard/avancado', { 
      params: { periodo } 
    });
    return response.data;
  }
};

// Serviços de Upload
export const uploadService = {
  async uploadImage(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  async uploadFile(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/upload/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }
};

// Exportar todos os serviços
export const apiService = {
  auth: authService,
  usuarios: usuarioService,
  eventos: eventoService,
  produtos: produtoService,
  vendas: vendaService,
  checkins: checkinService,
  listas: listaService,
  dashboard: dashboardService,
  upload: uploadService
};
