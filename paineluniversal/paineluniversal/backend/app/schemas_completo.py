"""
📋 SCHEMAS COMPLETOS E PADRONIZADOS - BACKEND
DTOs sincronizados com modelos e frontend
Última atualização: 05/01/2025
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Union, Any, Dict
from decimal import Decimal
from enum import Enum

# Importar enums padronizados
from .enums import (
    StatusEvento, TipoUsuario, TipoLista, StatusTransacao,
    TipoProduto, StatusProduto, TipoComanda, StatusComanda,
    StatusVendaPDV, TipoPagamentoPDV, TipoMovimentacaoFinanceira,
    StatusMovimentacaoFinanceira, TipoFormaPagamento, StatusFormaPagamento,
    TipoConquista, NivelBadge, StatusImportacao, TipoOperacao,
    StatusValidacao, TipoImpressora, InterfaceImpressora, StatusImpressora,
    StatusPrintJob, TipoPrintJob
)

# Importar validadores
from .validators import (
    validar_cpf, formatar_cpf, validar_cnpj, formatar_cnpj,
    validar_email_address, validar_telefone, formatar_telefone,
    validar_nome, validar_senha, validar_valor_monetario,
    validar_quantidade, validar_percentual, validar_datetime
)

# ===== SCHEMAS BASE REUTILIZÁVEIS =====

class TimestampSchema(BaseModel):
    """Schema base com campos de timestamp"""
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaginationParams(BaseModel):
    """Parâmetros de paginação"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=1000)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")

class PaginatedResponse(BaseModel):
    """Resposta paginada genérica"""
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int

# ===== SCHEMAS DE EMPRESA =====

class EmpresaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    cnpj: str
    email: EmailStr
    telefone: Optional[str] = None
    endereco: Optional[str] = Field(None, max_length=500)

class EmpresaCreate(EmpresaBase):
    @field_validator('cnpj')
    @classmethod
    def validar_cnpj(cls, v):
        return formatar_cnpj(v)
    
    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v):
        if v:
            return formatar_telefone(v)
        return v

class EmpresaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = Field(None, max_length=500)
    ativa: Optional[bool] = None

class EmpresaResponse(EmpresaBase, TimestampSchema):
    id: int
    ativa: bool = True
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE USUÁRIO =====

class UsuarioBase(BaseModel):
    cpf: str
    nome: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    telefone: Optional[str] = None
    tipo: str = Field(default="cliente")

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)
    tipo_usuario: Optional[str] = None  # Alias para compatibilidade
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        return formatar_cpf(v)
    
    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v):
        if v:
            return formatar_telefone(v)
        return v
    
    @field_validator('tipo')
    @classmethod
    def validar_tipo(cls, v):
        tipos_validos = ['admin', 'promoter', 'cliente', 'operador', 'vendedor', 'gestor']
        if v not in tipos_validos:
            raise ValueError(f'Tipo de usuário deve ser um dos: {", ".join(tipos_validos)}')
        return v
    
    def model_post_init(self, __context):
        # Mapear tipo_usuario para tipo se fornecido
        if self.tipo_usuario and not self.tipo:
            self.tipo = self.tipo_usuario

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    tipo: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(None, min_length=6)

class UsuarioResponse(UsuarioBase, TimestampSchema):
    id: int
    ativo: bool = True
    ultimo_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioLogin(BaseModel):
    cpf: str
    senha: str
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        # Aceitar CPF com ou sem formatação
        cpf_limpo = validar_cpf(v)
        return cpf_limpo

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse

# ===== SCHEMAS DE EVENTO =====

class EventoBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    descricao: Optional[str] = None
    data_evento: datetime
    local: str = Field(..., min_length=3, max_length=255)
    endereco: Optional[str] = None
    limite_idade: int = Field(default=18, ge=0, le=120)
    capacidade_maxima: Optional[int] = Field(None, ge=1)

class EventoCreate(EventoBase):
    empresa_id: Optional[int] = None
    
    @field_validator('data_evento')
    @classmethod
    def validar_data_futura(cls, v):
        if v < datetime.now():
            raise ValueError('Data do evento deve ser futura')
        return v

class EventoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = None
    data_evento: Optional[datetime] = None
    local: Optional[str] = Field(None, min_length=3, max_length=255)
    endereco: Optional[str] = None
    limite_idade: Optional[int] = Field(None, ge=0, le=120)
    capacidade_maxima: Optional[int] = Field(None, ge=1)
    status: Optional[StatusEvento] = None

class EventoResponse(EventoBase, TimestampSchema):
    id: int
    status: StatusEvento = StatusEvento.ATIVO
    empresa_id: Optional[int] = None
    criador_id: int
    
    # Campos calculados
    total_vendas: Optional[int] = 0
    receita_total: Optional[Decimal] = Decimal('0.00')
    total_checkins: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)

class EventoDetalhado(EventoResponse):
    """Evento com informações completas"""
    listas: List['ListaResponse'] = []
    promoters: List['PromoterEventoResponse'] = []
    estatisticas: Optional[Dict[str, Any]] = {}

# ===== SCHEMAS DE LISTA =====

class ListaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    tipo: TipoLista
    preco: Decimal = Field(default=Decimal('0.00'), ge=0)
    limite_vendas: Optional[int] = Field(None, ge=0)
    descricao: Optional[str] = None
    codigo_cupom: Optional[str] = Field(None, max_length=50)
    desconto_percentual: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, le=100)

class ListaCreate(ListaBase):
    evento_id: int
    promoter_id: Optional[int] = None

class ListaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    tipo: Optional[TipoLista] = None
    preco: Optional[Decimal] = Field(None, ge=0)
    limite_vendas: Optional[int] = Field(None, ge=0)
    ativa: Optional[bool] = None
    descricao: Optional[str] = None
    codigo_cupom: Optional[str] = Field(None, max_length=50)
    desconto_percentual: Optional[Decimal] = Field(None, ge=0, le=100)

class ListaResponse(ListaBase, TimestampSchema):
    id: int
    evento_id: int
    promoter_id: Optional[int] = None
    vendas_realizadas: int = 0
    ativa: bool = True
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE TRANSAÇÃO =====

class TransacaoBase(BaseModel):
    cpf_comprador: str
    nome_comprador: str = Field(..., min_length=2, max_length=255)
    email_comprador: Optional[EmailStr] = None
    telefone_comprador: Optional[str] = None
    valor: Decimal = Field(..., ge=0)
    metodo_pagamento: Optional[str] = None

class TransacaoCreate(TransacaoBase):
    evento_id: int
    lista_id: int
    usuario_id: Optional[int] = None
    
    @field_validator('cpf_comprador')
    @classmethod
    def validar_cpf(cls, v):
        return formatar_cpf(v)

class TransacaoUpdate(BaseModel):
    status: Optional[StatusTransacao] = None
    metodo_pagamento: Optional[str] = None

class TransacaoResponse(TransacaoBase, TimestampSchema):
    id: int
    evento_id: int
    lista_id: int
    usuario_id: Optional[int] = None
    status: StatusTransacao = StatusTransacao.PENDENTE
    codigo_transacao: Optional[str] = None
    qr_code_ticket: Optional[str] = None
    ip_origem: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE CHECKIN =====

class CheckinBase(BaseModel):
    cpf: str
    nome: str = Field(..., min_length=2, max_length=255)

class CheckinCreate(CheckinBase):
    evento_id: int
    usuario_id: Optional[int] = None
    transacao_id: Optional[int] = None
    metodo_checkin: Optional[str] = Field(None, pattern="^(cpf|qr_code|cartao)$")
    validacao_cpf: Optional[str] = Field(None, min_length=3, max_length=3)
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        return validar_cpf(v)

class CheckinResponse(CheckinBase):
    id: int
    evento_id: int
    usuario_id: Optional[int] = None
    transacao_id: Optional[int] = None
    metodo_checkin: Optional[str] = None
    ip_origem: Optional[str] = None
    checkin_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE PRODUTO =====

class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    descricao: Optional[str] = None
    tipo: TipoProduto
    preco: Decimal = Field(..., ge=0)
    codigo_interno: Optional[str] = Field(None, max_length=20)
    categoria: Optional[str] = Field(None, max_length=100)
    imagem_url: Optional[str] = None

class ProdutoCreate(ProdutoBase):
    estoque_atual: Optional[int] = Field(default=0, ge=0)
    estoque_minimo: Optional[int] = Field(default=0, ge=0)
    estoque_maximo: Optional[int] = Field(default=1000, ge=0)
    controla_estoque: bool = True
    empresa_id: Optional[int] = None

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    descricao: Optional[str] = None
    tipo: Optional[TipoProduto] = None
    preco: Optional[Decimal] = Field(None, ge=0)
    codigo_interno: Optional[str] = Field(None, max_length=20)
    estoque_atual: Optional[int] = Field(None, ge=0)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    estoque_maximo: Optional[int] = Field(None, ge=0)
    controla_estoque: Optional[bool] = None
    status: Optional[StatusProduto] = None
    categoria: Optional[str] = Field(None, max_length=100)
    imagem_url: Optional[str] = None

class ProdutoResponse(ProdutoBase, TimestampSchema):
    id: int
    estoque_atual: int = 0
    estoque_minimo: int = 0
    estoque_maximo: int = 1000
    controla_estoque: bool = True
    status: StatusProduto = StatusProduto.ATIVO
    empresa_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE VENDA PDV =====

class VendaPDVBase(BaseModel):
    cpf_cliente: Optional[str] = None
    nome_cliente: Optional[str] = None
    tipo_pagamento: TipoPagamentoPDV

class ItemVendaPDV(BaseModel):
    produto_id: int
    quantidade: int = Field(..., ge=1)
    preco_unitario: Optional[Decimal] = None
    desconto_aplicado: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0)
    observacoes: Optional[str] = None

class VendaPDVCreate(VendaPDVBase):
    evento_id: int
    comanda_id: Optional[int] = None
    promoter_id: Optional[int] = None
    cupom_codigo: Optional[str] = None
    itens: List[ItemVendaPDV]
    observacoes: Optional[str] = None

class VendaPDVResponse(VendaPDVBase, TimestampSchema):
    id: int
    numero_venda: str
    evento_id: int
    valor_total: Decimal
    valor_desconto: Decimal = Decimal('0.00')
    valor_final: Decimal
    status: StatusVendaPDV = StatusVendaPDV.PENDENTE
    comanda_id: Optional[int] = None
    empresa_id: Optional[int] = None
    usuario_vendedor_id: int
    promoter_id: Optional[int] = None
    cupom_codigo: Optional[str] = None
    observacoes: Optional[str] = None
    ip_origem: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE COMANDA =====

class ComandaBase(BaseModel):
    numero_comanda: str = Field(..., max_length=20)
    tipo: TipoComanda
    cpf_cliente: Optional[str] = None
    nome_cliente: Optional[str] = None

class ComandaCreate(ComandaBase):
    evento_id: int
    empresa_id: Optional[int] = None
    codigo_rfid: Optional[str] = Field(None, max_length=50)
    qr_code: Optional[str] = None

class ComandaRecarga(BaseModel):
    valor: Decimal = Field(..., gt=0)
    tipo_pagamento: TipoPagamentoPDV

class ComandaResponse(ComandaBase, TimestampSchema):
    id: int
    evento_id: int
    empresa_id: Optional[int] = None
    codigo_rfid: Optional[str] = None
    qr_code: Optional[str] = None
    saldo_atual: Decimal = Decimal('0.00')
    saldo_bloqueado: Decimal = Decimal('0.00')
    status: StatusComanda = StatusComanda.ATIVA
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS FINANCEIROS =====

class MovimentacaoFinanceiraBase(BaseModel):
    tipo: TipoMovimentacaoFinanceira
    categoria: str = Field(..., max_length=100)
    descricao: str
    valor: Decimal = Field(..., ge=0)

class MovimentacaoFinanceiraCreate(MovimentacaoFinanceiraBase):
    evento_id: int
    promoter_id: Optional[int] = None
    numero_documento: Optional[str] = None
    observacoes: Optional[str] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    metodo_pagamento: Optional[str] = None

class MovimentacaoFinanceiraResponse(MovimentacaoFinanceiraBase, TimestampSchema):
    id: int
    evento_id: int
    status: StatusMovimentacaoFinanceira = StatusMovimentacaoFinanceira.PENDENTE
    usuario_responsavel_id: int
    promoter_id: Optional[int] = None
    comprovante_url: Optional[str] = None
    numero_documento: Optional[str] = None
    observacoes: Optional[str] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    metodo_pagamento: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class CaixaEventoBase(BaseModel):
    saldo_inicial: Decimal = Field(default=Decimal('0.00'), ge=0)
    observacoes_abertura: Optional[str] = None

class CaixaEventoCreate(CaixaEventoBase):
    evento_id: int

class CaixaEventoFechar(BaseModel):
    observacoes_fechamento: Optional[str] = None

class CaixaEventoResponse(CaixaEventoBase):
    id: int
    evento_id: int
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    total_entradas: Decimal = Decimal('0.00')
    total_saidas: Decimal = Decimal('0.00')
    total_vendas_pdv: Decimal = Decimal('0.00')
    total_vendas_listas: Decimal = Decimal('0.00')
    saldo_final: Decimal = Decimal('0.00')
    status: str = "aberto"
    usuario_abertura_id: int
    usuario_fechamento_id: Optional[int] = None
    observacoes_fechamento: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE GAMIFICAÇÃO =====

class ConquistaBase(BaseModel):
    nome: str = Field(..., max_length=100)
    descricao: str
    tipo: TipoConquista
    criterio_valor: int = Field(..., ge=1)
    badge_nivel: NivelBadge
    icone: Optional[str] = Field(None, max_length=50)

class ConquistaCreate(ConquistaBase):
    pass

class ConquistaResponse(ConquistaBase):
    id: int
    ativa: bool = True
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PromoterConquistaResponse(BaseModel):
    id: int
    promoter_id: int
    conquista_id: int
    evento_id: Optional[int] = None
    valor_alcancado: int
    data_conquista: datetime
    notificado: bool = False
    conquista: ConquistaResponse
    
    model_config = ConfigDict(from_attributes=True)

class MetricaPromoterResponse(BaseModel):
    id: int
    promoter_id: int
    evento_id: Optional[int] = None
    periodo_inicio: date
    periodo_fim: date
    total_vendas: int = 0
    receita_gerada: Decimal = Decimal('0.00')
    total_convidados: int = 0
    total_presentes: int = 0
    taxa_presenca: Decimal = Decimal('0.00')
    taxa_conversao: Decimal = Decimal('0.00')
    crescimento_vendas: Decimal = Decimal('0.00')
    posicao_vendas: Optional[int] = None
    posicao_presenca: Optional[int] = None
    posicao_geral: Optional[int] = None
    badge_atual: NivelBadge = NivelBadge.BRONZE
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE IMPORT/EXPORT =====

class OperacaoImportExportBase(BaseModel):
    tipo_operacao: TipoOperacao
    nome_arquivo: str = Field(..., max_length=255)
    formato_arquivo: str = Field(..., pattern="^(csv|xlsx|json|xml)$")

class OperacaoImportExportCreate(OperacaoImportExportBase):
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    mapeamento_campos: Optional[Dict[str, str]] = None
    filtros_aplicados: Optional[Dict[str, Any]] = None
    campos_personalizados: Optional[List[str]] = None

class OperacaoImportExportResponse(OperacaoImportExportBase):
    id: int
    usuario_id: int
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    tamanho_arquivo: Optional[int] = None
    status: StatusImportacao = StatusImportacao.PENDENTE
    total_registros: int = 0
    registros_processados: int = 0
    registros_sucesso: int = 0
    registros_erro: int = 0
    registros_aviso: int = 0
    mapeamento_campos: Optional[Dict[str, str]] = None
    filtros_aplicados: Optional[Dict[str, Any]] = None
    campos_personalizados: Optional[List[str]] = None
    inicio_processamento: Optional[datetime] = None
    fim_processamento: Optional[datetime] = None
    criado_em: datetime
    log_detalhado: Optional[str] = None
    url_arquivo_resultado: Optional[str] = None
    resumo_operacao: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE IMPRESSORA =====

class ImpressoraBase(BaseModel):
    nome: str = Field(..., max_length=255)
    tipo: TipoImpressora
    interface: InterfaceImpressora
    endereco: str = Field(..., max_length=255)
    localizacao: Optional[str] = Field(None, max_length=255)

class ImpressoraCreate(ImpressoraBase):
    evento_id: int
    largura_mm: int = Field(default=80, ge=58, le=80)
    colunas: int = Field(default=42, ge=32, le=48)
    perfil_escpos: str = Field(default="epson", pattern="^(epson|star|bematech)$")
    densidade: int = Field(default=8, ge=1, le=8)
    impressora_backup_id: Optional[str] = None

class ImpressoraResponse(ImpressoraBase, TimestampSchema):
    id: str
    evento_id: int
    largura_mm: int = 80
    colunas: int = 42
    perfil_escpos: str = "epson"
    densidade: int = 8
    ativo: bool = True
    impressora_backup_id: Optional[str] = None
    status: StatusImpressora = StatusImpressora.OFFLINE
    ultimo_heartbeat: Optional[datetime] = None
    ip_bridge: Optional[str] = None
    versao_driver: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

class PrintJobBase(BaseModel):
    tipo: TipoPrintJob
    payload: Dict[str, Any]
    prioridade: int = Field(default=1, ge=1, le=3)

class PrintJobCreate(PrintJobBase):
    impressora_id: str
    evento_id: int
    template_id: Optional[int] = None
    venda_pdv_id: Optional[int] = None
    comanda_id: Optional[int] = None
    cpf_operador: str

class PrintJobResponse(PrintJobBase):
    id: str
    impressora_id: str
    evento_id: int
    template_id: Optional[int] = None
    venda_pdv_id: Optional[int] = None
    comanda_id: Optional[int] = None
    status: StatusPrintJob = StatusPrintJob.QUEUED
    tentativas: int = 0
    max_tentativas: int = 3
    erro_msg: Optional[str] = None
    cpf_operador: str
    usuario_id: int
    ip_cliente: Optional[str] = None
    criado_em: datetime
    processado_em: Optional[datetime] = None
    impresso_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# ===== SCHEMAS DE RESPOSTA PADRÃO =====

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[List[ErrorDetail]] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    database: str = "connected"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)

# Forward references para relacionamentos circulares
EventoDetalhado.model_rebuild()
ListaResponse.model_rebuild()

# Exportar schemas principais
__all__ = [
    # Base
    'TimestampSchema', 'PaginationParams', 'PaginatedResponse',
    # Empresa
    'EmpresaBase', 'EmpresaCreate', 'EmpresaUpdate', 'EmpresaResponse',
    # Usuário
    'UsuarioBase', 'UsuarioCreate', 'UsuarioUpdate', 'UsuarioResponse', 'UsuarioLogin', 'TokenResponse',
    # Evento
    'EventoBase', 'EventoCreate', 'EventoUpdate', 'EventoResponse', 'EventoDetalhado',
    # Lista
    'ListaBase', 'ListaCreate', 'ListaUpdate', 'ListaResponse',
    # Transação
    'TransacaoBase', 'TransacaoCreate', 'TransacaoUpdate', 'TransacaoResponse',
    # Checkin
    'CheckinBase', 'CheckinCreate', 'CheckinResponse',
    # Produto
    'ProdutoBase', 'ProdutoCreate', 'ProdutoUpdate', 'ProdutoResponse',
    # Venda PDV
    'VendaPDVBase', 'ItemVendaPDV', 'VendaPDVCreate', 'VendaPDVResponse',
    # Comanda
    'ComandaBase', 'ComandaCreate', 'ComandaRecarga', 'ComandaResponse',
    # Financeiro
    'MovimentacaoFinanceiraBase', 'MovimentacaoFinanceiraCreate', 'MovimentacaoFinanceiraResponse',
    'CaixaEventoBase', 'CaixaEventoCreate', 'CaixaEventoFechar', 'CaixaEventoResponse',
    # Gamificação
    'ConquistaBase', 'ConquistaCreate', 'ConquistaResponse', 'PromoterConquistaResponse', 'MetricaPromoterResponse',
    # Import/Export
    'OperacaoImportExportBase', 'OperacaoImportExportCreate', 'OperacaoImportExportResponse',
    # Impressora
    'ImpressoraBase', 'ImpressoraCreate', 'ImpressoraResponse', 'PrintJobBase', 'PrintJobCreate', 'PrintJobResponse',
    # Respostas
    'ErrorDetail', 'ErrorResponse', 'SuccessResponse', 'HealthCheckResponse'
]