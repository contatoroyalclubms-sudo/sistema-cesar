"""
Schemas Pydantic para Sistema de Split de Pagamentos
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


# ==================== ENUMS ====================

class TipoCalculoSplitEnum(str, Enum):
    PERCENTUAL = "percentual"
    VALOR_FIXO = "valor_fixo"
    VALOR_POR_ITEM = "valor_por_item"


class TipoBeneficiarioEnum(str, Enum):
    EMPRESA = "empresa"
    FORNECEDOR = "fornecedor"
    PARCEIRO = "parceiro"
    PROMOTER = "promoter"
    VENDEDOR = "vendedor"
    AFILIADO = "afiliado"


class StatusSplitEnum(str, Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    PAGO = "pago"
    ERRO = "erro"
    CANCELADO = "cancelado"


# ==================== SPLIT RULE ====================

class DadosPagamento(BaseModel):
    """Dados bancários/pagamento do beneficiário"""
    tipo: str = Field(..., description="pix, conta_bancaria, carteira_digital")
    
    # PIX
    chave_pix: Optional[str] = None
    tipo_chave_pix: Optional[str] = None  # cpf, cnpj, email, telefone, aleatorio
    
    # Conta Bancária
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[str] = None  # corrente, poupanca
    
    # Documento
    cpf_cnpj: Optional[str] = None
    nome_completo: Optional[str] = None


class CondicoesSplit(BaseModel):
    """Condições para aplicar uma regra de split"""
    produto_ids: Optional[List[int]] = Field(None, description="IDs dos produtos aplicáveis")
    categoria_ids: Optional[List[int]] = Field(None, description="IDs das categorias aplicáveis")
    min_valor: Optional[float] = Field(None, ge=0, description="Valor mínimo da venda")
    max_valor: Optional[float] = Field(None, ge=0, description="Valor máximo da venda")
    dias_semana: Optional[List[int]] = Field(None, description="Dias da semana (0=segunda, 6=domingo)")
    horario_inicio: Optional[str] = Field(None, regex="^\\d{2}:\\d{2}$", description="Horário início (HH:MM)")
    horario_fim: Optional[str] = Field(None, regex="^\\d{2}:\\d{2}$", description="Horário fim (HH:MM)")
    
    @validator('dias_semana')
    def validar_dias_semana(cls, v):
        if v:
            for dia in v:
                if dia < 0 or dia > 6:
                    raise ValueError('Dia da semana deve estar entre 0 (segunda) e 6 (domingo)')
        return v


class SplitRuleBase(BaseModel):
    """Base para regras de split"""
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    
    # Beneficiário
    beneficiario_tipo: TipoBeneficiarioEnum
    beneficiario_id: str = Field(..., min_length=1, max_length=100)
    beneficiario_nome: str = Field(..., min_length=3, max_length=200)
    dados_pagamento: DadosPagamento
    
    # Regra de cálculo
    tipo_calculo: TipoCalculoSplitEnum
    valor: float = Field(..., gt=0, description="Percentual ou valor fixo")
    
    # Condições
    condicoes: Optional[CondicoesSplit] = None
    
    # Configurações
    prioridade: int = Field(0, ge=0, le=999)
    valor_minimo: Optional[float] = Field(0, ge=0)
    valor_maximo: Optional[float] = Field(None, ge=0)
    ativo: bool = True
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    
    @validator('valor')
    def validar_valor(cls, v, values):
        if 'tipo_calculo' in values:
            if values['tipo_calculo'] == TipoCalculoSplitEnum.PERCENTUAL:
                if v > 100:
                    raise ValueError('Percentual não pode ser maior que 100%')
        return v


class SplitRuleCreate(SplitRuleBase):
    """Schema para criar regra de split"""
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    
    @validator('evento_id', 'empresa_id')
    def validar_associacao(cls, v, values):
        # Deve ter pelo menos evento_id ou empresa_id
        if not v and not values.get('evento_id') and not values.get('empresa_id'):
            raise ValueError('Deve especificar evento_id ou empresa_id')
        return v


class SplitRuleUpdate(BaseModel):
    """Schema para atualizar regra de split"""
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = None
    dados_pagamento: Optional[DadosPagamento] = None
    tipo_calculo: Optional[TipoCalculoSplitEnum] = None
    valor: Optional[float] = Field(None, gt=0)
    condicoes: Optional[CondicoesSplit] = None
    prioridade: Optional[int] = Field(None, ge=0, le=999)
    valor_minimo: Optional[float] = Field(None, ge=0)
    valor_maximo: Optional[float] = Field(None, ge=0)
    ativo: Optional[bool] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None


class SplitRuleResponse(SplitRuleBase):
    """Schema de resposta para regra de split"""
    id: int
    evento_id: Optional[int]
    empresa_id: Optional[int]
    criado_em: datetime
    atualizado_em: Optional[datetime]
    
    # Estatísticas
    total_execucoes: Optional[int] = 0
    valor_total_processado: Optional[float] = 0
    
    class Config:
        from_attributes = True


# ==================== SPLIT EXECUTION ====================

class SplitExecutionBase(BaseModel):
    """Base para execução de split"""
    venda_id: int
    rule_id: Optional[int]
    valor_venda: float
    valor_split: float
    beneficiario_tipo: TipoBeneficiarioEnum
    beneficiario_id: str
    beneficiario_nome: str


class SplitExecutionCreate(BaseModel):
    """Schema para criar execução de split (calculado automaticamente)"""
    venda_id: int
    executar_agora: bool = Field(False, description="Processar pagamento imediatamente")


class SplitExecutionResponse(SplitExecutionBase):
    """Schema de resposta para execução de split"""
    id: int
    valor_base_calculo: float
    valor_taxa: float
    valor_liquido: float
    dados_pagamento: Dict[str, Any]
    status: StatusSplitEnum
    gateway_usado: Optional[str]
    gateway_transaction_id: Optional[str]
    data_execucao: datetime
    data_processamento: Optional[datetime]
    data_pagamento: Optional[datetime]
    erro_mensagem: Optional[str]
    tentativas: int
    
    class Config:
        from_attributes = True


# ==================== CÁLCULO DE SPLIT ====================

class SplitCalculado(BaseModel):
    """Resultado do cálculo de split"""
    rule_id: Optional[int]
    beneficiario_tipo: str
    beneficiario_id: str
    beneficiario_nome: str
    valor: float
    tipo_calculo: str
    prioridade: int
    dados_pagamento: Optional[Dict[str, Any]]


class CalculoSplitRequest(BaseModel):
    """Request para calcular splits de uma venda"""
    venda_id: int
    simular: bool = Field(True, description="Apenas simular sem salvar")


class CalculoSplitResponse(BaseModel):
    """Response do cálculo de splits"""
    venda_id: int
    valor_total_venda: float
    splits: List[SplitCalculado]
    valor_total_splits: float
    valor_organizador: float
    
    @validator('valor_organizador')
    def calcular_valor_organizador(cls, v, values):
        if 'valor_total_venda' in values and 'valor_total_splits' in values:
            return values['valor_total_venda'] - values['valor_total_splits']
        return v


# ==================== RELATÓRIOS ====================

class FiltroRelatorioSplit(BaseModel):
    """Filtros para relatório de splits"""
    evento_id: Optional[int] = None
    empresa_id: Optional[int] = None
    beneficiario_id: Optional[str] = None
    beneficiario_tipo: Optional[TipoBeneficiarioEnum] = None
    status: Optional[StatusSplitEnum] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    gateway: Optional[str] = None


class TotaisRelatorio(BaseModel):
    """Totais do relatório"""
    quantidade: int
    valor_bruto: float
    valor_taxas: float
    valor_liquido: float


class StatusRelatorio(BaseModel):
    """Resumo por status"""
    status: str
    quantidade: int
    valor: float


class BeneficiarioRelatorio(BaseModel):
    """Resumo por beneficiário"""
    nome: str
    tipo: str
    quantidade: int
    valor_bruto: float
    valor_liquido: float


class RelatorioSplitResponse(BaseModel):
    """Response do relatório de splits"""
    periodo: Dict[str, Optional[str]]
    totais: TotaisRelatorio
    por_status: List[StatusRelatorio]
    por_beneficiario: List[BeneficiarioRelatorio]
    execucoes: List[SplitExecutionResponse]


# ==================== CONFIGURAÇÃO GLOBAL ====================

class ConfiguracaoSplitGlobalBase(BaseModel):
    """Base para configuração global de split"""
    processar_automaticamente: bool = True
    horario_processamento: str = Field("03:00", regex="^\\d{2}:\\d{2}$")
    dias_para_processar: int = Field(1, ge=0, le=30)
    
    # Taxas
    taxa_split_percentual: float = Field(2.5, ge=0, le=10)
    taxa_split_fixa: float = Field(0, ge=0)
    
    # Limites
    valor_minimo_split: float = Field(10.00, ge=0)
    valor_maximo_split_diario: float = Field(50000.00, ge=0)
    
    # Gateways
    gateways_habilitados: List[str] = ["stripe", "pagseguro"]
    gateway_padrao: str = "stripe"
    
    # Notificações
    notificar_beneficiarios: bool = True
    emails_notificacao: List[str] = []


class ConfiguracaoSplitGlobalCreate(ConfiguracaoSplitGlobalBase):
    """Schema para criar configuração global"""
    empresa_id: int


class ConfiguracaoSplitGlobalUpdate(BaseModel):
    """Schema para atualizar configuração global"""
    processar_automaticamente: Optional[bool] = None
    horario_processamento: Optional[str] = Field(None, regex="^\\d{2}:\\d{2}$")
    dias_para_processar: Optional[int] = Field(None, ge=0, le=30)
    taxa_split_percentual: Optional[float] = Field(None, ge=0, le=10)
    taxa_split_fixa: Optional[float] = Field(None, ge=0)
    valor_minimo_split: Optional[float] = Field(None, ge=0)
    valor_maximo_split_diario: Optional[float] = Field(None, ge=0)
    gateways_habilitados: Optional[List[str]] = None
    gateway_padrao: Optional[str] = None
    notificar_beneficiarios: Optional[bool] = None
    emails_notificacao: Optional[List[str]] = None


class ConfiguracaoSplitGlobalResponse(ConfiguracaoSplitGlobalBase):
    """Schema de resposta para configuração global"""
    id: int
    empresa_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== DASHBOARD ====================

class DashboardSplitResponse(BaseModel):
    """Dashboard com métricas de split"""
    periodo: str
    
    # Métricas principais
    total_splits: int
    valor_total_processado: float
    valor_total_taxas: float
    valor_total_liquido: float
    
    # Por status
    splits_pagos: int
    splits_pendentes: int
    splits_erro: int
    
    # Top beneficiários
    top_beneficiarios: List[BeneficiarioRelatorio]
    
    # Evolução temporal
    evolucao_diaria: List[Dict[str, Any]]
    
    # Próximos pagamentos
    proximos_pagamentos: List[SplitExecutionResponse]