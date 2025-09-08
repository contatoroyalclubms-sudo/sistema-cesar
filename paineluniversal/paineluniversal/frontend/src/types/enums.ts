/**
 * 🎯 ENUMS PADRONIZADOS - FRONTEND
 * Sincronizado com backend/app/enums.py
 * Última atualização: 05/01/2025
 */

// ===== ENUMS CORE =====

export enum StatusEvento {
  ATIVO = 'ATIVO',
  INATIVO = 'INATIVO',
  CANCELADO = 'CANCELADO',
  FINALIZADO = 'FINALIZADO',
  RASCUNHO = 'RASCUNHO'
}

export enum TipoUsuario {
  ADMIN = 'admin',
  PROMOTER = 'promoter',
  CLIENTE = 'cliente',
  OPERADOR = 'operador',
  VENDEDOR = 'vendedor',
  GESTOR = 'gestor'
}

export enum TipoLista {
  VIP = 'VIP',
  FREE = 'FREE',
  PAGANTE = 'PAGANTE',
  PROMOTER = 'PROMOTER',
  ANIVERSARIO = 'ANIVERSARIO',
  DESCONTO = 'DESCONTO',
  PREMIUM = 'PREMIUM',
  COMUM = 'COMUM'
}

export enum StatusTransacao {
  PENDENTE = 'PENDENTE',
  APROVADA = 'APROVADA',
  CANCELADA = 'CANCELADA',
  ESTORNADA = 'ESTORNADA',
  PROCESSANDO = 'PROCESSANDO',
  ERRO = 'ERRO'
}

// ===== ENUMS PRODUTOS E PDV =====

export enum TipoProduto {
  BEBIDA = 'BEBIDA',
  COMIDA = 'COMIDA',
  INGRESSO = 'INGRESSO',
  FICHA = 'FICHA',
  COMBO = 'COMBO',
  VOUCHER = 'VOUCHER',
  SERVICO = 'SERVICO',
  TAXA = 'TAXA',
  OUTROS = 'OUTROS'
}

export enum StatusProduto {
  ATIVO = 'ATIVO',
  INATIVO = 'INATIVO',
  ESGOTADO = 'ESGOTADO',
  PROMOCAO = 'PROMOCAO',
  SAZONAL = 'SAZONAL'
}

export enum TipoComanda {
  FISICA = 'FISICA',
  VIRTUAL = 'VIRTUAL',
  RFID = 'RFID',
  NFC = 'NFC',
  QR_CODE = 'QR_CODE',
  PULSEIRA = 'PULSEIRA'
}

export enum StatusComanda {
  ATIVA = 'ATIVA',
  BLOQUEADA = 'BLOQUEADA',
  CANCELADA = 'CANCELADA',
  PERDIDA = 'PERDIDA',
  FECHADA = 'FECHADA'
}

export enum StatusVendaPDV {
  PENDENTE = 'PENDENTE',
  APROVADA = 'APROVADA',
  CANCELADA = 'CANCELADA',
  ESTORNADA = 'ESTORNADA',
  PARCIAL = 'PARCIAL'
}

export enum TipoPagamentoPDV {
  PIX = 'PIX',
  CARTAO_CREDITO = 'CARTAO_CREDITO',
  CARTAO_DEBITO = 'CARTAO_DEBITO',
  DINHEIRO = 'DINHEIRO',
  SALDO_COMANDA = 'SALDO_COMANDA',
  VOUCHER = 'VOUCHER',
  SPLIT = 'SPLIT',
  TRANSFERENCIA = 'TRANSFERENCIA',
  BOLETO = 'BOLETO',
  CREDITO_LOJA = 'CREDITO_LOJA'
}

// ===== ENUMS FINANCEIRO =====

export enum TipoMovimentacaoFinanceira {
  ENTRADA = 'ENTRADA',
  SAIDA = 'SAIDA',
  AJUSTE = 'AJUSTE',
  REPASSE_PROMOTER = 'REPASSE_PROMOTER',
  RECEITA_VENDAS = 'RECEITA_VENDAS',
  RECEITA_LISTAS = 'RECEITA_LISTAS',
  DESPESA_OPERACIONAL = 'DESPESA_OPERACIONAL',
  DESPESA_FORNECEDOR = 'DESPESA_FORNECEDOR',
  TAXA = 'TAXA',
  COMISSAO = 'COMISSAO'
}

export enum StatusMovimentacaoFinanceira {
  PENDENTE = 'PENDENTE',
  APROVADA = 'APROVADA',
  CANCELADA = 'CANCELADA',
  ESTORNADA = 'ESTORNADA',
  AGENDADA = 'AGENDADA'
}

export enum TipoFormaPagamento {
  DINHEIRO = 'DINHEIRO',
  PIX = 'PIX',
  CARTAO_CREDITO = 'CARTAO_CREDITO',
  CARTAO_DEBITO = 'CARTAO_DEBITO',
  TRANSFERENCIA = 'TRANSFERENCIA',
  BOLETO = 'BOLETO',
  VOUCHER = 'VOUCHER',
  CREDITO_LOJA = 'CREDITO_LOJA',
  CHEQUE = 'CHEQUE',
  VALE_REFEICAO = 'VALE_REFEICAO',
  VALE_ALIMENTACAO = 'VALE_ALIMENTACAO'
}

export enum StatusFormaPagamento {
  ATIVO = 'ATIVO',
  INATIVO = 'INATIVO',
  MANUTENCAO = 'MANUTENCAO',
  BLOQUEADO = 'BLOQUEADO'
}

// ===== ENUMS GAMIFICAÇÃO =====

export enum TipoConquista {
  VENDAS = 'VENDAS',
  PRESENCA = 'PRESENCA',
  FIDELIDADE = 'FIDELIDADE',
  CRESCIMENTO = 'CRESCIMENTO',
  ESPECIAL = 'ESPECIAL',
  MARCO = 'MARCO',
  DESAFIO = 'DESAFIO'
}

export enum NivelBadge {
  BRONZE = 'BRONZE',
  PRATA = 'PRATA',
  OURO = 'OURO',
  PLATINA = 'PLATINA',
  DIAMANTE = 'DIAMANTE',
  LENDA = 'LENDA',
  MESTRE = 'MESTRE'
}

// ===== ENUMS IMPORT/EXPORT =====

export enum StatusImportacao {
  PENDENTE = 'PENDENTE',
  PROCESSANDO = 'PROCESSANDO',
  CONCLUIDA = 'CONCLUIDA',
  ERRO = 'ERRO',
  CANCELADA = 'CANCELADA',
  PAUSADA = 'PAUSADA',
  VALIDANDO = 'VALIDANDO'
}

export enum TipoOperacao {
  IMPORTACAO = 'IMPORTACAO',
  EXPORTACAO = 'EXPORTACAO',
  SINCRONIZACAO = 'SINCRONIZACAO',
  BACKUP = 'BACKUP',
  RESTAURACAO = 'RESTAURACAO'
}

export enum StatusValidacao {
  VALIDO = 'VALIDO',
  ERRO_CRITICO = 'ERRO_CRITICO',
  AVISO = 'AVISO',
  IGNORADO = 'IGNORADO',
  CORRIGIDO = 'CORRIGIDO'
}

// ===== ENUMS IMPRESSORAS =====

export enum TipoImpressora {
  COZINHA = 'COZINHA',
  BAR = 'BAR',
  SOBREMESA = 'SOBREMESA',
  CAIXA = 'CAIXA',
  GERENCIAL = 'GERENCIAL',
  PEDIDO = 'PEDIDO',
  COMANDA = 'COMANDA'
}

export enum InterfaceImpressora {
  USB = 'USB',
  NETWORK = 'NETWORK',
  BLUETOOTH = 'BLUETOOTH',
  SERIAL = 'SERIAL',
  PARALELA = 'PARALELA'
}

export enum StatusImpressora {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  ERRO = 'ERRO',
  MANUTENCAO = 'MANUTENCAO',
  IMPRIMINDO = 'IMPRIMINDO',
  PAUSADA = 'PAUSADA'
}

export enum StatusPrintJob {
  QUEUED = 'QUEUED',
  PRINTING = 'PRINTING',
  DONE = 'DONE',
  ERROR = 'ERROR',
  RETRY = 'RETRY',
  CANCELLED = 'CANCELLED'
}

export enum TipoPrintJob {
  RECIBO_CAIXA = 'RECIBO_CAIXA',
  PEDIDO_COZINHA = 'PEDIDO_COZINHA',
  PEDIDO_BAR = 'PEDIDO_BAR',
  COMANDA_RECHARGE = 'COMANDA_RECHARGE',
  RELATORIO = 'RELATORIO',
  ETIQUETA = 'ETIQUETA',
  CUPOM_FISCAL = 'CUPOM_FISCAL'
}

// ===== ENUMS ESTOQUE =====

export enum TipoMovimentoEstoque {
  ENTRADA = 'ENTRADA',
  SAIDA = 'SAIDA',
  AJUSTE = 'AJUSTE',
  TRANSFERENCIA = 'TRANSFERENCIA',
  DEVOLUCAO = 'DEVOLUCAO',
  PERDA = 'PERDA',
  INVENTARIO = 'INVENTARIO'
}

export enum StatusEstoque {
  DISPONIVEL = 'DISPONIVEL',
  RESERVADO = 'RESERVADO',
  BLOQUEADO = 'BLOQUEADO',
  EM_TRANSITO = 'EM_TRANSITO',
  VENCIDO = 'VENCIDO',
  QUARENTENA = 'QUARENTENA'
}

// ===== ENUMS CASHLESS =====

export enum StatusCashless {
  ATIVO = 'ATIVO',
  INATIVO = 'INATIVO',
  SUSPENSO = 'SUSPENSO',
  BLOQUEADO = 'BLOQUEADO',
  EXPIRADO = 'EXPIRADO'
}

export enum TipoRecarga {
  DINHEIRO = 'DINHEIRO',
  PIX = 'PIX',
  CARTAO = 'CARTAO',
  TRANSFERENCIA = 'TRANSFERENCIA',
  CORTESIA = 'CORTESIA',
  PROMOCIONAL = 'PROMOCIONAL'
}

// ===== ENUMS KDS =====

export enum StatusPedidoKDS {
  RECEBIDO = 'RECEBIDO',
  EM_PREPARO = 'EM_PREPARO',
  PRONTO = 'PRONTO',
  ENTREGUE = 'ENTREGUE',
  CANCELADO = 'CANCELADO',
  PAUSADO = 'PAUSADO'
}

export enum PrioridadePedidoKDS {
  BAIXA = 'BAIXA',
  NORMAL = 'NORMAL',
  ALTA = 'ALTA',
  URGENTE = 'URGENTE',
  VIP = 'VIP'
}

// ===== ENUMS FIDELIDADE =====

export enum TipoProgramaFidelidade {
  PONTOS = 'PONTOS',
  CASHBACK = 'CASHBACK',
  NIVEIS = 'NIVEIS',
  SELOS = 'SELOS',
  MILHAS = 'MILHAS',
  DESCONTOS = 'DESCONTOS'
}

export enum StatusFidelidade {
  ATIVO = 'ATIVO',
  INATIVO = 'INATIVO',
  SUSPENSO = 'SUSPENSO',
  EXPIRADO = 'EXPIRADO',
  BLOQUEADO = 'BLOQUEADO'
}

// ===== ENUMS AUTOMAÇÃO =====

export enum TipoGatilho {
  EVENTO = 'EVENTO',
  HORARIO = 'HORARIO',
  CONDICAO = 'CONDICAO',
  WEBHOOK = 'WEBHOOK',
  MANUAL = 'MANUAL',
  API = 'API',
  SENSOR = 'SENSOR'
}

export enum StatusAutomacao {
  ATIVO = 'ATIVO',
  INATIVO = 'INATIVO',
  PAUSADO = 'PAUSADO',
  ERRO = 'ERRO',
  TESTANDO = 'TESTANDO',
  AGENDADO = 'AGENDADO'
}

// ===== ENUMS INTEGRAÇÕES =====

export enum TipoIntegracao {
  COMUNICACAO = 'COMUNICACAO',
  ERP = 'ERP',
  FISCAL = 'FISCAL',
  DELIVERY = 'DELIVERY',
  PAGAMENTO = 'PAGAMENTO',
  MARKETING = 'MARKETING',
  CRM = 'CRM',
  BI = 'BI'
}

export enum StatusIntegracao {
  CONECTADO = 'CONECTADO',
  DESCONECTADO = 'DESCONECTADO',
  ERRO = 'ERRO',
  SINCRONIZANDO = 'SINCRONIZANDO',
  PAUSADO = 'PAUSADO',
  AUTENTICANDO = 'AUTENTICANDO'
}

// ===== FUNÇÕES AUXILIARES =====

/**
 * Retorna array com todos os valores de um enum
 */
export function getEnumValues<T extends Record<string, string>>(enumObj: T): T[keyof T][] {
  return Object.values(enumObj) as T[keyof T][];
}

/**
 * Retorna array de opções para select/dropdown
 */
export function getEnumOptions<T extends Record<string, string>>(enumObj: T): Array<{value: T[keyof T], label: string}> {
  return Object.entries(enumObj).map(([key, value]) => ({
    value: value as T[keyof T],
    label: key.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())
  }));
}

/**
 * Valida se um valor pertence ao enum
 */
export function validateEnumValue<T extends Record<string, string>>(enumObj: T, value: any): boolean {
  return Object.values(enumObj).includes(value);
}

/**
 * Converte string para valor do enum com validação
 */
export function parseEnumValue<T extends Record<string, string>>(enumObj: T, value: string): T[keyof T] | null {
  const upperValue = value.toUpperCase();
  if (validateEnumValue(enumObj, upperValue)) {
    return upperValue as T[keyof T];
  }
  // Tentar também o valor original
  if (validateEnumValue(enumObj, value)) {
    return value as T[keyof T];
  }
  return null;
}

// Re-exportar tipos compatíveis com o sistema antigo
export type UserRole = TipoUsuario;
export const UserRoleEnum = TipoUsuario;