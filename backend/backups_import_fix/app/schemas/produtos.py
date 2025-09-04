from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal
from datetime import datetime

# Import dos enums necessários
try:
    from ..models import StatusProduto, TipoProduto
    # Convertendo para enums compatíveis
    StatusProdutoEnum = StatusProduto
    TipoProdutoEnum = TipoProduto
except ImportError:
    # Fallback para desenvolvimento
    from enum import Enum
    
    class StatusProdutoEnum(str, Enum):
        ATIVO = "ATIVO"
        INATIVO = "INATIVO"
        ESGOTADO = "ESGOTADO"
        
    class TipoProdutoEnum(str, Enum):
        BEBIDA = "BEBIDA"
        COMIDA = "COMIDA"
        INGRESSO = "INGRESSO"
        FICHA = "FICHA"
        COMBO = "COMBO"
        VOUCHER = "VOUCHER"

class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do produto")
    tipo: Optional[TipoProdutoEnum] = Field(TipoProdutoEnum.INGRESSO, description="Tipo do produto")
    preco: Decimal = Field(..., gt=0, description="Preço do produto")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoria do produto")
    codigo_interno: Optional[str] = Field(None, max_length=20, description="Código interno")
    estoque_atual: Optional[int] = Field(0, ge=0, description="Estoque atual")
    estoque_minimo: Optional[int] = Field(0, ge=0, description="Estoque mínimo")
    estoque_maximo: Optional[int] = Field(1000, ge=0, description="Estoque máximo")
    controla_estoque: Optional[bool] = Field(True, description="Se controla estoque")
    status: Optional[StatusProdutoEnum] = Field(StatusProdutoEnum.ATIVO, description="Status do produto")
    imagem_url: Optional[str] = Field(None, max_length=500, description="URL da imagem")

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
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProdutoDetalhado(ProdutoResponse):
    vendas_total: Optional[int] = 0
    receita_total: Optional[Decimal] = Decimal('0.00')
    ultima_venda: Optional[datetime] = None

# Schemas para importação/exportação
class ProdutoImport(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: Optional[str] = "produto"
    preco: Decimal
    categoria: Optional[str] = None
    codigo_interno: Optional[str] = None
    estoque_atual: Optional[int] = 0
    estoque_minimo: Optional[int] = 0
    estoque_maximo: Optional[int] = 1000

class ProdutoExport(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    tipo: str
    preco: Decimal
    categoria: Optional[str] = None
    codigo_interno: Optional[str] = None
    estoque_atual: int
    estoque_minimo: int
    estoque_maximo: int
    status: str
    criado_em: datetime

# Schema para filtros de pesquisa
class ProdutoFiltros(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    tipo: Optional[TipoProdutoEnum] = None
    status: Optional[StatusProdutoEnum] = None
    preco_min: Optional[Decimal] = None
    preco_max: Optional[Decimal] = None
    controla_estoque: Optional[bool] = None
    estoque_baixo: Optional[bool] = None  # Para produtos com estoque abaixo do mínimo

# Alias para compatibilidade com routers
ProdutoFilter = ProdutoFiltros

# Schema para listas paginadas
class ProdutoList(BaseModel):
    produtos: list[ProdutoResponse] = []
    total: int = 0
    skip: int = 0
    limit: int = 100
    
    class Config:
        from_attributes = True

# Schema para relatórios
class RelatorioProdutos(BaseModel):
    total_produtos: int = 0
    produtos_ativos: int = 0
    produtos_inativos: int = 0
    produtos_estoque_baixo: int = 0
    valor_total_estoque: Decimal = Decimal('0.00')
    categoria_mais_vendida: Optional[str] = None
    produto_mais_vendido: Optional[str] = None
