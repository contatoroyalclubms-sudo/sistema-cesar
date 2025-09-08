from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TipoImpressoraEnum(str, Enum):
    COZINHA = "cozinha"
    BAR = "bar" 
    SOBREMESA = "sobremesa"
    CAIXA = "caixa"
    GERENCIAL = "gerencial"

class InterfaceImpressoraEnum(str, Enum):
    USB = "usb"
    NETWORK = "network"
    BLUETOOTH = "bluetooth"

class StatusImpressoraEnum(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERRO = "erro"
    MANUTENCAO = "manutencao"

class TipoPrintJobEnum(str, Enum):
    RECIBO_CAIXA = "recibo_caixa"
    PEDIDO_COZINHA = "pedido_cozinha"
    PEDIDO_BAR = "pedido_bar"
    COMANDA_RECHARGE = "comanda_recharge"
    RELATORIO = "relatorio"

class StatusPrintJobEnum(str, Enum):
    QUEUED = "queued"
    PRINTING = "printing"
    DONE = "done"
    ERROR = "error"
    RETRY = "retry"

# ================ SCHEMAS IMPRESSORAS ================

class ImpressoraBase(BaseModel):
    nome: str = Field(..., max_length=255)
    tipo: TipoImpressoraEnum
    interface: InterfaceImpressoraEnum
    endereco: str = Field(..., max_length=255)
    largura_mm: int = Field(default=80, ge=58, le=110)
    colunas: int = Field(default=42, ge=32, le=80)
    perfil_escpos: str = Field(default="epson", max_length=50)
    densidade: int = Field(default=8, ge=1, le=15)
    localizacao: Optional[str] = Field(None, max_length=255)
    impressora_backup_id: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None

class ImpressoraCreate(ImpressoraBase):
    evento_id: int

class ImpressoraUpdate(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None
    largura_mm: Optional[int] = None
    colunas: Optional[int] = None
    densidade: Optional[int] = None
    localizacao: Optional[str] = None
    ativo: Optional[bool] = None
    impressora_backup_id: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None

class Impressora(ImpressoraBase):
    id: str
    evento_id: int
    ativo: bool
    status: StatusImpressoraEnum
    ultimo_heartbeat: Optional[datetime]
    ip_bridge: Optional[str]
    versao_driver: Optional[str]
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ================ SCHEMAS TEMPLATES ================

class PrintTemplateBase(BaseModel):
    nome: str = Field(..., max_length=255)
    tipo_job: TipoPrintJobEnum
    template_content: str
    comandos_escpos: Optional[Dict[str, Any]] = None
    largura_colunas: int = Field(default=42, ge=32, le=80)
    fonte_tamanho: str = Field(default="normal", pattern="^(small|normal|large)$")
    padrao: bool = False

class PrintTemplateCreate(PrintTemplateBase):
    evento_id: int

class PrintTemplateUpdate(BaseModel):
    nome: Optional[str] = None
    template_content: Optional[str] = None
    comandos_escpos: Optional[Dict[str, Any]] = None
    largura_colunas: Optional[int] = None
    fonte_tamanho: Optional[str] = None
    ativo: Optional[bool] = None
    padrao: Optional[bool] = None

class PrintTemplate(PrintTemplateBase):
    id: int
    evento_id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ================ SCHEMAS PRINT JOBS ================

class PrintJobCreate(BaseModel):
    impressora_id: Optional[str] = None  # Se None, roteamento automático
    template_id: Optional[int] = None    # Se None, usa template padrão
    tipo: TipoPrintJobEnum
    prioridade: int = Field(default=1, ge=1, le=3)
    payload: Dict[str, Any]
    venda_pdv_id: Optional[int] = None
    comanda_id: Optional[int] = None

class PrintJobResponse(BaseModel):
    id: str
    impressora_id: str
    template_id: Optional[int]
    tipo: TipoPrintJobEnum
    status: StatusPrintJobEnum
    tentativas: int
    max_tentativas: int
    erro_msg: Optional[str]
    cpf_operador: str
    criado_em: datetime
    processado_em: Optional[datetime]
    impresso_em: Optional[datetime]

    class Config:
        from_attributes = True

# ================ REQUESTS ESPECÍFICOS ================

class ImprimirReciboRequest(BaseModel):
    venda_pdv_id: int
    impressora_id: Optional[str] = None
    abrir_gaveta: bool = True
    enviar_por_email: bool = False
    email_cliente: Optional[str] = None

class ImprimirPedidoRequest(BaseModel):
    venda_pdv_id: Optional[int] = None
    comanda_id: Optional[int] = None
    itens_personalizados: Optional[List[Dict[str, Any]]] = None
    observacoes: Optional[str] = None
    mesa_numero: Optional[str] = None

class ImprimirComandaRequest(BaseModel):
    comanda_id: int
    tipo_operacao: str  # "recarga", "fechamento", "abertura"
    valor: Optional[float] = None
    impressora_id: Optional[str] = None

class StatusImpressorasResponse(BaseModel):
    impressoras_online: int
    impressoras_offline: int
    jobs_pendentes: int
    jobs_erro: int
    ultima_atualizacao: datetime

class FilaImpressaoResponse(BaseModel):
    impressora_id: str
    impressora_nome: str
    jobs_pendentes: int
    job_atual: Optional[PrintJobResponse]
    estimativa_minutos: int
