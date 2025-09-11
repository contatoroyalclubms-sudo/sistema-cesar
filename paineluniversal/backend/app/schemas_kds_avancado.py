from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

# ====== ENUMS ======

class TipoFluxoKDS(str, Enum):
    SEQUENCIAL = "sequencial"
    PARALELO = "paralelo"
    CONDICIONAL = "condicional"

class StatusEtapaKDS(str, Enum):
    PENDENTE = "pendente"
    EM_PREPARO = "em_preparo"
    CONCLUIDA = "concluida"
    PULADA = "pulada"

class TipoNotificacaoKDS(str, Enum):
    ATRASO = "atraso"
    ERRO = "erro"
    ALERTA = "alerta"
    INFO = "info"

class SeveridadeAlerta(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class ComplexidadeTemplate(str, Enum):
    SIMPLES = "simples"
    MEDIO = "medio"
    COMPLEXO = "complexo"

# ====== FILA KDS SCHEMAS ======

class FilaKDSBase(BaseModel):
    estacao_id: int
    nome: str
    cor: Optional[str] = "#3B82F6"
    ordem: Optional[int] = 0
    tempo_maximo_minutos: Optional[int] = 30
    auto_mover: Optional[bool] = True
    notificar_atraso: Optional[bool] = True
    ativo: Optional[bool] = True

class FilaKDSCreate(FilaKDSBase):
    pass

class FilaKDSUpdate(BaseModel):
    nome: Optional[str] = None
    cor: Optional[str] = None
    ordem: Optional[int] = None
    tempo_maximo_minutos: Optional[int] = None
    auto_mover: Optional[bool] = None
    notificar_atraso: Optional[bool] = None
    ativo: Optional[bool] = None

class FilaKDSResponse(FilaKDSBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# ====== FLUXO KDS SCHEMAS ======

class FluxoKDSBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: TipoFluxoKDS
    estacoes: List[int]  # Lista de IDs das estações
    regras: Optional[Dict[str, Any]] = None
    tempo_estimado_total: Optional[int] = None
    ativo: Optional[bool] = True

    @validator('estacoes')
    def validate_estacoes(cls, v):
        if not v or len(v) == 0:
            raise ValueError('É necessário pelo menos uma estação')
        return v

class FluxoKDSCreate(FluxoKDSBase):
    pass

class FluxoKDSUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[TipoFluxoKDS] = None
    estacoes: Optional[List[int]] = None
    regras: Optional[Dict[str, Any]] = None
    tempo_estimado_total: Optional[int] = None
    ativo: Optional[bool] = None

class FluxoKDSResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    tipo: TipoFluxoKDS
    estacoes: List[int]
    regras: Optional[Dict[str, Any]]
    tempo_estimado_total: Optional[int]
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== ETAPA FLUXO KDS SCHEMAS ======

class EtapaFluxoKDSBase(BaseModel):
    fluxo_id: int
    pedido_id: int
    estacao_id: int
    ordem: int
    status: Optional[StatusEtapaKDS] = StatusEtapaKDS.PENDENTE
    tempo_estimado: Optional[int] = None
    observacoes: Optional[str] = None

class EtapaFluxoKDSCreate(EtapaFluxoKDSBase):
    pass

class EtapaFluxoKDSUpdate(BaseModel):
    status: Optional[StatusEtapaKDS] = None
    observacoes: Optional[str] = None
    tempo_real: Optional[int] = None

class EtapaFluxoKDSResponse(EtapaFluxoKDSBase):
    id: int
    tempo_real: Optional[int]
    iniciado_em: Optional[datetime]
    concluido_em: Optional[datetime]
    criado_em: datetime

    class Config:
        from_attributes = True

# ====== NOTIFICAÇÃO KDS SCHEMAS ======

class NotificacaoKDSBase(BaseModel):
    tipo: TipoNotificacaoKDS
    titulo: str
    mensagem: Optional[str] = None
    estacao_id: int
    pedido_id: Optional[int] = None
    usuario_id: Optional[int] = None
    urgente: Optional[bool] = False

class NotificacaoKDSCreate(NotificacaoKDSBase):
    pass

class NotificacaoKDSUpdate(BaseModel):
    lida: Optional[bool] = None

class NotificacaoKDSResponse(NotificacaoKDSBase):
    id: int
    lida: bool
    criado_em: datetime
    lida_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== TEMPLATE FLUXO KDS SCHEMAS ======

class TemplateFluxoKDSBase(BaseModel):
    nome: str
    categoria: Optional[str] = None
    fluxo_config: Dict[str, Any]
    tempo_estimado: Optional[int] = None
    complexidade: Optional[ComplexidadeTemplate] = ComplexidadeTemplate.SIMPLES
    tags: Optional[List[str]] = []

class TemplateFluxoKDSCreate(TemplateFluxoKDSBase):
    criado_por_id: int

class TemplateFluxoKDSUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    fluxo_config: Optional[Dict[str, Any]] = None
    tempo_estimado: Optional[int] = None
    complexidade: Optional[ComplexidadeTemplate] = None
    tags: Optional[List[str]] = None
    ativo: Optional[bool] = None

class TemplateFluxoKDSResponse(TemplateFluxoKDSBase):
    id: int
    uso_count: int
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime]
    criado_por_id: int

    class Config:
        from_attributes = True

# ====== MÉTRICA KDS SCHEMAS ======

class MetricaKDSBase(BaseModel):
    estacao_id: int
    data_coleta: date
    total_pedidos: Optional[int] = 0
    pedidos_concluidos: Optional[int] = 0
    tempo_medio_preparo: Optional[float] = None
    tempo_maximo_preparo: Optional[float] = None
    tempo_minimo_preparo: Optional[float] = None
    taxa_atraso: Optional[float] = None
    picos_demanda: Optional[Dict[str, Any]] = None
    eficiencia: Optional[float] = None
    satisfacao: Optional[float] = None

class MetricaKDSCreate(MetricaKDSBase):
    pass

class MetricaKDSUpdate(BaseModel):
    total_pedidos: Optional[int] = None
    pedidos_concluidos: Optional[int] = None
    tempo_medio_preparo: Optional[float] = None
    tempo_maximo_preparo: Optional[float] = None
    tempo_minimo_preparo: Optional[float] = None
    taxa_atraso: Optional[float] = None
    picos_demanda: Optional[Dict[str, Any]] = None
    eficiencia: Optional[float] = None
    satisfacao: Optional[float] = None

class MetricaKDSResponse(MetricaKDSBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True

# ====== ALERTA KDS SCHEMAS ======

class AlertaKDSBase(BaseModel):
    tipo: str
    severidade: SeveridadeAlerta
    titulo: str
    descricao: Optional[str] = None
    estacao_id: int
    pedido_id: Optional[int] = None
    regra_config: Optional[Dict[str, Any]] = None

class AlertaKDSCreate(AlertaKDSBase):
    pass

class AlertaKDSUpdate(BaseModel):
    resolvido: Optional[bool] = None
    resolvido_por_id: Optional[int] = None
    notas_resolucao: Optional[str] = None

class AlertaKDSResponse(AlertaKDSBase):
    id: int
    resolvido: bool
    resolvido_por_id: Optional[int]
    resolvido_em: Optional[datetime]
    notas_resolucao: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True

# ====== SCHEMAS COMPLEXOS PARA DASHBOARDS ======

class DashboardKDSMetricas(BaseModel):
    """Métricas consolidadas para dashboard KDS"""
    total_estacoes_ativas: int
    total_pedidos_fila: int
    tempo_medio_atual: float
    eficiencia_geral: float
    alertas_ativos: int
    notificacoes_nao_lidas: int
    
    # Métricas por estação
    estacoes_performance: List[Dict[str, Any]]
    
    # Gráficos
    pedidos_por_hora: List[Dict[str, Any]]
    tempos_preparo_historico: List[Dict[str, Any]]
    distribuicao_tipos_pedido: List[Dict[str, Any]]

class FluxoKDSCompleto(BaseModel):
    """Fluxo KDS com todas as etapas e dados relacionados"""
    fluxo: FluxoKDSResponse
    etapas: List[EtapaFluxoKDSResponse]
    template_origem: Optional[TemplateFluxoKDSResponse]
    metricas_performance: Optional[Dict[str, Any]]

class EstacaoKDSStatus(BaseModel):
    """Status completo de uma estação KDS"""
    estacao_id: int
    nome: str
    status: str  # ativa, inativa, manutencao, erro
    filas: List[FilaKDSResponse]
    pedidos_na_fila: int
    tempo_medio_atual: Optional[float]
    ultimo_pedido: Optional[datetime]
    alertas_ativos: List[AlertaKDSResponse]
    operadores_online: int

class ResumoOperacionalKDS(BaseModel):
    """Resumo operacional completo do KDS"""
    periodo: str
    total_pedidos: int
    pedidos_concluidos: int
    pedidos_em_andamento: int
    tempo_medio_preparo: float
    pico_demanda: Dict[str, Any]
    eficiencia_por_estacao: List[Dict[str, Any]]
    problemas_identificados: List[str]
    recomendacoes: List[str]