// Frontend Service para Sistema de Fidelidade Expandido
// Gestão completa de níveis, pontuação, campanhas e recompensas

import { api } from './api';

// ================================================================================
// INTERFACES E TIPOS
// ================================================================================

export enum TipoNivelFidelidade {
  BRONZE = 'bronze',
  PRATA = 'prata',
  OURO = 'ouro',
  PLATINA = 'platina',
  DIAMANTE = 'diamante'
}

export enum TipoMovimentacaoPonto {
  ACUMULO = 'acumulo',
  RESGATE = 'resgate',
  EXPIRACAO = 'expiracao',
  BONUS = 'bonus',
  INDICACAO = 'indicacao',
  CAMPANHA = 'campanha',
  ESTORNO = 'estorno'
}

export enum StatusCampanha {
  RASCUNHO = 'rascunho',
  ATIVA = 'ativa',
  PAUSADA = 'pausada',
  FINALIZADA = 'finalizada',
  CANCELADA = 'cancelada'
}

export enum TipoRecompensa {
  DESCONTO_PERCENTUAL = 'desconto_percentual',
  DESCONTO_VALOR = 'desconto_valor',
  PRODUTO_GRATIS = 'produto_gratis',
  FRETE_GRATIS = 'frete_gratis',
  CUPOM_DESCONTO = 'cupom_desconto'
}

export enum StatusIndicacao {
  PENDENTE = 'pendente',
  CONFIRMADA = 'confirmada',
  CANCELADA = 'cancelada',
  EXPIRADA = 'expirada'
}

export interface NivelFidelidade {
  id: number;
  empresa_id: number;
  nome: string;
  tipo: TipoNivelFidelidade;
  cor_hexadecimal: string;
  icone?: string;
  pontos_minimos: number;
  valor_gasto_minimo: number;
  compras_minimas: number;
  multiplicador_pontos: number;
  desconto_percentual: number;
  frete_gratis: boolean;
  acesso_ofertas_exclusivas: boolean;
  suporte_prioritario: boolean;
  descricao?: string;
  ordem_exibicao: number;
  ativo: boolean;
  criado_em: string;
  atualizado_em?: string;
}

export interface PontuacaoCliente {
  id: number;
  empresa_id: number;
  cliente_id: number;
  tipo_movimentacao: TipoMovimentacaoPonto;
  pontos: number;
  pontos_antes: number;
  pontos_depois: number;
  motivo: string;
  observacoes?: string;
  venda_id?: number;
  resgate_id?: number;
  campanha_id?: number;
  indicacao_id?: number;
  data_expiracao?: string;
  criado_em: string;
  criado_por_id: number;
}

export interface CampanhaFidelidade {
  id: number;
  empresa_id: number;
  nome: string;
  descricao?: string;
  data_inicio: string;
  data_fim: string;
  publico_alvo: string;
  codigo?: string;
  limite_participantes?: number;
  participantes_atuais: number;
  multiplicador_pontos: number;
  pontos_bonus: number;
  valor_minimo_compra?: number;
  tipo_recompensa?: TipoRecompensa;
  valor_recompensa?: number;
  produto_recompensa_id?: number;
  requer_codigo: boolean;
  status: StatusCampanha;
  criado_em: string;
  criado_por_id: number;
}

export interface IndicacaoCliente {
  id: number;
  empresa_id: number;
  cliente_indicador_id: number;
  cliente_indicado_id?: number;
  nome_indicado: string;
  email_indicado: string;
  telefone_indicado?: string;
  codigo_indicacao: string;
  status: StatusIndicacao;
  pontos_indicador: number;
  pontos_indicado: number;
  data_confirmacao?: string;
  data_expiracao?: string;
  criado_em: string;
}

export interface ResgateRecompensa {
  id: number;
  empresa_id: number;
  cliente_id: number;
  codigo_resgate: string;
  tipo_recompensa: TipoRecompensa;
  pontos_utilizados: number;
  valor_desconto?: number;
  percentual_desconto?: number;
  produto_id?: number;
  data_expiracao?: string;
  data_utilizacao?: string;
  utilizado: boolean;
  criado_em: string;
  criado_por_id: number;
}

export interface NivelFidelidadeCreate {
  nome: string;
  tipo: TipoNivelFidelidade;
  cor_hexadecimal?: string;
  icone?: string;
  pontos_minimos?: number;
  valor_gasto_minimo?: number;
  compras_minimas?: number;
  multiplicador_pontos?: number;
  desconto_percentual?: number;
  frete_gratis?: boolean;
  acesso_ofertas_exclusivas?: boolean;
  suporte_prioritario?: boolean;
  descricao?: string;
}

export interface CampanhaFidelidadeCreate {
  nome: string;
  descricao?: string;
  data_inicio: string;
  data_fim: string;
  publico_alvo?: string;
  limite_participantes?: number;
  multiplicador_pontos?: number;
  pontos_bonus?: number;
  valor_minimo_compra?: number;
  tipo_recompensa?: TipoRecompensa;
  valor_recompensa?: number;
  produto_recompensa_id?: number;
  requer_codigo?: boolean;
}

export interface ResgateRecompensaCreate {
  tipo_recompensa: TipoRecompensa;
  pontos_utilizados: number;
  valor_desconto?: number;
  percentual_desconto?: number;
  produto_id?: number;
  data_expiracao?: string;
}

export interface IndicacaoCreate {
  nome_indicado: string;
  email_indicado: string;
  telefone_indicado?: string;
}

export interface MovimentacaoPontosCreate {
  cliente_id: number;
  tipo_movimentacao: TipoMovimentacaoPonto;
  pontos: number;
  motivo: string;
  observacoes?: string;
}

export interface DashboardFidelidade {
  total_clientes: number;
  clientes_ativos: number;
  pontos_em_circulacao: number;
  campanhas_ativas: number;
  distribuicao_niveis: Array<{
    nome: string;
    tipo: TipoNivelFidelidade;
    quantidade: number;
  }>;
  movimentacoes_mes: Array<{
    tipo: TipoMovimentacaoPonto;
    total_pontos: number;
    total_movimentacoes: number;
  }>;
  top_clientes: Array<{
    id: number;
    nome: string;
    pontos: number;
    nivel: string;
  }>;
}

// ================================================================================
// SERVIÇO PRINCIPAL
// ================================================================================

export class FidelidadeService {

  // ============================================================================
  // NÍVEIS DE FIDELIDADE
  // ============================================================================

  static async criarNivelFidelidade(dados: NivelFidelidadeCreate): Promise<{ id: number; message: string }> {
    try {
      const response = await api.post('/api/fidelidade/niveis', dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao criar nível de fidelidade');
    }
  }

  static async listarNiveisFidelidade(ativo?: boolean): Promise<Array<{ nivel: NivelFidelidade; total_clientes: number }>> {
    try {
      const params = ativo !== undefined ? { ativo } : {};
      const response = await api.get('/api/fidelidade/niveis', { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao listar níveis de fidelidade');
    }
  }

  static async atualizarNivelFidelidade(nivelId: number, dados: Partial<NivelFidelidadeCreate>): Promise<{ message: string }> {
    try {
      const response = await api.patch(`/api/fidelidade/niveis/${nivelId}`, dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao atualizar nível de fidelidade');
    }
  }

  // ============================================================================
  // GESTÃO DE PONTOS
  // ============================================================================

  static async criarMovimentacaoPontos(movimento: MovimentacaoPontosCreate): Promise<{
    message: string;
    pontos_anteriores: number;
    pontos_atuais: number;
  }> {
    try {
      const response = await api.post('/api/fidelidade/pontos/movimentacao', movimento);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao registrar movimentação de pontos');
    }
  }

  static async obterHistoricoPontos(clienteId: number, limite: number = 50): Promise<Array<{
    movimentacao: PontuacaoCliente;
    saldo_periodo: number;
  }>> {
    try {
      const response = await api.get(`/api/fidelidade/pontos/historico/${clienteId}`, {
        params: { limite }
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao obter histórico de pontos');
    }
  }

  // ============================================================================
  // CAMPANHAS DE FIDELIDADE
  // ============================================================================

  static async criarCampanhaFidelidade(dados: CampanhaFidelidadeCreate): Promise<{
    id: number;
    codigo?: string;
    message: string;
  }> {
    try {
      const response = await api.post('/api/fidelidade/campanhas', dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao criar campanha de fidelidade');
    }
  }

  static async listarCampanhasFidelidade(
    status?: StatusCampanha,
    ativa?: boolean
  ): Promise<Array<{ campanha: CampanhaFidelidade }>> {
    try {
      const params: any = {};
      if (status) params.status = status;
      if (ativa !== undefined) params.ativa = ativa;
      
      const response = await api.get('/api/fidelidade/campanhas', { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao listar campanhas de fidelidade');
    }
  }

  // ============================================================================
  // SISTEMA DE INDICAÇÕES
  // ============================================================================

  static async criarIndicacao(clienteId: number, dados: IndicacaoCreate): Promise<{
    id: number;
    codigo_indicacao: string;
    message: string;
  }> {
    try {
      const response = await api.post(`/api/fidelidade/indicacoes?cliente_id=${clienteId}`, dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao criar indicação');
    }
  }

  static async confirmarIndicacao(codigo: string, clienteIndicadoId: number): Promise<{ message: string }> {
    try {
      const response = await api.post(`/api/fidelidade/indicacoes/${codigo}/confirmar`, {
        cliente_indicado_id: clienteIndicadoId
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao confirmar indicação');
    }
  }

  // ============================================================================
  // RESGATES E RECOMPENSAS
  // ============================================================================

  static async criarResgateRecompensa(clienteId: number, dados: ResgateRecompensaCreate): Promise<{
    id: number;
    codigo_resgate: string;
    message: string;
  }> {
    try {
      const response = await api.post(`/api/fidelidade/resgates?cliente_id=${clienteId}`, dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao criar resgate de recompensa');
    }
  }

  // ============================================================================
  // DASHBOARD
  // ============================================================================

  static async obterDashboardFidelidade(): Promise<DashboardFidelidade> {
    try {
      const response = await api.get('/api/fidelidade/dashboard/resumo');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao obter dashboard de fidelidade');
    }
  }

  // ============================================================================
  // UTILITÁRIOS
  // ============================================================================

  static formatarPontos(pontos: number): string {
    return new Intl.NumberFormat('pt-BR').format(pontos);
  }

  static obterCorNivel(tipo: TipoNivelFidelidade): string {
    const cores = {
      [TipoNivelFidelidade.BRONZE]: '#CD7F32',
      [TipoNivelFidelidade.PRATA]: '#C0C0C0',
      [TipoNivelFidelidade.OURO]: '#FFD700',
      [TipoNivelFidelidade.PLATINA]: '#E5E4E2',
      [TipoNivelFidelidade.DIAMANTE]: '#B9F2FF'
    };
    return cores[tipo] || '#888888';
  }

  static obterIconeNivel(tipo: TipoNivelFidelidade): string {
    const icones = {
      [TipoNivelFidelidade.BRONZE]: '🥉',
      [TipoNivelFidelidade.PRATA]: '🥈',
      [TipoNivelFidelidade.OURO]: '🥇',
      [TipoNivelFidelidade.PLATINA]: '💎',
      [TipoNivelFidelidade.DIAMANTE]: '💠'
    };
    return icones[tipo] || '⭐';
  }

  static obterDescricaoMovimentacao(tipo: TipoMovimentacaoPonto): string {
    const descricoes = {
      [TipoMovimentacaoPonto.ACUMULO]: 'Acúmulo de pontos',
      [TipoMovimentacaoPonto.RESGATE]: 'Resgate de pontos',
      [TipoMovimentacaoPonto.EXPIRACAO]: 'Expiração de pontos',
      [TipoMovimentacaoPonto.BONUS]: 'Bônus de pontos',
      [TipoMovimentacaoPonto.INDICACAO]: 'Pontos por indicação',
      [TipoMovimentacaoPonto.CAMPANHA]: 'Pontos de campanha',
      [TipoMovimentacaoPonto.ESTORNO]: 'Estorno de pontos'
    };
    return descricoes[tipo] || 'Movimentação';
  }

  static calcularPontosProximoNivel(pontosAtuais: number, niveis: NivelFidelidade[]): {
    proximoNivel?: NivelFidelidade;
    pontosNecessarios: number;
    progresso: number;
  } {
    const niveisOrdenados = niveis
      .filter(n => n.ativo)
      .sort((a, b) => a.pontos_minimos - b.pontos_minimos);

    const proximoNivel = niveisOrdenados.find(n => n.pontos_minimos > pontosAtuais);
    
    if (!proximoNivel) {
      return {
        pontosNecessarios: 0,
        progresso: 100
      };
    }

    const nivelAtual = niveisOrdenados
      .filter(n => n.pontos_minimos <= pontosAtuais)
      .pop();

    const pontosBase = nivelAtual?.pontos_minimos || 0;
    const pontosNecessarios = proximoNivel.pontos_minimos - pontosAtuais;
    const intervaloNivel = proximoNivel.pontos_minimos - pontosBase;
    const progresso = intervaloNivel > 0 ? ((pontosAtuais - pontosBase) / intervaloNivel) * 100 : 0;

    return {
      proximoNivel,
      pontosNecessarios,
      progresso: Math.max(0, Math.min(100, progresso))
    };
  }

  static validarCampanha(campanha: CampanhaFidelidadeCreate): string[] {
    const erros: string[] = [];

    if (!campanha.nome.trim()) {
      erros.push('Nome da campanha é obrigatório');
    }

    if (new Date(campanha.data_inicio) >= new Date(campanha.data_fim)) {
      erros.push('Data de início deve ser anterior à data de fim');
    }

    if (new Date(campanha.data_inicio) < new Date()) {
      erros.push('Data de início não pode ser no passado');
    }

    if (campanha.multiplicador_pontos && campanha.multiplicador_pontos < 0) {
      erros.push('Multiplicador de pontos deve ser positivo');
    }

    if (campanha.pontos_bonus && campanha.pontos_bonus < 0) {
      erros.push('Pontos bônus deve ser positivo');
    }

    if (campanha.valor_minimo_compra && campanha.valor_minimo_compra < 0) {
      erros.push('Valor mínimo da compra deve ser positivo');
    }

    if (campanha.limite_participantes && campanha.limite_participantes <= 0) {
      erros.push('Limite de participantes deve ser maior que zero');
    }

    return erros;
  }

  static validarResgate(resgate: ResgateRecompensaCreate): string[] {
    const erros: string[] = [];

    if (resgate.pontos_utilizados <= 0) {
      erros.push('Pontos utilizados deve ser maior que zero');
    }

    if (resgate.tipo_recompensa === TipoRecompensa.DESCONTO_VALOR && !resgate.valor_desconto) {
      erros.push('Valor do desconto é obrigatório para desconto em valor');
    }

    if (resgate.tipo_recompensa === TipoRecompensa.DESCONTO_PERCENTUAL && !resgate.percentual_desconto) {
      erros.push('Percentual do desconto é obrigatório para desconto percentual');
    }

    if (resgate.tipo_recompensa === TipoRecompensa.PRODUTO_GRATIS && !resgate.produto_id) {
      erros.push('Produto é obrigatório para produto grátis');
    }

    if (resgate.percentual_desconto && (resgate.percentual_desconto < 0 || resgate.percentual_desconto > 100)) {
      erros.push('Percentual de desconto deve estar entre 0 e 100');
    }

    if (resgate.valor_desconto && resgate.valor_desconto <= 0) {
      erros.push('Valor do desconto deve ser positivo');
    }

    return erros;
  }

  static formatarDataExpiracao(data: string): string {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(data));
  }

  static gerarRelatorioPontos(historico: Array<{ movimentacao: PontuacaoCliente; saldo_periodo: number }>): {
    totalAcumulado: number;
    totalResgatado: number;
    saldoAtual: number;
    mediaMovimentacao: number;
  } {
    const acumulos = historico.filter(h => h.movimentacao.tipo_movimentacao === TipoMovimentacaoPonto.ACUMULO);
    const resgates = historico.filter(h => h.movimentacao.tipo_movimentacao === TipoMovimentacaoPonto.RESGATE);

    const totalAcumulado = acumulos.reduce((total, h) => total + h.movimentacao.pontos, 0);
    const totalResgatado = resgates.reduce((total, h) => total + h.movimentacao.pontos, 0);
    const saldoAtual = historico.length > 0 ? historico[0].saldo_periodo : 0;
    const mediaMovimentacao = historico.length > 0 ? historico.reduce((total, h) => total + Math.abs(h.movimentacao.pontos), 0) / historico.length : 0;

    return {
      totalAcumulado,
      totalResgatado,
      saldoAtual,
      mediaMovimentacao: Math.round(mediaMovimentacao)
    };
  }
}
