"""
Schemas para funcionalidades de Import/Export do estoque
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


class StatusImportacao(str, Enum):
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDA = "CONCLUIDA"
    ERRO = "ERRO"
    CANCELADA = "CANCELADA"


class TipoOperacao(str, Enum):
    IMPORTACAO = "IMPORTACAO"
    EXPORTACAO = "EXPORTACAO"


class StatusValidacao(str, Enum):
    VALIDO = "VALIDO"
    ERRO_CRITICO = "ERRO_CRITICO"
    AVISO = "AVISO"


class FormatoArquivo(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


# ==================== SCHEMAS DE IMPORTAÇÃO ====================

class ProdutoImportacao(BaseModel):
    """Schema para importação de produtos"""
    # Campos obrigatórios
    codigo: str = Field(..., min_length=1, max_length=50, description="SKU/Código do produto")
    nome: str = Field(..., min_length=3, max_length=255, description="Nome do produto")
    categoria: str = Field(..., min_length=1, max_length=100, description="Categoria do produto")
    preco_venda: float = Field(..., gt=0, description="Preço de venda")
    
    # Campos opcionais básicos
    codigo_barras: Optional[str] = Field(None, max_length=50, description="EAN/Código de barras")
    descricao: Optional[str] = Field(None, description="Descrição detalhada")
    marca: Optional[str] = Field(None, max_length=100, description="Marca do produto")
    fornecedor: Optional[str] = Field(None, max_length=200, description="Nome/código fornecedor")
    preco_custo: Optional[float] = Field(None, ge=0, description="Preço de custo")
    margem_lucro: Optional[float] = Field(None, ge=0, le=100, description="% de margem")
    
    # Estoque
    quantidade_inicial: Optional[int] = Field(None, ge=0, description="Estoque inicial")
    estoque_minimo: Optional[int] = Field(None, ge=0, description="Alerta estoque baixo")
    estoque_maximo: Optional[int] = Field(None, ge=0, description="Limite máximo")
    unidade_medida: Optional[str] = Field("UN", max_length=10, description="UN, LT, KG, etc")
    
    # Produto específico
    volume: Optional[float] = Field(None, ge=0, description="Volume em ml, L, etc")
    teor_alcoolico: Optional[float] = Field(None, ge=0, le=100, description="% álcool")
    temperatura_ideal: Optional[str] = Field(None, max_length=20, description="Gelado, Ambiente, etc")
    validade_dias: Optional[int] = Field(None, gt=0, description="Dias até vencer")
    
    # Fiscal
    ncm: Optional[str] = Field(None, pattern=r"^\d{8}$", description="Código NCM (8 dígitos)")
    icms: Optional[float] = Field(None, ge=0, le=100, description="% ICMS")
    ipi: Optional[float] = Field(None, ge=0, le=100, description="% IPI")
    
    # Controle
    ativo: Optional[bool] = Field(True, description="Produto ativo")
    destaque: Optional[bool] = Field(False, description="Produto em destaque")
    promocional: Optional[bool] = Field(False, description="Em promoção")
    observacoes: Optional[str] = Field(None, description="Observações gerais")

    @validator('codigo')
    def validate_codigo(cls, v):
        if not v or not v.strip():
            raise ValueError('Código não pode estar vazio')
        return v.strip().upper()

    @validator('codigo_barras')
    def validate_codigo_barras(cls, v):
        if v and not v.isdigit():
            raise ValueError('Código de barras deve conter apenas números')
        return v


class MapeamentoCampo(BaseModel):
    """Mapeamento entre campo do arquivo e campo do sistema"""
    campo_arquivo: str = Field(..., description="Nome da coluna no arquivo")
    campo_sistema: str = Field(..., description="Nome do campo no sistema")
    obrigatorio: bool = Field(False, description="Se é obrigatório")
    transformacao: Optional[str] = Field(None, description="Regra de transformação")


class ConfiguracaoImportacao(BaseModel):
    """Configuração para importação"""
    formato_arquivo: FormatoArquivo
    mapeamento: List[MapeamentoCampo]
    separador_csv: Optional[str] = Field(",", description="Separador para CSV")
    encoding: Optional[str] = Field("UTF-8", description="Codificação do arquivo")
    linha_cabecalho: Optional[int] = Field(1, description="Linha do cabeçalho")
    validar_apenas: bool = Field(False, description="Apenas validar sem importar")
    sobrescrever_existentes: bool = Field(False, description="Sobrescrever produtos existentes")


class ValidacaoImportacaoResponse(BaseModel):
    """Resposta de validação"""
    linha: int
    campo: Optional[str]
    tipo_validacao: str
    status: StatusValidacao
    mensagem: str
    valor_original: Optional[str]
    valor_sugerido: Optional[str]
    
    class Config:
        from_attributes = True


class PreviewImportacao(BaseModel):
    """Preview dos dados para importação"""
    linha: int
    dados: Dict[str, Any]
    validacoes: List[ValidacaoImportacaoResponse]
    status: StatusValidacao


class OperacaoImportacaoCreate(BaseModel):
    """Criar nova operação de importação"""
    nome_arquivo: str
    formato_arquivo: FormatoArquivo
    configuracao: ConfiguracaoImportacao


class OperacaoImportacaoResponse(BaseModel):
    """Resposta da operação de importação"""
    id: int
    tipo_operacao: TipoOperacao
    nome_arquivo: str
    formato_arquivo: str
    status: StatusImportacao
    total_registros: int
    registros_processados: int
    registros_sucesso: int
    registros_erro: int
    registros_aviso: int
    inicio_processamento: Optional[datetime]
    fim_processamento: Optional[datetime]
    criado_em: datetime
    resumo_operacao: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS DE EXPORTAÇÃO ====================

class TipoExportacao(str, Enum):
    ESTOQUE_COMPLETO = "estoque_completo"
    ESTOQUE_BAIXO = "estoque_baixo"
    LISTA_PRECOS = "lista_precos"
    INVENTARIO = "inventario"
    FISCAL = "fiscal"
    PERSONALIZADO = "personalizado"


class FiltroExportacao(BaseModel):
    """Filtros para exportação"""
    categorias: Optional[List[str]] = Field(None, description="Filtrar por categorias")
    fornecedores: Optional[List[str]] = Field(None, description="Filtrar por fornecedores")
    estoque_status: Optional[str] = Field(None, description="normal, baixo, zerado, excesso")
    data_inicio: Optional[datetime] = Field(None, description="Data início")
    data_fim: Optional[datetime] = Field(None, description="Data fim")
    preco_min: Optional[float] = Field(None, ge=0, description="Preço mínimo")
    preco_max: Optional[float] = Field(None, ge=0, description="Preço máximo")
    apenas_ativos: bool = Field(True, description="Apenas produtos ativos")
    apenas_com_estoque: bool = Field(False, description="Apenas com estoque > 0")


class ConfiguracaoExportacao(BaseModel):
    """Configuração para exportação"""
    tipo_exportacao: TipoExportacao
    formato: FormatoArquivo
    campos_personalizados: Optional[List[str]] = Field(None, description="Campos específicos")
    filtros: Optional[FiltroExportacao] = Field(None, description="Filtros aplicados")
    incluir_cabecalho: bool = Field(True, description="Incluir linha de cabeçalho")
    separador_csv: Optional[str] = Field(",", description="Separador para CSV")
    encoding: Optional[str] = Field("UTF-8", description="Codificação do arquivo")


class PreviewExportacao(BaseModel):
    """Preview da exportação"""
    total_registros: int
    campos_incluidos: List[str]
    primeiras_linhas: List[Dict[str, Any]]
    tamanho_estimado: str


# ==================== SCHEMAS DE TEMPLATES ====================

class TemplateImportacaoCreate(BaseModel):
    """Criar template de importação"""
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = Field(None)
    formato: FormatoArquivo
    mapeamento_padrao: Dict[str, Any]
    campos_obrigatorios: List[str]
    validacoes_personalizadas: Optional[Dict[str, Any]] = Field(None)


class TemplateImportacaoResponse(BaseModel):
    """Resposta do template"""
    id: int
    nome: str
    descricao: Optional[str]
    formato: str
    mapeamento_padrao: Dict[str, Any]
    campos_obrigatorios: List[str]
    ativo: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS DE MONITORAMENTO ====================

class EstatisticasImportExport(BaseModel):
    """Estatísticas do dashboard"""
    importacoes_hoje: int
    produtos_atualizados: int
    ultimo_import_erros: int
    tempo_medio_processo: float  # em segundos
    operacoes_recentes: List[OperacaoImportacaoResponse]


class ResumoOperacao(BaseModel):
    """Resumo detalhado da operação"""
    operacao_id: int
    duracao_segundos: float
    taxa_sucesso: float
    principais_erros: List[str]
    categorias_afetadas: List[str]
    valor_total_produtos: float


# ==================== SCHEMAS DE RELATÓRIOS ====================

class RelatorioGiroEstoque(BaseModel):
    """Relatório de giro de estoque"""
    codigo: str
    nome: str
    categoria: str
    estoque_medio: float
    vendas_periodo: int
    giro: float


class RelatorioAnaliseABC(BaseModel):
    """Análise ABC de produtos"""
    produto_id: int
    nome: str
    faturamento: float
    classe: str  # A, B, C
    percentual_acumulado: float


class RelatorioPerdas(BaseModel):
    """Relatório de perdas"""
    nome_produto: str
    motivo: str
    quantidade_perdida: int
    valor_perdido: float


# ==================== SCHEMAS DE VALIDAÇÃO ====================

class RegraValidacao(BaseModel):
    """Regra de validação customizada"""
    campo: str
    tipo: str  # required, unique, pattern, range, custom
    parametros: Dict[str, Any]
    mensagem_erro: str
    severidade: StatusValidacao


class ResultadoValidacao(BaseModel):
    """Resultado completo da validação"""
    total_linhas: int
    linhas_validas: int
    linhas_com_erro: int
    linhas_com_aviso: int
    pode_importar: bool
    resumo_erros: Dict[str, int]
    detalhes: List[ValidacaoImportacaoResponse]


# ==================== SCHEMAS UTILITÁRIOS ====================

class ProgressoOperacao(BaseModel):
    """Progresso de uma operação"""
    operacao_id: int
    porcentagem: float
    etapa_atual: str
    tempo_estimado_restante: Optional[int]  # em segundos
    ultima_atualizacao: datetime


class CampoDisponivel(BaseModel):
    """Campo disponível para mapeamento"""
    nome: str
    tipo: str
    obrigatorio: bool
    descricao: str
    aliases: List[str]  # possíveis nomes alternativos
    validacoes: List[str]


class OpcoesImportacao(BaseModel):
    """Opções disponíveis para importação"""
    formatos_suportados: List[FormatoArquivo]
    campos_disponiveis: List[CampoDisponivel]
    templates_disponiveis: List[TemplateImportacaoResponse]
    categorias_existentes: List[str]
    fornecedores_existentes: List[str]