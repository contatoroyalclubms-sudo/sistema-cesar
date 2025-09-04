// 🚀 TIPOS COMPLETOS E COMPATÍVEIS - BACKEND ↔ FRONTEND ↔ DATABASE
// Sincronizado automaticamente com os modelos SQLAlchemy
// Última atualização: 2025-08-27

// ===== TIPOS BÁSICOS =====
export type UserRole = 'admin' | 'promoter' | 'cliente' | 'operador';
export type StatusEvento = 'ATIVO' | 'INATIVO' | 'CANCELADO' | 'FINALIZADO';
export type TipoLista = 'VIP' | 'PREMIUM' | 'COMUM' | 'PROMOTER' | 'FREE';
export type StatusTransacao = 'PENDENTE' | 'APROVADA' | 'CANCELADA' | 'ESTORNADA';
export type TipoProduto = 'BEBIDA' | 'COMIDA' | 'INGRESSO' | 'FICHA' | 'COMBO' | 'VOUCHER';
export type StatusProduto = 'ATIVO' | 'INATIVO' | 'ESGOTADO';
export type TipoComanda = 'INDIVIDUAL' | 'MESA' | 'BALCAO';
export type StatusComanda = 'ABERTA' | 'FECHADA' | 'CANCELADA';
export type StatusVendaPDV = 'PENDENTE' | 'FINALIZADA' | 'CANCELADA' | 'ESTORNADA';
export type TipoPagamentoPDV = 'DINHEIRO' | 'CARTAO_CREDITO' | 'CARTAO_DEBITO' | 'PIX' | 'TRANSFERENCIA';

// ===== INTERFACES PRINCIPAIS =====

export interface Usuario {
  id?: number;
  cpf: string;
  nome: string;
  email: string;
  telefone?: string;
  tipo: UserRole;
  // COMPATIBILIDADE: Aceitar também tipo_usuario do backend
  tipo_usuario?: UserRole;
  ativo?: boolean;
  ultimo_login?: string;
  criado_em?: string;
  atualizado_em?: string;
}

export interface UsuarioCreate {
  cpf: string;
  nome: string;
  email: string;
  telefone?: string;
  senha: string;
  tipo: UserRole;
}

export interface UsuarioDetalhado extends Usuario {
  id: number;
  ativo: boolean;
  criado_em: string;
  empresa?: {
    id: number;
    nome: string;
  };
}

export interface Empresa {
  id?: number;
  nome: string;
  cnpj: string;
  email: string;
  telefone?: string;
  endereco?: string;
  ativa?: boolean;
  criado_em?: string;
  atualizado_em?: string;
}

export interface EmpresaCreate {
  nome: string;
  cnpj: string;
  email: string;
  telefone?: string;
  endereco?: string;
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
  status?: StatusEvento;
  empresa_id?: number;  // OPCIONAL conforme modelo
  criador_id?: number;
  criado_em?: string;
  atualizado_em?: string;
}

export interface EventoCreate {
  nome: string;
  descricao?: string;
  data_evento: string;
  local: string;
  endereco?: string;
  limite_idade?: number;
  capacidade_maxima?: number;
  empresa_id?: number;  // OPCIONAL conforme backend
}

export interface EventoDetalhado extends Evento {
  id: number;
  total_vendas?: number;
  receita_total?: number;
  total_checkins?: number;
  promoters_vinculados?: any[];
  status_financeiro?: string;
}

export interface Lista {
  id?: number;
  nome: string;
  tipo: TipoLista;
  preco: number;
  limite_vendas?: number;
  vendas_realizadas?: number;
  ativa?: boolean;
  evento_id: number;
  promoter_id?: number;
  descricao?: string;
  codigo_cupom?: string;
  desconto_percentual?: number;
  criado_em?: string;
}

export interface ListaCreate {
  nome: string;
  tipo: TipoLista;
  preco: number;
  limite_vendas?: number;
  evento_id: number;
  promoter_id?: number;
  descricao?: string;
  codigo_cupom?: string;
  desconto_percentual?: number;
}

export interface ListaDetalhada extends Lista {
  total_convidados?: number;
  convidados_presentes?: number;
  taxa_presenca?: number;
  receita_gerada?: number;
  promoter_nome?: string;
}

export interface Transacao {
  id?: number;
  evento_id: number;
  lista_id: number;
  usuario_id: number;
  valor: number;
  status: StatusTransacao;
  metodo_pagamento?: string;
  observacoes?: string;
  criado_em?: string;
  atualizado_em?: string;
}

export interface TransacaoCreate {
  evento_id: number;
  lista_id: number;
  usuario_id: number;
  valor: number;
  metodo_pagamento?: string;
  observacoes?: string;
}

export interface Checkin {
  id?: number;
  evento_id: number;
  usuario_id: number;
  lista_id?: number;
  data_checkin: string;
  latitude?: number;
  longitude?: number;
  observacoes?: string;
  criado_em?: string;
}

export interface CheckinCreate {
  evento_id: number;
  usuario_id?: number;
  cpf?: string;  // Para checkin por CPF
  lista_id?: number;
  latitude?: number;
  longitude?: number;
  observacoes?: string;
  validacao_cpf?: string;  // Para MEEP
}

export interface PromoterEvento {
  id?: number;
  promoter_id: number;
  evento_id: number;
  meta_vendas?: number;
  vendas_realizadas?: number;
  comissao_percentual?: number;
  ativo?: boolean;
  criado_em?: string;
}

export interface PromoterEventoCreate {
  promoter_id: number;
  evento_id: number;
  meta_vendas?: number;
  comissao_percentual?: number;
}

export interface PromoterEventoResponse extends PromoterEvento {
  id: number;
  promoter_nome: string;
}

// ===== PRODUTOS E PDV =====

export interface CategoriaProduto {
  id?: number;
  nome: string;
  descricao?: string;
  cor?: string;
  ativo?: boolean;
  criado_em?: string;
  atualizado_em?: string;
}

export interface CategoriaCreate {
  nome: string;
  descricao?: string;
  cor?: string;
  evento_id?: number;
}

export interface Produto {
  id?: number;
  nome: string;
  tipo: TipoProduto;
  preco: number;
  categoria_id?: number;
  categoria?: CategoriaProduto;
  codigo_interno?: string;
  codigo_barras?: string;
  descricao?: string;
  estoque_atual?: number;
  estoque_minimo?: number;
  estoque_maximo?: number;
  controla_estoque?: boolean;
  status?: StatusProduto;
  destaque?: boolean;
  habilitado?: boolean;
  promocional?: boolean;
  ativo?: boolean;
  // Campos adicionais para compatibilidade
  codigo?: string;
  valor?: number;
  estoque?: number;
  marca?: string;
  fornecedor?: string;
  preco_custo?: number;
  margem_lucro?: number;
  unidade_medida?: string;
  volume?: number;
  teor_alcoolico?: number;
  temperatura_ideal?: string;
  validade_dias?: number;
  ncm?: string;
  cfop?: string;
  cest?: string;
  icms?: number;
  ipi?: number;
  observacoes?: string;
  imagem_url?: string;
  evento_id?: number;
  empresa_id?: number;
  criado_em?: Date | string;
  atualizado_em?: Date | string;
}

export interface ProdutoCreate {
  nome: string;
  tipo: TipoProduto;
  preco: number;
  categoria_id?: number;
  categoria?: string; // Para compatibilidade
  codigo_interno?: string;
  codigo_barras?: string;
  descricao?: string;
  estoque_atual?: number;
  estoque_minimo?: number;
  estoque_maximo?: number;
  controla_estoque?: boolean;
  status?: StatusProduto;
  destaque?: boolean;
  habilitado?: boolean;
  promocional?: boolean;
  marca?: string;
  fornecedor?: string;
  preco_custo?: number;
  margem_lucro?: number;
  unidade_medida?: string;
  volume?: number;
  teor_alcoolico?: number;
  temperatura_ideal?: string;
  validade_dias?: number;
  ncm?: string;
  cfop?: string;
  cest?: string;
  icms?: number;
  ipi?: number;
  observacoes?: string;
  imagem_url?: string;
  // evento_id removido - produtos são globais, não atrelados a eventos
  empresa_id?: number;
}

export interface Comanda {
  id?: number;
  numero: string;
  tipo: TipoComanda;
  mesa_numero?: string;
  cliente_nome?: string;
  status: StatusComanda;
  subtotal?: number;
  desconto?: number;
  total?: number;
  observacoes?: string;
  evento_id?: number;
  usuario_id?: number;
  criado_em?: string;
  atualizado_em?: string;
}

export interface VendaPDV {
  id?: number;
  numero_venda: string;
  produto_id: number;
  quantidade: number;
  preco_unitario: number;
  subtotal: number;
  desconto?: number;
  total: number;
  tipo_pagamento: TipoPagamentoPDV;
  status: StatusVendaPDV;
  comanda_id?: number;
  evento_id?: number;
  usuario_id?: number;
  observacoes?: string;
  criado_em?: string;
  atualizado_em?: string;
}

// ===== MEEP INTEGRATION =====

export interface ClienteEvento {
  id?: number;
  cpf: string;
  nome_completo: string;
  nome_social?: string;
  data_nascimento?: string;
  nome_mae?: string;
  telefone?: string;
  email?: string;
  status?: string;
  criado_em?: string;
  atualizado_em?: string;
}

export interface ValidacaoAcesso {
  id?: number;
  cpf: string;
  evento_id: number;
  status_validacao: string;
  detalhes_validacao?: string;
  tentativas_acesso?: number;
  bloqueado?: boolean;
  motivo_bloqueio?: string;
  criado_em?: string;
  atualizado_em?: string;
}

export interface EquipamentoEvento {
  id?: number;
  evento_id: number;
  nome: string;
  tipo: string;
  ip_address: string;
  mac_address?: string;
  status?: string;
  configuracao?: string;
  localizacao?: string;
  responsavel_id?: number;
  heartbeat_interval?: number;
  ultima_atividade?: string;
  criado_em?: string;
  atualizado_em?: string;
}

// ===== GAMIFICAÇÃO =====

export interface ConquistaGamificacao {
  id?: number;
  nome: string;
  descricao?: string;
  icone?: string;
  condicoes: string;
  pontos: number;
  ativa?: boolean;
  criado_em?: string;
}

export interface AchievementUsuario {
  id?: number;
  usuario_id: number;
  conquista_id: number;
  data_conquista: string;
  pontos_ganhos: number;
  detalhes?: string;
}

// ===== FINANCEIRO =====

export interface MovimentacaoFinanceira {
  id?: number;
  evento_id?: number;
  tipo: string;
  valor: number;
  descricao?: string;
  categoria?: string;
  data_movimentacao: string;
  usuario_id?: number;
  observacoes?: string;
  criado_em?: string;
}

export interface CaixaEvento {
  id?: number;
  evento_id: number;
  data_abertura: string;
  data_fechamento?: string;
  saldo_inicial?: number;
  total_entradas?: number;
  total_saidas?: number;
  total_vendas_pdv?: number;
  total_vendas_listas?: number;
  saldo_final?: number;
  status?: string;
  usuario_abertura_id: number;
  usuario_fechamento_id?: number;
  observacoes_abertura?: string;
  observacoes_fechamento?: string;
}

// ===== RELATÓRIOS E DASHBOARD =====

export interface DashboardResumo {
  total_eventos?: number;
  total_usuarios?: number;
  total_vendas?: number;
  receita_total?: number;
  eventos_hoje?: number;
  checkins_hoje?: number;
  vendas_hoje?: number;
  top_promoters?: RankingPromoter[];
}

export interface RankingPromoter {
  id: number;
  nome: string;
  total_vendas: number;
  total_comissao: number;
  eventos_ativos: number;
  posicao: number;
}

export interface EstatisticasEvento {
  evento_id: number;
  total_listas: number;
  total_vendas: number;
  receita_total: number;
  total_checkins: number;
  taxa_comparecimento: number;
  vendas_por_lista: { [key: string]: number };
  checkins_por_hora: { [key: string]: number };
}

// ===== INTERFACES DE API =====

export interface LoginRequest {
  cpf: string;
  senha: string;
  codigo_verificacao?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
  timestamp?: string;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// ===== FILTROS E PESQUISAS =====

export interface EventoFiltros {
  nome?: string;
  status?: StatusEvento;
  empresa_id?: number;
  data_inicio?: string;
  data_fim?: string;
  local?: string;
  limite_idade_min?: number;
  limite_idade_max?: number;
}

export interface UsuarioFiltros {
  nome?: string;
  email?: string;
  tipo?: UserRole;
  ativo?: boolean;
  empresa_id?: number;
}

export interface ProdutoFiltros {
  nome?: string;
  categoria_id?: number;
  tipo?: TipoProduto;
  status?: StatusProduto;
  destaque?: boolean;
  promocional?: boolean;
}

export interface TransacaoFiltros {
  evento_id?: number;
  usuario_id?: number;
  status?: StatusTransacao;
  data_inicio?: string;
  data_fim?: string;
  valor_min?: number;
  valor_max?: number;
}

// ===== WEBHOOKS E INTEGRAÇÕES =====

export interface WebhookPayload {
  event: string;
  data: any;
  timestamp: string;
  signature?: string;
}

export interface WhatsAppMessage {
  to: string;
  message: string;
  template?: string;
  variables?: { [key: string]: string };
}

export interface N8NWebhook {
  url: string;
  method: string;
  headers?: { [key: string]: string };
  payload: any;
}

// ===== EXPORTS PARA COMPATIBILIDADE =====

// Aliases para compatibilidade com código existente
export type { Usuario as UsuarioType };
export type { Evento as EventoType };
export type { Produto as ProdutoType };
export type { Lista as ListaType };
export type { Transacao as TransacaoType };

// Interface para formulários (compatibilidade)
export interface ProdutoFormData extends ProdutoCreate {}
export interface EventoFormData extends EventoCreate {}
export interface UsuarioFormData extends UsuarioCreate {}

// Re-exports de tipos de produto para compatibilidade
export interface Categoria extends CategoriaProduto {}

// ===== WEBSOCKET EVENTS =====

export interface WebSocketEvent {
  type: string;
  data: any;
  timestamp: string;
  event_id?: number;
}

export interface PDVWebSocketEvent extends WebSocketEvent {
  type: 'venda_realizada' | 'produto_atualizado' | 'estoque_baixo';
}

export interface CheckinWebSocketEvent extends WebSocketEvent {
  type: 'checkin_realizado' | 'usuario_chegou' | 'lista_atualizada';
}

// ===== CONFIGURAÇÕES E PREFERÊNCIAS =====

export interface ConfiguracaoSistema {
  id?: number;
  chave: string;
  valor: string;
  descricao?: string;
  tipo?: 'string' | 'number' | 'boolean' | 'json';
  ativa?: boolean;
  criado_em?: string;
  atualizado_em?: string;
}

export interface PreferenciaUsuario {
  id?: number;
  usuario_id: number;
  chave: string;
  valor: string;
  criado_em?: string;
  atualizado_em?: string;
}

export default {
  // Re-export principal
  Usuario,
  Evento,
  Produto,
  Lista,
  Transacao,
  Checkin,
  Empresa
};
