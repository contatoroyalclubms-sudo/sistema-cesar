"""
Schemas Pydantic para o Sistema de Impressoras
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import ipaddress


# Enums
class TipoImpressoraEnum(str, Enum):
    TERMICA = "termica"
    FISCAL = "fiscal"
    ETIQUETA = "etiqueta"
    MATRICIAL = "matricial"
    LASER = "laser"
    POS = "pos"


class StatusImpressoraEnum(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERRO = "erro"
    MANUTENCAO = "manutencao"
    PAUSADA = "pausada"


class ModeloImpressoraEnum(str, Enum):
    EPSON_TM_T20 = "Epson TM-T20"
    EPSON_TM_T20X = "Epson TM-T20x"
    BEMATECH_4200 = "Bematech MP-4200"
    ELGIN_I8 = "Elgin i8"
    ELGIN_I9 = "Elgin i9"
    GENERICA = "Genérica"


class TipoEquipamentoEnum(str, Enum):
    POS = "POS"
    TOTEM = "Totem"
    TABLET = "Tablet"
    TERMINAL = "Terminal"
    CHECK = "Check"


class StatusFilaEnum(str, Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDO = "concluido"
    ERRO = "erro"
    CANCELADO = "cancelado"


# ====== SCHEMAS DE IMPRESSORA ======

class ImpressoraBase(BaseModel):
    """Base para Impressora"""
    nome: str = Field(..., min_length=1, max_length=100)
    ip: str = Field(..., min_length=7, max_length=45)
    porta: int = Field(default=9100, ge=1, le=65535)
    tipo: TipoImpressoraEnum = TipoImpressoraEnum.TERMICA
    modelo: ModeloImpressoraEnum = ModeloImpressoraEnum.GENERICA
    localizacao: Optional[str] = Field(None, max_length=100)
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    
    # Configurações específicas
    largura_papel: int = Field(default=80, ge=40, le=120)
    caracteres_linha: int = Field(default=48, ge=32, le=80)
    suporta_guilhotina: bool = True
    suporta_qrcode: bool = True
    suporta_codigo_barras: bool = True
    
    # Configurações de rede e driver
    driver: Optional[str] = Field(None, max_length=100)
    configuracoes_json: Optional[Dict[str, Any]] = None
    
    ativa: bool = True
    
    @field_validator('ip')
    def validate_ip(cls, v):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError('IP inválido')
        return v


class ImpressoraCreate(ImpressoraBase):
    """Schema para criar impressora"""
    pass


class ImpressoraUpdate(BaseModel):
    """Schema para atualizar impressora"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    ip: Optional[str] = Field(None, min_length=7, max_length=45)
    porta: Optional[int] = Field(None, ge=1, le=65535)
    tipo: Optional[TipoImpressoraEnum] = None
    modelo: Optional[ModeloImpressoraEnum] = None
    status: Optional[StatusImpressoraEnum] = None
    localizacao: Optional[str] = Field(None, max_length=100)
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    
    largura_papel: Optional[int] = Field(None, ge=40, le=120)
    caracteres_linha: Optional[int] = Field(None, ge=32, le=80)
    suporta_guilhotina: Optional[bool] = None
    suporta_qrcode: Optional[bool] = None
    suporta_codigo_barras: Optional[bool] = None
    
    driver: Optional[str] = Field(None, max_length=100)
    configuracoes_json: Optional[Dict[str, Any]] = None
    ativa: Optional[bool] = None
    
    @field_validator('ip')
    def validate_ip(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError('IP inválido')
        return v


class ImpressoraResponse(ImpressoraBase):
    """Schema de resposta para impressora"""
    id: int
    status: StatusImpressoraEnum = StatusImpressoraEnum.OFFLINE
    total_impressoes: int = 0
    ultima_impressao: Optional[datetime] = None
    ultima_verificacao: Optional[datetime] = None
    criada_em: datetime
    atualizada_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ====== SCHEMAS DE IMPRESSORA INTELIGENTE ======

class ImpressoraInteligenteBase(BaseModel):
    """Base para roteamento inteligente"""
    nome: str = Field(..., min_length=1, max_length=100)
    impressora_id: int
    tipo_impressao: str = Field(..., min_length=1, max_length=50)
    
    # Regras de roteamento
    local_origem: Optional[str] = Field(None, max_length=100)
    categoria_produto: Optional[str] = Field(None, max_length=100)
    prioridade: int = Field(default=0, ge=0, le=100)
    
    # Configurações
    ativo: bool = True
    imprimir_logo: bool = False
    numero_vias: int = Field(default=1, ge=1, le=5)
    template_id: Optional[int] = None
    
    # Horário de funcionamento
    hora_inicio: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    hora_fim: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    dias_semana: Optional[str] = Field(None, max_length=20)
    
    evento_id: Optional[int] = None


class ImpressoraInteligenteCreate(ImpressoraInteligenteBase):
    """Schema para criar roteamento inteligente"""
    pass


class ImpressoraInteligenteUpdate(BaseModel):
    """Schema para atualizar roteamento inteligente"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    impressora_id: Optional[int] = None
    tipo_impressao: Optional[str] = Field(None, min_length=1, max_length=50)
    local_origem: Optional[str] = Field(None, max_length=100)
    categoria_produto: Optional[str] = Field(None, max_length=100)
    prioridade: Optional[int] = Field(None, ge=0, le=100)
    ativo: Optional[bool] = None
    imprimir_logo: Optional[bool] = None
    numero_vias: Optional[int] = Field(None, ge=1, le=5)
    template_id: Optional[int] = None
    hora_inicio: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    hora_fim: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    dias_semana: Optional[str] = Field(None, max_length=20)
    evento_id: Optional[int] = None


class ImpressoraInteligenteResponse(ImpressoraInteligenteBase):
    """Schema de resposta para roteamento inteligente"""
    id: int
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ====== SCHEMAS DE TEMPLATE ======

class TemplateImpressaoBase(BaseModel):
    """Base para template de impressão"""
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., min_length=1, max_length=50)
    
    # Configurações do template
    cabecalho: Optional[str] = None
    corpo: Optional[str] = None
    rodape: Optional[str] = None
    
    # Formatação
    fonte_tamanho: Optional[str] = Field(None, max_length=10)
    negrito_titulo: bool = True
    centralizar_logo: bool = True
    separadores: bool = True
    
    # QR Code e Código de Barras
    incluir_qrcode: bool = False
    qrcode_conteudo: Optional[str] = Field(None, max_length=500)
    incluir_codigo_barras: bool = False
    codigo_barras_tipo: Optional[str] = Field(None, max_length=20)
    
    evento_id: Optional[int] = None
    ativo: bool = True


class TemplateImpressaoCreate(TemplateImpressaoBase):
    """Schema para criar template"""
    pass


class TemplateImpressaoUpdate(BaseModel):
    """Schema para atualizar template"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None, min_length=1, max_length=50)
    cabecalho: Optional[str] = None
    corpo: Optional[str] = None
    rodape: Optional[str] = None
    fonte_tamanho: Optional[str] = Field(None, max_length=10)
    negrito_titulo: Optional[bool] = None
    centralizar_logo: Optional[bool] = None
    separadores: Optional[bool] = None
    incluir_qrcode: Optional[bool] = None
    qrcode_conteudo: Optional[str] = Field(None, max_length=500)
    incluir_codigo_barras: Optional[bool] = None
    codigo_barras_tipo: Optional[str] = Field(None, max_length=20)
    evento_id: Optional[int] = None
    ativo: Optional[bool] = None


class TemplateImpressaoResponse(TemplateImpressaoBase):
    """Schema de resposta para template"""
    id: int
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ====== SCHEMAS DE FILA DE IMPRESSÃO ======

class FilaImpressaoBase(BaseModel):
    """Base para fila de impressão"""
    impressora_id: int
    tipo_documento: str = Field(..., min_length=1, max_length=50)
    conteudo: str
    prioridade: int = Field(default=0, ge=0, le=100)
    
    # Referências opcionais
    pedido_id: Optional[int] = None
    venda_id: Optional[int] = None
    usuario_id: Optional[int] = None


class FilaImpressaoCreate(FilaImpressaoBase):
    """Schema para adicionar à fila"""
    pass


class FilaImpressaoResponse(FilaImpressaoBase):
    """Schema de resposta para fila"""
    id: int
    status: StatusFilaEnum = StatusFilaEnum.PENDENTE
    tentativas: int = 0
    max_tentativas: int = 3
    criado_em: datetime
    processado_em: Optional[datetime] = None
    erro_mensagem: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ====== SCHEMAS DE LOG ======

class LogImpressaoResponse(BaseModel):
    """Schema de resposta para log de impressão"""
    id: int
    impressora_id: int
    fila_impressao_id: Optional[int] = None
    tipo_documento: Optional[str] = None
    tamanho_bytes: Optional[int] = None
    numero_linhas: Optional[int] = None
    tempo_processamento: Optional[float] = None
    sucesso: bool = True
    mensagem_erro: Optional[str] = None
    codigo_erro: Optional[str] = None
    ip_origem: Optional[str] = None
    usuario_id: Optional[int] = None
    evento_id: Optional[int] = None
    data_hora: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ====== SCHEMAS DE EQUIPAMENTO PDV ======

class EquipamentoPDVBase(BaseModel):
    """Base para equipamento PDV"""
    codigo: str = Field(..., min_length=1, max_length=20)
    tipo: TipoEquipamentoEnum
    nome: Optional[str] = Field(None, max_length=100)
    
    # Configuração
    perfil_venda: Optional[str] = Field(None, max_length=50)
    impressora_padrao_id: Optional[int] = None
    operador_id: Optional[int] = None
    
    # Status e licenciamento
    licenciado: bool = False
    data_licenca_inicio: Optional[date] = None
    data_licenca_fim: Optional[date] = None
    status: str = Field(default="inativo", max_length=20)
    
    # Localização
    localizacao: Optional[str] = Field(None, max_length=100)
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    
    versao_software: Optional[str] = Field(None, max_length=20)


class EquipamentoPDVCreate(EquipamentoPDVBase):
    """Schema para criar equipamento"""
    pass


class EquipamentoPDVUpdate(BaseModel):
    """Schema para atualizar equipamento"""
    tipo: Optional[TipoEquipamentoEnum] = None
    nome: Optional[str] = Field(None, max_length=100)
    perfil_venda: Optional[str] = Field(None, max_length=50)
    impressora_padrao_id: Optional[int] = None
    operador_id: Optional[int] = None
    licenciado: Optional[bool] = None
    data_licenca_inicio: Optional[date] = None
    data_licenca_fim: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)
    localizacao: Optional[str] = Field(None, max_length=100)
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    versao_software: Optional[str] = Field(None, max_length=20)


class EquipamentoPDVResponse(EquipamentoPDVBase):
    """Schema de resposta para equipamento"""
    id: int
    ultima_sincronizacao: Optional[datetime] = None
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ====== SCHEMAS DE OPERADOR PDV ======

class OperadorPDVBase(BaseModel):
    """Base para operador PDV"""
    nome: str = Field(..., min_length=1, max_length=100)
    cpf: Optional[str] = Field(None, pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$")
    codigo_acesso: Optional[str] = Field(None, max_length=20)
    
    # Comissionamento
    comissao_percentual: float = Field(default=0, ge=0, le=100)
    comissao_fixa: float = Field(default=0, ge=0)
    
    # Permissões
    pode_cancelar: bool = False
    pode_dar_desconto: bool = False
    desconto_maximo: float = Field(default=0, ge=0, le=100)
    
    # Status
    ativo: bool = True
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None


class OperadorPDVCreate(OperadorPDVBase):
    """Schema para criar operador"""
    pass


class OperadorPDVUpdate(BaseModel):
    """Schema para atualizar operador"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    cpf: Optional[str] = Field(None, pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$")
    codigo_acesso: Optional[str] = Field(None, max_length=20)
    comissao_percentual: Optional[float] = Field(None, ge=0, le=100)
    comissao_fixa: Optional[float] = Field(None, ge=0)
    pode_cancelar: Optional[bool] = None
    pode_dar_desconto: Optional[bool] = None
    desconto_maximo: Optional[float] = Field(None, ge=0, le=100)
    ativo: Optional[bool] = None
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None


class OperadorPDVResponse(OperadorPDVBase):
    """Schema de resposta para operador"""
    id: int
    total_vendas: int = 0
    valor_total_vendido: float = 0
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ====== SCHEMAS DE STATUS E TESTE ======

class StatusImpressoraResponse(BaseModel):
    """Status de uma impressora"""
    impressora_id: int
    nome: str
    ip: str
    porta: int
    status: StatusImpressoraEnum
    online: bool
    ultima_verificacao: Optional[datetime] = None
    mensagem: Optional[str] = None


class TesteImpressaoRequest(BaseModel):
    """Request para teste de impressão"""
    impressora_id: int
    tipo_teste: str = Field(default="completo", pattern="^(simples|completo|guilhotina|qrcode)$")
    mensagem_customizada: Optional[str] = None


class TesteImpressaoResponse(BaseModel):
    """Response do teste de impressão"""
    sucesso: bool
    impressora_id: int
    tempo_resposta: float  # Em segundos
    mensagem: str
    detalhes: Optional[Dict[str, Any]] = None