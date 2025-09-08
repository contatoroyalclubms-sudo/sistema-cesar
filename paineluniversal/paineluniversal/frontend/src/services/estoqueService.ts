import { api } from './api';

// ================================================================================
// INTERFACES TYPESCRIPT
// ================================================================================

export interface EstoqueProduto {
  id: number;
  produto_id: number;
  local_id: number;
  quantidade_atual: number;
  quantidade_reservada: number;
  quantidade_disponivel: number;
  estoque_minimo: number;
  estoque_maximo: number;
  ponto_pedido: number;
  custo_medio: number;
  ultimo_custo: number;
  giro_estoque: number;
  cobertura_dias: number;
  metodo_controle: string;
  produto?: Produto;
  local_estoque?: LocalEstoque;
}

export interface LocalEstoque {
  id: number;
  empresa_id: number;
  nome: string;
  descricao?: string;
  tipo_local: string;
  endereco?: string;
  responsavel_id?: number;
  ativo: boolean;
  permite_venda: boolean;
  permite_compra: boolean;
  permite_transferencia: boolean;
}

export interface MovimentacaoEstoque {
  id: number;
  estoque_produto_id: number;
  produto_id: number;
  local_origem_id?: number;
  local_destino_id?: number;
  tipo_movimentacao: string;
  quantidade: number;
  valor_unitario?: number;
  valor_total?: number;
  numero_documento?: string;
  observacoes?: string;
  saldo_anterior: number;
  saldo_atual: number;
  data_movimento: string;
  criado_por_id?: number;
  produto?: Produto;
  local_origem?: LocalEstoque;
  local_destino?: LocalEstoque;
  criado_por?: Usuario;
}

export interface Produto {
  id: number;
  codigo: string;
  nome: string;
  descricao?: string;
  categoria?: string;
  preco_venda: number;
  unidade_medida: string;
  ativo: boolean;
}

export interface Usuario {
  id: number;
  nome: string;
  email: string;
}

export interface Fornecedor {
  id: number;
  empresa_id: number;
  nome: string;
  tipo_pessoa: string;
  documento: string;
  email?: string;
  telefone?: string;
  endereco?: string;
  tipo_fornecedor: string;
  status: string;
  observacoes?: string;
}

export interface OrdemCompra {
  id: number;
  empresa_id: number;
  fornecedor_id: number;
  numero: string;
  data_pedido: string;
  data_entrega_prevista?: string;
  data_entrega_real?: string;
  valor_total: number;
  status: string;
  observacoes?: string;
  criado_por_id: number;
  aprovado_por_id?: number;
  itens?: ItemOrdemCompra[];
  fornecedor?: Fornecedor;
}

export interface ItemOrdemCompra {
  id: number;
  ordem_compra_id: number;
  produto_id: number;
  quantidade_pedida: number;
  quantidade_recebida?: number;
  valor_unitario: number;
  valor_total: number;
  observacoes?: string;
  produto?: Produto;
}

export interface AlertaEstoque {
  estoque_baixo: Array<{
    produto_id: number;
    produto_nome: string;
    quantidade_atual: number;
    estoque_minimo: number;
  }>;
  estoque_zerado: Array<{
    produto_id: number;
    produto_nome: string;
    quantidade_atual: number;
  }>;
  estoque_alto: Array<{
    produto_id: number;
    produto_nome: string;
    quantidade_atual: number;
    estoque_maximo: number;
  }>;
}

export interface SugestaoCompra {
  produto_id: number;
  produto_nome: string;
  produto_codigo: string;
  quantidade_atual: number;
  estoque_minimo: number;
  ponto_pedido: number;
  quantidade_sugerida: number;
  ultimo_custo: number;
  valor_total_sugerido: number;
  giro_estoque: number;
  cobertura_dias: number;
}

export interface DashboardEstoque {
  valor_total_estoque: number;
  quantidade_total_produtos: number;
  produtos_com_estoque_baixo: number;
  produtos_sem_estoque: number;
  giro_medio: number;
  produtos_por_categoria: Array<{
    categoria: string;
    quantidade: number;
    valor: number;
  }>;
  movimentacoes_recentes: MovimentacaoEstoque[];
  alertas_criticos: number;
}

// ================================================================================
// FILTROS E PARÂMETROS
// ================================================================================

export interface FiltroEstoque {
  local_id?: number;
  produto_id?: number;
  categoria?: string;
  status?: 'todos' | 'com_estoque' | 'estoque_baixo' | 'sem_estoque';
  page?: number;
  size?: number;
}

export interface FiltroMovimentacao {
  local_id?: number;
  produto_id?: number;
  tipo_movimentacao?: string;
  data_inicio?: string;
  data_fim?: string;
  page?: number;
  size?: number;
}

export interface CriarMovimentacao {
  produto_id: number;
  local_id: number;
  tipo_movimentacao: string;
  quantidade: number;
  valor_unitario?: number;
  numero_documento?: string;
  observacoes?: string;
}

export interface CriarLocalEstoque {
  nome: string;
  descricao?: string;
  tipo_local: string;
  endereco?: string;
  responsavel_id?: number;
  permite_venda: boolean;
  permite_compra: boolean;
  permite_transferencia: boolean;
}

export interface AtualizarEstoque {
  estoque_minimo?: number;
  estoque_maximo?: number;
  ponto_pedido?: number;
  metodo_controle?: string;
}

// ================================================================================
// SERVIÇO DE ESTOQUE
// ================================================================================

class EstoqueService {
  private readonly baseURL = '/api/estoque-controle';

  // POSIÇÕES DE ESTOQUE
  async obterPosicaoEstoque(filtros: FiltroEstoque = {}): Promise<{ itens: EstoqueProduto[]; total: number }> {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`${this.baseURL}/posicao-estoque?${params}`);
    return response.data;
  }

  async obterPosicaoProduto(produtoId: number, localId: number): Promise<EstoqueProduto> {
    const response = await api.get(`${this.baseURL}/posicao-estoque/${produtoId}/local/${localId}`);
    return response.data;
  }

  async atualizarParametrosEstoque(produtoId: number, localId: number, dados: AtualizarEstoque): Promise<EstoqueProduto> {
    const response = await api.patch(`${this.baseURL}/posicao-estoque/${produtoId}/local/${localId}`, dados);
    return response.data;
  }

  // MOVIMENTAÇÕES
  async criarMovimentacao(dados: CriarMovimentacao): Promise<MovimentacaoEstoque> {
    const response = await api.post(`${this.baseURL}/movimentacao`, dados);
    return response.data;
  }

  async listarMovimentacoes(filtros: FiltroMovimentacao = {}): Promise<{ itens: MovimentacaoEstoque[]; total: number }> {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`${this.baseURL}/movimentacoes?${params}`);
    return response.data;
  }

  async obterMovimentacao(id: number): Promise<MovimentacaoEstoque> {
    const response = await api.get(`${this.baseURL}/movimentacoes/${id}`);
    return response.data;
  }

  // LOCAIS DE ESTOQUE
  async criarLocalEstoque(dados: CriarLocalEstoque): Promise<LocalEstoque> {
    const response = await api.post(`${this.baseURL}/locais`, dados);
    return response.data;
  }

  async listarLocaisEstoque(): Promise<LocalEstoque[]> {
    const response = await api.get(`${this.baseURL}/locais`);
    return response.data;
  }

  async obterLocalEstoque(id: number): Promise<LocalEstoque> {
    const response = await api.get(`${this.baseURL}/locais/${id}`);
    return response.data;
  }

  async atualizarLocalEstoque(id: number, dados: Partial<CriarLocalEstoque>): Promise<LocalEstoque> {
    const response = await api.patch(`${this.baseURL}/locais/${id}`, dados);
    return response.data;
  }

  async excluirLocalEstoque(id: number): Promise<void> {
    await api.delete(`${this.baseURL}/locais/${id}`);
  }

  // ALERTAS E ANÁLISES
  async obterAlertasEstoque(localId: number): Promise<AlertaEstoque> {
    const response = await api.get(`${this.baseURL}/alertas/${localId}`);
    return response.data;
  }

  async obterSugestoesCompra(localId: number): Promise<SugestaoCompra[]> {
    const response = await api.get(`${this.baseURL}/sugestoes-compra/${localId}`);
    return response.data;
  }

  async obterDashboardEstoque(localId?: number): Promise<DashboardEstoque> {
    const url = localId 
      ? `${this.baseURL}/dashboard/${localId}`
      : `${this.baseURL}/dashboard`;
    
    const response = await api.get(url);
    return response.data;
  }

  // UTILITÁRIOS
  async atualizarEstatisticasEstoque(produtoId?: number, localId?: number): Promise<void> {
    const params = new URLSearchParams();
    if (produtoId) params.append('produto_id', produtoId.toString());
    if (localId) params.append('local_id', localId.toString());

    await api.post(`${this.baseURL}/atualizar-estatisticas?${params}`);
  }

  async reservarEstoque(produtoId: number, localId: number, quantidade: number): Promise<boolean> {
    const response = await api.post(`${this.baseURL}/reservar`, {
      produto_id: produtoId,
      local_id: localId,
      quantidade
    });
    return response.data.sucesso;
  }

  async liberarReserva(produtoId: number, localId: number, quantidade: number): Promise<void> {
    await api.post(`${this.baseURL}/liberar-reserva`, {
      produto_id: produtoId,
      local_id: localId,
      quantidade
    });
  }
}

// ================================================================================
// UTILITY FUNCTIONS
// ================================================================================

export const formatarQuantidade = (quantidade: number, unidade?: string): string => {
  const qtdFormatada = new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 3
  }).format(quantidade);
  
  return unidade ? `${qtdFormatada} ${unidade}` : qtdFormatada;
};

export const formatarValor = (valor: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

export const obterCorStatusEstoque = (estoque: EstoqueProduto): string => {
  if (estoque.quantidade_atual === 0) return 'error';
  if (estoque.quantidade_atual <= estoque.estoque_minimo) return 'warning';
  if (estoque.quantidade_atual >= estoque.estoque_maximo) return 'info';
  return 'success';
};

export const obterTextoStatusEstoque = (estoque: EstoqueProduto): string => {
  if (estoque.quantidade_atual === 0) return 'Sem Estoque';
  if (estoque.quantidade_atual <= estoque.estoque_minimo) return 'Estoque Baixo';
  if (estoque.quantidade_atual >= estoque.estoque_maximo) return 'Estoque Alto';
  return 'Normal';
};

export const calcularPercentualGiro = (giro: number): { cor: string; texto: string } => {
  if (giro >= 6) return { cor: 'success', texto: 'Excelente' };
  if (giro >= 3) return { cor: 'warning', texto: 'Bom' };
  if (giro >= 1) return { cor: 'info', texto: 'Regular' };
  return { cor: 'error', texto: 'Baixo' };
};

export const formatarDataMovimentacao = (data: string): string => {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(data));
};

export const obterIconeMovimentacao = (tipo: string): string => {
  if (tipo.includes('entrada')) return '↗️';
  if (tipo.includes('saida')) return '↘️';
  if (tipo.includes('transferencia')) return '↔️';
  if (tipo.includes('inventario')) return '📊';
  return '📦';
};

export const tiposMovimentacao = [
  { value: 'entrada_compra', label: 'Entrada por Compra', icon: '↗️' },
  { value: 'entrada_devolucao', label: 'Entrada por Devolução', icon: '↗️' },
  { value: 'entrada_transferencia', label: 'Entrada por Transferência', icon: '↗️' },
  { value: 'entrada_inventario', label: 'Entrada por Inventário', icon: '↗️' },
  { value: 'entrada_producao', label: 'Entrada por Produção', icon: '↗️' },
  { value: 'saida_venda', label: 'Saída por Venda', icon: '↘️' },
  { value: 'saida_transferencia', label: 'Saída por Transferência', icon: '↘️' },
  { value: 'saida_inventario', label: 'Saída por Inventário', icon: '↘️' },
  { value: 'saida_perda', label: 'Saída por Perda', icon: '↘️' },
  { value: 'saida_consumo', label: 'Saída por Consumo', icon: '↘️' }
];

export const metodosControle = [
  { value: 'custo_medio', label: 'Custo Médio Ponderado' },
  { value: 'fifo', label: 'FIFO (Primeiro a Entrar, Primeiro a Sair)' },
  { value: 'lifo', label: 'LIFO (Último a Entrar, Primeiro a Sair)' }
];

export const tiposLocal = [
  { value: 'deposito', label: 'Depósito Principal' },
  { value: 'loja', label: 'Loja/Ponto de Venda' },
  { value: 'almoxarifado', label: 'Almoxarifado' },
  { value: 'expedicao', label: 'Expedição' },
  { value: 'transito', label: 'Em Trânsito' },
  { value: 'producao', label: 'Produção' },
  { value: 'devolucao', label: 'Devolução' },
  { value: 'quarentena', label: 'Quarentena' }
];

// ================================================================================
// INSTÂNCIA DO SERVIÇO
// ================================================================================

export const estoqueService = new EstoqueService();
export default estoqueService;
