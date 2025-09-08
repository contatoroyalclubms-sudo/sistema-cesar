from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/produtos", tags=["produtos"])

# Schemas simplificados
class CategoriaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    cor: Optional[str] = "#3b82f6"

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    cor: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    id: int
    ativo: bool = True
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# Mock data para desenvolvimento
mock_categorias = [
    {
        "id": 1,
        "nome": "Bebidas",
        "descricao": "Bebidas alcoólicas e não alcoólicas",
        "cor": "#10B981",
        "ativo": True,
        "criado_em": datetime.now(),
        "atualizado_em": datetime.now()
    },
    {
        "id": 2,
        "nome": "Comidas",
        "descricao": "Pratos principais e petiscos",
        "cor": "#F59E0B",
        "ativo": True,
        "criado_em": datetime.now(),
        "atualizado_em": datetime.now()
    },
    {
        "id": 3,
        "nome": "Sobremesas",
        "descricao": "Doces e sobremesas",
        "cor": "#EF4444",
        "ativo": False,
        "criado_em": datetime.now(),
        "atualizado_em": datetime.now()
    }
]

# Endpoints de Categorias
@router.get("/categorias/", response_model=List[CategoriaResponse])
async def listar_categorias():
    """Listar todas as categorias"""
    return mock_categorias

@router.post("/categorias/", response_model=CategoriaResponse)
async def criar_categoria(categoria: CategoriaCreate):
    """Criar nova categoria"""
    nova_categoria = {
        "id": len(mock_categorias) + 1,
        "nome": categoria.nome,
        "descricao": categoria.descricao,
        "cor": categoria.cor,
        "ativo": True,
        "criado_em": datetime.now(),
        "atualizado_em": datetime.now()
    }
    mock_categorias.append(nova_categoria)
    return nova_categoria

@router.get("/categorias/{categoria_id}", response_model=CategoriaResponse)
async def obter_categoria(categoria_id: int):
    """Obter categoria por ID"""
    categoria = next((c for c in mock_categorias if c["id"] == categoria_id), None)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria

@router.put("/categorias/{categoria_id}", response_model=CategoriaResponse)
async def atualizar_categoria(categoria_id: int, categoria: CategoriaUpdate):
    """Atualizar categoria"""
    for i, c in enumerate(mock_categorias):
        if c["id"] == categoria_id:
            if categoria.nome:
                mock_categorias[i]["nome"] = categoria.nome
            if categoria.descricao:
                mock_categorias[i]["descricao"] = categoria.descricao
            if categoria.cor:
                mock_categorias[i]["cor"] = categoria.cor
            mock_categorias[i]["atualizado_em"] = datetime.now()
            return mock_categorias[i]
    raise HTTPException(status_code=404, detail="Categoria não encontrada")

@router.delete("/categorias/{categoria_id}")
async def deletar_categoria(categoria_id: int):
    """Deletar categoria"""
    for i, c in enumerate(mock_categorias):
        if c["id"] == categoria_id:
            del mock_categorias[i]
            return {"message": "Categoria deletada com sucesso"}
    raise HTTPException(status_code=404, detail="Categoria não encontrada")
