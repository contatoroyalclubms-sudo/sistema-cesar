import api from '@/lib/api';

// ====== INTERFACES ======

export interface Impressora {
  id: number;
  nome: string;
  ip: string;
  porta: number;
  tipo: 'termica' | 'fiscal' | 'etiqueta' | 'matricial' | 'laser' | 'pos';
  modelo: 'Epson TM-T20' | 'Epson TM-T20x' | 'Bematech MP-4200' | 'Elgin i8' | 'Elgin i9' | 'Genérica';
  status: 'online' | 'offline' | 'erro' | 'manutencao' | 'pausada';
  localizacao?: string;
  evento_id?: number;
  empresa_id?: number;
  
  // Configurações específicas
  largura_papel: number;
  caracteres_linha: number;
  suporta_guilhotina: boolean;
  suporta_qrcode: boolean;
  suporta_codigo_barras: boolean;
  driver?: string;
  configuracoes_json?: Record<string, any>;
  
  ativa: boolean;
  total_impressoes: number;
  ultima_impressao?: string;
  ultima_verificacao?: string;
  criada_em: string;
  atualizada_em?: string;
}

export interface ImpressoraCreate {
  nome: string;
  ip: string;
  porta?: number;
  tipo?: 'termica' | 'fiscal' | 'etiqueta' | 'matricial' | 'laser' | 'pos';
  modelo?: 'Epson TM-T20' | 'Epson TM-T20x' | 'Bematech MP-4200' | 'Elgin i8' | 'Elgin i9' | 'Genérica';
  localizacao?: string;
  evento_id?: number;
  empresa_id?: number;
  largura_papel?: number;
  caracteres_linha?: number;
  suporta_guilhotina?: boolean;
  suporta_qrcode?: boolean;
  suporta_codigo_barras?: boolean;
  driver?: string;
  configuracoes_json?: Record<string, any>;
  ativa?: boolean;
}

export interface ImpressoraUpdate {
  nome?: string;
  ip?: string;
  porta?: number;
  tipo?: 'termica' | 'fiscal' | 'etiqueta' | 'matricial' | 'laser' | 'pos';
  modelo?: 'Epson TM-T20' | 'Epson TM-T20x' | 'Bematech MP-4200' | 'Elgin i8' | 'Elgin i9' | 'Genérica';
  status?: 'online' | 'offline' | 'erro' | 'manutencao' | 'pausada';
  localizacao?: string;
  evento_id?: number;
  empresa_id?: number;
  largura_papel?: number;
  caracteres_linha?: number;
  suporta_guilhotina?: boolean;
  suporta_qrcode?: boolean;
  suporta_codigo_barras?: boolean;
  driver?: string;
  configuracoes_json?: Record<string, any>;
  ativa?: boolean;
}

export interface ImpressoraInteligente {
  id: number;
  nome: string;
  impressora_id: number;
  tipo_impressao: string;
  local_origem?: string;
  categoria_produto?: string;
  prioridade: number;
  ativo: boolean;
  imprimir_logo: boolean;
  numero_vias: number;
  template_id?: number;
  hora_inicio?: string;
  hora_fim?: string;
  dias_semana?: string;
  evento_id?: number;
  criado_em: string;
}

export interface ImpressoraInteligenteCreate {
  nome: string;
  impressora_id: number;
  tipo_impressao: string;
  local_origem?: string;
  categoria_produto?: string;
  prioridade?: number;
  ativo?: boolean;
  imprimir_logo?: boolean;
  numero_vias?: number;
  template_id?: number;
  hora_inicio?: string;
  hora_fim?: string;
  dias_semana?: string;
  evento_id?: number;
}

export interface TemplateImpressao {
  id: number;
  nome: string;
  tipo: string;
  cabecalho?: string;
  corpo?: string;
  rodape?: string;
  fonte_tamanho?: string;
  negrito_titulo: boolean;
  centralizar_logo: boolean;
  separadores: boolean;
  incluir_qrcode: boolean;
  qrcode_conteudo?: string;
  incluir_codigo_barras: boolean;
  codigo_barras_tipo?: string;
  evento_id?: number;
  ativo: boolean;
  criado_em: string;
}

export interface TemplateImpressaoCreate {
  nome: string;
  tipo: string;
  cabecalho?: string;
  corpo?: string;
  rodape?: string;
  fonte_tamanho?: string;
  negrito_titulo?: boolean;
  centralizar_logo?: boolean;
  separadores?: boolean;
  incluir_qrcode?: boolean;
  qrcode_conteudo?: string;
  incluir_codigo_barras?: boolean;
  codigo_barras_tipo?: string;
  evento_id?: number;
  ativo?: boolean;
}

export interface FilaImpressao {
  id: number;
  impressora_id: number;
  tipo_documento: string;
  conteudo: string;
  prioridade: number;
  status: 'pendente' | 'processando' | 'concluido' | 'erro' | 'cancelado';
  tentativas: number;
  max_tentativas: number;
  pedido_id?: number;
  venda_id?: number;
  usuario_id?: number;
  criado_em: string;
  processado_em?: string;
  erro_mensagem?: string;
}

export interface FilaImpressaoCreate {
  impressora_id: number;
  tipo_documento: string;
  conteudo: string;
  prioridade?: number;
  pedido_id?: number;
  venda_id?: number;
  usuario_id?: number;
}

export interface TesteImpressaoRequest {
  impressora_id: number;
  tipo_teste: 'simples' | 'completo' | 'guilhotina' | 'qrcode';
  mensagem_customizada?: string;
}

export interface TesteImpressaoResponse {
  sucesso: boolean;
  impressora_id: number;
  tempo_resposta: number;
  mensagem: string;
  detalhes?: Record<string, any>;
}

export interface StatusImpressoraResponse {
  impressora_id: number;
  nome: string;
  ip: string;
  porta: number;
  status: 'online' | 'offline' | 'erro' | 'manutencao' | 'pausada';
  online: boolean;
  ultima_verificacao?: string;
  mensagem?: string;
}

export interface EquipamentoPDV {
  id: number;
  codigo: string;
  tipo: 'POS' | 'Totem' | 'Tablet' | 'Terminal' | 'Check';
  nome?: string;
  perfil_venda?: string;
  impressora_padrao_id?: number;
  operador_id?: number;
  licenciado: boolean;
  data_licenca_inicio?: string;
  data_licenca_fim?: string;
  status: string;
  localizacao?: string;
  evento_id?: number;
  empresa_id?: number;
  versao_software?: string;
  ultima_sincronizacao?: string;
  criado_em: string;
}

export interface OperadorPDV {
  id: number;
  nome: string;
  cpf?: string;
  codigo_acesso?: string;
  comissao_percentual: number;
  comissao_fixa: number;
  pode_cancelar: boolean;
  pode_dar_desconto: boolean;
  desconto_maximo: number;
  ativo: boolean;
  evento_id?: number;
  empresa_id?: number;
  total_vendas: number;
  valor_total_vendido: number;
  criado_em: string;
}

// ====== SERVIÇO DE API ======

export const impressoraService = {
  // ====== IMPRESSORAS ======
  
  async listarImpressoras(evento_id?: number): Promise<Impressora[]> {
    try {
      const params = evento_id ? { evento_id } : {};
      const response = await api.get('/api/impressoras/', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar impressoras:', error);
      throw error;
    }
  },

  async obterImpressora(id: number): Promise<Impressora> {
    try {
      const response = await api.get(`/api/impressoras/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao obter impressora:', error);
      throw error;
    }
  },

  async criarImpressora(data: ImpressoraCreate): Promise<Impressora> {
    try {
      const response = await api.post('/api/impressoras/', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar impressora:', error);
      throw error;
    }
  },

  async atualizarImpressora(id: number, data: ImpressoraUpdate): Promise<Impressora> {
    try {
      const response = await api.put(`/api/impressoras/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar impressora:', error);
      throw error;
    }
  },

  async deletarImpressora(id: number): Promise<void> {
    try {
      await api.delete(`/api/impressoras/${id}`);
    } catch (error) {
      console.error('Erro ao deletar impressora:', error);
      throw error;
    }
  },

  async verificarStatus(id: number): Promise<StatusImpressoraResponse> {
    try {
      const response = await api.post(`/api/impressoras/${id}/status`);
      return response.data;
    } catch (error) {
      console.error('Erro ao verificar status:', error);
      throw error;
    }
  },

  async enviarTeste(data: TesteImpressaoRequest): Promise<TesteImpressaoResponse> {
    try {
      const response = await api.post(`/api/impressoras/${data.impressora_id}/teste`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao enviar teste:', error);
      throw error;
    }
  },

  // ====== ROTEAMENTO INTELIGENTE ======

  async listarRoteamentos(evento_id?: number): Promise<ImpressoraInteligente[]> {
    try {
      const params = evento_id ? { evento_id } : {};
      const response = await api.get('/api/impressoras/roteamento', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar roteamentos:', error);
      throw error;
    }
  },

  async criarRoteamento(data: ImpressoraInteligenteCreate): Promise<ImpressoraInteligente> {
    try {
      const response = await api.post('/api/impressoras/roteamento', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar roteamento:', error);
      throw error;
    }
  },

  async atualizarRoteamento(id: number, data: Partial<ImpressoraInteligenteCreate>): Promise<ImpressoraInteligente> {
    try {
      const response = await api.put(`/api/impressoras/roteamento/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar roteamento:', error);
      throw error;
    }
  },

  async deletarRoteamento(id: number): Promise<void> {
    try {
      await api.delete(`/api/impressoras/roteamento/${id}`);
    } catch (error) {
      console.error('Erro ao deletar roteamento:', error);
      throw error;
    }
  },

  // ====== TEMPLATES ======

  async listarTemplates(evento_id?: number): Promise<TemplateImpressao[]> {
    try {
      const params = evento_id ? { evento_id } : {};
      const response = await api.get('/api/impressoras/templates', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar templates:', error);
      throw error;
    }
  },

  async criarTemplate(data: TemplateImpressaoCreate): Promise<TemplateImpressao> {
    try {
      const response = await api.post('/api/impressoras/templates', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar template:', error);
      throw error;
    }
  },

  async atualizarTemplate(id: number, data: Partial<TemplateImpressaoCreate>): Promise<TemplateImpressao> {
    try {
      const response = await api.put(`/api/impressoras/templates/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar template:', error);
      throw error;
    }
  },

  async deletarTemplate(id: number): Promise<void> {
    try {
      await api.delete(`/api/impressoras/templates/${id}`);
    } catch (error) {
      console.error('Erro ao deletar template:', error);
      throw error;
    }
  },

  // ====== FILA DE IMPRESSÃO ======

  async listarFila(impressora_id?: number, status?: string): Promise<FilaImpressao[]> {
    try {
      const params: Record<string, any> = {};
      if (impressora_id) params.impressora_id = impressora_id;
      if (status) params.status = status;
      
      const response = await api.get('/api/impressoras/fila', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar fila:', error);
      throw error;
    }
  },

  async adicionarFila(data: FilaImpressaoCreate): Promise<FilaImpressao> {
    try {
      const response = await api.post('/api/impressoras/fila', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao adicionar à fila:', error);
      throw error;
    }
  },

  async processarFila(impressora_id?: number): Promise<{ processados: number; erros: number }> {
    try {
      const data = impressora_id ? { impressora_id } : {};
      const response = await api.post('/api/impressoras/fila/processar', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao processar fila:', error);
      throw error;
    }
  },

  async cancelarJob(job_id: number): Promise<void> {
    try {
      await api.delete(`/api/impressoras/fila/${job_id}`);
    } catch (error) {
      console.error('Erro ao cancelar job:', error);
      throw error;
    }
  },

  // ====== LOGS ======

  async listarLogs(impressora_id?: number, limit: number = 100): Promise<any[]> {
    try {
      const params: Record<string, any> = { limit };
      if (impressora_id) params.impressora_id = impressora_id;
      
      const response = await api.get('/api/impressoras/logs', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar logs:', error);
      throw error;
    }
  },

  // ====== EQUIPAMENTOS PDV ======

  async listarEquipamentos(evento_id?: number): Promise<EquipamentoPDV[]> {
    try {
      const params = evento_id ? { evento_id } : {};
      const response = await api.get('/api/impressoras/equipamentos-pdv', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar equipamentos:', error);
      throw error;
    }
  },

  async criarEquipamento(data: Partial<EquipamentoPDV>): Promise<EquipamentoPDV> {
    try {
      const response = await api.post('/api/impressoras/equipamentos-pdv', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar equipamento:', error);
      throw error;
    }
  },

  async atualizarEquipamento(id: number, data: Partial<EquipamentoPDV>): Promise<EquipamentoPDV> {
    try {
      const response = await api.put(`/api/impressoras/equipamentos-pdv/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar equipamento:', error);
      throw error;
    }
  },

  // ====== OPERADORES PDV ======

  async listarOperadores(evento_id?: number): Promise<OperadorPDV[]> {
    try {
      const params = evento_id ? { evento_id } : {};
      const response = await api.get('/api/impressoras/operadores-pdv', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar operadores:', error);
      throw error;
    }
  },

  async criarOperador(data: Partial<OperadorPDV>): Promise<OperadorPDV> {
    try {
      const response = await api.post('/api/impressoras/operadores-pdv', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar operador:', error);
      throw error;
    }
  },

  async atualizarOperador(id: number, data: Partial<OperadorPDV>): Promise<OperadorPDV> {
    try {
      const response = await api.put(`/api/impressoras/operadores-pdv/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar operador:', error);
      throw error;
    }
  },

  // ====== UTILITÁRIOS ======

  async imprimirCupom(impressora_id: number, venda: any, template_id?: number): Promise<FilaImpressao> {
    try {
      const conteudo = JSON.stringify(venda);
      const data: FilaImpressaoCreate = {
        impressora_id,
        tipo_documento: 'cupom',
        conteudo,
        prioridade: 10,
        venda_id: venda.id
      };
      
      return await this.adicionarFila(data);
    } catch (error) {
      console.error('Erro ao imprimir cupom:', error);
      throw error;
    }
  },

  async imprimirComanda(impressora_id: number, pedido: any): Promise<FilaImpressao> {
    try {
      const conteudo = JSON.stringify(pedido);
      const data: FilaImpressaoCreate = {
        impressora_id,
        tipo_documento: 'comanda',
        conteudo,
        prioridade: 5,
        pedido_id: pedido.id
      };
      
      return await this.adicionarFila(data);
    } catch (error) {
      console.error('Erro ao imprimir comanda:', error);
      throw error;
    }
  },

  async imprimirRelatorio(impressora_id: number, relatorio: any): Promise<FilaImpressao> {
    try {
      const conteudo = typeof relatorio === 'string' ? relatorio : JSON.stringify(relatorio);
      const data: FilaImpressaoCreate = {
        impressora_id,
        tipo_documento: 'relatorio',
        conteudo,
        prioridade: 1
      };
      
      return await this.adicionarFila(data);
    } catch (error) {
      console.error('Erro ao imprimir relatório:', error);
      throw error;
    }
  }
};

export default impressoraService;