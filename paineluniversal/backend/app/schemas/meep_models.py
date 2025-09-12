"""
MEEP Domain Schemas - Modelos Pydantic
Kit Legal - Sem código proprietário
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import re

# Enums

class EventType(str, Enum):
    """Tipos de evento"""
    CONFERENCIA = "CONFERENCIA"
    WORKSHOP = "WORKSHOP"
    SHOW = "SHOW"
    FESTIVAL = "FESTIVAL"
    FESTA = "FESTA"
    CORPORATIVO = "CORPORATIVO"
    ESPORTIVO = "ESPORTIVO"
    FEIRA = "FEIRA"
    OUTROS = "OUTROS"

class TicketType(str, Enum):
    """Tipos de ingresso"""
    VIP = "VIP"
    PAGANTE = "PAGANTE"
    FREE = "FREE"
    PROMOCIONAL = "PROMOCIONAL"
    ESTUDANTE = "ESTUDANTE"
    IDOSO = "IDOSO"

class PaymentMethod(str, Enum):
    """Métodos de pagamento"""
    DINHEIRO = "DINHEIRO"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    PIX = "PIX"
    BOLETO = "BOLETO"
    TRANSFERENCIA = "TRANSFERENCIA"
    VOUCHER = "VOUCHER"
    OUTROS = "OUTROS"

class PaymentStatus(str, Enum):
    """Status de pagamento"""
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    PAGO = "PAGO"
    APROVADO = "APROVADO"
    CANCELADO = "CANCELADO"
    RECUSADO = "RECUSADO"
    REEMBOLSADO = "REEMBOLSADO"
    CHARGEBACK = "CHARGEBACK"

class CheckinMethod(str, Enum):
    """Métodos de check-in"""
    QRCODE = "QRCODE"
    CODIGO_BARRAS = "CODIGO_BARRAS"
    NFC = "NFC"
    MANUAL = "MANUAL"
    CPF = "CPF"
    FACIAL = "FACIAL"

# Base Models

class CPFMixin(BaseModel):
    """Mixin para validação de CPF"""
    
    @validator('cpf', 'documento', 'cliente_cpf', 'participante_cpf', check_fields=False)
    def validate_cpf(cls, v):
        if not v:
            return v
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', str(v))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # Verifica se todos os dígitos são iguais
        if len(set(cpf)) == 1:
            raise ValueError('CPF inválido')
        
        # Validação dos dígitos verificadores
        for i in range(9, 11):
            value = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != int(cpf[i]):
                raise ValueError('CPF inválido')
        
        return cpf

class AddressSchema(BaseModel):
    """Schema de endereço"""
    logradouro: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=8)
    
    @validator('cep')
    def validate_cep(cls, v):
        if v:
            cep = re.sub(r'\D', '', v)
            if len(cep) != 8:
                raise ValueError('CEP deve ter 8 dígitos')
            return cep
        return v

# Event Schemas

class EventBase(BaseModel):
    """Schema base de evento"""
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    local: Optional[str] = Field(None, max_length=255)
    capacidade: int = Field(0, ge=0)
    tipo: EventType = EventType.OUTROS
    status: str = "ATIVO"
    organizador: Optional[str] = Field(None, max_length=255)
    
    @validator('data_fim')
    def validate_dates(cls, v, values):
        if 'data_inicio' in values and v < values['data_inicio']:
            raise ValueError('Data fim deve ser após data início')
        return v

class EventCreate(EventBase):
    """Schema para criar evento"""
    pass

class EventUpdate(BaseModel):
    """Schema para atualizar evento"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    local: Optional[str] = Field(None, max_length=255)
    capacidade: Optional[int] = Field(None, ge=0)
    tipo: Optional[EventType] = None
    status: Optional[str] = None
    organizador: Optional[str] = Field(None, max_length=255)

class EventResponse(EventBase):
    """Schema de resposta de evento"""
    id: int
    meep_event_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Ticket Schemas

class TicketBase(BaseModel):
    """Schema base de ingresso"""
    nome: str = Field(..., min_length=1, max_length=255)
    tipo: TicketType = TicketType.PAGANTE
    preco: float = Field(0, ge=0)
    quantidade: int = Field(0, ge=0)
    vendidos: int = Field(0, ge=0)
    lote: int = Field(1, ge=1)
    descricao: Optional[str] = None
    beneficios: List[str] = []
    restricoes: List[str] = []
    data_inicio_vendas: Optional[datetime] = None
    data_fim_vendas: Optional[datetime] = None
    
    @validator('vendidos')
    def validate_vendidos(cls, v, values):
        if 'quantidade' in values and v > values['quantidade']:
            raise ValueError('Vendidos não pode ser maior que quantidade')
        return v

class TicketCreate(TicketBase):
    """Schema para criar ingresso"""
    evento_id: int

class TicketUpdate(BaseModel):
    """Schema para atualizar ingresso"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    tipo: Optional[TicketType] = None
    preco: Optional[float] = Field(None, ge=0)
    quantidade: Optional[int] = Field(None, ge=0)
    vendidos: Optional[int] = Field(None, ge=0)
    lote: Optional[int] = Field(None, ge=1)
    descricao: Optional[str] = None
    beneficios: Optional[List[str]] = None
    restricoes: Optional[List[str]] = None
    data_inicio_vendas: Optional[datetime] = None
    data_fim_vendas: Optional[datetime] = None

class TicketResponse(TicketBase):
    """Schema de resposta de ingresso"""
    id: int
    evento_id: int
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Attendee Schemas

class AttendeeBase(BaseModel):
    """Schema base de participante"""
    cpf: str = Field(..., min_length=11, max_length=11)
    nome: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=20)
    documento: Optional[str] = Field(None, max_length=20)
    tipo_documento: str = "CPF"
    data_nascimento: Optional[date] = None
    genero: Optional[str] = Field(None, max_length=20)
    endereco: Optional[AddressSchema] = None
    
    @validator('cpf')
    def validate_cpf(cls, v):
        if not v:
            raise ValueError('CPF é obrigatório')
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', str(v))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # CPF de teste
        if cpf == "00000000000":
            return cpf
        
        # Verifica se todos os dígitos são iguais
        if len(set(cpf)) == 1:
            raise ValueError('CPF inválido')
        
        # Validação dos dígitos verificadores
        for i in range(9, 11):
            value = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != int(cpf[i]):
                raise ValueError('CPF inválido')
        
        return cpf
    
    @validator('telefone')
    def validate_telefone(cls, v):
        if v:
            telefone = re.sub(r'\D', '', v)
            if len(telefone) < 10 or len(telefone) > 13:
                raise ValueError('Telefone inválido')
            return telefone
        return v

class AttendeeCreate(AttendeeBase):
    """Schema para criar participante"""
    pass

class AttendeeUpdate(BaseModel):
    """Schema para atualizar participante"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None
    genero: Optional[str] = Field(None, max_length=20)
    endereco: Optional[AddressSchema] = None

class AttendeeResponse(AttendeeBase):
    """Schema de resposta de participante"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Check-in Schemas

class CheckinBase(BaseModel):
    """Schema base de check-in"""
    evento_id: int
    participante_cpf: str = Field(..., min_length=11, max_length=11)
    ingresso_id: Optional[int] = None
    data_hora: datetime = Field(default_factory=datetime.utcnow)
    metodo: CheckinMethod = CheckinMethod.MANUAL
    portao: str = Field("Principal", max_length=100)
    operador: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    dispositivo: Optional[str] = Field(None, max_length=255)

class CheckinCreate(CheckinBase):
    """Schema para criar check-in"""
    pass

class CheckinResponse(CheckinBase):
    """Schema de resposta de check-in"""
    id: int
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Transaction Schemas

class TransactionBase(BaseModel):
    """Schema base de transação"""
    codigo: str = Field(..., min_length=1, max_length=100)
    tipo: str = "VENDA"
    valor: float = Field(..., gt=0)
    taxa: float = Field(0, ge=0)
    valor_liquido: float = Field(0, ge=0)
    metodo_pagamento: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDENTE
    cliente_cpf: str = Field(..., min_length=11, max_length=11)
    data_criacao: datetime = Field(default_factory=datetime.utcnow)
    data_pagamento: Optional[datetime] = None
    parcelas: int = Field(1, ge=1, le=12)
    gateway: Optional[str] = Field(None, max_length=100)
    gateway_id: Optional[str] = Field(None, max_length=255)
    
    @validator('valor_liquido', always=True)
    def calculate_valor_liquido(cls, v, values):
        if 'valor' in values and 'taxa' in values:
            return values['valor'] - values['taxa']
        return v

class TransactionCreate(TransactionBase):
    """Schema para criar transação"""
    evento_id: Optional[int] = None

class TransactionUpdate(BaseModel):
    """Schema para atualizar transação"""
    status: Optional[PaymentStatus] = None
    data_pagamento: Optional[datetime] = None
    gateway_id: Optional[str] = Field(None, max_length=255)

class TransactionResponse(TransactionBase):
    """Schema de resposta de transação"""
    id: int
    evento_id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Analytics Schemas

class MetricsSchema(BaseModel):
    """Schema de métricas"""
    vendas_total: int = 0
    vendas_hoje: int = 0
    receita_total: float = 0
    receita_hoje: float = 0
    checkins_total: int = 0
    checkins_hoje: int = 0
    taxa_conversao: float = 0
    ticket_medio: float = 0
    ocupacao: float = 0

class DemographicsSchema(BaseModel):
    """Schema de demográficos"""
    genero: Dict[str, int] = {}
    idade: Dict[str, int] = {}
    cidade: Dict[str, int] = {}
    estado: Dict[str, int] = {}

class AnalyticsBase(BaseModel):
    """Schema base de analytics"""
    evento_id: int
    data: date = Field(default_factory=lambda: date.today())
    metricas: MetricsSchema
    demograficos: DemographicsSchema
    canais: Dict[str, int] = {}
    horarios_pico: List[str] = []

class AnalyticsCreate(AnalyticsBase):
    """Schema para criar analytics"""
    pass

class AnalyticsResponse(AnalyticsBase):
    """Schema de resposta de analytics"""
    id: int
    created_at: datetime
    meta_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Sync Schemas

class SyncRequest(BaseModel):
    """Schema de requisição de sincronização"""
    direction: str = "bidirectional"  # meep_to_local, local_to_meep, bidirectional
    entities: List[str] = ["events", "tickets", "attendees", "checkins", "transactions", "analytics"]
    event_ids: Optional[List[int]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    force: bool = False

class SyncResponse(BaseModel):
    """Schema de resposta de sincronização"""
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    direction: str
    events: Dict[str, int]
    tickets: Dict[str, int]
    attendees: Dict[str, int]
    checkins: Dict[str, int]
    transactions: Dict[str, int]
    analytics: Dict[str, int]
    conflicts: List[Dict[str, Any]] = []
    errors: List[str] = []

# Integration Status

class IntegrationStatus(BaseModel):
    """Schema de status da integração"""
    connected: bool
    last_sync: Optional[datetime] = None
    sync_status: Optional[str] = None
    total_events: int = 0
    total_attendees: int = 0
    total_checkins: int = 0
    total_transactions: int = 0
    errors: List[str] = []
    warnings: List[str] = []

# Webhook Schemas

class WebhookEvent(BaseModel):
    """Schema de evento webhook"""
    event_type: str  # checkin.created, transaction.paid, etc.
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None

class WebhookResponse(BaseModel):
    """Schema de resposta webhook"""
    received: bool = True
    processed: bool = False
    message: Optional[str] = None

# Batch Operations

class BatchImportRequest(BaseModel):
    """Schema de importação em lote"""
    entity_type: str  # events, tickets, attendees
    data: List[Dict[str, Any]]
    validate_only: bool = False
    update_existing: bool = False

class BatchImportResponse(BaseModel):
    """Schema de resposta de importação"""
    total: int
    imported: int
    updated: int
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]

# Health Check

class HealthCheckResponse(BaseModel):
    """Schema de health check"""
    status: str = "healthy"  # healthy, degraded, unhealthy
    meep_api: bool
    database: bool
    cache: bool = False
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)