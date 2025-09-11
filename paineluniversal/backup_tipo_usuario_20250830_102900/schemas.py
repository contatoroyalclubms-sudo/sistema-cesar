from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime, date, timezone
from typing import Optional, List
from decimal import Decimal
# Import absoluto para compatibilidade tanto em desenvolvimento quanto produção
try:
    from .models import StatusEvento, TipoLista, StatusTransacao, TipoProduto, StatusProduto, TipoComanda, StatusComanda, StatusVendaPDV, TipoPagamentoPDV, TipoFormaPagamento, StatusFormaPagamento
except ImportError:
    # Fallback para execução direta ou testes
    from backend.app.models import StatusEvento, TipoLista, StatusTransacao, TipoProduto, StatusProduto, TipoComanda, StatusComanda, StatusVendaPDV, TipoPagamentoPDV
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
            raise ValueError('CNPJ deve ter 14 dígitos')
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
    tipo: str  # Campo principal: 'admin', 'promoter', 'cliente'

class UsuarioCreate(UsuarioBase):
    senha: str
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

class UsuarioRegister(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    senha: str
    tipo: str = "cliente"  # Campo principal: 'admin', 'promoter', 'cliente'
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        cpf = re.sub(r'\D', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf  # Manter apenas os números para o registro público
    
    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório e não pode estar vazio')
        if len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()
    
    @field_validator('senha')
    @classmethod 
    def validar_senha(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Senha deve ter pelo menos 3 caracteres')
        return v
    
    @field_validator('tipo')
    @classmethod
    def validar_tipo(cls, v):
        tipos_validos = ['admin', 'promoter', 'cliente']
        if v not in tipos_validos:
            raise ValueError(f'Tipo de usuário deve ser um dos: {", ".join(tipos_validos)}')
        return v

class Usuario(BaseModel):
    # Campos básicos do usuário
    id: int
    cpf: str
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    tipo: str  # Campo principal: 'admin', 'promoter', 'cliente'
    # COMPATIBILIDADE TEMPORÁRIA: manter tipo_usuario para transição
        ativo: bool
    ultimo_login: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Garantir que tipo seja sempre definido (priorizar campo 'tipo' do banco)
        if hasattr(self, 'tipo_usuario') and self.tipo and not self.tipo:
            self.tipo = self.tipo
        # Para compatibilidade reversa: se tipo_usuario não estiver definido, usar tipo
        if not self.tipo and self.tipo:
            self.tipo = self.tipo
    
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
                raise ValueError(f'Formato de data inválido: {v}. Use ISO 8601 format (ex: 2025-08-09T20:00:00Z)')
        
        # Se já é datetime, garantir que tenha timezone
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
            raise ValueError('CPF deve ter 11 dígitos')
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
            raise ValueError('CPF deve ter 11 dígitos')
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    @field_validator('validacao_cpf')
    @classmethod
    def validar_tres_digitos(cls, v):
        if len(v) != 3 or not v.isdigit():
            raise ValueError('Validação deve ter exatamente 3 dígitos')
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
    # evento_id removido - produtos são globais, não atrelados a eventos específicos
    pass

class Produto(ProdutoBase):
    id: int
    status: StatusProduto
    # evento_id removido - produtos são globais, não atrelados a eventos específicos
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
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único da forma de pagamento")
    tipo: TipoFormaPagamento = Field(..., description="Tipo da forma de pagamento")
    status: StatusFormaPagamento = Field(default=StatusFormaPagamento.ATIVO, description="Status da forma de pagamento")
    descricao: Optional[str] = Field(None, description="Descrição da forma de pagamento")
    taxa_percentual: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, le=100, description="Taxa percentual (0-100)")
    taxa_fixa: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, description="Taxa fixa em reais")
    tempo_compensacao: Optional[int] = Field(default=0, ge=0, description="Tempo de compensação em horas")
    limite_minimo: Optional[Decimal] = Field(default=Decimal('0.00'), ge=0, description="Valor mínimo aceito")
    limite_maximo: Optional[Decimal] = Field(None, ge=0, description="Valor máximo aceito")
    icone: Optional[str] = Field(None, max_length=100, description="Ícone ou imagem")
    cor_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Cor hexadecimal (ex: #1E40AF)")
    configuracoes_extras: Optional[str] = Field(None, description="Configurações específicas (JSON)")
    ordem_exibicao: Optional[int] = Field(default=1, ge=1, description="Ordem na listagem")
    ativo: Optional[bool] = Field(default=True, description="Forma de pagamento ativa")

class FormaPagamentoCreate(FormaPagamentoBase):
    """Schema para criação de forma de pagamento"""
    pass

class FormaPagamentoUpdate(BaseModel):
    """Schema para atualização de forma de pagamento"""
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
    """Schema detalhado com informações do criador"""
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
            raise ValueError('CPF deve ter 11 dígitos')
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
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
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
from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Enums
class TipoProdutoEnum(str, Enum):
    BEBIDA = "BEBIDA"
    COMIDA = "COMIDA"
    INGRESSO = "INGRESSO"
    FICHA = "FICHA"
    COMBO = "COMBO"
    VOUCHER = "VOUCHER"

class StatusProdutoEnum(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    ESGOTADO = "ESGOTADO"

# Categoria Schemas
class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição da categoria")
    cor: Optional[str] = Field("#3b82f6", pattern="^#[0-9A-Fa-f]{6}$", description="Cor em formato hex")
    
    @validator('nome')
    def validar_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()

class CategoriaCreate(CategoriaBase):
    evento_id: int = Field(..., description="ID do evento")

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(None, max_length=1000)
    cor: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    ativo: Optional[bool] = None

    @validator('nome')
    def validar_nome(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Nome não pode ser vazio')
        return v.strip() if v else v

class CategoriaResponse(CategoriaBase):
    id: int
    ativo: bool
    evento_id: int
    empresa_id: Optional[int]
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

# Produto Schemas
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do produto")
    tipo: TipoProdutoEnum = Field(..., description="Tipo do produto")
    preco: Decimal = Field(..., gt=0, description="Preço do produto")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoria do produto")
    codigo_interno: Optional[str] = Field(None, max_length=20, description="Código interno")
    estoque_atual: Optional[int] = Field(0, ge=0, description="Estoque atual")
    estoque_minimo: Optional[int] = Field(0, ge=0, description="Estoque mínimo")
    estoque_maximo: Optional[int] = Field(1000, ge=0, description="Estoque máximo")
    controla_estoque: Optional[bool] = Field(True, description="Se controla estoque")
    status: Optional[StatusProdutoEnum] = Field(StatusProdutoEnum.ATIVO, description="Status do produto")
    imagem_url: Optional[str] = Field(None, max_length=500, description="URL da imagem")
    # evento_id removido do schema frontend - produtos são globais

    @validator('nome')
    def validar_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    tipo: Optional[TipoProdutoEnum] = None
    preco: Optional[Decimal] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, max_length=100)
    codigo_interno: Optional[str] = Field(None, max_length=20)
    estoque_atual: Optional[int] = Field(None, ge=0)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    estoque_maximo: Optional[int] = Field(None, ge=0)
    controla_estoque: Optional[bool] = None
    status: Optional[StatusProdutoEnum] = None
    imagem_url: Optional[str] = Field(None, max_length=500)

class ProdutoResponse(ProdutoBase):
    id: int
    empresa_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]  # Permitir NULL para compatibilidade

    class Config:
        from_attributes = True

# Schemas para listagem com filtros
class ProdutoFilter(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[TipoProdutoEnum] = None
    categoria: Optional[str] = None
    status: Optional[StatusProdutoEnum] = None
    preco_min: Optional[Decimal] = None
    preco_max: Optional[Decimal] = None
    estoque_baixo: Optional[bool] = None  # Produtos com estoque <= mínimo

class ProdutoList(BaseModel):
    produtos: List[ProdutoResponse]
    total: int
    page: int
    size: int
    pages: int

class CategoriaList(BaseModel):
    categorias: List[CategoriaResponse]
    total: int
    page: int
    size: int
    pages: int

# Schemas para relatórios
class ProdutoStats(BaseModel):
    total_produtos: int
    produtos_ativos: int
    produtos_inativos: int
    produtos_estoque_baixo: int
    valor_total_estoque: Decimal
    produtos_por_categoria: List[dict]
    produtos_mais_vendidos: List[dict]

class CategoriaStats(BaseModel):
    total_categorias: int
    categorias_ativas: int
    produtos_por_categoria: List[dict]
