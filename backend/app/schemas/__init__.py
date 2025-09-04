# Schemas package
from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime, date, timezone
from typing import Optional, List
from decimal import Decimal

# Schemas básicos para auth
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    cpf: Optional[str] = None

class LoginRequest(BaseModel):
    cpf: str
    senha: str

# Schemas básicos para usuários
class UsuarioBase(BaseModel):
    nome: str
    email: str
    cpf: str
    telefone: Optional[str] = None
    tipo_usuario: str = "cliente"
    
class UsuarioCreate(UsuarioBase):
    senha: str
    
class UsuarioUpdate(UsuarioBase):
    senha: Optional[str] = None
    
class UsuarioRegister(BaseModel):
    nome: str
    email: str
    cpf: str
    telefone: Optional[str] = None
    senha: str
    tipo: Optional[str] = "cliente"
    
class Usuario(UsuarioBase):
    id: int
    ativo: bool = True
    
    class Config:
        from_attributes = True

# Schemas básicos para eventos
class EventoBase(BaseModel):
    nome: str
    local: str
    data_evento: datetime
    endereco: Optional[str] = None
    limite_idade: Optional[int] = None
    capacidade_maxima: Optional[int] = None
    
class EventoCreate(EventoBase):
    pass
    
class Evento(EventoBase):
    id: int
    ativo: bool = True
    
    class Config:
        from_attributes = True
        
class EventoDetalhado(Evento):
    total_vendas: int = 0
    receita_total: float = 0.0
    
class EventoFiltros(BaseModel):
    nome: Optional[str] = None

# Outros schemas básicos necessários
class PromoterEventoCreate(BaseModel):
    evento_id: int
    
class PromoterEventoResponse(BaseModel):
    id: int
    evento_id: int

# Schemas para empresas
class EmpresaBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    inscricao_estadual: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    email: str
    telefone: str
    telefone_secundario: Optional[str] = None
    whatsapp: Optional[str] = None
    site: Optional[str] = None
    responsavel_nome: Optional[str] = None
    responsavel_cargo: Optional[str] = None
    responsavel_email: Optional[str] = None
    responsavel_telefone: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[str] = None
    observacoes: Optional[str] = None
    
    @field_validator('cnpj')
    @classmethod
    def validar_cnpj(cls, v):
        # Remove caracteres especiais
        cnpj = ''.join(filter(str.isdigit, v))
        if len(cnpj) != 14:
            raise ValueError('CNPJ deve ter 14 dígitos')
        return cnpj
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        if v and len(v) != 2:
            raise ValueError('Estado deve ter 2 caracteres')
        return v.upper() if v else v
    
    @field_validator('tipo_conta')
    @classmethod
    def validar_tipo_conta(cls, v):
        if v and v not in ['corrente', 'poupanca']:
            raise ValueError('Tipo de conta deve ser "corrente" ou "poupanca"')
        return v
    
class EmpresaCreate(EmpresaBase):
    pass
    
class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    telefone_secundario: Optional[str] = None
    whatsapp: Optional[str] = None
    site: Optional[str] = None
    responsavel_nome: Optional[str] = None
    responsavel_cargo: Optional[str] = None
    responsavel_email: Optional[str] = None
    responsavel_telefone: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[str] = None
    observacoes: Optional[str] = None
    ativa: Optional[bool] = None
    
class Empresa(EmpresaBase):
    id: int
    ativa: bool = True
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para listas
class ListaBase(BaseModel):
    nome: str
    
class ListaCreate(ListaBase):
    pass
    
class Lista(ListaBase):
    id: int
    evento_id: int
    
    class Config:
        from_attributes = True

# Schema detalhado para listas (usado por routers/listas.py)
class ListaDetalhada(Lista):
    total_convidados: int = 0
    convidados_presentes: int = 0
    taxa_presenca: float = 0.0
    receita_gerada: Decimal = Decimal('0.00')
    promoter_nome: Optional[str] = None

class ConvidadoCreate(BaseModel):
    cpf: str
    nome: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None

class ConvidadoImport(BaseModel):
    cpf: str
    nome: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None

# Schemas para transações
class TransacaoBase(BaseModel):
    valor: float
    
class TransacaoCreate(TransacaoBase):
    pass
    
class Transacao(TransacaoBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para checkins
class CheckinBase(BaseModel):
    data_checkin: datetime
    
class CheckinCreate(CheckinBase):
    pass
    
class Checkin(CheckinBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para dashboard
class DashboardResumo(BaseModel):
    total_eventos: int = 0
    total_usuarios: int = 0
    total_checkins: int = 0
    receita_total: float = 0.0
    eventos_hoje: int = 0
    vendas_hoje: int = 0


# Schema para retorno do dashboard de listas
class DashboardListas(BaseModel):
    total_listas: int = 0
    total_convidados: int = 0
    total_presentes: int = 0
    taxa_presenca_geral: float = 0.0
    listas_mais_ativas: List[dict] = []
    promoters_destaque: List[dict] = []
    convidados_por_tipo: List[dict] = []
    presencas_tempo_real: List[dict] = []


# Schemas para ranking e dashboards avançados
class RankingPromoter(BaseModel):
    promoter_id: int
    nome_promoter: str
    total_vendas: int
    receita_gerada: Decimal
    posicao: int

class RankingPromoterAvancado(RankingPromoter):
    total_checkins: int = 0
    taxa_presenca: float = 0.0
    taxa_conversao: float = 0.0
    badge: Optional[str] = None

class DadosGrafico(BaseModel):
    data: str
    vendas: int
    receita: float

class FiltrosDashboard(BaseModel):
    evento_id: Optional[int] = None
    promoter_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

class DashboardAvancado(BaseModel):
    total_eventos: int = 0
    total_vendas: int = 0
    total_checkins: int = 0
    receita_total: float = 0.0
    taxa_conversao: float = 0.0
    vendas_hoje: int = 0
    vendas_semana: int = 0
    vendas_mes: int = 0
    receita_hoje: float = 0.0
    receita_semana: float = 0.0
    receita_mes: float = 0.0
    checkins_hoje: int = 0
    checkins_semana: int = 0
    taxa_presenca: float = 0.0
    fila_espera: int = 0
    cortesias: int = 0
    inadimplentes: int = 0
    aniversariantes_mes: int = 0
    consumo_medio: float = 0.0


# Schema para relatórios de vendas
class RelatorioVendas(BaseModel):
    evento_id: int
    nome_evento: str
    total_vendas: int
    receita_total: float
    vendas_por_lista: List[dict] = []
    vendas_por_promoter: List[dict] = []

# Schemas mínimos para PDV
class ProdutoCreate(BaseModel):
    nome: str
    codigo_barras: Optional[str] = None
    codigo_interno: Optional[str] = None
    preco: float
    controla_estoque: bool = False
    estoque_atual: Optional[int] = 0
    estoque_minimo: Optional[int] = 0
    categoria: Optional[str] = None

class Produto(BaseModel):
    id: int
    nome: str
    codigo_barras: Optional[str] = None
    codigo_interno: Optional[str] = None
    preco: float
    controla_estoque: bool = False
    estoque_atual: Optional[int] = 0
    estoque_minimo: Optional[int] = 0
    categoria: Optional[str] = None

class ProdutoUpdate(ProdutoCreate):
    nome: Optional[str] = None
    preco: Optional[float] = None
    controla_estoque: Optional[bool] = None
    estoque_atual: Optional[int] = None
    estoque_minimo: Optional[int] = None

class ProdutoResponse(Produto):
    pass

class ComandaCreate(BaseModel):
    evento_id: int
    cpf_cliente: Optional[str] = None
    saldo_inicial: Decimal = Decimal('0.00')

class Comanda(BaseModel):
    id: int
    evento_id: int
    cpf_cliente: Optional[str] = None
    saldo_atual: Decimal = Decimal('0.00')

class RecargaComandaCreate(BaseModel):
    valor: Decimal
    tipo_pagamento: Optional[str] = None

class RecargaComanda(BaseModel):
    id: int
    comanda_id: int
    valor: Decimal

class ItemVendaPDVCreate(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal
    observacoes: Optional[str] = None

class PagamentoPDVCreate(BaseModel):
    tipo_pagamento: str
    valor: Decimal
    promoter_id: Optional[int] = None
    comissao_percentual: Optional[Decimal] = None

class VendaPDVCreate(BaseModel):
    evento_id: int
    cpf_cliente: Optional[str] = None
    nome_cliente: Optional[str] = None
    itens: List[ItemVendaPDVCreate]
    pagamentos: List[PagamentoPDVCreate]
    comanda_id: Optional[int] = None
    cupom_codigo: Optional[str] = None
    observacoes: Optional[str] = None

class VendaPDV(BaseModel):
    id: int
    numero_venda: str
    valor_final: Decimal

class CaixaPDVCreate(BaseModel):
    evento_id: int
    numero_caixa: str
    valor_abertura: Decimal

class CaixaPDV(BaseModel):
    id: int
    numero_caixa: str
    evento_id: int
    valor_abertura: Decimal
    valor_vendas: Decimal = Decimal('0.00')
    valor_fechamento: Optional[Decimal] = None
    status: str = "aberto"

class RelatorioVendasPDV(BaseModel):
    total_vendas: int
    valor_total: float

class DashboardPDV(BaseModel):
    vendas_hoje: int
    valor_vendas_hoje: float
    produtos_em_falta: int
    comandas_ativas: int
    caixas_abertos: int
    vendas_por_hora: List[dict] = []
    produtos_mais_vendidos: List[dict] = []
    alertas: List[dict] = []

# Schemas mínimos para gamificação
class ConquistaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    criterio_valor: int = 0
    ativa: bool = True
    badge_nivel: Optional[str] = None
    icone: Optional[str] = None

class Conquista(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    criterio_valor: int = 0
    ativa: bool = True
    badge_nivel: Optional[str] = None
    icone: Optional[str] = None

class MetricaPromoterResponse(BaseModel):
    promoter_id: int
    total_vendas: int
    total_checkins: int

class RankingGamificado(BaseModel):
    promoter_id: int
    nome_promoter: str
    badge_principal: str
    nivel_experiencia: int
    total_vendas: int
    receita_gerada: Decimal
    taxa_presenca: float
    taxa_conversao: float
    crescimento_mensal: float
    posicao_atual: int
    posicao_anterior: Optional[int]
    conquistas_total: int
    conquistas_mes: int
    eventos_ativos: int
    streak_vendas: int
    pontuacao_total: int

class FiltrosRanking(BaseModel):
    evento_id: Optional[int] = None
    periodo_inicio: Optional[date] = None
    periodo_fim: Optional[date] = None

class PromoterConquistaResponse(BaseModel):
    id: int
    conquista_nome: str
    conquista_descricao: Optional[str]
    badge_nivel: Optional[str]
    icone: Optional[str]
    valor_alcancado: Optional[int]
    data_conquista: Optional[datetime]
    evento_nome: Optional[str]

class DashboardGamificacao(BaseModel):
    ranking_geral: List[RankingGamificado]
    conquistas_recentes: List[PromoterConquistaResponse]
    metricas_periodo: dict
    badges_disponiveis: List[dict]
    alertas_gamificacao: List[dict]
    estatisticas_gerais: dict

# Schemas para cupons
class CupomBase(BaseModel):
    codigo: str
    
class CupomCreate(CupomBase):
    pass
    
class Cupom(CupomBase):
    id: int
    
    class Config:
        from_attributes = True

class CupomResponse(BaseModel):
    id: int
    codigo: str
    desconto_percentual: Optional[float] = None
    desconto_valor: Optional[float] = None
    lista_nome: Optional[str] = None
    evento_nome: Optional[str] = None

# ----- Adições para evitar ImportErrors em múltiplos routers -----
# Schemas adicionais para listagem e filtros de produtos
class ProdutoFilter(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    status: Optional[str] = None
    estoque_baixo: Optional[bool] = None


class ProdutoList(BaseModel):
    produtos: List[Produto] = []
    total: int = 0
    page: int = 1
    size: int = 0
    pages: int = 1


# Schemas para MEep / analytics / equipamentos / clientes
class ClienteEventoResponse(BaseModel):
    id: int
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    status: Optional[str] = None


class ClienteEventoCreate(BaseModel):
    evento_id: int
    nome_completo: str
    cpf: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    status: Optional[str] = "ativo"


class ValidacaoAcessoResponse(BaseModel):
    id: int
    cliente_id: Optional[int] = None
    evento_id: Optional[int] = None
    sucesso: bool = False
    timestamp_validacao: Optional[datetime] = None
    motivo_falha: Optional[str] = None
    ip_address: Optional[str] = None


class EquipamentoEventoResponse(BaseModel):
    id: int
    evento_id: int
    ip_address: Optional[str] = None
    serial: Optional[str] = None
    status: Optional[str] = None
    ultima_atividade: Optional[datetime] = None


class EquipamentoEventoCreate(BaseModel):
    evento_id: int
    ip_address: str
    serial: Optional[str] = None


class PrevisaoIAResponse(BaseModel):
    id: int
    evento_id: int
    tipo_previsao: Optional[str] = None
    timestamp_previsao: Optional[datetime] = None
    dados_entrada: Optional[dict] = {}
    resultado_previsao: Optional[dict] = {}


class AnalyticsMEEPResponse(BaseModel):
    metricas: dict
    timestamp: Optional[datetime] = None


class LogSegurancaMEEPResponse(BaseModel):
    id: int
    evento_id: Optional[int] = None
    gravidade: Optional[str] = None
    tipo_evento: Optional[str] = None
    dados_evento: Optional[dict] = {}
    timestamp_evento: Optional[datetime] = None
    resolvido: bool = False


# Schemas para formas de pagamento
class FormaPagamento(BaseModel):
    id: int
    nome: str
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    ativo: bool = True
    ordem_exibicao: Optional[int] = 0
    limite_minimo: Optional[float] = None
    limite_maximo: Optional[float] = None


class FormaPagamentoCreate(BaseModel):
    nome: str
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    ativo: bool = True
    ordem_exibicao: Optional[int] = 0
    limite_minimo: Optional[float] = None
    limite_maximo: Optional[float] = None


class FormaPagamentoUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    ativo: Optional[bool] = None
    ordem_exibicao: Optional[int] = None
    limite_minimo: Optional[float] = None
    limite_maximo: Optional[float] = None


class FormaPagamentoDetalhada(FormaPagamento):
    detalhes: Optional[dict] = {}


class FormaPagamentoList(BaseModel):
    items: List[FormaPagamento] = []
    total: int = 0
    page: int = 1
    per_page: int = 10
    pages: int = 1

# ----- Fim adições -----

# Schemas financeiros mínimos
class MovimentacaoFinanceiraBase(BaseModel):
    evento_id: int
    tipo: str
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valor: Decimal
    status: Optional[str] = "pendente"
    promoter_id: Optional[int] = None


class MovimentacaoFinanceiraCreate(MovimentacaoFinanceiraBase):
    pass


class MovimentacaoFinanceiraUpdate(BaseModel):
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valor: Optional[Decimal] = None
    status: Optional[str] = None


class MovimentacaoFinanceira(MovimentacaoFinanceiraBase):
    id: int
    criado_em: Optional[datetime] = None


class CaixaEventoCreate(BaseModel):
    evento_id: int
    numero_caixa: str
    saldo_inicial: Decimal


class CaixaEvento(BaseModel):
    id: int
    evento_id: int
    numero_caixa: str
    saldo_inicial: Decimal
    total_entradas: Decimal = Decimal('0.00')
    total_saidas: Decimal = Decimal('0.00')
    total_vendas_listas: Decimal = Decimal('0.00')
    total_vendas_pdv: Decimal = Decimal('0.00')
    saldo_final: Decimal = Decimal('0.00')
    status: str = "aberto"
    criado_em: Optional[datetime] = None


class DashboardFinanceiro(BaseModel):
    evento_id: int
    saldo_atual: Decimal
    total_entradas: Decimal
    total_saidas: Decimal
    total_vendas: Decimal
    lucro_prejuizo: Decimal
    movimentacoes_recentes: List[dict] = []
    categorias_despesas: List[dict] = []
    repasses_promoters: List[dict] = []
    status_caixa: str = "fechado"
# Export essentials
__all__ = [
    "Token", "TokenData", "LoginRequest",
    "UsuarioBase", "UsuarioCreate", "UsuarioUpdate", "UsuarioRegister", "Usuario",
    "EventoBase", "EventoCreate", "Evento", "EventoDetalhado", "EventoFiltros",
    "PromoterEventoCreate", "PromoterEventoResponse",
    "EmpresaBase", "EmpresaCreate", "EmpresaUpdate", "Empresa",
    "ListaBase", "ListaCreate", "Lista", "ListaDetalhada",
    "TransacaoBase", "TransacaoCreate", "Transacao",
    "CheckinBase", "CheckinCreate", "Checkin",
    "DashboardResumo",
    "DashboardListas",
    "ConvidadoCreate", "ConvidadoImport",
    "CupomBase", "CupomCreate", "Cupom"
]

__all__.extend([
    # produtos
    "ProdutoFilter", "ProdutoList",
    # meep / analytics
    "ClienteEventoResponse", "ClienteEventoCreate", "ValidacaoAcessoResponse",
    "EquipamentoEventoResponse", "EquipamentoEventoCreate", "PrevisaoIAResponse",
    "AnalyticsMEEPResponse", "LogSegurancaMEEPResponse",
    # formas de pagamento
    "FormaPagamento", "FormaPagamentoCreate", "FormaPagamentoUpdate", "FormaPagamentoDetalhada", "FormaPagamentoList"
])

__all__.extend([
    # financeiro
    "MovimentacaoFinanceiraBase", "MovimentacaoFinanceiraCreate", "MovimentacaoFinanceiraUpdate", "MovimentacaoFinanceira",
    "CaixaEventoCreate", "CaixaEvento", "DashboardFinanceiro"
])
