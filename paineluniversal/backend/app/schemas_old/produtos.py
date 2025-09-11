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
