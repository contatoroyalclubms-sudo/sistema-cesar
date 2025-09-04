"""
Schemas Pydantic para Sistema de Mesas + KDS - Implementação Completa Meep
==========================================================================

Schemas de validação e serialização para o sistema avançado de gestão 
de mesas e cozinha baseado na engenharia reversa do sistema Meep.

Funcionalidades cobertas:
- Validação de dados para pedidos de mesa
- Schemas para KDS (Kitchen Display System)
- Filtros e consultas avançadas
- Relatórios e analytics
- Notificações em tempo real
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional, Dict, Any, Union, Generic, TypeVar
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum

# Tipos genéricos para schemas
T = TypeVar('T')

# Importar enums dos modelos
from .models_mesa_kds import (
    StatusPedidoMesa, PrioridadePedido, TipoNotificacaoKDS,
    StatusItemPedido, TipoEstacaoKDS, ModoPedidoMesa
)

# ================================================================================
# SCHEMAS BASE E CONFIGURAÇÕES
# ================================================================================

class ConfigBase(BaseModel):
    """Configuração base para todos os schemas"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )

# ================================================================================
# SCHEMAS PARA PEDIDOS DE MESA
# ================================================================================

class PedidoMesaBase(ConfigBase):
    """Schema base para pedidos de mesa"""
    mesa_id: int = Field(..., description="ID da mesa")
    numero_mesa: str = Field(..., max_length=10, description="Número da mesa")
    nome_cliente: Optional[str] = Field(None, max_length=255, description="Nome do cliente")
    cpf_cliente: Optional[str] = Field(None, max_length=14, description="CPF do cliente")
    telefone_cliente: Optional[str] = Field(None, max_length=20, description="Telefone do cliente")
    observacoes: Optional[str] = Field(None, description="Observações gerais")
    observacoes_cozinha: Optional[str] = Field(None, description="Observações para a cozinha")
    prioridade: PrioridadePedido = Field(PrioridadePedido.NORMAL, description="Prioridade do pedido")
    modo_pedido: ModoPedidoMesa = Field(ModoPedidoMesa.MESA, description="Modo do pedido")
    tempo_estimado_preparo: int = Field(0, ge=0, description="Tempo estimado em minutos")
    empresa_id: int = Field(..., description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento (opcional)")

class PedidoMesaCreate(PedidoMesaBase):
    """Schema para criação de pedido de mesa"""
    pass

class PedidoMesaUpdate(ConfigBase):
    """Schema para atualização de pedido de mesa"""
    nome_cliente: Optional[str] = Field(None, max_length=255)
    cpf_cliente: Optional[str] = Field(None, max_length=14)
    telefone_cliente: Optional[str] = Field(None, max_length=20)
    observacoes: Optional[str] = None
    observacoes_cozinha: Optional[str] = None
    status: Optional[StatusPedidoMesa] = None
    prioridade: Optional[PrioridadePedido] = None
    tempo_estimado_preparo: Optional[int] = Field(None, ge=0)

class PedidoMesaResponse(PedidoMesaBase):
    """Schema de resposta para pedido de mesa"""
    id: int
    numero_pedido: str
    status: StatusPedidoMesa
    valor_subtotal: Decimal
    valor_desconto: Decimal
    valor_acrescimo: Decimal
    valor_total: Decimal
    data_pedido: datetime
    data_confirmacao: Optional[datetime]
    data_inicio_preparo: Optional[datetime]
    data_conclusao: Optional[datetime]
    data_entrega: Optional[datetime]
    usuario_criacao_id: int
    usuario_confirmacao_id: Optional[int]
    usuario_entrega_id: Optional[int]
    estacao_responsavel: TipoEstacaoKDS
    alertas_enviados: List[str]
    configuracoes_kds: Dict[str, Any]

class PedidoMesaDetalhado(PedidoMesaResponse):
    """Schema detalhado com itens e relacionamentos"""
    itens: List['ItemPedidoMesaResponse'] = []
    notificacoes: List['NotificacaoKDSResponse'] = []
    tempo_decorrido: Optional[int] = Field(None, description="Tempo decorrido em minutos")
    atraso_estimado: Optional[int] = Field(None, description="Atraso estimado em minutos")

# ================================================================================
# SCHEMAS PARA ITENS DE PEDIDO
# ================================================================================

class ItemPedidoMesaBase(ConfigBase):
    """Schema base para itens de pedido"""
    produto_id: Optional[int] = Field(None, description="ID do produto")
    nome_produto: str = Field(..., max_length=255, description="Nome do produto")
    categoria_produto: Optional[str] = Field(None, max_length=100, description="Categoria do produto")
    codigo_produto: Optional[str] = Field(None, max_length=50, description="Código do produto")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade do item")
    valor_unitario: Decimal = Field(..., gt=0, description="Valor unitário")
    observacoes: Optional[str] = Field(None, description="Observações do item")
    modificacoes: List[str] = Field(default_factory=list, description="Lista de modificações")
    ingredientes_removidos: List[str] = Field(default_factory=list, description="Ingredientes removidos")
    ingredientes_adicionados: List[str] = Field(default_factory=list, description="Ingredientes adicionados")
    tempo_estimado_item: int = Field(0, ge=0, description="Tempo estimado em minutos")
    estacao_preparo: TipoEstacaoKDS = Field(TipoEstacaoKDS.GERAL, description="Estação de preparo")
    prioridade_preparo: int = Field(1, ge=1, le=5, description="Prioridade de preparo")

    @validator('valor_unitario', 'quantidade')
    def validar_valores_positivos(cls, v):
        if v <= 0:
            raise ValueError('Valores devem ser positivos')
        return v

class ItemPedidoMesaCreate(ItemPedidoMesaBase):
    """Schema para criação de item de pedido"""
    pedido_id: int = Field(..., description="ID do pedido")

class ItemPedidoMesaUpdate(ConfigBase):
    """Schema para atualização de item de pedido"""
    quantidade: Optional[Decimal] = Field(None, gt=0)
    valor_unitario: Optional[Decimal] = Field(None, gt=0)
    observacoes: Optional[str] = None
    status: Optional[StatusItemPedido] = None
    modificacoes: Optional[List[str]] = None
    ingredientes_removidos: Optional[List[str]] = None
    ingredientes_adicionados: Optional[List[str]] = None
    tempo_estimado_item: Optional[int] = Field(None, ge=0)
    prioridade_preparo: Optional[int] = Field(None, ge=1, le=5)

class ItemPedidoMesaResponse(ItemPedidoMesaBase):
    """Schema de resposta para item de pedido"""
    id: int
    pedido_id: int
    status: StatusItemPedido
    valor_total: Decimal
    data_inicio_preparo: Optional[datetime]
    data_conclusao_preparo: Optional[datetime]
    data_entrega: Optional[datetime]
    responsavel_preparo_id: Optional[int]
    responsavel_entrega_id: Optional[int]

# ================================================================================
# SCHEMAS PARA KDS (KITCHEN DISPLAY SYSTEM)
# ================================================================================

class EstacaoKDSBase(ConfigBase):
    """Schema base para estações KDS"""
    nome: str = Field(..., max_length=100, description="Nome da estação")
    tipo: TipoEstacaoKDS = Field(..., description="Tipo da estação")
    descricao: Optional[str] = Field(None, description="Descrição da estação")
    cor_tema: str = Field("#2563eb", max_length=7, description="Cor do tema")
    icone: Optional[str] = Field(None, max_length=50, description="Ícone da estação")
    posicao_ordem: int = Field(1, ge=1, description="Ordem de exibição")
    capacidade_maxima_pedidos: int = Field(10, ge=1, description="Capacidade máxima")
    tempo_alerta_atraso: int = Field(30, ge=5, description="Tempo para alerta de atraso em minutos")
    tempo_alerta_urgente: int = Field(45, ge=10, description="Tempo para alerta urgente em minutos")
    setor_cozinha: Optional[str] = Field(None, max_length=100, description="Setor da cozinha")
    equipamentos: List[str] = Field(default_factory=list, description="Lista de equipamentos")
    empresa_id: int = Field(..., description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento")

class EstacaoKDSCreate(EstacaoKDSBase):
    """Schema para criação de estação KDS"""
    pass

class EstacaoKDSUpdate(ConfigBase):
    """Schema para atualização de estação KDS"""
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = None
    cor_tema: Optional[str] = Field(None, max_length=7)
    icone: Optional[str] = Field(None, max_length=50)
    posicao_ordem: Optional[int] = Field(None, ge=1)
    capacidade_maxima_pedidos: Optional[int] = Field(None, ge=1)
    tempo_alerta_atraso: Optional[int] = Field(None, ge=5)
    tempo_alerta_urgente: Optional[int] = Field(None, ge=10)
    setor_cozinha: Optional[str] = Field(None, max_length=100)
    equipamentos: Optional[List[str]] = None
    ativa: Optional[bool] = None
    configuracoes_tela: Optional[Dict[str, Any]] = None

class EstacaoKDSResponse(EstacaoKDSBase):
    """Schema de resposta para estação KDS"""
    id: int
    ativa: bool
    configuracoes_tela: Dict[str, Any]
    criado_em: datetime
    atualizado_em: Optional[datetime]

class ConfiguracaoKDSBase(ConfigBase):
    """Schema base para configurações KDS"""
    nome_configuracao: str = Field(..., max_length=100, description="Nome da configuração")
    tipo_configuracao: str = Field(..., max_length=50, description="Tipo da configuração")
    tempo_alerta_padrao: int = Field(30, ge=5, description="Tempo padrão para alertas")
    tempo_critico_padrao: int = Field(45, ge=10, description="Tempo crítico padrão")
    som_notificacao: bool = Field(True, description="Ativar som")
    vibrar_notificacao: bool = Field(False, description="Ativar vibração")
    tamanho_fonte: str = Field("medium", description="Tamanho da fonte")
    tema_cor: str = Field("blue", description="Tema de cor")
    mostrar_fotos_produtos: bool = Field(True, description="Mostrar fotos dos produtos")
    mostrar_tempo_decorrido: bool = Field(True, description="Mostrar tempo decorrido")
    mostrar_observacoes: bool = Field(True, description="Mostrar observações")
    intervalo_atualizacao: int = Field(5, ge=1, le=60, description="Intervalo de atualização em segundos")
    auto_refresh: bool = Field(True, description="Auto refresh")
    notificacao_tempo_real: bool = Field(True, description="Notificações em tempo real")
    empresa_id: int = Field(..., description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento")

class ConfiguracaoKDSCreate(ConfiguracaoKDSBase):
    """Schema para criação de configuração KDS"""
    pass

class ConfiguracaoKDSUpdate(ConfigBase):
    """Schema para atualização de configuração KDS"""
    tempo_alerta_padrao: Optional[int] = Field(None, ge=5)
    tempo_critico_padrao: Optional[int] = Field(None, ge=10)
    som_notificacao: Optional[bool] = None
    vibrar_notificacao: Optional[bool] = None
    tamanho_fonte: Optional[str] = None
    tema_cor: Optional[str] = None
    mostrar_fotos_produtos: Optional[bool] = None
    mostrar_tempo_decorrido: Optional[bool] = None
    mostrar_observacoes: Optional[bool] = None
    intervalo_atualizacao: Optional[int] = Field(None, ge=1, le=60)
    auto_refresh: Optional[bool] = None
    notificacao_tempo_real: Optional[bool] = None
    ativa: Optional[bool] = None
    configuracoes_extras: Optional[Dict[str, Any]] = None

class ConfiguracaoKDSResponse(ConfiguracaoKDSBase):
    """Schema de resposta para configuração KDS"""
    id: int
    ativa: bool
    configuracoes_extras: Dict[str, Any]
    criado_em: datetime
    atualizado_em: Optional[datetime]

# ================================================================================
# SCHEMAS PARA NOTIFICAÇÕES
# ================================================================================

class NotificacaoKDSBase(ConfigBase):
    """Schema base para notificações KDS"""
    tipo: TipoNotificacaoKDS = Field(..., description="Tipo da notificação")
    titulo: str = Field(..., max_length=255, description="Título da notificação")
    mensagem: str = Field(..., description="Mensagem da notificação")
    urgencia: PrioridadePedido = Field(PrioridadePedido.NORMAL, description="Urgência")
    som: bool = Field(True, description="Reproduzir som")
    vibrar: bool = Field(False, description="Vibrar")
    cor_destaque: str = Field("#ef4444", max_length=7, description="Cor de destaque")

class NotificacaoKDSCreate(NotificacaoKDSBase):
    """Schema para criação de notificação KDS"""
    pedido_id: Optional[int] = Field(None, description="ID do pedido")
    estacao_id: Optional[int] = Field(None, description="ID da estação")
    mesa_id: Optional[int] = Field(None, description="ID da mesa")
    dados_extras: Dict[str, Any] = Field(default_factory=dict, description="Dados extras")
    data_expiracao: Optional[datetime] = Field(None, description="Data de expiração")

class NotificacaoKDSUpdate(ConfigBase):
    """Schema para atualização de notificação KDS"""
    lida: Optional[bool] = None
    data_leitura: Optional[datetime] = None
    usuario_leitura_id: Optional[int] = None

class NotificacaoKDSResponse(NotificacaoKDSBase):
    """Schema de resposta para notificação KDS"""
    id: int
    pedido_id: Optional[int]
    estacao_id: Optional[int]
    mesa_id: Optional[int]
    lida: bool
    data_leitura: Optional[datetime]
    usuario_leitura_id: Optional[int]
    dados_extras: Dict[str, Any]
    data_criacao: datetime
    data_expiracao: Optional[datetime]

# ================================================================================
# SCHEMAS PARA RELATÓRIOS E ANALYTICS
# ================================================================================

class RelatorioTempoMesaBase(ConfigBase):
    """Schema base para relatórios de tempo de mesa"""
    data_inicio: date = Field(..., description="Data de início do período")
    data_fim: date = Field(..., description="Data de fim do período")
    mesa_id: Optional[int] = Field(None, description="ID da mesa específica")

    @validator('data_fim')
    def validar_data_fim(cls, v, values):
        if 'data_inicio' in values and v < values['data_inicio']:
            raise ValueError('Data fim deve ser posterior à data início')
        return v

class RelatorioTempoMesaResponse(RelatorioTempoMesaBase):
    """Schema de resposta para relatório de tempo de mesa"""
    id: int
    numero_mesa: Optional[str]
    tempo_medio_preparo: int
    tempo_medio_entrega: int
    tempo_medio_ocupacao: int
    tempo_total_ocupada: int
    total_pedidos: int
    pedidos_no_prazo: int
    pedidos_atrasados: int
    pedidos_cancelados: int
    faturamento_total: Decimal
    ticket_medio: Decimal
    taxa_ocupacao: Decimal
    taxa_sucesso: Decimal
    indice_satisfacao: Decimal
    empresa_id: int
    evento_id: Optional[int]
    gerado_em: datetime

class DashboardKDSResponse(ConfigBase):
    """Schema para dashboard do KDS"""
    total_pedidos_pendentes: int = Field(0, description="Total de pedidos pendentes")
    total_pedidos_preparando: int = Field(0, description="Total de pedidos em preparo")
    total_pedidos_prontos: int = Field(0, description="Total de pedidos prontos")
    pedidos_atrasados: int = Field(0, description="Pedidos atrasados")
    tempo_medio_preparo: int = Field(0, description="Tempo médio de preparo em minutos")
    estacoes_ativas: int = Field(0, description="Estações ativas")
    notificacoes_nao_lidas: int = Field(0, description="Notificações não lidas")
    mesas_ocupadas: int = Field(0, description="Mesas ocupadas")
    ultima_atualizacao: datetime = Field(default_factory=datetime.now, description="Última atualização")

class EstatisticasEstacaoResponse(ConfigBase):
    """Schema para estatísticas por estação"""
    estacao_id: int
    nome_estacao: str
    tipo_estacao: TipoEstacaoKDS
    pedidos_pendentes: int = 0
    pedidos_preparando: int = 0
    pedidos_concluidos_hoje: int = 0
    tempo_medio_preparo: int = 0
    eficiencia_percentual: Decimal = Field(Decimal('0'), description="Eficiência em percentual")
    capacidade_utilizada: Decimal = Field(Decimal('0'), description="Capacidade utilizada em percentual")

# ================================================================================
# SCHEMAS PARA FILTROS E CONSULTAS
# ================================================================================

class FiltrosPedidoMesa(ConfigBase):
    """Filtros para consulta de pedidos de mesa"""
    status: Optional[List[StatusPedidoMesa]] = Field(None, description="Filtrar por status")
    prioridade: Optional[List[PrioridadePedido]] = Field(None, description="Filtrar por prioridade")
    mesa_id: Optional[List[int]] = Field(None, description="Filtrar por mesa")
    data_inicio: Optional[datetime] = Field(None, description="Data de início")
    data_fim: Optional[datetime] = Field(None, description="Data de fim")
    modo_pedido: Optional[List[ModoPedidoMesa]] = Field(None, description="Filtrar por modo")
    estacao_responsavel: Optional[List[TipoEstacaoKDS]] = Field(None, description="Filtrar por estação")
    atrasados_apenas: bool = Field(False, description="Apenas pedidos atrasados")
    empresa_id: Optional[int] = Field(None, description="Filtrar por empresa")
    evento_id: Optional[int] = Field(None, description="Filtrar por evento")

class FiltrosNotificacaoKDS(ConfigBase):
    """Filtros para consulta de notificações KDS"""
    tipo: Optional[List[TipoNotificacaoKDS]] = Field(None, description="Filtrar por tipo")
    urgencia: Optional[List[PrioridadePedido]] = Field(None, description="Filtrar por urgência")
    lida: Optional[bool] = Field(None, description="Filtrar por status de leitura")
    estacao_id: Optional[List[int]] = Field(None, description="Filtrar por estação")
    data_inicio: Optional[datetime] = Field(None, description="Data de início")
    data_fim: Optional[datetime] = Field(None, description="Data de fim")
    apenas_ativas: bool = Field(True, description="Apenas notificações ativas")

class ParametrosPaginacao(ConfigBase):
    """Parâmetros para paginação"""
    page: int = Field(1, ge=1, description="Número da página")
    size: int = Field(50, ge=1, le=200, description="Tamanho da página")
    ordenar_por: str = Field("id", description="Campo para ordenação")
    ordem_desc: bool = Field(False, description="Ordenação decrescente")

class RespostaPaginada(BaseModel, Generic[T]):
    """Resposta paginada genérica"""
    items: List[T] = Field(default_factory=list, description="Lista de itens")
    total: int = Field(0, description="Total de itens")
    page: int = Field(1, description="Página atual")
    size: int = Field(50, description="Tamanho da página")
    pages: int = Field(0, description="Total de páginas")
    has_next: bool = Field(False, description="Tem próxima página")
    has_prev: bool = Field(False, description="Tem página anterior")

# ================================================================================
# SCHEMAS PARA AÇÕES DO KDS
# ================================================================================

class AcaoStatusPedido(ConfigBase):
    """Schema para ações de mudança de status"""
    novo_status: StatusPedidoMesa = Field(..., description="Novo status do pedido")
    observacoes: Optional[str] = Field(None, description="Observações da ação")
    usuario_id: int = Field(..., description="ID do usuário responsável")

class AcaoStatusItem(ConfigBase):
    """Schema para ações de mudança de status de item"""
    novo_status: StatusItemPedido = Field(..., description="Novo status do item")
    observacoes: Optional[str] = Field(None, description="Observações da ação")
    usuario_id: int = Field(..., description="ID do usuário responsável")

class AcaoTransferirEstacao(ConfigBase):
    """Schema para transferir pedido entre estações"""
    nova_estacao: TipoEstacaoKDS = Field(..., description="Nova estação responsável")
    motivo: str = Field(..., description="Motivo da transferência")
    usuario_id: int = Field(..., description="ID do usuário responsável")

class ComandoKDS(ConfigBase):
    """Schema para comandos do KDS"""
    comando: str = Field(..., description="Tipo de comando")
    parametros: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros do comando")
    usuario_id: int = Field(..., description="ID do usuário")

# Atualizar referências circulares
PedidoMesaDetalhado.model_rebuild()
ItemPedidoMesaResponse.model_rebuild()
