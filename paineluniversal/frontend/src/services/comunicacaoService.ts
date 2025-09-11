import { api } from './api';

// === INTERFACES E TIPOS ===

export enum TipoCanal {
  WHATSAPP = 'whatsapp',
  EMAIL = 'email',
  SMS = 'sms',
  PUSH = 'push',
  SISTEMA = 'sistema',
  CHAT_INTERNO = 'chat_interno'
}

export enum StatusCanal {
  ATIVO = 'ativo',
  INATIVO = 'inativo',
  CONFIGURANDO = 'configurando',
  ERRO = 'erro',
  SUSPENSO = 'suspenso'
}

export enum TipoTemplate {
  MARKETING = 'marketing',
  TRANSACIONAL = 'transacional',
  NOTIFICACAO = 'notificacao',
  PROMOCIONAL = 'promocional',
  OPERACIONAL = 'operacional'
}

export enum StatusMensagem {
  PENDENTE = 'pendente',
  ENVIANDO = 'enviando',
  ENVIADA = 'enviada',
  ENTREGUE = 'entregue',
  LIDA = 'lida',
  ERRO = 'erro',
  REJEITADA = 'rejeitada'
}

export enum TipoCampanha {
  IMEDIATA = 'imediata',
  AGENDADA = 'agendada',
  RECORRENTE = 'recorrente',
  GATILHO = 'gatilho',
  AB_TEST = 'ab_test'
}

export enum StatusCampanha {
  RASCUNHO = 'rascunho',
  AGENDADA = 'agendada',
  ATIVA = 'ativa',
  PAUSADA = 'pausada',
  CONCLUIDA = 'concluida',
  CANCELADA = 'cancelada'
}

export enum TipoEvento {
  NOVO_PEDIDO = 'novo_pedido',
  PAGAMENTO_APROVADO = 'pagamento_aprovado',
  PEDIDO_PRONTO = 'pedido_pronto',
  ANIVERSARIO = 'aniversario',
  CARRINHO_ABANDONADO = 'carrinho_abandonado',
  NOVA_PROMOCAO = 'nova_promocao',
  FEEDBACK_PEDIDO = 'feedback_pedido',
  LEMBRETE_EVENTO = 'lembrete_evento',
  PONTO_FIDELIDADE = 'ponto_fidelidade',
  NIVEL_FIDELIDADE = 'nivel_fidelidade'
}

export enum PrioridadeMensagem {
  BAIXA = 'baixa',
  NORMAL = 'normal',
  ALTA = 'alta',
  CRITICA = 'critica'
}

// === INTERFACES DE DADOS ===

export interface CanalComunicacao {
  id: number;
  nome: string;
  tipo: TipoCanal;
  descricao?: string;
  status: StatusCanal;
  configuracoes: Record<string, any>;
  ativo: boolean;
  limite_diario: number;
  limite_mensal: number;
  tempo_throttle: number;
  total_enviados: number;
  total_entregues: number;
  total_erros: number;
  taxa_entrega: number;
  ultimo_teste?: string;
  ultimo_erro?: string;
  criado_em: string;
  atualizado_em: string;
}

export interface TemplateMensagem {
  id: number;
  nome: string;
  tipo: TipoTemplate;
  canal_nome: string;
  canal_tipo: TipoCanal;
  assunto?: string;
  conteudo: string;
  conteudo_html?: string;
  variaveis: string[];
  configuracoes: Record<string, any>;
  aprovado_whatsapp: boolean;
  codigo_template_whatsapp?: string;
  total_usado: number;
  taxa_entrega: number;
  taxa_abertura: number;
  taxa_clique: number;
  ativo: boolean;
  criado_em: string;
}

export interface ContatoComunicacao {
  id: number;
  nome: string;
  email?: string;
  telefone?: string;
  whatsapp?: string;
  cliente_id?: number;
  dados_extras: Record<string, any>;
  aceita_marketing: boolean;
  aceita_promocional: boolean;
  aceita_whatsapp: boolean;
  aceita_email: boolean;
  aceita_sms: boolean;
  tags: string[];
  segmentos: string[];
  ativo: boolean;
  bloqueado: boolean;
  motivo_bloqueio?: string;
  total_mensagens_recebidas: number;
  total_mensagens_abertas: number;
  total_cliques: number;
  ultima_interacao?: string;
  criado_em: string;
}

export interface CampanhaComunicacao {
  id: number;
  nome: string;
  descricao?: string;
  tipo: TipoCampanha;
  status: StatusCampanha;
  template_nome: string;
  data_inicio?: string;
  data_fim?: string;
  recorrencia?: Record<string, any>;
  filtros_segmentacao: Record<string, any>;
  total_contatos_alvo: number;
  variante_a_template_id?: number;
  variante_b_template_id?: number;
  percentual_variante_a: number;
  total_enviadas: number;
  total_entregues: number;
  total_abertas: number;
  total_cliques: number;
  total_conversoes: number;
  iniciada_em?: string;
  finalizada_em?: string;
  pausada_em?: string;
  criado_em: string;
}

export interface Mensagem {
  id: number;
  canal_nome: string;
  template_nome?: string;
  campanha_nome?: string;
  contato_nome?: string;
  destinatario: string;
  nome_destinatario?: string;
  assunto?: string;
  conteudo: string;
  status: StatusMensagem;
  prioridade: PrioridadeMensagem;
  tentativas: number;
  max_tentativas: number;
  id_externo?: string;
  enviada_em?: string;
  entregue_em?: string;
  aberta_em?: string;
  clicada_em?: string;
  erro_detalhes?: string;
  criado_em: string;
}

export interface EventoNotificacao {
  id: number;
  nome: string;
  tipo_evento: TipoEvento;
  template_nome: string;
  descricao?: string;
  condicoes: Record<string, any>;
  delay_minutos: number;
  filtros: Record<string, any>;
  ativo: boolean;
  total_disparos: number;
  total_sucessos: number;
  total_erros: number;
  criado_em: string;
}

export interface DashboardComunicacao {
  total_canais: number;
  canais_ativos: number;
  total_templates: number;
  total_contatos: number;
  total_campanhas: number;
  campanhas_ativas: number;
  mensagens_hoje: number;
  mensagens_mes: number;
  taxa_entrega_media: number;
  taxa_abertura_media: number;
  canais_por_tipo: Record<string, number>;
  mensagens_por_canal: Record<string, number>;
  atividade_recente: Array<{
    tipo: string;
    descricao: string;
    canal?: string;
    status?: string;
    timestamp: string;
  }>;
}

// === INTERFACES DE REQUEST ===

export interface CreateCanalRequest {
  nome: string;
  tipo: TipoCanal;
  descricao?: string;
  configuracoes?: Record<string, any>;
  limite_diario?: number;
  limite_mensal?: number;
  tempo_throttle?: number;
}

export interface UpdateCanalRequest {
  nome?: string;
  descricao?: string;
  configuracoes?: Record<string, any>;
  limite_diario?: number;
  limite_mensal?: number;
  tempo_throttle?: number;
  ativo?: boolean;
}

export interface CreateTemplateRequest {
  canal_id: number;
  nome: string;
  tipo: TipoTemplate;
  assunto?: string;
  conteudo: string;
  conteudo_html?: string;
  variaveis?: string[];
  configuracoes?: Record<string, any>;
}

export interface CreateContatoRequest {
  nome: string;
  email?: string;
  telefone?: string;
  whatsapp?: string;
  cliente_id?: number;
  dados_extras?: Record<string, any>;
  aceita_marketing?: boolean;
  aceita_promocional?: boolean;
  aceita_whatsapp?: boolean;
  aceita_email?: boolean;
  aceita_sms?: boolean;
  tags?: string[];
}

export interface CreateCampanhaRequest {
  template_id: number;
  nome: string;
  descricao?: string;
  tipo?: TipoCampanha;
  data_inicio?: string;
  data_fim?: string;
  filtros_segmentacao?: Record<string, any>;
  variante_a_template_id?: number;
  variante_b_template_id?: number;
  percentual_variante_a?: number;
}

export interface EnvioMensagemRequest {
  canal_id: number;
  template_id?: number;
  contato_id?: number;
  destinatario: string;
  nome_destinatario?: string;
  assunto?: string;
  conteudo: string;
  conteudo_html?: string;
  prioridade?: PrioridadeMensagem;
  variaveis?: Record<string, any>;
  agendado_para?: string;
}

export interface CreateEventoRequest {
  template_id: number;
  nome: string;
  tipo_evento: TipoEvento;
  descricao?: string;
  condicoes?: Record<string, any>;
  delay_minutos?: number;
  filtros?: Record<string, any>;
}

// === FILTROS E PARÂMETROS ===

export interface FiltroContatos {
  ativo?: boolean;
  aceita_marketing?: boolean;
  tag?: string;
  busca?: string;
  skip?: number;
  limit?: number;
}

export interface FiltroMensagens {
  canal_id?: number;
  status?: StatusMensagem;
  data_inicio?: string;
  data_fim?: string;
  skip?: number;
  limit?: number;
}

export interface FiltroTemplates {
  canal_id?: number;
  tipo?: TipoTemplate;
  ativo?: boolean;
}

export interface FiltroCampanhas {
  status?: StatusCampanha;
  tipo?: TipoCampanha;
  data_inicio?: string;
  data_fim?: string;
}

export interface FiltroEventos {
  ativo?: boolean;
  tipo_evento?: TipoEvento;
}

// === CLASSE DE SERVIÇO ===

export class ComunicacaoService {
  private baseUrl = '/api/comunicacao';

  // === MÉTODOS DE CANAIS ===

  async criarCanal(dados: CreateCanalRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/canais`, dados);
    return response.data;
  }

  async listarCanais(filtros?: { ativo?: boolean; tipo?: TipoCanal }): Promise<CanalComunicacao[]> {
    const params = new URLSearchParams();
    if (filtros?.ativo !== undefined) params.append('ativo', filtros.ativo.toString());
    if (filtros?.tipo) params.append('tipo', filtros.tipo);

    const response = await api.get(`${this.baseUrl}/canais?${params}`);
    return response.data;
  }

  async obterCanal(id: number): Promise<CanalComunicacao> {
    const response = await api.get(`${this.baseUrl}/canais/${id}`);
    return response.data;
  }

  async atualizarCanal(id: number, dados: UpdateCanalRequest): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/canais/${id}`, dados);
    return response.data;
  }

  async testarCanal(id: number, destinatario: string): Promise<{ sucesso: boolean; message: string; timestamp: string }> {
    const response = await api.post(`${this.baseUrl}/canais/${id}/testar`, null, {
      params: { destinatario_teste: destinatario }
    });
    return response.data;
  }

  // === MÉTODOS DE TEMPLATES ===

  async criarTemplate(dados: CreateTemplateRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/templates`, dados);
    return response.data;
  }

  async listarTemplates(filtros?: FiltroTemplates): Promise<TemplateMensagem[]> {
    const params = new URLSearchParams();
    if (filtros?.canal_id) params.append('canal_id', filtros.canal_id.toString());
    if (filtros?.tipo) params.append('tipo', filtros.tipo);
    if (filtros?.ativo !== undefined) params.append('ativo', filtros.ativo.toString());

    const response = await api.get(`${this.baseUrl}/templates?${params}`);
    return response.data;
  }

  async obterTemplate(id: number): Promise<TemplateMensagem> {
    const response = await api.get(`${this.baseUrl}/templates/${id}`);
    return response.data;
  }

  async atualizarTemplate(id: number, dados: Partial<CreateTemplateRequest>): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/templates/${id}`, dados);
    return response.data;
  }

  async deletarTemplate(id: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.baseUrl}/templates/${id}`);
    return response.data;
  }

  // === MÉTODOS DE CONTATOS ===

  async criarContato(dados: CreateContatoRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/contatos`, dados);
    return response.data;
  }

  async listarContatos(filtros?: FiltroContatos): Promise<ContatoComunicacao[]> {
    const params = new URLSearchParams();
    if (filtros?.ativo !== undefined) params.append('ativo', filtros.ativo.toString());
    if (filtros?.aceita_marketing !== undefined) params.append('aceita_marketing', filtros.aceita_marketing.toString());
    if (filtros?.tag) params.append('tag', filtros.tag);
    if (filtros?.busca) params.append('busca', filtros.busca);
    if (filtros?.skip) params.append('skip', filtros.skip.toString());
    if (filtros?.limit) params.append('limit', filtros.limit.toString());

    const response = await api.get(`${this.baseUrl}/contatos?${params}`);
    return response.data;
  }

  async obterContato(id: number): Promise<ContatoComunicacao> {
    const response = await api.get(`${this.baseUrl}/contatos/${id}`);
    return response.data;
  }

  async atualizarContato(id: number, dados: Partial<CreateContatoRequest>): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/contatos/${id}`, dados);
    return response.data;
  }

  async importarContatos(arquivo: File): Promise<{ importados: number; erros: number; detalhes: string[] }> {
    const formData = new FormData();
    formData.append('arquivo', arquivo);

    const response = await api.post(`${this.baseUrl}/contatos/importar`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  // === MÉTODOS DE CAMPANHAS ===

  async criarCampanha(dados: CreateCampanhaRequest): Promise<{ id: number; message: string; contatos_alvo: number }> {
    const response = await api.post(`${this.baseUrl}/campanhas`, dados);
    return response.data;
  }

  async listarCampanhas(filtros?: FiltroCampanhas): Promise<CampanhaComunicacao[]> {
    const params = new URLSearchParams();
    if (filtros?.status) params.append('status', filtros.status);
    if (filtros?.tipo) params.append('tipo', filtros.tipo);
    if (filtros?.data_inicio) params.append('data_inicio', filtros.data_inicio);
    if (filtros?.data_fim) params.append('data_fim', filtros.data_fim);

    const response = await api.get(`${this.baseUrl}/campanhas?${params}`);
    return response.data;
  }

  async obterCampanha(id: number): Promise<CampanhaComunicacao> {
    const response = await api.get(`${this.baseUrl}/campanhas/${id}`);
    return response.data;
  }

  async executarCampanha(id: number): Promise<{ message: string; status: string }> {
    const response = await api.post(`${this.baseUrl}/campanhas/${id}/executar`);
    return response.data;
  }

  async pausarCampanha(id: number): Promise<{ message: string }> {
    const response = await api.post(`${this.baseUrl}/campanhas/${id}/pausar`);
    return response.data;
  }

  async cancelarCampanha(id: number): Promise<{ message: string }> {
    const response = await api.post(`${this.baseUrl}/campanhas/${id}/cancelar`);
    return response.data;
  }

  // === MÉTODOS DE MENSAGENS ===

  async enviarMensagem(dados: EnvioMensagemRequest): Promise<{ id: number; message: string; agendado_para: string }> {
    const response = await api.post(`${this.baseUrl}/mensagens/enviar`, dados);
    return response.data;
  }

  async listarMensagens(filtros?: FiltroMensagens): Promise<Mensagem[]> {
    const params = new URLSearchParams();
    if (filtros?.canal_id) params.append('canal_id', filtros.canal_id.toString());
    if (filtros?.status) params.append('status', filtros.status);
    if (filtros?.data_inicio) params.append('data_inicio', filtros.data_inicio);
    if (filtros?.data_fim) params.append('data_fim', filtros.data_fim);
    if (filtros?.skip) params.append('skip', filtros.skip.toString());
    if (filtros?.limit) params.append('limit', filtros.limit.toString());

    const response = await api.get(`${this.baseUrl}/mensagens?${params}`);
    return response.data;
  }

  async obterMensagem(id: number): Promise<Mensagem> {
    const response = await api.get(`${this.baseUrl}/mensagens/${id}`);
    return response.data;
  }

  async reenviarMensagem(id: number): Promise<{ message: string }> {
    const response = await api.post(`${this.baseUrl}/mensagens/${id}/reenviar`);
    return response.data;
  }

  // === MÉTODOS DE EVENTOS AUTOMÁTICOS ===

  async criarEvento(dados: CreateEventoRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/eventos`, dados);
    return response.data;
  }

  async listarEventos(filtros?: FiltroEventos): Promise<EventoNotificacao[]> {
    const params = new URLSearchParams();
    if (filtros?.ativo !== undefined) params.append('ativo', filtros.ativo.toString());
    if (filtros?.tipo_evento) params.append('tipo_evento', filtros.tipo_evento);

    const response = await api.get(`${this.baseUrl}/eventos?${params}`);
    return response.data;
  }

  async obterEvento(id: number): Promise<EventoNotificacao> {
    const response = await api.get(`${this.baseUrl}/eventos/${id}`);
    return response.data;
  }

  async atualizarEvento(id: number, dados: Partial<CreateEventoRequest>): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/eventos/${id}`, dados);
    return response.data;
  }

  async ativarEvento(id: number): Promise<{ message: string }> {
    const response = await api.post(`${this.baseUrl}/eventos/${id}/ativar`);
    return response.data;
  }

  async desativarEvento(id: number): Promise<{ message: string }> {
    const response = await api.post(`${this.baseUrl}/eventos/${id}/desativar`);
    return response.data;
  }

  // === DASHBOARD E MÉTRICAS ===

  async obterDashboard(): Promise<DashboardComunicacao> {
    const response = await api.get(`${this.baseUrl}/dashboard`);
    return response.data;
  }

  async obterMetricas(periodo: 'diario' | 'semanal' | 'mensal' = 'diario'): Promise<any> {
    const response = await api.get(`${this.baseUrl}/metricas?periodo=${periodo}`);
    return response.data;
  }

  async obterRelatorioEntrega(canal_id?: number, data_inicio?: string, data_fim?: string): Promise<any> {
    const params = new URLSearchParams();
    if (canal_id) params.append('canal_id', canal_id.toString());
    if (data_inicio) params.append('data_inicio', data_inicio);
    if (data_fim) params.append('data_fim', data_fim);

    const response = await api.get(`${this.baseUrl}/relatorios/entrega?${params}`);
    return response.data;
  }

  // === UTILITÁRIOS E VALIDAÇÕES ===

  validarEmail(email: string): boolean {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }

  validarTelefone(telefone: string): boolean {
    const regex = /^\+?[1-9]\d{1,14}$/;
    return regex.test(telefone.replace(/\s/g, ''));
  }

  formatarTelefone(telefone: string): string {
    const cleaned = telefone.replace(/\D/g, '');
    if (cleaned.length === 11) {
      return `+55 (${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7)}`;
    }
    return telefone;
  }

  extrairVariaveis(template: string): string[] {
    const regex = /\{([^}]+)\}/g;
    const variaveis: string[] = [];
    let match;
    
    while ((match = regex.exec(template)) !== null) {
      if (!variaveis.includes(match[1])) {
        variaveis.push(match[1]);
      }
    }
    
    return variaveis;
  }

  processarTemplate(template: string, variaveis: Record<string, any>): string {
    let resultado = template;
    
    Object.entries(variaveis).forEach(([key, value]) => {
      const regex = new RegExp(`\\{${key}\\}`, 'g');
      resultado = resultado.replace(regex, String(value));
    });
    
    return resultado;
  }

  obterCorStatus(status: StatusMensagem): string {
    const cores: Record<StatusMensagem, string> = {
      [StatusMensagem.PENDENTE]: '#FFA726',
      [StatusMensagem.ENVIANDO]: '#42A5F5',
      [StatusMensagem.ENVIADA]: '#66BB6A',
      [StatusMensagem.ENTREGUE]: '#4CAF50',
      [StatusMensagem.LIDA]: '#2E7D32',
      [StatusMensagem.ERRO]: '#F44336',
      [StatusMensagem.REJEITADA]: '#E91E63'
    };
    
    return cores[status] || '#757575';
  }

  obterIconeCanal(tipo: TipoCanal): string {
    const icones: Record<TipoCanal, string> = {
      [TipoCanal.WHATSAPP]: '📱',
      [TipoCanal.EMAIL]: '📧',
      [TipoCanal.SMS]: '💬',
      [TipoCanal.PUSH]: '🔔',
      [TipoCanal.SISTEMA]: '⚙️',
      [TipoCanal.CHAT_INTERNO]: '💭'
    };
    
    return icones[tipo] || '📢';
  }

  calcularTaxaEngajamento(mensagem: Mensagem): number {
    const { total_mensagens_recebidas, total_mensagens_abertas, total_cliques } = mensagem as any;
    
    if (total_mensagens_recebidas === 0) return 0;
    
    const taxa_abertura = (total_mensagens_abertas / total_mensagens_recebidas) * 100;
    const taxa_clique = total_mensagens_abertas > 0 ? (total_cliques / total_mensagens_abertas) * 100 : 0;
    
    return (taxa_abertura + taxa_clique) / 2;
  }

  obterSugestoesMelhoria(canal: CanalComunicacao): string[] {
    const sugestoes: string[] = [];
    
    if (canal.taxa_entrega < 90) {
      sugestoes.push('Taxa de entrega baixa. Verifique a configuração do canal.');
    }
    
    if (canal.total_erros > canal.total_enviados * 0.1) {
      sugestoes.push('Muitos erros detectados. Revise as configurações.');
    }
    
    if (!canal.ultimo_teste) {
      sugestoes.push('Execute um teste para validar o funcionamento do canal.');
    }
    
    return sugestoes;
  }

  gerarRelatorioPerformance(campanhas: CampanhaComunicacao[]): any {
    const total_campanhas = campanhas.length;
    const campanhas_ativas = campanhas.filter(c => c.status === StatusCampanha.ATIVA).length;
    const total_enviadas = campanhas.reduce((sum, c) => sum + c.total_enviadas, 0);
    const total_entregues = campanhas.reduce((sum, c) => sum + c.total_entregues, 0);
    const total_abertas = campanhas.reduce((sum, c) => sum + c.total_abertas, 0);
    const total_cliques = campanhas.reduce((sum, c) => sum + c.total_cliques, 0);
    
    return {
      total_campanhas,
      campanhas_ativas,
      total_enviadas,
      total_entregues,
      total_abertas,
      total_cliques,
      taxa_entrega: total_enviadas > 0 ? (total_entregues / total_enviadas) * 100 : 0,
      taxa_abertura: total_entregues > 0 ? (total_abertas / total_entregues) * 100 : 0,
      taxa_clique: total_abertas > 0 ? (total_cliques / total_abertas) * 100 : 0
    };
  }
}

// === INSTÂNCIA DO SERVIÇO ===

export const comunicacaoService = new ComunicacaoService();
