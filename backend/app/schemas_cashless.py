"""
Schemas Pydantic para o Sistema Cashless
Baseado na análise do sistema Meep - Validação e serialização de dados
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ================================================================================
# SCHEMAS PARA CATEGORIAS DE CLIENTES
# ================================================================================

class TipoCategoriaClienteEnum(str, Enum):
    VIP = "vip"
    SOCIO = "socio"
    PREMIUM = "premium"
    REGULAR = "regular"
    CORPORATIVO = "corporativo"

class StatusCategoriaClienteEnum(str, Enum):
    ATIVA = "ativa"
    INATIVA = "inativa"
    TEMPORARIA = "temporaria"

class CategoriaClienteBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")
    tipo: TipoCategoriaClienteEnum = Field(..., description="Tipo da categoria")
    cor: str = Field("#3b82f6", pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor em formato hex")
    icone: Optional[str] = Field(None, max_length=50, description="Nome do ícone")
    desconto_percentual: Decimal = Field(0, ge=0, le=100, description="Desconto padrão (%)")
    prioridade_atendimento: bool = Field(False, description="Prioridade no atendimento")
    acesso_areas_vip: bool = Field(False, description="Acesso a áreas VIP")
    cashback_percentual: Decimal = Field(0, ge=0, le=100, description="Cashback (%)")

class CategoriaClienteCreate(CategoriaClienteBase):
    empresa_id: Optional[int] = Field(None, description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento")

class CategoriaClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icone: Optional[str] = Field(None, max_length=50)
    desconto_percentual: Optional[Decimal] = Field(None, ge=0, le=100)
    prioridade_atendimento: Optional[bool] = None
    acesso_areas_vip: Optional[bool] = None
    cashback_percentual: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[StatusCategoriaClienteEnum] = None
    ativa: Optional[bool] = None

class CategoriaCliente(CategoriaClienteBase):
    id: int
    status: StatusCategoriaClienteEnum
    ativa: bool
    empresa_id: Optional[int]
    evento_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]
    
    class Config:
        from_attributes = True

class ClienteCategoriaBase(BaseModel):
    cpf_cliente: str = Field(..., pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", description="CPF do cliente")
    categoria_id: int = Field(..., gt=0, description="ID da categoria")
    data_inicio: date = Field(..., description="Data de início da categoria")
    data_fim: Optional[date] = Field(None, description="Data de fim (null = permanente)")
    observacoes: Optional[str] = Field(None, description="Observações sobre a atribuição")

class ClienteCategoriaCreate(ClienteCategoriaBase):
    pass

class ClienteCategoria(ClienteCategoriaBase):
    id: int
    ativa: bool
    criado_em: datetime
    categoria: CategoriaCliente
    
    class Config:
        from_attributes = True

# ================================================================================
# SCHEMAS PARA SISTEMA DE PERMISSÕES
# ================================================================================

class TipoPermissaoEnum(str, Enum):
    ADMIN_TOTAL = "admin_total"
    GESTAO_USUARIOS = "gestao_usuarios"
    GESTAO_EMPRESA = "gestao_empresa"
    CRIAR_EVENTO = "criar_evento"
    EDITAR_EVENTO = "editar_evento"
    EXCLUIR_EVENTO = "excluir_evento"
    VISUALIZAR_EVENTO = "visualizar_evento"
    OPERAR_PDV = "operar_pdv"
    CANCELAR_VENDA = "cancelar_venda"
    ESTORNAR_VENDA = "estornar_venda"
    DESCONTO_VENDA = "desconto_venda"
    GESTAO_CARTOES = "gestao_cartoes"
    BLOQUEAR_CARTAO = "bloquear_cartao"
    RECARREGAR_CARTAO = "recarregar_cartao"
    EXTRATO_CARTAO = "extrato_cartao"
    RELATORIO_VENDAS = "relatorio_vendas"
    RELATORIO_FINANCEIRO = "relatorio_financeiro"
    RELATORIO_ESTOQUE = "relatorio_estoque"
    RELATORIO_CLIENTES = "relatorio_clientes"
    GESTAO_MESAS = "gestao_mesas"
    ABRIR_MESA = "abrir_mesa"
    FECHAR_MESA = "fechar_mesa"
    TRANSFERIR_MESA = "transferir_mesa"

class PermissaoBase(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único da permissão")
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da permissão")
    descricao: Optional[str] = Field(None, description="Descrição da permissão")
    tipo: TipoPermissaoEnum = Field(..., description="Tipo da permissão")
    modulo: Optional[str] = Field(None, max_length=50, description="Módulo do sistema")
    nivel_critico: int = Field(1, ge=1, le=5, description="Nível crítico (1-5)")

class PermissaoCreate(PermissaoBase):
    pass

class Permissao(PermissaoBase):
    id: int
    ativa: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

class CargoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do cargo")
    descricao: Optional[str] = Field(None, description="Descrição do cargo")
    nivel_hierarquia: int = Field(1, ge=1, le=10, description="Nível hierárquico (1-10)")
    cor: str = Field("#6b7280", pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor em formato hex")

class CargoCreate(CargoBase):
    empresa_id: Optional[int] = Field(None, description="ID da empresa")
    permissoes_ids: List[int] = Field([], description="IDs das permissões do cargo")

class CargoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    nivel_hierarquia: Optional[int] = Field(None, ge=1, le=10)
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    ativo: Optional[bool] = None
    permissoes_ids: Optional[List[int]] = Field(None, description="IDs das permissões do cargo")

class Cargo(CargoBase):
    id: int
    ativo: bool
    empresa_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]
    permissoes: List[Permissao] = []
    
    class Config:
        from_attributes = True

class CargoComContadores(Cargo):
    total_permissoes: int = Field(..., description="Total de permissões do cargo")
    total_colaboradores: int = Field(..., description="Total de colaboradores com este cargo")

# ================================================================================
# SCHEMAS PARA SISTEMA DE MESAS
# ================================================================================

class TipoMesaEnum(str, Enum):
    COMUM = "comum"
    VIP = "vip"
    CAMAROTE = "camarote"
    BAR = "bar"
    EXTERNA = "externa"
    ESPECIAL = "especial"

class StatusMesaEnum(str, Enum):
    DISPONIVEL = "disponivel"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"
    MANUTENCAO = "manutencao"
    INATIVA = "inativa"

class MesaBase(BaseModel):
    numero: str = Field(..., min_length=1, max_length=10, description="Número da mesa")
    nome_personalizado: Optional[str] = Field(None, max_length=50, description="Nome personalizado")
    tipo: TipoMesaEnum = Field(TipoMesaEnum.COMUM, description="Tipo da mesa")
    capacidade: int = Field(4, ge=1, le=20, description="Capacidade de pessoas")
    area: Optional[str] = Field(None, max_length=50, description="Área física")
    posicao_x: Optional[int] = Field(None, description="Coordenada X no mapa")
    posicao_y: Optional[int] = Field(None, description="Coordenada Y no mapa")
    andar: str = Field("Térreo", max_length=10, description="Andar do estabelecimento")
    permite_reserva: bool = Field(True, description="Permite reserva")
    valor_consumacao_minima: Decimal = Field(0, ge=0, description="Valor mínimo de consumação")
    observacoes: Optional[str] = Field(None, description="Observações sobre a mesa")

class MesaCreate(MesaBase):
    empresa_id: Optional[int] = Field(None, description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento")

class MesaUpdate(BaseModel):
    numero: Optional[str] = Field(None, min_length=1, max_length=10)
    nome_personalizado: Optional[str] = Field(None, max_length=50)
    tipo: Optional[TipoMesaEnum] = None
    capacidade: Optional[int] = Field(None, ge=1, le=20)
    area: Optional[str] = Field(None, max_length=50)
    posicao_x: Optional[int] = None
    posicao_y: Optional[int] = None
    andar: Optional[str] = Field(None, max_length=10)
    status: Optional[StatusMesaEnum] = None
    ativa: Optional[bool] = None
    permite_reserva: Optional[bool] = None
    valor_consumacao_minima: Optional[Decimal] = Field(None, ge=0)
    observacoes: Optional[str] = None

class Mesa(MesaBase):
    id: int
    status: StatusMesaEnum
    ativa: bool
    qr_code_mesa: Optional[str]
    codigo_identificacao: Optional[str]
    empresa_id: Optional[int]
    evento_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]
    
    class Config:
        from_attributes = True

class MesaComStatus(Mesa):
    """Mesa com informações de status operacional"""
    comanda_ativa: Optional[int] = Field(None, description="ID da comanda ativa na mesa")
    cliente_atual: Optional[str] = Field(None, description="Nome do cliente atual")
    valor_conta: Optional[Decimal] = Field(None, description="Valor atual da conta")
    tempo_ocupacao: Optional[int] = Field(None, description="Tempo de ocupação em minutos")

# ================================================================================
# SCHEMAS PARA CARTÕES CASHLESS
# ================================================================================

class TipoCartaoCashlessEnum(str, Enum):
    RFID = "rfid"
    NFC = "nfc"
    QR_CODE = "qr_code"
    CODIGO_BARRAS = "codigo_barras"
    VIRTUAL = "virtual"

class StatusCartaoCashlessEnum(str, Enum):
    ATIVO = "ativo"
    BLOQUEADO = "bloqueado"
    CANCELADO = "cancelado"
    PENDENTE_ATIVACAO = "pendente_ativacao"

class GrupoCartaoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do grupo")
    descricao: Optional[str] = Field(None, description="Descrição do grupo")
    cor: str = Field("#3b82f6", pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor em formato hex")
    icone: Optional[str] = Field(None, max_length=50, description="Nome do ícone")
    limite_recarga_diario: Optional[Decimal] = Field(None, gt=0, description="Limite diário de recarga")
    limite_gasto_diario: Optional[Decimal] = Field(None, gt=0, description="Limite diário de gasto")
    desconto_automatico: Decimal = Field(0, ge=0, le=100, description="Desconto automático (%)")
    cashback_percentual: Decimal = Field(0, ge=0, le=100, description="Cashback (%)")

class GrupoCartaoCreate(GrupoCartaoBase):
    empresa_id: Optional[int] = Field(None, description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento")

class GrupoCartao(GrupoCartaoBase):
    id: int
    status: str
    empresa_id: Optional[int]
    evento_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]
    
    class Config:
        from_attributes = True

class CartaoCashlessBase(BaseModel):
    numero_cartao: str = Field(..., min_length=1, max_length=20, description="Número do cartão")
    cpf_portador: Optional[str] = Field(None, pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", description="CPF do portador")
    nome_portador: Optional[str] = Field(None, max_length=255, description="Nome do portador")
    telefone_portador: Optional[str] = Field(None, max_length=20, description="Telefone do portador")
    email_portador: Optional[str] = Field(None, description="Email do portador")
    tipo: TipoCartaoCashlessEnum = Field(..., description="Tipo do cartão")
    limite_credito: Decimal = Field(0, ge=0, description="Limite de crédito")
    data_vencimento: Optional[date] = Field(None, description="Data de vencimento")

class CartaoCashlessCreate(CartaoCashlessBase):
    grupo_id: Optional[int] = Field(None, description="ID do grupo")
    mesa_id: Optional[int] = Field(None, description="ID da mesa")
    empresa_id: Optional[int] = Field(None, description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento")
    saldo_inicial: Decimal = Field(0, ge=0, description="Saldo inicial")

class CartaoCashlessUpdate(BaseModel):
    cpf_portador: Optional[str] = Field(None, pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
    nome_portador: Optional[str] = Field(None, max_length=255)
    telefone_portador: Optional[str] = Field(None, max_length=20)
    email_portador: Optional[str] = None
    status: Optional[StatusCartaoCashlessEnum] = None
    limite_credito: Optional[Decimal] = Field(None, ge=0)
    grupo_id: Optional[int] = None
    mesa_id: Optional[int] = None
    data_vencimento: Optional[date] = None

class CartaoCashless(CartaoCashlessBase):
    id: int
    codigo_rfid: Optional[str]
    codigo_nfc: Optional[str]
    qr_code: Optional[str]
    codigo_barras: Optional[str]
    status: StatusCartaoCashlessEnum
    saldo_atual: Decimal
    saldo_bonus: Decimal
    data_ativacao: Optional[datetime]
    data_ultimo_uso: Optional[datetime]
    grupo_id: Optional[int]
    mesa_id: Optional[int]
    empresa_id: Optional[int]
    evento_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]
    
    class Config:
        from_attributes = True

class PreAtivacaoCartaoBase(BaseModel):
    numero_cartao: str = Field(..., min_length=1, max_length=20, description="Número do cartão")
    tag_identificacao: str = Field(..., min_length=1, max_length=50, description="Tag de identificação")
    cpf_cliente: str = Field(..., pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", description="CPF do cliente")
    nome_cliente: str = Field(..., min_length=1, max_length=255, description="Nome do cliente")
    telefone_cliente: Optional[str] = Field(None, max_length=20, description="Telefone do cliente")
    email_cliente: Optional[str] = Field(None, description="Email do cliente")
    saldo_inicial: Decimal = Field(0, ge=0, description="Saldo inicial")
    observacoes: Optional[str] = Field(None, description="Observações")

class PreAtivacaoCartaoCreate(PreAtivacaoCartaoBase):
    grupo_id: Optional[int] = Field(None, description="ID do grupo")

class PreAtivacaoCartao(PreAtivacaoCartaoBase):
    id: int
    vinculado_por: int
    vinculado_em: datetime
    ativado: bool
    data_ativacao: Optional[datetime]
    grupo_id: Optional[int]
    
    class Config:
        from_attributes = True

# ================================================================================
# SCHEMAS PARA TRANSAÇÕES CASHLESS
# ================================================================================

class RecargaCashlessBase(BaseModel):
    valor_recarga: Decimal = Field(..., gt=0, description="Valor da recarga")
    valor_bonus: Decimal = Field(0, ge=0, description="Valor de bônus")
    metodo_pagamento: str = Field(..., min_length=1, max_length=50, description="Método de pagamento")
    observacoes: Optional[str] = Field(None, description="Observações da recarga")

class RecargaCashlessCreate(RecargaCashlessBase):
    cartao_id: int = Field(..., gt=0, description="ID do cartão")
    pdv_id: Optional[str] = Field(None, max_length=50, description="ID do PDV")

class RecargaCashless(RecargaCashlessBase):
    id: int
    cartao_id: int
    codigo_transacao_pagamento: Optional[str]
    status_pagamento: str
    operador_id: int
    pdv_id: Optional[str]
    ip_origem: Optional[str]
    criado_em: datetime
    
    class Config:
        from_attributes = True

class TransacaoCashlessBase(BaseModel):
    valor_transacao: Decimal = Field(..., gt=0, description="Valor da transação")
    valor_desconto: Decimal = Field(0, ge=0, description="Valor do desconto")
    produtos_json: Optional[Dict[str, Any]] = Field(None, description="Produtos comprados (JSON)")
    pdv_id: Optional[str] = Field(None, max_length=50, description="ID do PDV")

class TransacaoCashlessCreate(TransacaoCashlessBase):
    cartao_id: int = Field(..., gt=0, description="ID do cartão")
    mesa_id: Optional[int] = Field(None, description="ID da mesa")

class TransacaoCashless(TransacaoCashlessBase):
    id: int
    cartao_id: int
    valor_final: Decimal
    mesa_id: Optional[int]
    operador_id: int
    estornada: bool
    data_estorno: Optional[datetime]
    motivo_estorno: Optional[str]
    estornada_por: Optional[int]
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================================================================================
# SCHEMAS PARA CARDÁPIOS DIGITAIS
# ================================================================================

class CardapioDigitalBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do cardápio")
    descricao: Optional[str] = Field(None, description="Descrição do cardápio")
    cor_primaria: str = Field("#3b82f6", pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor primária")
    cor_secundaria: str = Field("#1f2937", pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor secundária")
    logo_url: Optional[str] = Field(None, max_length=500, description="URL do logo")
    imagem_fundo_url: Optional[str] = Field(None, max_length=500, description="URL da imagem de fundo")
    publico: bool = Field(True, description="Cardápio público")
    permite_pedidos: bool = Field(False, description="Permite fazer pedidos")
    exibe_precos: bool = Field(True, description="Exibe preços dos produtos")
    url_personalizada: Optional[str] = Field(None, max_length=255, description="URL personalizada")

class CardapioDigitalCreate(CardapioDigitalBase):
    empresa_id: Optional[int] = Field(None, description="ID da empresa")
    evento_id: Optional[int] = Field(None, description="ID do evento")

class CardapioDigital(CardapioDigitalBase):
    id: int
    uuid_cardapio: str
    ativo: bool
    qr_code_acesso: Optional[str]
    total_acessos: int
    ultimo_acesso: Optional[datetime]
    empresa_id: Optional[int]
    evento_id: Optional[int]
    criado_por: int
    criado_em: datetime
    atualizado_em: Optional[datetime]
    
    class Config:
        from_attributes = True

class CategoriaCardapioDigitalBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")
    ordem: int = Field(1, ge=1, description="Ordem de exibição")
    cor: str = Field("#6b7280", pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor da categoria")
    icone: Optional[str] = Field(None, max_length=50, description="Nome do ícone")

class CategoriaCardapioDigitalCreate(CategoriaCardapioDigitalBase):
    cardapio_id: int = Field(..., gt=0, description="ID do cardápio")

class CategoriaCardapioDigital(CategoriaCardapioDigitalBase):
    id: int
    cardapio_id: int
    ativa: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================================================================================
# SCHEMAS PARA BUSCA E FILTROS
# ================================================================================

class FiltrosCartaoCashless(BaseModel):
    """Filtros para busca de cartões cashless"""
    cpf_portador: Optional[str] = Field(None, description="CPF do portador")
    nome_portador: Optional[str] = Field(None, description="Nome do portador")
    numero_cartao: Optional[str] = Field(None, description="Número do cartão")
    status: Optional[StatusCartaoCashlessEnum] = Field(None, description="Status do cartão")
    grupo_id: Optional[int] = Field(None, description="ID do grupo")
    ativo: Optional[bool] = Field(None, description="Somente cartões ativos")
    com_saldo: Optional[bool] = Field(None, description="Somente cartões com saldo")
    data_inicio: Optional[date] = Field(None, description="Data inicial de criação")
    data_fim: Optional[date] = Field(None, description="Data final de criação")

class FiltrosMesas(BaseModel):
    """Filtros para busca de mesas"""
    numero: Optional[str] = Field(None, description="Número da mesa")
    tipo: Optional[TipoMesaEnum] = Field(None, description="Tipo da mesa")
    status: Optional[StatusMesaEnum] = Field(None, description="Status da mesa")
    area: Optional[str] = Field(None, description="Área da mesa")
    ativa: Optional[bool] = Field(None, description="Somente mesas ativas")
    disponivel: Optional[bool] = Field(None, description="Somente mesas disponíveis")

class FiltrosCategoriaClientes(BaseModel):
    """Filtros para busca de categorias de clientes"""
    nome: Optional[str] = Field(None, description="Nome da categoria")
    tipo: Optional[TipoCategoriaClienteEnum] = Field(None, description="Tipo da categoria")
    status: Optional[StatusCategoriaClienteEnum] = Field(None, description="Status da categoria")
    ativa: Optional[bool] = Field(None, description="Somente categorias ativas")

# ================================================================================
# SCHEMAS PARA RELATÓRIOS E ESTATÍSTICAS
# ================================================================================

class EstatisticasCartoes(BaseModel):
    """Estatísticas dos cartões cashless"""
    total_cartoes: int = Field(..., description="Total de cartões")
    cartoes_ativos: int = Field(..., description="Cartões ativos")
    cartoes_bloqueados: int = Field(..., description="Cartões bloqueados")
    saldo_total: Decimal = Field(..., description="Saldo total de todos os cartões")
    recargas_hoje: int = Field(..., description="Recargas realizadas hoje")
    valor_recargas_hoje: Decimal = Field(..., description="Valor total das recargas de hoje")
    transacoes_hoje: int = Field(..., description="Transações realizadas hoje")
    valor_transacoes_hoje: Decimal = Field(..., description="Valor total das transações de hoje")

class EstatisticasMesas(BaseModel):
    """Estatísticas das mesas"""
    total_mesas: int = Field(..., description="Total de mesas")
    mesas_disponiveis: int = Field(..., description="Mesas disponíveis")
    mesas_ocupadas: int = Field(..., description="Mesas ocupadas")
    mesas_reservadas: int = Field(..., description="Mesas reservadas")
    taxa_ocupacao: Decimal = Field(..., description="Taxa de ocupação (%)")
    tempo_medio_ocupacao: Optional[int] = Field(None, description="Tempo médio de ocupação (minutos)")

class DashboardCashless(BaseModel):
    """Dashboard completo do sistema cashless"""
    estatisticas_cartoes: EstatisticasCartoes
    estatisticas_mesas: EstatisticasMesas
    categorias_clientes_count: int = Field(..., description="Total de categorias de clientes")
    grupos_cartoes_count: int = Field(..., description="Total de grupos de cartões")
    cardapios_digitais_count: int = Field(..., description="Total de cardápios digitais")
    ultima_atualizacao: datetime = Field(..., description="Última atualização dos dados")
