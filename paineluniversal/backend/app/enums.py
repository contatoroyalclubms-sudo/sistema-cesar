"""
🎯 ENUMS PADRONIZADOS - SISTEMA COMPLETO
Todos os enums do sistema centralizados e padronizados
Última atualização: 05/01/2025
"""

from enum import Enum

# ===== ENUMS CORE =====

class StatusEvento(Enum):
    """Status possíveis de um evento"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    CANCELADO = "CANCELADO"
    FINALIZADO = "FINALIZADO"
    RASCUNHO = "RASCUNHO"

class TipoUsuario(Enum):
    """Tipos de usuário do sistema"""
    ADMIN = "admin"
    PROMOTER = "promoter"
    CLIENTE = "cliente"
    OPERADOR = "operador"
    VENDEDOR = "vendedor"
    GESTOR = "gestor"

class TipoLista(Enum):
    """Tipos de lista de convidados"""
    VIP = "VIP"
    FREE = "FREE"
    PAGANTE = "PAGANTE"
    PROMOTER = "PROMOTER"
    ANIVERSARIO = "ANIVERSARIO"
    DESCONTO = "DESCONTO"
    PREMIUM = "PREMIUM"
    COMUM = "COMUM"

class StatusTransacao(Enum):
    """Status de transações financeiras"""
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    CANCELADA = "CANCELADA"
    ESTORNADA = "ESTORNADA"
    PROCESSANDO = "PROCESSANDO"
    ERRO = "ERRO"

# ===== ENUMS PRODUTOS E PDV =====

class TipoProduto(Enum):
    """Tipos de produtos do sistema"""
    BEBIDA = "BEBIDA"
    COMIDA = "COMIDA"
    INGRESSO = "INGRESSO"
    FICHA = "FICHA"
    COMBO = "COMBO"
    VOUCHER = "VOUCHER"
    SERVICO = "SERVICO"
    TAXA = "TAXA"
    OUTROS = "OUTROS"

class StatusProduto(Enum):
    """Status de produtos"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    ESGOTADO = "ESGOTADO"
    PROMOCAO = "PROMOCAO"
    SAZONAL = "SAZONAL"

class TipoComanda(Enum):
    """Tipos de comanda"""
    FISICA = "FISICA"
    VIRTUAL = "VIRTUAL"
    RFID = "RFID"
    NFC = "NFC"
    QR_CODE = "QR_CODE"
    PULSEIRA = "PULSEIRA"

class StatusComanda(Enum):
    """Status de comandas"""
    ATIVA = "ATIVA"
    BLOQUEADA = "BLOQUEADA"
    CANCELADA = "CANCELADA"
    PERDIDA = "PERDIDA"
    FECHADA = "FECHADA"

class StatusVendaPDV(Enum):
    """Status de vendas PDV"""
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    CANCELADA = "CANCELADA"
    ESTORNADA = "ESTORNADA"
    PARCIAL = "PARCIAL"

class TipoPagamentoPDV(Enum):
    """Tipos de pagamento PDV"""
    PIX = "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    DINHEIRO = "DINHEIRO"
    SALDO_COMANDA = "SALDO_COMANDA"
    VOUCHER = "VOUCHER"
    SPLIT = "SPLIT"
    TRANSFERENCIA = "TRANSFERENCIA"
    BOLETO = "BOLETO"
    CREDITO_LOJA = "CREDITO_LOJA"

# ===== ENUMS FINANCEIRO =====

class TipoMovimentacaoFinanceira(Enum):
    """Tipos de movimentação financeira"""
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"
    REPASSE_PROMOTER = "REPASSE_PROMOTER"
    RECEITA_VENDAS = "RECEITA_VENDAS"
    RECEITA_LISTAS = "RECEITA_LISTAS"
    DESPESA_OPERACIONAL = "DESPESA_OPERACIONAL"
    DESPESA_FORNECEDOR = "DESPESA_FORNECEDOR"
    TAXA = "TAXA"
    COMISSAO = "COMISSAO"

class StatusMovimentacaoFinanceira(Enum):
    """Status de movimentações financeiras"""
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    CANCELADA = "CANCELADA"
    ESTORNADA = "ESTORNADA"
    AGENDADA = "AGENDADA"

class TipoFormaPagamento(Enum):
    """Tipos de forma de pagamento"""
    DINHEIRO = "DINHEIRO"
    PIX = "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    TRANSFERENCIA = "TRANSFERENCIA"
    BOLETO = "BOLETO"
    VOUCHER = "VOUCHER"
    CREDITO_LOJA = "CREDITO_LOJA"
    CHEQUE = "CHEQUE"
    VALE_REFEICAO = "VALE_REFEICAO"
    VALE_ALIMENTACAO = "VALE_ALIMENTACAO"

class StatusFormaPagamento(Enum):
    """Status de formas de pagamento"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    MANUTENCAO = "MANUTENCAO"
    BLOQUEADO = "BLOQUEADO"

# ===== ENUMS GAMIFICAÇÃO =====

class TipoConquista(Enum):
    """Tipos de conquista/achievement"""
    VENDAS = "VENDAS"
    PRESENCA = "PRESENCA"
    FIDELIDADE = "FIDELIDADE"
    CRESCIMENTO = "CRESCIMENTO"
    ESPECIAL = "ESPECIAL"
    MARCO = "MARCO"
    DESAFIO = "DESAFIO"

class NivelBadge(Enum):
    """Níveis de badge/medalha"""
    BRONZE = "BRONZE"
    PRATA = "PRATA"
    OURO = "OURO"
    PLATINA = "PLATINA"
    DIAMANTE = "DIAMANTE"
    LENDA = "LENDA"
    MESTRE = "MESTRE"

# ===== ENUMS IMPORT/EXPORT =====

class StatusImportacao(Enum):
    """Status de operações de importação"""
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDA = "CONCLUIDA"
    ERRO = "ERRO"
    CANCELADA = "CANCELADA"
    PAUSADA = "PAUSADA"
    VALIDANDO = "VALIDANDO"

class TipoOperacao(Enum):
    """Tipos de operação import/export"""
    IMPORTACAO = "IMPORTACAO"
    EXPORTACAO = "EXPORTACAO"
    SINCRONIZACAO = "SINCRONIZACAO"
    BACKUP = "BACKUP"
    RESTAURACAO = "RESTAURACAO"

class StatusValidacao(Enum):
    """Status de validação de dados"""
    VALIDO = "VALIDO"
    ERRO_CRITICO = "ERRO_CRITICO"
    AVISO = "AVISO"
    IGNORADO = "IGNORADO"
    CORRIGIDO = "CORRIGIDO"

# ===== ENUMS IMPRESSORAS =====

class TipoImpressora(Enum):
    """Tipos de impressora térmica"""
    COZINHA = "COZINHA"
    BAR = "BAR"
    SOBREMESA = "SOBREMESA"
    CAIXA = "CAIXA"
    GERENCIAL = "GERENCIAL"
    PEDIDO = "PEDIDO"
    COMANDA = "COMANDA"

class InterfaceImpressora(Enum):
    """Interfaces de conexão de impressora"""
    USB = "USB"
    NETWORK = "NETWORK"
    BLUETOOTH = "BLUETOOTH"
    SERIAL = "SERIAL"
    PARALELA = "PARALELA"

class StatusImpressora(Enum):
    """Status de impressoras"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERRO = "ERRO"
    MANUTENCAO = "MANUTENCAO"
    IMPRIMINDO = "IMPRIMINDO"
    PAUSADA = "PAUSADA"

class StatusPrintJob(Enum):
    """Status de jobs de impressão"""
    QUEUED = "QUEUED"
    PRINTING = "PRINTING"
    DONE = "DONE"
    ERROR = "ERROR"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"

class TipoPrintJob(Enum):
    """Tipos de job de impressão"""
    RECIBO_CAIXA = "RECIBO_CAIXA"
    PEDIDO_COZINHA = "PEDIDO_COZINHA"
    PEDIDO_BAR = "PEDIDO_BAR"
    COMANDA_RECHARGE = "COMANDA_RECHARGE"
    RELATORIO = "RELATORIO"
    ETIQUETA = "ETIQUETA"
    CUPOM_FISCAL = "CUPOM_FISCAL"

# ===== ENUMS ESTOQUE =====

class TipoMovimentoEstoque(Enum):
    """Tipos de movimento de estoque"""
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"
    TRANSFERENCIA = "TRANSFERENCIA"
    DEVOLUCAO = "DEVOLUCAO"
    PERDA = "PERDA"
    INVENTARIO = "INVENTARIO"

class StatusEstoque(Enum):
    """Status de itens em estoque"""
    DISPONIVEL = "DISPONIVEL"
    RESERVADO = "RESERVADO"
    BLOQUEADO = "BLOQUEADO"
    EM_TRANSITO = "EM_TRANSITO"
    VENCIDO = "VENCIDO"
    QUARENTENA = "QUARENTENA"

# ===== ENUMS CASHLESS =====

class StatusCashless(Enum):
    """Status do sistema cashless"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    SUSPENSO = "SUSPENSO"
    BLOQUEADO = "BLOQUEADO"
    EXPIRADO = "EXPIRADO"

class TipoRecarga(Enum):
    """Tipos de recarga cashless"""
    DINHEIRO = "DINHEIRO"
    PIX = "PIX"
    CARTAO = "CARTAO"
    TRANSFERENCIA = "TRANSFERENCIA"
    CORTESIA = "CORTESIA"
    PROMOCIONAL = "PROMOCIONAL"

# ===== ENUMS KDS (Kitchen Display System) =====

class StatusPedidoKDS(Enum):
    """Status de pedidos no KDS"""
    RECEBIDO = "RECEBIDO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"
    PAUSADO = "PAUSADO"

class PrioridadePedidoKDS(Enum):
    """Prioridade de pedidos no KDS"""
    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"
    URGENTE = "URGENTE"
    VIP = "VIP"

# ===== ENUMS FIDELIDADE =====

class TipoProgramaFidelidade(Enum):
    """Tipos de programa de fidelidade"""
    PONTOS = "PONTOS"
    CASHBACK = "CASHBACK"
    NIVEIS = "NIVEIS"
    SELOS = "SELOS"
    MILHAS = "MILHAS"
    DESCONTOS = "DESCONTOS"

class StatusFidelidade(Enum):
    """Status de participante de fidelidade"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    SUSPENSO = "SUSPENSO"
    EXPIRADO = "EXPIRADO"
    BLOQUEADO = "BLOQUEADO"

# ===== ENUMS AUTOMAÇÃO =====

class TipoGatilho(Enum):
    """Tipos de gatilho para automações"""
    EVENTO = "EVENTO"
    HORARIO = "HORARIO"
    CONDICAO = "CONDICAO"
    WEBHOOK = "WEBHOOK"
    MANUAL = "MANUAL"
    API = "API"
    SENSOR = "SENSOR"

class StatusAutomacao(Enum):
    """Status de automações"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    PAUSADO = "PAUSADO"
    ERRO = "ERRO"
    TESTANDO = "TESTANDO"
    AGENDADO = "AGENDADO"

# ===== ENUMS INTEGRAÇÕES =====

class TipoIntegracao(Enum):
    """Tipos de integração externa"""
    COMUNICACAO = "COMUNICACAO"
    ERP = "ERP"
    FISCAL = "FISCAL"
    DELIVERY = "DELIVERY"
    PAGAMENTO = "PAGAMENTO"
    MARKETING = "MARKETING"
    CRM = "CRM"
    BI = "BI"

class StatusIntegracao(Enum):
    """Status de integrações"""
    CONECTADO = "CONECTADO"
    DESCONECTADO = "DESCONECTADO"
    ERRO = "ERRO"
    SINCRONIZANDO = "SINCRONIZANDO"
    PAUSADO = "PAUSADO"
    AUTENTICANDO = "AUTENTICANDO"

# ===== FUNÇÕES AUXILIARES =====

def get_enum_values(enum_class: Enum) -> list:
    """Retorna lista com todos os valores de um enum"""
    return [e.value for e in enum_class]

def get_enum_choices(enum_class: Enum) -> list:
    """Retorna lista de tuplas (value, name) para choices"""
    return [(e.value, e.name) for e in enum_class]

def validate_enum_value(enum_class: Enum, value: str) -> bool:
    """Valida se um valor pertence ao enum"""
    return value in get_enum_values(enum_class)

# Exportar todos os enums
__all__ = [
    # Core
    'StatusEvento', 'TipoUsuario', 'TipoLista', 'StatusTransacao',
    # Produtos e PDV
    'TipoProduto', 'StatusProduto', 'TipoComanda', 'StatusComanda',
    'StatusVendaPDV', 'TipoPagamentoPDV',
    # Financeiro
    'TipoMovimentacaoFinanceira', 'StatusMovimentacaoFinanceira',
    'TipoFormaPagamento', 'StatusFormaPagamento',
    # Gamificação
    'TipoConquista', 'NivelBadge',
    # Import/Export
    'StatusImportacao', 'TipoOperacao', 'StatusValidacao',
    # Impressoras
    'TipoImpressora', 'InterfaceImpressora', 'StatusImpressora',
    'StatusPrintJob', 'TipoPrintJob',
    # Estoque
    'TipoMovimentoEstoque', 'StatusEstoque',
    # Cashless
    'StatusCashless', 'TipoRecarga',
    # KDS
    'StatusPedidoKDS', 'PrioridadePedidoKDS',
    # Fidelidade
    'TipoProgramaFidelidade', 'StatusFidelidade',
    # Automação
    'TipoGatilho', 'StatusAutomacao',
    # Integrações
    'TipoIntegracao', 'StatusIntegracao',
    # Funções
    'get_enum_values', 'get_enum_choices', 'validate_enum_value'
]