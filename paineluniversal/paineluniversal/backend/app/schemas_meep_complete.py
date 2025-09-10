"""
Schemas Pydantic completos - Sistema Universal com funcionalidades MEEP
Validação e serialização de dados
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal
import enum

# ==================== SCHEMAS BASE ====================

class EmpresaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    cnpj: str = Field(..., pattern=r'^\d{14}$|^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')
    segmento: Optional[str] = "BARES"
    plano: Optional[str] = "PREMIUM"
    logo_url: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = {}

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaUpdate(BaseModel):
    nome: Optional[str] = None
    segmento: Optional[str] = None
    plano: Optional[str] = None
    logo_url: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None

class EmpresaResponse(EmpresaBase):
    id: int
    ativo: bool
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==================== USUÁRIO ====================

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    cpf: str = Field(..., pattern=r'^\d{11}$|^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    telefone: Optional[str] = None
    tipo: Optional[str] = "CLIENTE"
    avatar_url: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)
    empresa_id: Optional[int] = None

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    avatar_url: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id: int
    empresa_id: Optional[int]
    ativo: bool
    ultimo_acesso: Optional[datetime]
    criado_em: datetime
    cargos: List[Dict] = []
    
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    cpf: str
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse

# ==================== CLIENTE ====================

class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    cpf: str = Field(..., pattern=r'^\d{11}$|^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    categoria_id: Optional[int] = None
    tag_rfid: Optional[str] = None

class ClienteCreate(ClienteBase):
    empresa_id: int

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    categoria_id: Optional[int] = None
    tag_rfid: Optional[str] = None
    ativo: Optional[bool] = None

class ClienteResponse(ClienteBase):
    id: int
    empresa_id: int
    pontos_fidelidade: int
    nivel_fidelidade: str
    saldo_cashless: Decimal
    ativo: bool
    criado_em: datetime
    categoria: Optional[Dict] = None
    
    model_config = ConfigDict(from_attributes=True)

# ==================== PRODUTO ====================

class ProdutoBase(BaseModel):
    codigo: Optional[str] = None
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = None
    preco: Decimal = Field(..., gt=0)
    preco_custo: Optional[Decimal] = None
    imagem_url: Optional[str] = None
    unidade_medida: Optional[str] = "UN"
    estoque_minimo: Optional[Decimal] = 0
    pontos_fidelidade: Optional[int] = 0
    disponivel_app: Optional[bool] = True
    disponivel_pdv: Optional[bool] = True

class ProdutoCreate(ProdutoBase):
    empresa_id: int
    categoria_ids: Optional[List[int]] = []

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[Decimal] = None
    preco_custo: Optional[Decimal] = None
    imagem_url: Optional[str] = None
    estoque_minimo: Optional[Decimal] = None
    pontos_fidelidade: Optional[int] = None
    disponivel_app: Optional[bool] = None
    disponivel_pdv: Optional[bool] = None
    ativo: Optional[bool] = None

class ProdutoResponse(ProdutoBase):
    id: int
    empresa_id: int
    estoque_atual: Decimal
    ativo: bool
    criado_em: datetime
    categorias: List[Dict] = []
    
    model_config = ConfigDict(from_attributes=True)

# ==================== CARDÁPIO ====================

class CardapioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = None
    tipo: Optional[str] = "PDV"  # APP, PDV, DIGITAL, DELIVERY

class CardapioCreate(CardapioBase):
    empresa_id: int
    produto_ids: Optional[List[int]] = []

class CardapioUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    produto_ids: Optional[List[int]] = None
    ativo: Optional[bool] = None

class CardapioResponse(CardapioBase):
    id: int
    empresa_id: int
    uuid: str
    url_digital: Optional[str]
    qr_code_url: Optional[str]
    ativo: bool
    criado_em: datetime
    produtos: List[ProdutoResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# ==================== COMANDA ====================

class ComandaBase(BaseModel):
    numero: str = Field(..., min_length=1, max_length=50)
    mesa: Optional[str] = None
    observacoes: Optional[str] = None

class ComandaCreate(ComandaBase):
    cliente_id: Optional[int] = None

class ComandaUpdate(BaseModel):
    mesa: Optional[str] = None
    status: Optional[str] = None
    taxa_servico: Optional[Decimal] = None
    desconto: Optional[Decimal] = None
    observacoes: Optional[str] = None

class ComandaResponse(ComandaBase):
    id: int
    cliente_id: Optional[int]
    status: str
    valor_total: Decimal
    taxa_servico: Decimal
    desconto: Decimal
    aberta_em: datetime
    fechada_em: Optional[datetime]
    pedidos: List[Dict] = []
    pagamentos: List[Dict] = []
    
    model_config = ConfigDict(from_attributes=True)

# ==================== PEDIDO ====================

class PedidoBase(BaseModel):
    produto_id: int
    quantidade: Decimal = Field(..., gt=0)
    observacoes: Optional[str] = None

class PedidoCreate(PedidoBase):
    comanda_id: int

class PedidoUpdate(BaseModel):
    quantidade: Optional[Decimal] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class PedidoResponse(PedidoBase):
    id: int
    comanda_id: int
    preco_unitario: Decimal
    valor_total: Decimal
    status: str
    criado_em: datetime
    preparado_em: Optional[datetime]
    entregue_em: Optional[datetime]
    produto: ProdutoResponse
    
    model_config = ConfigDict(from_attributes=True)

# ==================== VENDA ====================

class ItemVendaBase(BaseModel):
    produto_id: int
    quantidade: Decimal = Field(..., gt=0)
    preco_unitario: Decimal

class VendaBase(BaseModel):
    cliente_cpf: Optional[str] = None
    tipo_pagamento: str
    desconto: Optional[Decimal] = 0
    observacoes: Optional[str] = None

class VendaCreate(VendaBase):
    evento_id: Optional[int] = None
    vendedor_id: int
    itens: List[ItemVendaBase]

class VendaResponse(VendaBase):
    id: int
    evento_id: Optional[int]
    vendedor_id: int
    numero_venda: str
    valor_total: Decimal
    status: str
    criado_em: datetime
    itens: List[Dict] = []
    vendedor: Dict
    
    model_config = ConfigDict(from_attributes=True)

# ==================== CASHLESS ====================

class CartaoCashlessBase(BaseModel):
    numero: str = Field(..., min_length=1, max_length=50)
    tag_rfid: Optional[str] = None
    limite_credito: Optional[Decimal] = 0

class CartaoCashlessCreate(CartaoCashlessBase):
    cliente_id: int

class CartaoCashlessUpdate(BaseModel):
    limite_credito: Optional[Decimal] = None
    bloqueado: Optional[bool] = None

class RecargaCashless(BaseModel):
    cartao_id: int
    valor: Decimal = Field(..., gt=0)
    forma_pagamento: str

class CartaoCashlessResponse(CartaoCashlessBase):
    id: int
    cliente_id: int
    saldo: Decimal
    bloqueado: bool
    criado_em: datetime
    cliente: Dict
    
    model_config = ConfigDict(from_attributes=True)

# ==================== CHECK-IN ====================

class CheckinBase(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    tipo_entrada: str = "MANUAL"  # QR_CODE, MANUAL, FACIAL, RFID

class CheckinCreate(CheckinBase):
    evento_id: int
    lista_id: Optional[int] = None

class CheckinResponse(CheckinBase):
    id: int
    evento_id: int
    lista_id: Optional[int]
    horario_entrada: datetime
    horario_saida: Optional[datetime]
    evento: Dict
    lista: Optional[Dict]
    
    model_config = ConfigDict(from_attributes=True)

# ==================== EVENTO ====================

class EventoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    local: Optional[str] = None
    capacidade_maxima: Optional[int] = None
    idade_minima: Optional[int] = None
    configuracoes: Optional[Dict[str, Any]] = {}

class EventoCreate(EventoBase):
    empresa_id: int

class EventoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    local: Optional[str] = None
    capacidade_maxima: Optional[int] = None
    idade_minima: Optional[int] = None
    configuracoes: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None

class EventoResponse(EventoBase):
    id: int
    empresa_id: int
    ativo: bool
    criado_em: datetime
    total_checkins: Optional[int] = 0
    total_vendas: Optional[Decimal] = 0
    
    model_config = ConfigDict(from_attributes=True)

# ==================== DASHBOARD ====================

class DashboardStats(BaseModel):
    vendas_hoje: Decimal
    vendas_mes: Decimal
    clientes_novos_mes: int
    produtos_mais_vendidos: List[Dict]
    horarios_pico: List[Dict]
    taxa_ocupacao: float
    ticket_medio: Decimal

class DashboardFinanceiro(BaseModel):
    receita_total: Decimal
    receita_dinheiro: Decimal
    receita_cartao: Decimal
    receita_pix: Decimal
    receita_cashless: Decimal
    comandas_abertas: int
    comandas_fechadas: int
    valor_comandas_abertas: Decimal

# ==================== RELATÓRIOS ====================

class FiltroRelatorio(BaseModel):
    data_inicio: date
    data_fim: date
    empresa_id: Optional[int] = None
    evento_id: Optional[int] = None
    caixa_id: Optional[int] = None
    tipo_pagamento: Optional[str] = None

class RelatorioVendas(BaseModel):
    filtros: FiltroRelatorio
    formato: str = "JSON"  # JSON, EXCEL, PDF

class RelatorioResponse(BaseModel):
    total_vendas: int
    valor_total: Decimal
    ticket_medio: Decimal
    produtos_vendidos: List[Dict]
    formas_pagamento: Dict[str, Decimal]
    vendas_por_dia: List[Dict]
    vendas_por_hora: List[Dict]

# ==================== ESTOQUE ====================

class MovimentacaoEstoqueBase(BaseModel):
    produto_id: int
    tipo_operacao: str  # ENTRADA, SAIDA, TRANSFERENCIA, AJUSTE
    quantidade: Decimal
    motivo: Optional[str] = None
    documento: Optional[str] = None

class MovimentacaoEstoqueCreate(MovimentacaoEstoqueBase):
    usuario_id: int

class MovimentacaoEstoqueResponse(MovimentacaoEstoqueBase):
    id: int
    saldo_anterior: Decimal
    saldo_posterior: Decimal
    criado_em: datetime
    produto: Dict
    usuario: Dict
    
    model_config = ConfigDict(from_attributes=True)

# ==================== INTEGRAÇÃO ====================

class IntegracaoBase(BaseModel):
    nome: str
    tipo: str  # COMUNICACAO, ERP, FISCAL, DELIVERY, PESQUISA
    configuracoes: Dict[str, Any] = {}
    webhook_url: Optional[str] = None

class IntegracaoCreate(IntegracaoBase):
    token: Optional[str] = None

class IntegracaoUpdate(BaseModel):
    configuracoes: Optional[Dict[str, Any]] = None
    token: Optional[str] = None
    webhook_url: Optional[str] = None
    status: Optional[str] = None

class IntegracaoResponse(IntegracaoBase):
    id: int
    status: str
    ultima_sincronizacao: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# ==================== AUTOMAÇÃO ====================

class AutomacaoBase(BaseModel):
    nome: str
    gatilho: str  # VENDA_REALIZADA, CLIENTE_CADASTRADO, etc
    condicoes: Dict[str, Any] = {}
    acoes: List[Dict[str, Any]] = []

class AutomacaoCreate(AutomacaoBase):
    pass

class AutomacaoUpdate(BaseModel):
    nome: Optional[str] = None
    condicoes: Optional[Dict[str, Any]] = None
    acoes: Optional[List[Dict[str, Any]]] = None
    status: Optional[bool] = None

class AutomacaoResponse(AutomacaoBase):
    id: int
    status: bool
    execucoes: int
    ultima_execucao: Optional[datetime]
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==================== FIDELIDADE ====================

class NivelFidelidadeBase(BaseModel):
    nome: str
    pontuacao_minima: int
    beneficios: List[str] = []
    desconto_percentual: float = 0

class ProgramaFidelidade(BaseModel):
    cliente_id: int
    pontos: int
    nivel: str
    historico: List[Dict] = []

class ResgatePontos(BaseModel):
    cliente_id: int
    pontos: int
    tipo_resgate: str  # DESCONTO, PRODUTO, CASHBACK
    valor: Decimal

# ==================== MARKETING ====================

class CampanhaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: str  # EMAIL, SMS, PUSH, WHATSAPP
    segmentacao: Dict[str, Any] = {}
    conteudo: Dict[str, Any] = {}
    data_inicio: datetime
    data_fim: datetime

class CampanhaCreate(CampanhaBase):
    pass

class CampanhaResponse(CampanhaBase):
    id: int
    status: str
    enviados: int
    abertos: int
    cliques: int
    conversoes: int
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CupomDescontoBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=50)
    descricao: Optional[str] = None
    tipo: str  # PERCENTUAL, VALOR_FIXO
    valor: Decimal
    quantidade_maxima: Optional[int] = None
    valido_de: datetime
    valido_ate: datetime
    condicoes: Dict[str, Any] = {}

class CupomDescontoCreate(CupomDescontoBase):
    pass

class CupomDescontoResponse(CupomDescontoBase):
    id: int
    quantidade_usada: int
    ativo: bool
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)