"""
Pydantic schemas for KDS and Tables Management systems
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ====== KDS SCHEMAS ======

class TipoEstacaoKDSSchema(str, Enum):
    COZINHA = "cozinha"
    BAR = "bar"
    EXPEDITOR = "expeditor"
    ESPECIAL = "especial"

class StatusPedidoKDSSchema(str, Enum):
    PENDENTE = "PENDENTE"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

# EstacaoKDS Schemas
class EstacaoKDSBase(BaseModel):
    nome: str = Field(..., max_length=100)
    tipo: TipoEstacaoKDSSchema = TipoEstacaoKDSSchema.COZINHA
    descricao: Optional[str] = None
    evento_id: int
    ativo: bool = True
    ordem_exibicao: int = 1
    configuracoes: Optional[dict] = None

class EstacaoKDSCreate(EstacaoKDSBase):
    pass

class EstacaoKDSUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    tipo: Optional[TipoEstacaoKDSSchema] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None
    ordem_exibicao: Optional[int] = None
    configuracoes: Optional[dict] = None

class EstacaoKDSResponse(EstacaoKDSBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# PedidoKDS Schemas
class PedidoKDSBase(BaseModel):
    numero_pedido: str = Field(..., max_length=50)
    estacao_id: int
    status: StatusPedidoKDSSchema = StatusPedidoKDSSchema.PENDENTE
    tempo_estimado_minutos: Optional[int] = None
    observacoes: Optional[str] = None
    comanda_id: Optional[int] = None
    venda_id: Optional[int] = None
    prioridade: str = 'NORMAL'

class PedidoKDSCreate(PedidoKDSBase):
    pass

class PedidoKDSUpdate(BaseModel):
    status: Optional[StatusPedidoKDSSchema] = None
    tempo_estimado_minutos: Optional[int] = None
    observacoes: Optional[str] = None
    prioridade: Optional[str] = None

class PedidoKDSResponse(PedidoKDSBase):
    id: int
    created_at: datetime
    iniciado_em: Optional[datetime] = None
    finalizado_em: Optional[datetime] = None
    entregue_em: Optional[datetime] = None
    itens: Optional[List['ItemPedidoKDSResponse']] = []

    class Config:
        from_attributes = True

# ItemPedidoKDS Schemas
class ItemPedidoKDSBase(BaseModel):
    produto_id: int
    produto_nome: str = Field(..., max_length=200)
    quantidade: int = Field(1, ge=1)
    observacoes: Optional[str] = None
    pronto: bool = False

class ItemPedidoKDSCreate(ItemPedidoKDSBase):
    pass

class ItemPedidoKDSUpdate(BaseModel):
    quantidade: Optional[int] = Field(None, ge=1)
    observacoes: Optional[str] = None
    pronto: Optional[bool] = None

class ItemPedidoKDSResponse(ItemPedidoKDSBase):
    id: int
    pedido_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ====== TABLES MANAGEMENT SCHEMAS ======

class StatusMesaSchema(str, Enum):
    LIVRE = "LIVRE"
    OCUPADA = "OCUPADA"
    RESERVADA = "RESERVADA"
    MANUTENCAO = "MANUTENCAO"
    INATIVA = "INATIVA"

class TipoMesaSchema(str, Enum):
    NORMAL = "NORMAL"
    VIP = "VIP"
    REDONDA = "REDONDA"
    RETANGULAR = "RETANGULAR"
    BALCAO = "BALCAO"
    EXTERNA = "EXTERNA"

# MesaEvento Schemas
class MesaEventoBase(BaseModel):
    numero: str = Field(..., max_length=20)
    nome: str = Field(..., max_length=100)
    tipo: TipoMesaSchema = TipoMesaSchema.NORMAL
    status: StatusMesaSchema = StatusMesaSchema.LIVRE
    capacidade: int = Field(4, ge=1)
    evento_id: int
    posicao_x: int = 0
    posicao_y: int = 0
    largura: int = 100
    altura: int = 100
    rotacao: int = 0
    cor: str = '#3B82F6'
    ativo: bool = True

class MesaEventoCreate(MesaEventoBase):
    pass

class MesaEventoUpdate(BaseModel):
    numero: Optional[str] = Field(None, max_length=20)
    nome: Optional[str] = Field(None, max_length=100)
    tipo: Optional[TipoMesaSchema] = None
    status: Optional[StatusMesaSchema] = None
    capacidade: Optional[int] = Field(None, ge=1)
    posicao_x: Optional[int] = None
    posicao_y: Optional[int] = None
    largura: Optional[int] = None
    altura: Optional[int] = None
    rotacao: Optional[int] = None
    cor: Optional[str] = None
    ativo: Optional[bool] = None

class MesaEventoResponse(MesaEventoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    ocupada_em: Optional[datetime] = None
    liberada_em: Optional[datetime] = None
    reservada_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# Mesa Reserva Schemas (for future use)
class MesaEventoReservaCreate(BaseModel):
    mesa_id: int
    cliente_nome: str
    cliente_telefone: Optional[str] = None
    data_reserva: datetime
    observacoes: Optional[str] = None

class MesaEventoReservaUpdate(BaseModel):
    cliente_nome: Optional[str] = None
    cliente_telefone: Optional[str] = None
    data_reserva: Optional[datetime] = None
    observacoes: Optional[str] = None

class MesaEventoReservaResponse(BaseModel):
    id: int
    mesa_id: int
    cliente_nome: str
    cliente_telefone: Optional[str] = None
    data_reserva: datetime
    observacoes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Update forward references
PedidoKDSResponse.model_rebuild()