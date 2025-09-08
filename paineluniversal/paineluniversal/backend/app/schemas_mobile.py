"""
Schemas Pydantic para o App PDV Mobile
Modelos de dados para validação e serialização das APIs mobile
"""
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ==================== ENUMS ====================

class StatusSessaoGarcomEnum(str, Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"

class TipoValidacaoNFCEnum(str, Enum):
    COMANDA = "comanda"
    PULSEIRA = "pulseira"
    CARTAO = "cartao"

class StatusValidacaoNFCEnum(str, Enum):
    SUCESSO = "sucesso"
    FALHA_CPF = "falha_cpf"
    FALHA_SALDO = "falha_saldo"
    COMANDA_BLOQUEADA = "comanda_bloqueada"
    NFC_ERRO = "nfc_erro"

class StatusPedidoMobileEnum(str, Enum):
    CARRINHO = "carrinho"
    ENVIADO = "enviado"
    PREPARANDO = "preparando"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

# ==================== SESSÃO GARÇOM ====================

class SessaoGarcomBase(BaseModel):
    device_id: Optional[str] = None
    app_version: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    area_atendimento: Optional[str] = None
    mesa_inicial: Optional[int] = None
    mesa_final: Optional[int] = None
    configuracoes: Optional[Dict[str, Any]] = None

class SessaoGarcomCreate(SessaoGarcomBase):
    evento_id: int
    device_id: str = Field(..., min_length=1, description="ID único do dispositivo")

class SessaoGarcomUpdate(BaseModel):
    status: Optional[StatusSessaoGarcomEnum] = None
    area_atendimento: Optional[str] = None
    mesa_inicial: Optional[int] = None
    mesa_final: Optional[int] = None
    configuracoes: Optional[Dict[str, Any]] = None

class SessaoGarcom(SessaoGarcomBase):
    id: str
    garcom_id: int
    evento_id: int
    token_sessao: str
    status: StatusSessaoGarcomEnum
    inicio_sessao: datetime
    fim_sessao: Optional[datetime] = None
    ultimo_heartbeat: datetime
    total_vendas: int = 0
    valor_total_vendido: Decimal = Decimal('0.00')
    total_comandas_atendidas: int = 0

    class Config:
        from_attributes = True

# ==================== VALIDAÇÃO NFC ====================

class ValidacaoNFCRequest(BaseModel):
    nfc_uid: str = Field(..., min_length=1, description="UID único do chip NFC")
    nfc_data: Optional[str] = None
    tipo_validacao: TipoValidacaoNFCEnum = TipoValidacaoNFCEnum.COMANDA
    cpf_digits: str = Field(..., min_length=3, max_length=3, description="3 primeiros dígitos do CPF")
    device_info: Optional[Dict[str, Any]] = None

    @validator('cpf_digits')
    def validate_cpf_digits(cls, v):
        if not v.isdigit():
            raise ValueError('CPF deve conter apenas dígitos')
        if len(v) != 3:
            raise ValueError('CPF deve ter exatamente 3 dígitos')
        return v

class ValidacaoNFCResponse(BaseModel):
    status: StatusValidacaoNFCEnum
    comanda_id: Optional[int] = None
    cliente_nome: Optional[str] = None
    saldo_disponivel: Optional[Decimal] = None
    limite_credito: Optional[Decimal] = None
    detalhes_erro: Optional[str] = None
    retry_permitido: bool = True
    tentativas_restantes: int = 3

class ValidacaoNFCMobile(BaseModel):
    id: str
    sessao_id: str
    comanda_id: Optional[int] = None
    nfc_uid: str
    tipo_validacao: TipoValidacaoNFCEnum
    cpf_informado: str
    cpf_valido: bool
    status: StatusValidacaoNFCEnum
    saldo_disponivel: Optional[Decimal] = None
    timestamp_validacao: datetime
    detalhes_erro: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== CATEGORIAS MOBILE ====================

class CategoriaMobileBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    icone: str = Field(..., min_length=1, max_length=50, description="Emoji ou nome do ícone")
    cor: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Cor em formato hex")
    ordem_exibicao: int = 1
    destino_impressao: Optional[str] = None
    tempo_preparo_medio: int = 10

class CategoriaMobileCreate(CategoriaMobileBase):
    evento_id: int

class CategoriaMobileUpdate(BaseModel):
    nome: Optional[str] = None
    icone: Optional[str] = None
    cor: Optional[str] = None
    ordem_exibicao: Optional[int] = None
    destino_impressao: Optional[str] = None
    tempo_preparo_medio: Optional[int] = None
    ativo: Optional[bool] = None

class CategoriaMobile(CategoriaMobileBase):
    id: int
    evento_id: int
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True

# ==================== PRODUTOS MOBILE ====================

class ProdutoMobileBase(BaseModel):
    categoria_mobile_id: int
    imagem_mobile: Optional[str] = None
    destaque: bool = False
    novo: bool = False
    promocao: bool = False
    vendas_rapidas: bool = False
    ordem_categoria: int = 1
    tempo_preparo: Optional[int] = None
    ingredientes: Optional[str] = None
    observacoes_padrao: Optional[str] = None

class ProdutoMobileCreate(ProdutoMobileBase):
    produto_id: int

class ProdutoMobileUpdate(BaseModel):
    categoria_mobile_id: Optional[int] = None
    imagem_mobile: Optional[str] = None
    destaque: Optional[bool] = None
    novo: Optional[bool] = None
    promocao: Optional[bool] = None
    vendas_rapidas: Optional[bool] = None
    ordem_categoria: Optional[int] = None
    tempo_preparo: Optional[int] = None
    ingredientes: Optional[str] = None
    observacoes_padrao: Optional[str] = None
    ativo_mobile: Optional[bool] = None

class ProdutoMobileResponse(ProdutoMobileBase):
    id: int
    produto_id: int
    ativo_mobile: bool
    criado_em: datetime
    
    # Dados do produto principal
    nome: str
    preco: Decimal
    estoque_atual: int
    categoria: str
    status: str

    class Config:
        from_attributes = True

# ==================== PEDIDOS MOBILE ====================

class ItemPedidoMobileBase(BaseModel):
    produto_mobile_id: int
    quantidade: int = Field(..., gt=0, description="Quantidade deve ser maior que zero")
    preco_unitario: Decimal = Field(..., gt=0, description="Preço deve ser maior que zero")
    observacoes: Optional[str] = None
    sem_ingredientes: Optional[str] = None
    extras: Optional[str] = None

class ItemPedidoMobileCreate(ItemPedidoMobileBase):
    pass

class ItemPedidoMobile(ItemPedidoMobileBase):
    id: int
    pedido_id: str
    preco_total: Decimal
    status_preparo: str = "pendente"
    tempo_preparo_estimado: Optional[int] = None
    criado_em: datetime

    class Config:
        from_attributes = True

class PedidoMobileBase(BaseModel):
    comanda_id: int
    cpf_cliente: Optional[str] = None
    nome_cliente: Optional[str] = None
    mesa_numero: Optional[str] = None
    area_atendimento: Optional[str] = None
    observacoes_gerais: Optional[str] = None
    prioridade: int = 1

class PedidoMobileCreate(PedidoMobileBase):
    itens: List[ItemPedidoMobileCreate] = Field(..., min_items=1, description="Pedido deve ter pelo menos 1 item")

    @validator('itens')
    def validate_itens(cls, v):
        if not v:
            raise ValueError('Pedido deve ter pelo menos um item')
        return v

class PedidoMobileUpdate(BaseModel):
    status: Optional[StatusPedidoMobileEnum] = None
    observacoes_gerais: Optional[str] = None
    prioridade: Optional[int] = None
    mesa_numero: Optional[str] = None
    area_atendimento: Optional[str] = None

class PedidoMobile(PedidoMobileBase):
    id: str
    numero_pedido: str
    sessao_id: str
    evento_id: int
    valor_total: Decimal
    valor_desconto: Decimal = Decimal('0.00')
    valor_final: Decimal
    status: StatusPedidoMobileEnum
    tempo_estimado_preparo: Optional[int] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    enviado_impressao_em: Optional[datetime] = None
    itens: List[ItemPedidoMobile] = []

    class Config:
        from_attributes = True

# ==================== CONFIGURAÇÕES MOBILE ====================

class ConfiguracaoMobileBase(BaseModel):
    nfc_habilitado: bool = True
    nfc_timeout_segundos: int = 30
    cpf_max_tentativas: int = 3
    tema_escuro: bool = True
    tamanho_fonte: str = "normal"
    vibrar_feedback: bool = True
    som_notificacao: bool = False
    modo_offline: bool = True
    sync_automatico: bool = True
    backup_local: bool = True
    valor_maximo_pedido: Decimal = Decimal('1000.00')
    itens_maximos_pedido: int = 50
    timeout_sessao_minutos: int = 480
    impressao_automatica: bool = True
    impressao_duplicada: bool = False
    impressao_prioritaria: bool = False

class ConfiguracaoMobileCreate(ConfiguracaoMobileBase):
    evento_id: int

class ConfiguracaoMobileUpdate(BaseModel):
    nfc_habilitado: Optional[bool] = None
    nfc_timeout_segundos: Optional[int] = None
    cpf_max_tentativas: Optional[int] = None
    tema_escuro: Optional[bool] = None
    tamanho_fonte: Optional[str] = None
    vibrar_feedback: Optional[bool] = None
    som_notificacao: Optional[bool] = None
    modo_offline: Optional[bool] = None
    sync_automatico: Optional[bool] = None
    backup_local: Optional[bool] = None
    valor_maximo_pedido: Optional[Decimal] = None
    itens_maximos_pedido: Optional[int] = None
    timeout_sessao_minutos: Optional[int] = None
    impressao_automatica: Optional[bool] = None
    impressao_duplicada: Optional[bool] = None
    impressao_prioritaria: Optional[bool] = None

class ConfiguracaoMobile(ConfiguracaoMobileBase):
    id: int
    evento_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== DASHBOARD MOBILE ====================

class DashboardGarcom(BaseModel):
    """Dashboard específico para o garçom"""
    sessao_ativa: bool
    pedidos_pendentes: int
    pedidos_preparando: int
    pedidos_prontos: int
    valor_vendido_hoje: Decimal
    total_comandas_atendidas: int
    tempo_sessao_ativa: int  # minutos
    proximos_prontos: List[Dict[str, Any]] = []
    alertas: List[str] = []

class DashboardEventoMobile(BaseModel):
    """Dashboard geral do evento para mobile"""
    total_garcons_ativos: int
    total_pedidos_dia: int
    valor_total_dia: Decimal
    produto_mais_vendido: Optional[str] = None
    categoria_mais_vendida: Optional[str] = None
    tempo_medio_preparo: Optional[int] = None
    impressoras_status: Dict[str, str] = {}
    alertas_estoque: List[str] = []

# ==================== RESPONSES ESPECÍFICAS ====================

class LoginMobileResponse(BaseModel):
    """Response do login mobile"""
    success: bool
    token: str
    sessao_id: str
    garcom: Dict[str, Any]
    evento: Dict[str, Any]
    configuracao: ConfiguracaoMobile
    categorias: List[CategoriaMobile] = []
    message: str = "Login realizado com sucesso"

class HeartbeatResponse(BaseModel):
    """Response do heartbeat"""
    success: bool
    sessao_ativa: bool
    timestamp: datetime
    configuracao_atualizada: bool = False
    nova_configuracao: Optional[ConfiguracaoMobile] = None

class StatusPedidoResponse(BaseModel):
    """Response do status do pedido"""
    pedido_id: str
    status_atual: StatusPedidoMobileEnum
    tempo_restante_estimado: Optional[int] = None
    ultima_atualizacao: datetime
    detalhes: Optional[str] = None

class ComandaInfoResponse(BaseModel):
    """Response com informações da comanda após validação NFC"""
    comanda_id: int
    numero_comanda: str
    cliente_nome: Optional[str] = None
    saldo_disponivel: Decimal
    limite_credito: Optional[Decimal] = None
    historico_recente: List[Dict[str, Any]] = []
    bloqueios: List[str] = []

# ==================== REQUESTS ESPECÍFICAS ====================

class HeartbeatRequest(BaseModel):
    """Request do heartbeat"""
    device_info: Optional[Dict[str, Any]] = None
    localizacao: Optional[Dict[str, float]] = None
    status_app: str = "ativo"
    memoria_disponivel: Optional[int] = None
    bateria_nivel: Optional[int] = None

class FinalizarSessaoRequest(BaseModel):
    """Request para finalizar sessão"""
    motivo: str = "fim_turno"
    observacoes: Optional[str] = None
    relatorio_problemas: Optional[List[str]] = None

class SyncOfflineRequest(BaseModel):
    """Request para sincronização offline"""
    pedidos_offline: List[Dict[str, Any]] = []
    validacoes_nfc: List[Dict[str, Any]] = []
    logs_atividade: List[Dict[str, Any]] = []
    timestamp_ultimo_sync: Optional[datetime] = None

# ==================== FILTERS ====================

class ProdutoMobileFilter(BaseModel):
    """Filtros para listagem de produtos mobile"""
    categoria_id: Optional[int] = None
    destaque: Optional[bool] = None
    promocao: Optional[bool] = None
    vendas_rapidas: Optional[bool] = None
    disponivel: Optional[bool] = None
    busca: Optional[str] = None

class PedidoMobileFilter(BaseModel):
    """Filtros para listagem de pedidos mobile"""
    status: Optional[StatusPedidoMobileEnum] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    comanda_id: Optional[int] = None
    garcom_id: Optional[int] = None
    prioridade: Optional[int] = None
