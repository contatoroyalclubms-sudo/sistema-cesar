/**
 * 📋 INTERFACES COMPLETAS E PADRONIZADAS - FRONTEND
 * Sincronizado com backend/app/schemas_completo.py
 * Última atualização: 05/01/2025
 */

import {
  StatusEvento, TipoUsuario, TipoLista, StatusTransacao,
  TipoProduto, StatusProduto, TipoComanda, StatusComanda,
  StatusVendaPDV, TipoPagamentoPDV, TipoMovimentacaoFinanceira,
  StatusMovimentacaoFinanceira, TipoFormaPagamento, StatusFormaPagamento,
  TipoConquista, NivelBadge, StatusImportacao, TipoOperacao,
  StatusValidacao, TipoImpressora, InterfaceImpressora, StatusImpressora,
  StatusPrintJob, TipoPrintJob
} from './enums';

// ===== TIPOS BASE REUTILIZÁVEIS =====

export interface TimestampFields {
  criado_em?: string | Date;
  atualizado_em?: string | Date;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// ===== INTERFACES DE EMPRESA =====

export interface EmpresaBase {
  nome: string;
  cnpj: string;
  email: string;
  telefone?: string;
  endereco?: string;
}

export interface EmpresaCreate extends EmpresaBase {}

export interface EmpresaUpdate {
  nome?: string;
  email?: string;
  telefone?: string;
  endereco?: string;
  ativa?: boolean;
}

export interface Empresa extends EmpresaBase, TimestampFields {
  id: number;
  ativa: boolean;
}

// ===== INTERFACES DE USUÁRIO =====

export interface UsuarioBase {
  cpf: string;
  nome: string;
  email: string;
  telefone?: string;
  tipo: TipoUsuario | string;
}

export interface UsuarioCreate extends UsuarioBase {
  senha: string;
  tipo_usuario?: string; // Alias para compatibilidade
}

export interface UsuarioUpdate {
  nome?: string;
  email?: string;
  telefone?: string;
  tipo?: TipoUsuario | string;
  ativo?: boolean;
  senha?: string;
}

export interface Usuario extends UsuarioBase, TimestampFields {
  id: number;
  ativo: boolean;
  ultimo_login?: string | Date;
}

export interface UsuarioLogin {
  cpf: string;
  senha: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: Usuario;
}

// ===== INTERFACES DE EVENTO =====

export interface EventoBase {
  nome: string;
  descricao?: string;
  data_evento: string | Date;
  local: string;
  endereco?: string;
  limite_idade?: number;
  capacidade_maxima?: number;
}

export interface EventoCreate extends EventoBase {
  empresa_id?: number;
}

export interface EventoUpdate {
  nome?: string;
  descricao?: string;
  data_evento?: string | Date;
  local?: string;
  endereco?: string;
  limite_idade?: number;
  capacidade_maxima?: number;
  status?: StatusEvento;
}

export interface Evento extends EventoBase, TimestampFields {
  id: number;
  status: StatusEvento;
  empresa_id?: number;
  criador_id: number;
  // Campos calculados
  total_vendas?: number;
  receita_total?: number;
  total_checkins?: number;
}

export interface EventoDetalhado extends Evento {
  listas: Lista[];
  promoters: PromoterEvento[];
  estatisticas?: Record<string, any>;
}

// ===== INTERFACES DE LISTA =====

export interface ListaBase {
  nome: string;
  tipo: TipoLista;
  preco: number;
  limite_vendas?: number;
  descricao?: string;
  codigo_cupom?: string;
  desconto_percentual?: number;
}

export interface ListaCreate extends ListaBase {
  evento_id: number;
  promoter_id?: number;
}

export interface ListaUpdate {
  nome?: string;
  tipo?: TipoLista;
  preco?: number;
  limite_vendas?: number;
  ativa?: boolean;
  descricao?: string;
  codigo_cupom?: string;
  desconto_percentual?: number;
}

export interface Lista extends ListaBase, TimestampFields {
  id: number;
  evento_id: number;
  promoter_id?: number;
  vendas_realizadas: number;
  ativa: boolean;
}

// ===== INTERFACES DE TRANSAÇÃO =====

export interface TransacaoBase {
  cpf_comprador: string;
  nome_comprador: string;
  email_comprador?: string;
  telefone_comprador?: string;
  valor: number;
  metodo_pagamento?: string;
}

export interface TransacaoCreate extends TransacaoBase {
  evento_id: number;
  lista_id: number;
  usuario_id?: number;
}

export interface TransacaoUpdate {
  status?: StatusTransacao;
  metodo_pagamento?: string;
}

export interface Transacao extends TransacaoBase, TimestampFields {
  id: number;
  evento_id: number;
  lista_id: number;
  usuario_id?: number;
  status: StatusTransacao;
  codigo_transacao?: string;
  qr_code_ticket?: string;
  ip_origem?: string;
}

// ===== INTERFACES DE CHECKIN =====

export interface CheckinBase {
  cpf: string;
  nome: string;
}

export interface CheckinCreate extends CheckinBase {
  evento_id: number;
  usuario_id?: number;
  transacao_id?: number;
  metodo_checkin?: 'cpf' | 'qr_code' | 'cartao';
  validacao_cpf?: string; // 3 primeiros dígitos
}

export interface Checkin extends CheckinBase {
  id: number;
  evento_id: number;
  usuario_id?: number;
  transacao_id?: number;
  metodo_checkin?: string;
  ip_origem?: string;
  checkin_em: string | Date;
}

// ===== INTERFACES DE PRODUTO =====

export interface ProdutoBase {
  nome: string;
  descricao?: string;
  tipo: TipoProduto;
  preco: number;
  codigo_interno?: string;
  categoria?: string;
  imagem_url?: string;
}

export interface ProdutoCreate extends ProdutoBase {
  estoque_atual?: number;
  estoque_minimo?: number;
  estoque_maximo?: number;
  controla_estoque?: boolean;
  empresa_id?: number;
}

export interface ProdutoUpdate {
  nome?: string;
  descricao?: string;
  tipo?: TipoProduto;
  preco?: number;
  codigo_interno?: string;
  estoque_atual?: number;
  estoque_minimo?: number;
  estoque_maximo?: number;
  controla_estoque?: boolean;
  status?: StatusProduto;
  categoria?: string;
  imagem_url?: string;
}

export interface Produto extends ProdutoBase, TimestampFields {
  id: number;
  estoque_atual: number;
  estoque_minimo: number;
  estoque_maximo: number;
  controla_estoque: boolean;
  status: StatusProduto;
  empresa_id?: number;
}

// ===== INTERFACES DE VENDA PDV =====

export interface VendaPDVBase {
  cpf_cliente?: string;
  nome_cliente?: string;
  tipo_pagamento: TipoPagamentoPDV;
}

export interface ItemVendaPDV {
  produto_id: number;
  quantidade: number;
  preco_unitario?: number;
  desconto_aplicado?: number;
  observacoes?: string;
}

export interface VendaPDVCreate extends VendaPDVBase {
  evento_id: number;
  comanda_id?: number;
  promoter_id?: number;
  cupom_codigo?: string;
  itens: ItemVendaPDV[];
  observacoes?: string;
}

export interface VendaPDV extends VendaPDVBase, TimestampFields {
  id: number;
  numero_venda: string;
  evento_id: number;
  valor_total: number;
  valor_desconto: number;
  valor_final: number;
  status: StatusVendaPDV;
  comanda_id?: number;
  empresa_id?: number;
  usuario_vendedor_id: number;
  promoter_id?: number;
  cupom_codigo?: string;
  observacoes?: string;
  ip_origem?: string;
}

// ===== INTERFACES DE COMANDA =====

export interface ComandaBase {
  numero_comanda: string;
  tipo: TipoComanda;
  cpf_cliente?: string;
  nome_cliente?: string;
}

export interface ComandaCreate extends ComandaBase {
  evento_id: number;
  empresa_id?: number;
  codigo_rfid?: string;
  qr_code?: string;
}

export interface ComandaRecarga {
  valor: number;
  tipo_pagamento: TipoPagamentoPDV;
}

export interface Comanda extends ComandaBase, TimestampFields {
  id: number;
  evento_id: number;
  empresa_id?: number;
  codigo_rfid?: string;
  qr_code?: string;
  saldo_atual: number;
  saldo_bloqueado: number;
  status: StatusComanda;
}

// ===== INTERFACES FINANCEIRAS =====

export interface MovimentacaoFinanceiraBase {
  tipo: TipoMovimentacaoFinanceira;
  categoria: string;
  descricao: string;
  valor: number;
}

export interface MovimentacaoFinanceiraCreate extends MovimentacaoFinanceiraBase {
  evento_id: number;
  promoter_id?: number;
  numero_documento?: string;
  observacoes?: string;
  data_vencimento?: string | Date;
  data_pagamento?: string | Date;
  metodo_pagamento?: string;
}

export interface MovimentacaoFinanceira extends MovimentacaoFinanceiraBase, TimestampFields {
  id: number;
  evento_id: number;
  status: StatusMovimentacaoFinanceira;
  usuario_responsavel_id: number;
  promoter_id?: number;
  comprovante_url?: string;
  numero_documento?: string;
  observacoes?: string;
  data_vencimento?: string | Date;
  data_pagamento?: string | Date;
  metodo_pagamento?: string;
}

export interface CaixaEventoBase {
  saldo_inicial: number;
  observacoes_abertura?: string;
}

export interface CaixaEventoCreate extends CaixaEventoBase {
  evento_id: number;
}

export interface CaixaEventoFechar {
  observacoes_fechamento?: string;
}

export interface CaixaEvento extends CaixaEventoBase {
  id: number;
  evento_id: number;
  data_abertura: string | Date;
  data_fechamento?: string | Date;
  total_entradas: number;
  total_saidas: number;
  total_vendas_pdv: number;
  total_vendas_listas: number;
  saldo_final: number;
  status: string;
  usuario_abertura_id: number;
  usuario_fechamento_id?: number;
  observacoes_fechamento?: string;
}

// ===== INTERFACES DE PROMOTER =====

export interface PromoterEvento {
  id?: number;
  promoter_id: number;
  evento_id: number;
  meta_vendas?: number;
  vendas_realizadas?: number;
  comissao_percentual?: number;
  ativo?: boolean;
  criado_em?: string | Date;
}

export interface PromoterEventoCreate {
  promoter_id: number;
  evento_id: number;
  meta_vendas?: number;
  comissao_percentual?: number;
}

// ===== INTERFACES DE GAMIFICAÇÃO =====

export interface ConquistaBase {
  nome: string;
  descricao: string;
  tipo: TipoConquista;
  criterio_valor: number;
  badge_nivel: NivelBadge;
  icone?: string;
}

export interface ConquistaCreate extends ConquistaBase {}

export interface Conquista extends ConquistaBase {
  id: number;
  ativa: boolean;
  criado_em: string | Date;
}

export interface PromoterConquista {
  id: number;
  promoter_id: number;
  conquista_id: number;
  evento_id?: number;
  valor_alcancado: number;
  data_conquista: string | Date;
  notificado: boolean;
  conquista: Conquista;
}

export interface MetricaPromoter {
  id: number;
  promoter_id: number;
  evento_id?: number;
  periodo_inicio: string | Date;
  periodo_fim: string | Date;
  total_vendas: number;
  receita_gerada: number;
  total_convidados: number;
  total_presentes: number;
  taxa_presenca: number;
  taxa_conversao: number;
  crescimento_vendas: number;
  posicao_vendas?: number;
  posicao_presenca?: number;
  posicao_geral?: number;
  badge_atual: NivelBadge;
  atualizado_em: string | Date;
}

// ===== INTERFACES DE IMPORT/EXPORT =====

export interface OperacaoImportExportBase {
  tipo_operacao: TipoOperacao;
  nome_arquivo: string;
  formato_arquivo: 'csv' | 'xlsx' | 'json' | 'xml';
}

export interface OperacaoImportExportCreate extends OperacaoImportExportBase {
  evento_id?: number;
  empresa_id?: number;
  mapeamento_campos?: Record<string, string>;
  filtros_aplicados?: Record<string, any>;
  campos_personalizados?: string[];
}

export interface OperacaoImportExport extends OperacaoImportExportBase {
  id: number;
  usuario_id: number;
  evento_id?: number;
  empresa_id?: number;
  tamanho_arquivo?: number;
  status: StatusImportacao;
  total_registros: number;
  registros_processados: number;
  registros_sucesso: number;
  registros_erro: number;
  registros_aviso: number;
  mapeamento_campos?: Record<string, string>;
  filtros_aplicados?: Record<string, any>;
  campos_personalizados?: string[];
  inicio_processamento?: string | Date;
  fim_processamento?: string | Date;
  criado_em: string | Date;
  log_detalhado?: string;
  url_arquivo_resultado?: string;
  resumo_operacao?: Record<string, any>;
}

// ===== INTERFACES DE IMPRESSORA =====

export interface ImpressoraBase {
  nome: string;
  tipo: TipoImpressora;
  interface: InterfaceImpressora;
  endereco: string;
  localizacao?: string;
}

export interface ImpressoraCreate extends ImpressoraBase {
  evento_id: number;
  largura_mm?: number;
  colunas?: number;
  perfil_escpos?: 'epson' | 'star' | 'bematech';
  densidade?: number;
  impressora_backup_id?: string;
}

export interface Impressora extends ImpressoraBase, TimestampFields {
  id: string;
  evento_id: number;
  largura_mm: number;
  colunas: number;
  perfil_escpos: string;
  densidade: number;
  ativo: boolean;
  impressora_backup_id?: string;
  status: StatusImpressora;
  ultimo_heartbeat?: string | Date;
  ip_bridge?: string;
  versao_driver?: string;
  configuracoes?: Record<string, any>;
}

export interface PrintJobBase {
  tipo: TipoPrintJob;
  payload: Record<string, any>;
  prioridade?: number;
}

export interface PrintJobCreate extends PrintJobBase {
  impressora_id: string;
  evento_id: number;
  template_id?: number;
  venda_pdv_id?: number;
  comanda_id?: number;
  cpf_operador: string;
}

export interface PrintJob extends PrintJobBase {
  id: string;
  impressora_id: string;
  evento_id: number;
  template_id?: number;
  venda_pdv_id?: number;
  comanda_id?: number;
  status: StatusPrintJob;
  tentativas: number;
  max_tentativas: number;
  erro_msg?: string;
  cpf_operador: string;
  usuario_id: number;
  ip_cliente?: string;
  criado_em: string | Date;
  processado_em?: string | Date;
  impresso_em?: string | Date;
}

// ===== INTERFACES DE RESPOSTA PADRÃO =====

export interface ErrorDetail {
  field?: string;
  message: string;
  code?: string;
}

export interface ErrorResponse {
  error: string;
  details?: ErrorDetail[];
  status_code: number;
  timestamp: string | Date;
}

export interface SuccessResponse<T = any> {
  message: string;
  data?: T;
  timestamp: string | Date;
}

export interface HealthCheckResponse {
  status: string;
  database: string;
  version: string;
  timestamp: string | Date;
}

// ===== INTERFACES DE FORMULÁRIO =====

export interface FormErrors {
  [field: string]: string | undefined;
}

export interface FormState<T> {
  values: T;
  errors: FormErrors;
  touched: { [K in keyof T]?: boolean };
  isSubmitting: boolean;
  isValid: boolean;
}

export interface SelectOption<T = string | number> {
  value: T;
  label: string;
  disabled?: boolean;
  group?: string;
}

// ===== INTERFACES DE API =====

export interface ApiConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

export interface ApiError {
  response?: {
    data: ErrorResponse;
    status: number;
    statusText: string;
  };
  request?: any;
  message: string;
}

// Exportar tipos compatíveis com sistema antigo
export type UserRole = TipoUsuario;

// Exportar todas as interfaces
export default {
  // Re-export para compatibilidade
};