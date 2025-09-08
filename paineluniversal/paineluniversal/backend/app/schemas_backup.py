from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime, date, timezone
from typing import Optional, List
from decimal import Decimal
# Import absoluto para compatibilidade tanto em desenvolvimento quanto produ√ß√£o
try:
    from .models import StatusEvento, TipoLista, StatusTransacao, TipoUsuario, TipoProduto, StatusProduto, TipoComanda, StatusComanda, StatusVendaPDV, TipoPagamentoPDV, TipoFormaPagamento, StatusFormaPagamento
except ImportError:
    # Fallback para execu√ß√£o direta ou testes
    from backend.app.models import StatusEvento, TipoLista, StatusTransacao, TipoUsuario, TipoProduto, StatusProduto, TipoComanda, StatusComanda, StatusVendaPDV, TipoPagamentoPDV
import re


class MovimentacaoFinanceiraBase(BaseModel):
    tipo: str
    categoria: str
    descricao: str
    valor: Decimal
    promoter_id: Optional[int] = None
    numero_documento: Optional[str] = None
    observacoes: Optional[str] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    metodo_pagamento: Optional[str] = None


class MovimentacaoFinanceiraCreate(MovimentacaoFinanceiraBase):
    evento_id: int


class MovimentacaoFinanceiraUpdate(BaseModel):
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valor: Optional[Decimal] = None
    status: Optional[str] = None
    promoter_id: Optional[int] = None
    numero_documento: Optional[str] = None
    observacoes: Optional[str] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    metodo_pagamento: Optional[str] = None


class MovimentacaoFinanceira(MovimentacaoFinanceiraBase):
    id: int
    evento_id: int
    status: str
    usuario_responsavel_id: int
    comprovante_url: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    evento_nome: Optional[str] = None
    usuario_responsavel_nome: Optional[str] = None
    promoter_nome: Optional[str] = None
    
    class Config:
        from_attributes = True


class CaixaEventoBase(BaseModel):
    saldo_inicial: Decimal = Decimal('0.00')
    observacoes_abertura: Optional[str] = None


class CaixaEventoCreate(CaixaEventoBase):
    evento_id: int


class CaixaEvento(CaixaEventoBase):
    id: int
    evento_id: int
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    total_entradas: Decimal
    total_saidas: Decimal
    total_vendas_pdv: Decimal
    total_vendas_listas: Decimal
    saldo_final: Decimal
    status: str
    usuario_abertura_id: int
    usuario_fechamento_id: Optional[int] = None
    observacoes_fechamento: Optional[str] = None
    
    class Config:
        from_attributes = True


class DashboardFinanceiro(BaseModel):
    evento_id: int
    saldo_atual: Decimal
    total_entradas: Decimal
    total_saidas: Decimal
    total_vendas: Decimal
    lucro_prejuizo: Decimal
    movimentacoes_recentes: List[dict]
    categorias_despesas: List[dict]
    repasses_promoters: List[dict]
    status_caixa: str

class EmpresaBase(BaseModel):
    nome: str
    cnpj: str
    email: EmailStr
    telefone: Optional[str] = None
    endereco: Optional[str] = None

class EmpresaCreate(EmpresaBase):
    @field_validator('cnpj')
    @classmethod
    def validar_cnpj(cls, v):
        cnpj = re.sub(r'\D', '', v)
        if len(cnpj) != 14:
            raise ValueError('CNPJ deve ter 14 d√≠gitos')
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

class Empresa(EmpresaBase):
    id: int
    ativa: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    tipo: TipoUsuario

class UsuarioCreate(UsuarioBase):
    senha: str
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 d√≠gitos')
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

class UsuarioRegister(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    senha: str
    tipo: TipoUsuario = TipoUsuario.CLIENTE
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 d√≠gitos')
        return cpf  # Manter apenas os n√∫meros para o registro p√∫blico
    
    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome √© obrigat√≥rio e n√£o pode estar vazio')
        if len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()
    
    @field_validator('senha')
    @classmethod 
    def validar_senha(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Senha deve ter pelo menos 3 caracteres')
        return v

class Usuario(BaseModel):
    # Campos b√°sicos do usu√°rio
    id: int
    cpf: str
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    tipo: TipoUsuario
    ativo: bool
    ultimo_login: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None  # Campo que estava faltando
    
    class Config:
        from_attributes = True

class EventoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    data_evento: datetime
    local: str
    endereco: Optional[str] = None
    limite_idade: int = 18
    capacidade_maxima: Optional[int] = None

    @field_validator('data_evento')
    @classmethod
    def validar_data_evento(cls, v):
        if isinstance(v, str):
            try:
                # Tentar diferentes formatos de data
                # 1. ISO com Z
                if v.endswith('Z'):
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
                
                # 2. ISO com timezone
                if '+' in v or v.endswith('Z'):
                    return datetime.fromisoformat(v)
                
                # 3. ISO sem timezone (assumir UTC)
                dt = datetime.fromisoformat(v)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
                
            except ValueError as e:
                print(f"Erro ao converter data '{v}': {e}")
                raise ValueError(f'Formato de data inv√°lido: {v}. Use ISO 8601 format (ex: 2025-08-09T20:00:00Z)')
        
        # Se j√° √© datetime, garantir que tenha timezone
        if isinstance(v, datetime) and v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        return v

class EventoCreate(EventoBase):
    empresa_id: Optional[int] = None

class Evento(EventoBase):
    id: int
    status: StatusEvento
    empresa_id: Optional[int] = None
    criador_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EventoDetalhado(EventoBase):
    id: int
    status: StatusEvento
    empresa_id: Optional[int] = None
    criador_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    total_vendas: int = 0
    receita_total: Decimal = Decimal('0.00')
    total_checkins: int = 0
    promoters_vinculados: List[dict] = []
    status_financeiro: str = "sem_vendas"
    
    class Config:
        from_attributes = True

class EventoFiltros(BaseModel):
    nome: Optional[str] = None
    status: Optional[StatusEvento] = None
    empresa_id: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    local: Optional[str] = None
    limite_idade_min: Optional[int] = None
    limite_idade_max: Optional[int] = None

class PromoterEventoCreate(BaseModel):
    promoter_id: int
    meta_vendas: Optional[int] = None
    comissao_percentual: Optional[Decimal] = None

class PromoterEventoResponse(BaseModel):
    id: int
    promoter_id: int
    evento_id: int
    meta_vendas: Optional[int] = None
    vendas_realizadas: int = 0
    comissao_percentual: Optional[Decimal] = None
    ativo: bool = True
    promoter_nome: str
    
    class Config:
        from_attributes = True

class ListaBase(BaseModel):
    nome: str
    tipo: TipoLista
    preco: Decimal = Decimal('0.00')
    limite_vendas: Optional[int] = None
    ativa: bool = True
    descricao: Optional[str] = None
    codigo_cupom: Optional[str] = None
    desconto_percentual: Decimal = Decimal('0.00')

class ListaCreate(ListaBase):
    evento_id: int
    promoter_id: Optional[int] = None

class Lista(ListaBase):
    id: int
    vendas_realizadas: int
    evento_id: int
    promoter_id: Optional[int] = None
    criado_em: datetime
    
    class Config:
        from_attributes = True

class TransacaoBase(BaseModel):
    cpf_comprador: str
    nome_comprador: str
    email_comprador: Optional[EmailStr] = None
    telefone_comprador: Optional[str] = None
    valor: Decimal
    metodo_pagamento: Optional[str] = None

class TransacaoCreate(TransacaoBase):
    evento_id: int
    lista_id: int
    
    @field_validator('cpf_comprador')
    @classmethod
    def validar_cpf_comprador(cls, v):
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 d√≠gitos')
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

class Transacao(TransacaoBase):
    id: int
    status: StatusTransacao
    codigo_transacao: Optional[str] = None
    qr_code_ticket: Optional[str] = None
    evento_id: int
    lista_id: int
    usuario_id: Optional[int] = None
    criado_em: datetime
    
    class Config:
        from_attributes = True

class CheckinBase(BaseModel):
    cpf: str
    metodo_checkin: str
    validacao_cpf: str

class CheckinCreate(CheckinBase):
    evento_id: int
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 d√≠gitos')
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    @field_validator('validacao_cpf')
    @classmethod
    def validar_tres_digitos(cls, v):
        if len(v) != 3 or not v.isdigit():
            raise ValueError('Valida√ß√£o deve ter exatamente 3 d√≠gitos')
        return v

class Checkin(CheckinBase):
    id: int
    nome: str
    evento_id: int
    usuario_id: Optional[int] = None
    transacao_id: Optional[int] = None
    checkin_em: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: Usuario

class TokenData(BaseModel):
    cpf: Optional[str] = None

class LoginRequest(BaseModel):
    cpf: str
    senha: str

class DashboardResumo(BaseModel):
    total_eventos: int
    total_vendas: int
    total_checkins: int
    receita_total: Decimal
    eventos_hoje: int
    vendas_hoje: int

class RankingPromoter(BaseModel):
    promoter_id: int
    nome_promoter: str
    total_vendas: int
    receita_gerada: Decimal
    posicao: int

class RelatorioVendas(BaseModel):
    evento_id: int
    nome_evento: str
    total_vendas: int
    receita_total: Decimal
    vendas_por_lista: List[dict]
    vendas_por_promoter: List[dict]

class CupomCreate(BaseModel):
    lista_id: int
    codigo: str
    desconto_percentual: Optional[Decimal] = None
    desconto_valor: Optional[Decimal] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    limite_uso: Optional[int] = None

class CupomResponse(BaseModel):
    id: int
    codigo: str
    desconto_percentual: Optional[Decimal]
    desconto_valor: Optional[Decimal]
    lista_nome: str
    evento_nome: str
    
    class Config:
        from_attributes = True

class ProdutoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: TipoProduto
    preco: Decimal
    codigo_interno: Optional[str] = None
    estoque_atual: int = 0
    estoque_minimo: int = 0
    estoque_maximo: int = 1000
    controla_estoque: bool = True
    categoria: Optional[str] = None
    imagem_url: Optional[str] = None

class ProdutoCreate(ProdutoBase):
    # evento_id removido - produtos s√£o globais, n√£o atrelados a eventos espec√≠ficos
    pass

class Produto(ProdutoBase):
    id: int
    status: StatusProduto
    # evento_id removido - produtos s√£o globais, n√£o atrelados a eventos espec√≠ficos
    empresa_id: Optional[int] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ComandaBase(BaseModel):
    numero_comanda: str
    cpf_cliente: Optional[str] = None
    nome_cliente: Optional[str] = None
    tipo: TipoComanda
    codigo_rfid: Optional[str] = None
    qr_code: Optional[str] = None

class ComandaCreate(ComandaBase):
    evento_id: int

class Comanda(ComandaBase):
    id: int
    saldo_atual: Decimal
    saldo_bloqueado: Decimal
    status: StatusComanda
    evento_id: int
    empresa_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ItemVendaPDVBase(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal
    observacoes: Optional[str] = None

class ItemVendaPDVCreate(ItemVendaPDVBase):
    pass

class ItemVendaPDV(ItemVendaPDVBase):
    id: int
    venda_id: int
    preco_total: Decimal
    desconto_aplicado: Decimal
    criado_em: datetime
    produto_nome: Optional[str] = None
    
    class Config:
        from_attributes = True

class PagamentoPDVBase(BaseModel):
    tipo_pagamento: TipoPagamentoPDV
    valor: Decimal
    promoter_id: Optional[int] = None
    comissao_percentual: Optional[Decimal] = None

class PagamentoPDVCreate(PagamentoPDVBase):
    pass

class PagamentoPDV(PagamentoPDVBase):
    id: int
    venda_id: int
    codigo_transacao: Optional[str] = None
    valor_comissao: Decimal
    status: StatusVendaPDV
    criado_em: datetime
    
    class Config:
        from_attributes = True

class VendaPDVBase(BaseModel):
    cpf_cliente: Optional[str] = None
    nome_cliente: Optional[str] = None
    comanda_id: Optional[int] = None
    cupom_codigo: Optional[str] = None
    observacoes: Optional[str] = None

class VendaPDVCreate(VendaPDVBase):
    evento_id: int
    itens: List[ItemVendaPDVCreate]
    pagamentos: List[PagamentoPDVCreate]

class VendaPDV(VendaPDVBase):
    id: int
    numero_venda: str
    valor_total: Decimal
    valor_desconto: Decimal
    valor_final: Decimal
    tipo_pagamento: TipoPagamentoPDV
    status: StatusVendaPDV
    evento_id: int
    empresa_id: int
    usuario_vendedor_id: int
    promoter_id: Optional[int] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    itens: List[ItemVendaPDV] = []
    pagamentos: List[PagamentoPDV] = []
    
    class Config:
        from_attributes = True

class RecargaComandaBase(BaseModel):
    valor: Decimal
    tipo_pagamento: TipoPagamentoPDV

class RecargaComandaCreate(RecargaComandaBase):
    comanda_id: int

class RecargaComanda(RecargaComandaBase):
    id: int
    comanda_id: int
    codigo_transacao: Optional[str] = None
    usuario_id: int
    status: StatusVendaPDV
    criado_em: datetime
    
    class Config:
        from_attributes = True

class CaixaPDVBase(BaseModel):
    numero_caixa: str
    valor_abertura: Decimal = Decimal('0.00')

class CaixaPDVCreate(CaixaPDVBase):
    evento_id: int

class CaixaPDV(CaixaPDVBase):
    id: int
    evento_id: int
    usuario_operador_id: int
    valor_vendas: Decimal
    valor_sangrias: Decimal
    valor_fechamento: Decimal
    status: str
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    observacoes: Optional[str] = None
    
    class Config:
        from_attributes = True

class RelatorioVendasPDV(BaseModel):
    evento_id: int
    periodo_inicio: datetime
    periodo_fim: datetime
    total_vendas: int
    valor_total: Decimal
    vendas_por_produto: List[dict]
    vendas_por_forma_pagamento: List[dict]
    vendas_por_hora: List[dict]
    top_produtos: List[dict]

class DashboardPDV(BaseModel):
    vendas_hoje: int
    valor_vendas_hoje: Decimal
    produtos_em_falta: int
    comandas_ativas: int
    caixas_abertos: int
    vendas_por_hora: List[dict]
    produtos_mais_vendidos: List[dict]
    alertas: List[dict]

class DashboardAvancado(BaseModel):
    total_eventos: int
    total_vendas: int
    total_checkins: int
    receita_total: Decimal
    taxa_conversao: float
    vendas_hoje: int
    vendas_semana: int
    vendas_mes: int
    receita_hoje: Decimal
    receita_semana: Decimal
    receita_mes: Decimal
    checkins_hoje: int
    checkins_semana: int
    taxa_presenca: float
    fila_espera: int
    cortesias: int
    inadimplentes: int
    aniversariantes_mes: int
    consumo_medio: Decimal

class FiltrosDashboard(BaseModel):
    evento_id: Optional[int] = None
    promoter_id: Optional[int] = None
    tipo_lista: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    metodo_pagamento: Optional[str] = None

class RankingPromoterAvancado(BaseModel):
    promoter_id: int
    nome_promoter: str
    total_vendas: int
    receita_total: Decimal
    conversao: float

# ===== SCHEMAS FORMAS DE PAGAMENTO =====

class FormaPagamentoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da forma de pagamento")
    codigo: str = Field(..., min_length=1, max_length=50, description="C√≥digo √∫nico da forma de pagamento")
    tipo: TipoFormaPagamento = Field(..., description="Tipo da forma de pagamento")
    status: StatusFormaPagamento = Field(default=StatusFormaPagamento.ATIVO, description="Status da forma de pagamento")
    descricao: Optional[str] = Field(None, description="Descri√ß√£o da forma de pagamento")
    taxa_percentual: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, le=100, description="Taxa percentual (0-100)")
    taxa_fixa: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, description="Taxa fixa em reais")
    tempo_compensacao: Optional[int] = Field(default=0, ge=0, description="Tempo de compensa√ß√£o em horas")
    limite_minimo: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, description="Valor m√≠nimo aceito")
    limite_maximo: Optional[Decimal] = Field(None, ge=0, description="Valor m√°ximo aceito")
    icone: Optional[str] = Field(None, max_length=100, description="√çcone ou imagem")
    cor_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Cor hexadecimal (ex: #1E40AF)")
    configuracoes_extras: Optional[str] = Field(None, description="Configura√ß√µes espec√≠ficas (JSON)")
    ordem_exibicao: Optional[int] = Field(default=1, ge=1, description="Ordem na listagem")
    ativo: Optional[bool] = Field(default=True, description="Forma de pagamento ativa")

class FormaPagamentoCreate(FormaPagamentoBase):
    """Schema para cria√ß√£o de forma de pagamento"""
    pass

class FormaPagamentoUpdate(BaseModel):
    """Schema para atualiza√ß√£o de forma de pagamento"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    tipo: Optional[TipoFormaPagamento] = None
    status: Optional[StatusFormaPagamento] = None
    descricao: Optional[str] = None
    taxa_percentual: Optional[Decimal] = Field(None, ge=0, le=100)
    taxa_fixa: Optional[Decimal] = Field(None, ge=0)
    tempo_compensacao: Optional[int] = Field(None, ge=0)
    limite_minimo: Optional[Decimal] = Field(None, ge=0)
    limite_maximo: Optional[Decimal] = Field(None, ge=0)
    icone: Optional[str] = Field(None, max_length=100)
    cor_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    configuracoes_extras: Optional[str] = None
    ordem_exibicao: Optional[int] = Field(None, ge=1)
    ativo: Optional[bool] = None

class FormaPagamento(FormaPagamentoBase):
    """Schema de resposta da forma de pagamento"""
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    criado_por: Optional[int] = None
    
    class Config:
        from_attributes = True

class FormaPagamentoDetalhada(FormaPagamento):
    """Schema detalhado com informa√ß√µes do criador"""
    criador: Optional[Usuario] = None

# Schema para listagem paginada
class FormaPagamentoList(BaseModel):
    items: List[FormaPagamento]
    total: int
    page: int
    per_page: int
    pages: int
    total_vendas: int
    receita_gerada: Decimal
    total_checkins: int
    taxa_presenca: float
    taxa_conversao: float
    posicao: int
    badge: str

class DadosGrafico(BaseModel):
    labels: List[str]
    datasets: List[dict]
    tipo: str

class ConvidadoBase(BaseModel):
    cpf: str
    nome: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 d√≠gitos')
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

class ConvidadoCreate(ConvidadoBase):
    lista_id: int
    evento_id: int

class ConvidadoImport(BaseModel):
    convidados: List[ConvidadoBase]
    lista_id: int
    evento_id: int

class ListaDetalhada(Lista):
    total_convidados: int = 0
    convidados_presentes: int = 0
    taxa_presenca: float = 0.0
    receita_gerada: Decimal = Decimal('0.00')
    promoter_nome: Optional[str] = None
    
class ListaFiltros(BaseModel):
    evento_id: Optional[int] = None
    promoter_id: Optional[int] = None
    tipo: Optional[str] = None
    ativa: Optional[bool] = None
    
class RankingPromoterLista(BaseModel):
    promoter_id: int
    nome_promoter: str
    total_listas: int
    total_convidados: int
    total_presentes: int
    receita_total: Decimal
    taxa_presenca: float
    taxa_conversao: float
    posicao: int
    badge: str
    eventos_ativos: int

class DashboardListas(BaseModel):
    total_listas: int
    total_convidados: int
    total_presentes: int
    taxa_presenca_geral: float
    listas_mais_ativas: List[dict]
    promoters_destaque: List[dict]
    convidados_por_tipo: List[dict]
    presencas_tempo_real: List[dict]

class ConquistaBase(BaseModel):
    nome: str
    descricao: str
    tipo: str
    criterio_valor: int
    badge_nivel: str
    icone: Optional[str] = None

class ConquistaCreate(ConquistaBase):
    pass

class Conquista(ConquistaBase):
    id: int
    ativa: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

class PromoterConquistaResponse(BaseModel):
    id: int
    conquista_nome: str
    conquista_descricao: str
    badge_nivel: str
    icone: Optional[str] = None
    valor_alcancado: int
    data_conquista: datetime
    evento_nome: Optional[str] = None
    
    class Config:
        from_attributes = True

class MetricaPromoterResponse(BaseModel):
    promoter_id: int
    promoter_nome: str
    evento_id: Optional[int] = None
    evento_nome: Optional[str] = None
    periodo_inicio: date
    periodo_fim: date
    total_vendas: int
    receita_gerada: Decimal
    total_convidados: int
    total_presentes: int
    taxa_presenca: Decimal
    taxa_conversao: Decimal
    crescimento_vendas: Decimal
    posicao_vendas: Optional[int] = None
    posicao_presenca: Optional[int] = None
    posicao_geral: Optional[int] = None
    badge_atual: str
    conquistas_recentes: List[PromoterConquistaResponse] = []
    
    class Config:
        from_attributes = True

class RankingGamificado(BaseModel):
    promoter_id: int
    nome_promoter: str
    avatar_url: Optional[str] = None
    badge_principal: str
    nivel_experiencia: int
    total_vendas: int
    receita_gerada: Decimal
    taxa_presenca: float
    taxa_conversao: float
    crescimento_mensal: float
    posicao_atual: int
    posicao_anterior: Optional[int] = None
    conquistas_total: int
    conquistas_mes: int
    eventos_ativos: int
    streak_vendas: int
    pontuacao_total: int
    
class DashboardGamificacao(BaseModel):
    ranking_geral: List[RankingGamificado]
    conquistas_recentes: List[PromoterConquistaResponse]
    metricas_periodo: dict
    badges_disponiveis: List[dict]
    alertas_gamificacao: List[dict]
    estatisticas_gerais: dict

class FiltrosRanking(BaseModel):
    evento_id: Optional[int] = None
    periodo_inicio: Optional[date] = None
    periodo_fim: Optional[date] = None
    badge_nivel: Optional[str] = None
    tipo_ranking: Optional[str] = "geral"
    limit: int = 20


# =====================================================
# MEEP Integration Schemas
# =====================================================

class ClienteEventoBase(BaseModel):
    cpf: str
    nome_completo: str
    nome_social: Optional[str] = None
    data_nascimento: Optional[date] = None
    nome_mae: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    status: str = "ativo"

    @field_validator('cpf')
    def validate_cpf(cls, v):
        # Remove caracteres n√£o num√©ricos
        cpf = re.sub(r'[^0-9]', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve conter 11 d√≠gitos')
        return cpf

class ClienteEventoCreate(ClienteEventoBase):
    pass

class ClienteEventoUpdate(BaseModel):
    nome_completo: Optional[str] = None
    nome_social: Optional[str] = None
    data_nascimento: Optional[date] = None
    nome_mae: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None

class ClienteEventoResponse(ClienteEventoBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class ValidacaoAcessoBase(BaseModel):
    evento_id: Optional[int] = None
    cliente_id: Optional[int] = None
    cpf_hash: str
    qr_code_data: str
    cpf_digits: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    sucesso: bool = False
    motivo_falha: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    device_info: Optional[str] = None

class ValidacaoAcessoCreate(ValidacaoAcessoBase):
    pass

class ValidacaoAcessoResponse(ValidacaoAcessoBase):
    id: int
    timestamp_validacao: datetime
    criado_em: datetime

    class Config:
        from_attributes = True

class EquipamentoEventoBase(BaseModel):
    evento_id: int
    nome: str
    tipo: str  # 'tablet', 'qr_reader', 'printer', 'pos', 'camera', 'sensor'
    ip_address: str
    mac_address: Optional[str] = None
    status: str = "offline"
    configuracao: Optional[str] = None
    localizacao: Optional[str] = None
    responsavel_id: Optional[int] = None
    heartbeat_interval: int = 30

    @field_validator('tipo')
    def validate_tipo(cls, v):
        tipos_validos = ['tablet', 'qr_reader', 'printer', 'pos', 'camera', 'sensor']
        if v not in tipos_validos:
            raise ValueError(f'Tipo deve ser um dos: {", ".join(tipos_validos)}')
        return v

class EquipamentoEventoCreate(EquipamentoEventoBase):
    pass

class EquipamentoEventoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    configuracao: Optional[str] = None
    localizacao: Optional[str] = None
    responsavel_id: Optional[int] = None
    heartbeat_interval: Optional[int] = None

class EquipamentoEventoResponse(EquipamentoEventoBase):
    id: int
    ultima_atividade: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class SessaoOperadorBase(BaseModel):
    usuario_id: int
    evento_id: int
    equipamento_id: Optional[int] = None
    token_sessao: str
    ip_address: Optional[str] = None
    ativo: bool = True
    configuracoes: Optional[str] = None

class SessaoOperadorCreate(SessaoOperadorBase):
    pass

class SessaoOperadorResponse(SessaoOperadorBase):
    id: int
    inicio_sessao: datetime
    fim_sessao: Optional[datetime] = None
    criado_em: datetime

    class Config:
        from_attributes = True

class PrevisaoIABase(BaseModel):
    evento_id: int
    tipo_previsao: str  # 'fluxo_horario', 'pico_entrada', 'estimativa_total'
    dados_entrada: str  # JSON string
    resultado_previsao: str  # JSON string
    confiabilidade: Optional[Decimal] = None
    aplicada: bool = False
    feedback_real: Optional[str] = None
    precisao_real: Optional[Decimal] = None

class PrevisaoIACreate(PrevisaoIABase):
    pass

class PrevisaoIAResponse(PrevisaoIABase):
    id: int
    timestamp_previsao: datetime
    criado_em: datetime

    class Config:
        from_attributes = True

class AnalyticsMEEPBase(BaseModel):
    evento_id: int
    metrica: str
    valor: Optional[Decimal] = None
    valor_anterior: Optional[Decimal] = None
    percentual_mudanca: Optional[Decimal] = None
    periodo: Optional[str] = None  # 'hora', 'dia', 'semana', 'mes'
    dados_detalhados: Optional[str] = None  # JSON string
    alertas: Optional[str] = None  # JSON string

class AnalyticsMEEPCreate(AnalyticsMEEPBase):
    pass

class AnalyticsMEEPResponse(AnalyticsMEEPBase):
    id: int
    timestamp_coleta: datetime
    criado_em: datetime

    class Config:
        from_attributes = True

class LogSegurancaMEEPBase(BaseModel):
    evento_id: Optional[int] = None
    tipo_evento: str  # 'tentativa_acesso', 'validacao_cpf', 'erro_sistema'
    gravidade: str = "info"  # 'info', 'warning', 'error', 'critical'
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    dados_evento: str  # JSON string
    usuario_id: Optional[int] = None
    resolvido: bool = False

    @field_validator('gravidade')
    def validate_gravidade(cls, v):
        gravidades_validas = ['info', 'warning', 'error', 'critical']
        if v not in gravidades_validas:
            raise ValueError(f'Gravidade deve ser uma das: {", ".join(gravidades_validas)}')
        return v

class LogSegurancaMEEPCreate(LogSegurancaMEEPBase):
    pass

class LogSegurancaMEEPResponse(LogSegurancaMEEPBase):
    id: int
    timestamp_evento: datetime
    criado_em: datetime

    class Config:
        from_attributes = True

# Schemas para requests complexos
class MEEPDashboardRequest(BaseModel):
    evento_id: int
    periodo: str = "24h"
    incluir_previsoes: bool = True
    incluir_equipamentos: bool = True

class MEEPAnalyticsRequest(BaseModel):
    evento_id: int
    tipo_analise: str  # 'fluxo', 'performance', 'seguranca'
    periodo: str = "7d"
    granularidade: str = "hora"  # 'minuto', 'hora', 'dia'

class MEEPValidacaoRequest(BaseModel):
    cpf: str
    evento_id: Optional[int] = None

class MEEPCheckinRequest(BaseModel):
    qr_code: str
    cpf_digits: str
    evento_id: Optional[int] = None

class MEEPEquipamentoHeartbeatRequest(BaseModel):
    equipamento_id: int
    status: str = "online"
    dados_status: Optional[dict] = None

# Responses complexos
class MEEPDashboardResponse(BaseModel):
    evento_id: int
    periodo: str
    metricas_gerais: dict
    equipamentos: dict
    seguranca: dict
    fluxo_horario: List[dict]
    timestamp: str

class MEEPAnalyticsResponse(BaseModel):
    evento_id: int
    tipo_analise: str
    periodo: str
    dados: dict
    insights: List[dict]
    timestamp: str

class MEEPValidacaoResponse(BaseModel):
    valido: bool
    nome: Optional[str] = None
    situacao: str
    fonte: str
    timestamp: str

class MEEPCheckinResponse(BaseModel):
    sucesso: bool
    cliente: Optional[dict] = None
    motivo: Optional[str] = None
    timestamp: str
f r o m   p y d a n t i c   i m p o r t   B a s e M o d e l ,   v a l i d a t o r ,   F i e l d  
 f r o m   t y p i n g   i m p o r t   O p t i o n a l ,   L i s t  
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e  
 f r o m   d e c i m a l   i m p o r t   D e c i m a l  
 f r o m   e n u m   i m p o r t   E n u m  
  
 #   E n u m s  
 c l a s s   T i p o P r o d u t o E n u m ( s t r ,   E n u m ) :  
         B E B I D A   =   " B E B I D A "  
         C O M I D A   =   " C O M I D A "  
         I N G R E S S O   =   " I N G R E S S O "  
         F I C H A   =   " F I C H A "  
         C O M B O   =   " C O M B O "  
         V O U C H E R   =   " V O U C H E R "  
  
 c l a s s   S t a t u s P r o d u t o E n u m ( s t r ,   E n u m ) :  
         A T I V O   =   " A T I V O "  
         I N A T I V O   =   " I N A T I V O "  
         E S G O T A D O   =   " E S G O T A D O "  
  
 #   C a t e g o r i a   S c h e m a s  
 c l a s s   C a t e g o r i a B a s e ( B a s e M o d e l ) :  
         n o m e :   s t r   =   F i e l d ( . . . ,   m i n _ l e n g t h = 1 ,   m a x _ l e n g t h = 1 0 0 ,   d e s c r i p t i o n = " N o m e   d a   c a t e g o r i a " )  
         d e s c r i c a o :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 1 0 0 0 ,   d e s c r i p t i o n = " D e s c r i √ ß √ £ o   d a   c a t e g o r i a " )  
         c o r :   O p t i o n a l [ s t r ]   =   F i e l d ( " # 3 b 8 2 f 6 " ,   p a t t e r n = " ^ # [ 0 - 9 A - F a - f ] { 6 } $ " ,   d e s c r i p t i o n = " C o r   e m   f o r m a t o   h e x " )  
          
         @ v a l i d a t o r ( ' n o m e ' )  
         d e f   v a l i d a r _ n o m e ( c l s ,   v ) :  
                 i f   n o t   v   o r   n o t   v . s t r i p ( ) :  
                         r a i s e   V a l u e E r r o r ( ' N o m e   √ ©   o b r i g a t √ ≥ r i o ' )  
                 r e t u r n   v . s t r i p ( )  
  
 c l a s s   C a t e g o r i a C r e a t e ( C a t e g o r i a B a s e ) :  
         e v e n t o _ i d :   i n t   =   F i e l d ( . . . ,   d e s c r i p t i o n = " I D   d o   e v e n t o " )  
  
 c l a s s   C a t e g o r i a U p d a t e ( B a s e M o d e l ) :  
         n o m e :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m i n _ l e n g t h = 1 ,   m a x _ l e n g t h = 1 0 0 )  
         d e s c r i c a o :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 1 0 0 0 )  
         c o r :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   p a t t e r n = " ^ # [ 0 - 9 A - F a - f ] { 6 } $ " )  
         a t i v o :   O p t i o n a l [ b o o l ]   =   N o n e  
  
         @ v a l i d a t o r ( ' n o m e ' )  
         d e f   v a l i d a r _ n o m e ( c l s ,   v ) :  
                 i f   v   i s   n o t   N o n e   a n d   ( n o t   v   o r   n o t   v . s t r i p ( ) ) :  
                         r a i s e   V a l u e E r r o r ( ' N o m e   n √ £ o   p o d e   s e r   v a z i o ' )  
                 r e t u r n   v . s t r i p ( )   i f   v   e l s e   v  
  
 c l a s s   C a t e g o r i a R e s p o n s e ( C a t e g o r i a B a s e ) :  
         i d :   i n t  
         a t i v o :   b o o l  
         e v e n t o _ i d :   i n t  
         e m p r e s a _ i d :   O p t i o n a l [ i n t ]  
         c r i a d o _ e m :   d a t e t i m e  
         a t u a l i z a d o _ e m :   d a t e t i m e  
  
         c l a s s   C o n f i g :  
                 f r o m _ a t t r i b u t e s   =   T r u e  
  
 #   P r o d u t o   S c h e m a s  
 c l a s s   P r o d u t o B a s e ( B a s e M o d e l ) :  
         n o m e :   s t r   =   F i e l d ( . . . ,   m i n _ l e n g t h = 1 ,   m a x _ l e n g t h = 2 5 5 ,   d e s c r i p t i o n = " N o m e   d o   p r o d u t o " )  
         d e s c r i c a o :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 1 0 0 0 ,   d e s c r i p t i o n = " D e s c r i √ ß √ £ o   d o   p r o d u t o " )  
         t i p o :   T i p o P r o d u t o E n u m   =   F i e l d ( . . . ,   d e s c r i p t i o n = " T i p o   d o   p r o d u t o " )  
         p r e c o :   D e c i m a l   =   F i e l d ( . . . ,   g t = 0 ,   d e s c r i p t i o n = " P r e √ ß o   d o   p r o d u t o " )  
         c a t e g o r i a :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 1 0 0 ,   d e s c r i p t i o n = " C a t e g o r i a   d o   p r o d u t o " )  
         c o d i g o _ i n t e r n o :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 2 0 ,   d e s c r i p t i o n = " C √ ≥ d i g o   i n t e r n o " )  
         e s t o q u e _ a t u a l :   O p t i o n a l [ i n t ]   =   F i e l d ( 0 ,   g e = 0 ,   d e s c r i p t i o n = " E s t o q u e   a t u a l " )  
         e s t o q u e _ m i n i m o :   O p t i o n a l [ i n t ]   =   F i e l d ( 0 ,   g e = 0 ,   d e s c r i p t i o n = " E s t o q u e   m √ ≠ n i m o " )  
         e s t o q u e _ m a x i m o :   O p t i o n a l [ i n t ]   =   F i e l d ( 1 0 0 0 ,   g e = 0 ,   d e s c r i p t i o n = " E s t o q u e   m √ ° x i m o " )  
         c o n t r o l a _ e s t o q u e :   O p t i o n a l [ b o o l ]   =   F i e l d ( T r u e ,   d e s c r i p t i o n = " S e   c o n t r o l a   e s t o q u e " )  
         s t a t u s :   O p t i o n a l [ S t a t u s P r o d u t o E n u m ]   =   F i e l d ( S t a t u s P r o d u t o E n u m . A T I V O ,   d e s c r i p t i o n = " S t a t u s   d o   p r o d u t o " )  
         i m a g e m _ u r l :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 5 0 0 ,   d e s c r i p t i o n = " U R L   d a   i m a g e m " )  
         #   e v e n t o _ i d   r e m o v i d o   d o   s c h e m a   f r o n t e n d   -   p r o d u t o s   s √ £ o   g l o b a i s  
  
         @ v a l i d a t o r ( ' n o m e ' )  
         d e f   v a l i d a r _ n o m e ( c l s ,   v ) :  
                 i f   n o t   v   o r   n o t   v . s t r i p ( ) :  
                         r a i s e   V a l u e E r r o r ( ' N o m e   √ ©   o b r i g a t √ ≥ r i o ' )  
                 r e t u r n   v . s t r i p ( )  
  
 c l a s s   P r o d u t o C r e a t e ( P r o d u t o B a s e ) :  
         p a s s  
  
 c l a s s   P r o d u t o U p d a t e ( B a s e M o d e l ) :  
         n o m e :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m i n _ l e n g t h = 1 ,   m a x _ l e n g t h = 2 5 5 )  
         d e s c r i c a o :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 1 0 0 0 )  
         t i p o :   O p t i o n a l [ T i p o P r o d u t o E n u m ]   =   N o n e  
         p r e c o :   O p t i o n a l [ D e c i m a l ]   =   F i e l d ( N o n e ,   g t = 0 )  
         c a t e g o r i a :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 1 0 0 )  
         c o d i g o _ i n t e r n o :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 2 0 )  
         e s t o q u e _ a t u a l :   O p t i o n a l [ i n t ]   =   F i e l d ( N o n e ,   g e = 0 )  
         e s t o q u e _ m i n i m o :   O p t i o n a l [ i n t ]   =   F i e l d ( N o n e ,   g e = 0 )  
         e s t o q u e _ m a x i m o :   O p t i o n a l [ i n t ]   =   F i e l d ( N o n e ,   g e = 0 )  
         c o n t r o l a _ e s t o q u e :   O p t i o n a l [ b o o l ]   =   N o n e  
         s t a t u s :   O p t i o n a l [ S t a t u s P r o d u t o E n u m ]   =   N o n e  
         i m a g e m _ u r l :   O p t i o n a l [ s t r ]   =   F i e l d ( N o n e ,   m a x _ l e n g t h = 5 0 0 )  
  
 c l a s s   P r o d u t o R e s p o n s e ( P r o d u t o B a s e ) :  
         i d :   i n t  
         e m p r e s a _ i d :   O p t i o n a l [ i n t ]  
         c r i a d o _ e m :   d a t e t i m e  
         a t u a l i z a d o _ e m :   O p t i o n a l [ d a t e t i m e ]     #   P e r m i t i r   N U L L   p a r a   c o m p a t i b i l i d a d e  
  
         c l a s s   C o n f i g :  
                 f r o m _ a t t r i b u t e s   =   T r u e  
  
 #   S c h e m a s   p a r a   l i s t a g e m   c o m   f i l t r o s  
 c l a s s   P r o d u t o F i l t e r ( B a s e M o d e l ) :  
         n o m e :   O p t i o n a l [ s t r ]   =   N o n e  
         t i p o :   O p t i o n a l [ T i p o P r o d u t o E n u m ]   =   N o n e  
         c a t e g o r i a :   O p t i o n a l [ s t r ]   =   N o n e  
         s t a t u s :   O p t i o n a l [ S t a t u s P r o d u t o E n u m ]   =   N o n e  
         p r e c o _ m i n :   O p t i o n a l [ D e c i m a l ]   =   N o n e  
         p r e c o _ m a x :   O p t i o n a l [ D e c i m a l ]   =   N o n e  
         e s t o q u e _ b a i x o :   O p t i o n a l [ b o o l ]   =   N o n e     #   P r o d u t o s   c o m   e s t o q u e   < =   m √ ≠ n i m o  
  
 c l a s s   P r o d u t o L i s t ( B a s e M o d e l ) :  
         p r o d u t o s :   L i s t [ P r o d u t o R e s p o n s e ]  
         t o t a l :   i n t  
         p a g e :   i n t  
         s i z e :   i n t  
         p a g e s :   i n t  
  
 c l a s s   C a t e g o r i a L i s t ( B a s e M o d e l ) :  
         c a t e g o r i a s :   L i s t [ C a t e g o r i a R e s p o n s e ]  
         t o t a l :   i n t  
         p a g e :   i n t  
         s i z e :   i n t  
         p a g e s :   i n t  
  
 #   S c h e m a s   p a r a   r e l a t √ ≥ r i o s  
 c l a s s   P r o d u t o S t a t s ( B a s e M o d e l ) :  
         t o t a l _ p r o d u t o s :   i n t  
         p r o d u t o s _ a t i v o s :   i n t  
         p r o d u t o s _ i n a t i v o s :   i n t  
         p r o d u t o s _ e s t o q u e _ b a i x o :   i n t  
         v a l o r _ t o t a l _ e s t o q u e :   D e c i m a l  
         p r o d u t o s _ p o r _ c a t e g o r i a :   L i s t [ d i c t ]  
         p r o d u t o s _ m a i s _ v e n d i d o s :   L i s t [ d i c t ]  
  
 c l a s s   C a t e g o r i a S t a t s ( B a s e M o d e l ) :  
         t o t a l _ c a t e g o r i a s :   i n t  
         c a t e g o r i a s _ a t i v a s :   i n t  
         p r o d u t o s _ p o r _ c a t e g o r i a :   L i s t [ d i c t ]  
 