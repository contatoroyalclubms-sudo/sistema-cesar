"""
Schemas para o sistema avançado de Split Payments
Baseado na arquitetura MEEP para pagamentos distribuídos
"""

from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from decimal import Decimal

# ====== ENUMS ======

class TipoSplitConfiguration(str, Enum):
    PERCENTUAL = "percentual"
    FIXO = "fixo" 
    VARIAVEL = "variavel"
    CONDICIONAL = "condicional"

class StatusSplitTransaction(str, Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDO = "concluido"
    ERRO = "erro"
    CANCELADO = "cancelado"

class StatusSplitParcela(str, Enum):
    PENDENTE = "pendente"
    PROCESSADO = "processado"
    TRANSFERIDO = "transferido"
    ERRO = "erro"

class TipoDisputa(str, Enum):
    CHARGEBACK = "chargeback"
    CONTESTACAO = "contestacao"
    ERRO_SPLIT = "erro_split"
    FRAUDE = "fraude"

class StatusDisputa(str, Enum):
    ABERTA = "aberta"
    EM_ANALISE = "em_analise"
    RESOLVIDA_FAVORAVEL = "resolvida_favoravel"
    RESOLVIDA_DESFAVORAVEL = "resolvida_desfavoravel"

class MotivoEscrow(str, Enum):
    GARANTIA = "garantia"
    DISPUTA = "disputa"
    ANALISE = "analise"
    MANUAL = "manual"

class StatusEscrow(str, Enum):
    RETIDO = "retido"
    LIBERADO = "liberado"
    PERDIDO = "perdido"
    DEVOLVIDO = "devolvido"

class TipoContaBancaria(str, Enum):
    CORRENTE = "corrente"
    POUPANCA = "poupanca"

# ====== SPLIT CONFIGURATION SCHEMAS ======

class SplitConfigurationBase(BaseModel):
    evento_id: int
    nome: str
    descricao: Optional[str] = None
    tipo: TipoSplitConfiguration
    configuracao: Dict[str, Any]
    ativo: Optional[bool] = True
    aplicar_automatico: Optional[bool] = False
    condicoes_aplicacao: Optional[Dict[str, Any]] = None
    taxa_plataforma: Optional[float] = 0.0
    taxa_gateway: Optional[float] = 0.0

    @validator('taxa_plataforma', 'taxa_gateway')
    def validate_taxa(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Taxa deve estar entre 0 e 100')
        return v

class SplitConfigurationCreate(SplitConfigurationBase):
    criado_por_id: int

class SplitConfigurationUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[TipoSplitConfiguration] = None
    configuracao: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None
    aplicar_automatico: Optional[bool] = None
    condicoes_aplicacao: Optional[Dict[str, Any]] = None
    taxa_plataforma: Optional[float] = None
    taxa_gateway: Optional[float] = None

class SplitConfigurationResponse(SplitConfigurationBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime]
    criado_por_id: int

    class Config:
        from_attributes = True

# ====== SPLIT RECIPIENT SCHEMAS ======

class SplitRecipientBase(BaseModel):
    split_config_id: int
    nome: str
    documento: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    banco_codigo: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[TipoContaBancaria] = None
    percentual: Optional[float] = None
    valor_fixo: Optional[float] = None
    ordem_prioridade: Optional[int] = 0
    ativo: Optional[bool] = True
    gateway_recipient_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('documento')
    def validate_documento(cls, v):
        # Remove caracteres especiais
        doc = ''.join(filter(str.isdigit, v))
        if len(doc) not in [11, 14]:
            raise ValueError('Documento deve ser CPF (11 dígitos) ou CNPJ (14 dígitos)')
        return doc

    @validator('percentual')
    def validate_percentual(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Percentual deve estar entre 0 e 100')
        return v

class SplitRecipientCreate(SplitRecipientBase):
    pass

class SplitRecipientUpdate(BaseModel):
    nome: Optional[str] = None
    documento: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    banco_codigo: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[TipoContaBancaria] = None
    percentual: Optional[float] = None
    valor_fixo: Optional[float] = None
    ordem_prioridade: Optional[int] = None
    ativo: Optional[bool] = None
    gateway_recipient_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SplitRecipientResponse(SplitRecipientBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== SPLIT TRANSACTION SCHEMAS ======

class SplitTransactionBase(BaseModel):
    transacao_principal_id: int
    split_config_id: int
    venda_pdv_id: Optional[int] = None
    valor_total: float
    valor_liquido: float
    taxa_total: Optional[float] = 0.0
    status: Optional[StatusSplitTransaction] = StatusSplitTransaction.PENDENTE
    gateway_transaction_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('valor_total', 'valor_liquido')
    def validate_valores(cls, v):
        if v < 0:
            raise ValueError('Valores não podem ser negativos')
        return v

class SplitTransactionCreate(SplitTransactionBase):
    pass

class SplitTransactionUpdate(BaseModel):
    valor_total: Optional[float] = None
    valor_liquido: Optional[float] = None
    taxa_total: Optional[float] = None
    status: Optional[StatusSplitTransaction] = None
    gateway_transaction_id: Optional[str] = None
    erro_detalhes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SplitTransactionResponse(SplitTransactionBase):
    id: int
    processado_em: Optional[datetime]
    erro_detalhes: Optional[str]
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== SPLIT PARCELA SCHEMAS ======

class SplitParcelaBase(BaseModel):
    split_transaction_id: int
    recipient_id: int
    valor_bruto: float
    valor_liquido: float
    percentual_aplicado: Optional[float] = None
    taxa_aplicada: Optional[float] = 0.0
    status: Optional[StatusSplitParcela] = StatusSplitParcela.PENDENTE
    gateway_split_id: Optional[str] = None

class SplitParcelaCreate(SplitParcelaBase):
    pass

class SplitParcelaUpdate(BaseModel):
    valor_bruto: Optional[float] = None
    valor_liquido: Optional[float] = None
    percentual_aplicado: Optional[float] = None
    taxa_aplicada: Optional[float] = None
    status: Optional[StatusSplitParcela] = None
    gateway_split_id: Optional[str] = None
    comprovante_transferencia: Optional[str] = None
    erro_detalhes: Optional[str] = None

class SplitParcelaResponse(SplitParcelaBase):
    id: int
    data_transferencia: Optional[datetime]
    comprovante_transferencia: Optional[str]
    erro_detalhes: Optional[str]
    tentativas_processamento: int
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== SPLIT ESCROW SCHEMAS ======

class SplitEscrowBase(BaseModel):
    split_transaction_id: int
    recipient_id: int
    valor_retido: float
    motivo_retencao: MotivoEscrow
    data_liberacao_prevista: Optional[datetime] = None
    observacoes: Optional[str] = None

class SplitEscrowCreate(SplitEscrowBase):
    pass

class SplitEscrowUpdate(BaseModel):
    valor_retido: Optional[float] = None
    motivo_retencao: Optional[MotivoEscrow] = None
    data_liberacao_prevista: Optional[datetime] = None
    status: Optional[StatusEscrow] = None
    observacoes: Optional[str] = None
    liberado_por_id: Optional[int] = None

class SplitEscrowResponse(SplitEscrowBase):
    id: int
    data_retencao: datetime
    data_liberacao_efetiva: Optional[datetime]
    status: StatusEscrow
    liberado_por_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== SPLIT DISPUTA SCHEMAS ======

class SplitDisputaBase(BaseModel):
    split_transaction_id: int
    tipo_disputa: TipoDisputa
    valor_disputado: float
    descricao: Optional[str] = None
    evidencias: Optional[Dict[str, Any]] = None
    gateway_dispute_id: Optional[str] = None

class SplitDisputaCreate(SplitDisputaBase):
    pass

class SplitDisputaUpdate(BaseModel):
    tipo_disputa: Optional[TipoDisputa] = None
    valor_disputado: Optional[float] = None
    status: Optional[StatusDisputa] = None
    descricao: Optional[str] = None
    evidencias: Optional[Dict[str, Any]] = None
    decisao: Optional[str] = None
    impacto_recipients: Optional[Dict[str, Any]] = None
    resolvido_por_id: Optional[int] = None

class SplitDisputaResponse(SplitDisputaBase):
    id: int
    data_inicio: datetime
    data_resolucao: Optional[datetime]
    status: StatusDisputa
    decisao: Optional[str]
    impacto_recipients: Optional[Dict[str, Any]]
    resolvido_por_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== SCHEMAS COMPLEXOS E RELATÓRIOS ======

class SplitAnalytics(BaseModel):
    """Analytics consolidadas do sistema de split payments"""
    periodo_inicio: date
    periodo_fim: date
    total_transacoes: int
    valor_total_processado: float
    valor_total_splits: float
    total_taxa_plataforma: float
    total_taxa_gateway: float
    
    # Por status
    transacoes_por_status: Dict[str, int]
    valores_por_status: Dict[str, float]
    
    # Por recipient
    top_recipients: List[Dict[str, Any]]
    
    # Disputas e chargebacks
    total_disputas: int
    valor_disputas: float
    taxa_disputa: float
    
    # Performance
    tempo_medio_processamento: float  # em minutos
    taxa_sucesso: float  # percentual
    
    # Tendências
    evolucao_diaria: List[Dict[str, Any]]
    sazonalidade: Dict[str, Any]

class SplitTransactionCompleta(BaseModel):
    """Transação split com todos os dados relacionados"""
    transacao: SplitTransactionResponse
    parcelas: List[SplitParcelaResponse]
    escrows: List[SplitEscrowResponse]
    disputas: List[SplitDisputaResponse]
    configuracao: SplitConfigurationResponse
    recipients: List[SplitRecipientResponse]
    auditoria: List[Dict[str, Any]]  # Logs de auditoria

class SplitReconciliacaoBase(BaseModel):
    data_reconciliacao: date
    total_transacoes: int
    valor_total_bruto: float
    valor_total_liquido: float
    total_taxas: float
    total_disputes: int
    valor_disputes: float
    total_chargebacks: int
    valor_chargebacks: float
    status: str
    arquivo_reconciliacao: Optional[str] = None
    divergencias: Optional[Dict[str, Any]] = None

class SplitReconciliacaoCreate(SplitReconciliacaoBase):
    processado_por_id: int

class SplitReconciliacaoResponse(SplitReconciliacaoBase):
    id: int
    processado_por_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

class ProcessarSplitRequest(BaseModel):
    """Request para processar um split payment"""
    transacao_id: int
    split_config_id: int
    forcar_reprocessamento: Optional[bool] = False
    observacoes: Optional[str] = None

class ProcessarSplitResponse(BaseModel):
    """Response do processamento de split payment"""
    sucesso: bool
    split_transaction_id: Optional[int] = None
    mensagem: str
    detalhes: Optional[Dict[str, Any]] = None
    parcelas_criadas: int
    valor_total_splitado: float
    tempo_processamento_ms: float

class SimularSplitRequest(BaseModel):
    """Request para simular um split payment"""
    valor_transacao: float
    split_config_id: int
    taxas_adicionais: Optional[Dict[str, float]] = None

class SimularSplitResponse(BaseModel):
    """Response da simulação de split payment"""
    valor_original: float
    valor_liquido_total: float
    total_taxas: float
    
    # Simulação por recipient
    parcelas_simuladas: List[Dict[str, Any]]
    
    # Resumo
    percentual_total_distribuido: float
    valor_restante: float
    
    # Validações
    configuracao_valida: bool
    alertas: List[str]
    sugestoes: List[str]

class GatewayIntegrationConfig(BaseModel):
    """Configuração para integração com gateways"""
    gateway_provider: str  # stripe, pagarme, mercadopago, etc
    api_key: str
    webhook_secret: Optional[str] = None
    sandbox_mode: Optional[bool] = True
    configuracoes_especiais: Optional[Dict[str, Any]] = None

# ====== CREDENCIAMENTO SCHEMAS ======

class TipoCredencialBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    categoria: str
    cor_identificacao: Optional[str] = "#3B82F6"
    icone: Optional[str] = None
    template_design: Optional[Dict[str, Any]] = None
    permissoes_acesso: Optional[Dict[str, Any]] = None
    validade_padrao_dias: Optional[int] = 1
    permite_reimpressao: Optional[bool] = True
    requer_aprovacao: Optional[bool] = False
    limite_emissao: Optional[int] = None
    ativo: Optional[bool] = True

class TipoCredencialCreate(TipoCredencialBase):
    pass

class TipoCredencialUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    cor_identificacao: Optional[str] = None
    icone: Optional[str] = None
    template_design: Optional[Dict[str, Any]] = None
    permissoes_acesso: Optional[Dict[str, Any]] = None
    validade_padrao_dias: Optional[int] = None
    permite_reimpressao: Optional[bool] = None
    requer_aprovacao: Optional[bool] = None
    limite_emissao: Optional[int] = None
    ativo: Optional[bool] = None

class TipoCredencialResponse(TipoCredencialBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

class CredencialEmitidaBase(BaseModel):
    codigo_credencial: str
    tipo_credencial_id: int
    evento_id: int
    cliente_evento_id: Optional[int] = None
    nome_portador: str
    documento_portador: Optional[str] = None
    email_portador: Optional[EmailStr] = None
    telefone_portador: Optional[str] = None
    empresa_portador: Optional[str] = None
    cargo_portador: Optional[str] = None
    foto_portador: Optional[str] = None
    data_validade: Optional[datetime] = None
    observacoes: Optional[str] = None

class CredencialEmitidaCreate(CredencialEmitidaBase):
    emitida_por_id: int

class CredencialEmitidaUpdate(BaseModel):
    nome_portador: Optional[str] = None
    documento_portador: Optional[str] = None
    email_portador: Optional[EmailStr] = None
    telefone_portador: Optional[str] = None
    empresa_portador: Optional[str] = None
    cargo_portador: Optional[str] = None
    foto_portador: Optional[str] = None
    data_validade: Optional[datetime] = None
    status: Optional[str] = None
    motivo_status: Optional[str] = None
    observacoes: Optional[str] = None

class CredencialEmitidaResponse(CredencialEmitidaBase):
    id: int
    qr_code_data: Optional[str]
    data_emissao: datetime
    status: str
    motivo_status: Optional[str]
    total_impressoes: int
    ultimo_acesso: Optional[datetime]
    metadata_acesso: Optional[Dict[str, Any]]
    emitida_por_id: int
    aprovada_por_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

class LogAcessoCredencialCreate(BaseModel):
    credencial_id: int
    tipo_acesso: str
    local_acesso: str
    equipamento_id: str
    ip_equipamento: Optional[str] = None
    sucesso: bool = True
    motivo_negacao: Optional[str] = None
    dados_biometricos: Optional[Dict[str, Any]] = None
    temperatura_corporal: Optional[float] = None
    foto_acesso: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LogAcessoCredencialResponse(LogAcessoCredencialCreate):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True

class RelatorioCredenciamentoRequest(BaseModel):
    """Request para relatório de credenciamento"""
    evento_id: int
    data_inicio: date
    data_fim: date
    tipos_credencial: Optional[List[int]] = None
    incluir_acessos: Optional[bool] = True
    formato_saida: Optional[str] = "json"  # json, csv, pdf

class RelatorioCredenciamentoResponse(BaseModel):
    """Response do relatório de credenciamento"""
    total_credenciais_emitidas: int
    credenciais_por_tipo: Dict[str, int]
    credenciais_por_status: Dict[str, int]
    total_acessos: int
    acessos_por_local: Dict[str, int]
    picos_acesso: List[Dict[str, Any]]
    credenciais_detalhadas: List[CredencialEmitidaResponse]
    logs_acesso: Optional[List[LogAcessoCredencialResponse]] = None