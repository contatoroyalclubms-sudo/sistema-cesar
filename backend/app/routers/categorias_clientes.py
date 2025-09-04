"""
Router para gerenciamento de categorias de clientes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    CategoriaCliente, CategoriaClienteCreate, CategoriaClienteUpdate,
    ClienteCategoria, ClienteCategoriaCreate
)

router = APIRouter(
    prefix="/api/categorias-clientes",
    tags=["categorias-clientes"]
)

@router.get("/", response_model=List[CategoriaCliente])
def listar_categorias(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as categorias de clientes"""
    query = db.query(models.CategoriaCliente)
    
    if search:
        query = query.filter(
            or_(
                models.CategoriaCliente.nome.ilike(f"%{search}%"),
                models.CategoriaCliente.descricao.ilike(f"%{search}%")
            )
        )
    
    if ativo is not None:
        query = query.filter(models.CategoriaCliente.ativo == ativo)
    
    query = query.order_by(models.CategoriaCliente.ordem, models.CategoriaCliente.nome)
    categorias = query.offset(skip).limit(limit).all()
    
    # Adicionar contagem de clientes para cada categoria
    for categoria in categorias:
        categoria.total_clientes = db.query(models.ClienteCategoria).filter(
            models.ClienteCategoria.categoria_id == categoria.id,
            models.ClienteCategoria.data_fim.is_(None)
        ).count()
    
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaCliente)
def obter_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém uma categoria específica"""
    categoria = db.query(models.CategoriaCliente).filter(
        models.CategoriaCliente.id == categoria_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    categoria.total_clientes = db.query(models.ClienteCategoria).filter(
        models.ClienteCategoria.categoria_id == categoria.id,
        models.ClienteCategoria.data_fim.is_(None)
    ).count()
    
    return categoria

@router.post("/", response_model=CategoriaCliente)
def criar_categoria(
    categoria: CategoriaClienteCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova categoria de clientes"""
    # Verificar se já existe uma categoria com o mesmo nome
    categoria_existente = db.query(models.CategoriaCliente).filter(
        models.CategoriaCliente.nome == categoria.nome
    ).first()
    
    if categoria_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma categoria com este nome"
        )
    
    # Converter benefícios para JSON string se necessário
    beneficios = None
    if categoria.beneficios:
        import json
        beneficios = json.dumps(categoria.beneficios)
    
    db_categoria = models.CategoriaCliente(
        **categoria.model_dump(exclude={'beneficios'}),
        beneficios=beneficios
    )
    
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    
    db_categoria.total_clientes = 0
    return db_categoria

@router.put("/{categoria_id}", response_model=CategoriaCliente)
def atualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaClienteUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma categoria existente"""
    categoria = db.query(models.CategoriaCliente).filter(
        models.CategoriaCliente.id == categoria_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar nome duplicado se estiver sendo alterado
    if categoria_update.nome and categoria_update.nome != categoria.nome:
        categoria_existente = db.query(models.CategoriaCliente).filter(
            models.CategoriaCliente.nome == categoria_update.nome,
            models.CategoriaCliente.id != categoria_id
        ).first()
        
        if categoria_existente:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma categoria com este nome"
            )
    
    # Atualizar campos
    update_data = categoria_update.model_dump(exclude_unset=True)
    
    # Converter benefícios para JSON string se necessário
    if 'beneficios' in update_data and update_data['beneficios']:
        import json
        update_data['beneficios'] = json.dumps(update_data['beneficios'])
    
    for key, value in update_data.items():
        setattr(categoria, key, value)
    
    db.commit()
    db.refresh(categoria)
    
    categoria.total_clientes = db.query(models.ClienteCategoria).filter(
        models.ClienteCategoria.categoria_id == categoria.id,
        models.ClienteCategoria.data_fim.is_(None)
    ).count()
    
    return categoria

@router.delete("/{categoria_id}")
def deletar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deleta uma categoria (soft delete - marca como inativa)"""
    categoria = db.query(models.CategoriaCliente).filter(
        models.CategoriaCliente.id == categoria_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar se há clientes associados
    clientes_ativos = db.query(models.ClienteCategoria).filter(
        models.ClienteCategoria.categoria_id == categoria_id,
        models.ClienteCategoria.data_fim.is_(None)
    ).count()
    
    if clientes_ativos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível deletar a categoria. Há {clientes_ativos} clientes associados."
        )
    
    categoria.ativo = False
    db.commit()
    
    return {"message": "Categoria desativada com sucesso"}

# ====== ROTAS DE ASSOCIAÇÃO CLIENTE-CATEGORIA ======

@router.post("/associar", response_model=ClienteCategoria)
def associar_cliente_categoria(
    associacao: ClienteCategoriaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Associa um cliente a uma categoria"""
    # Verificar se a categoria existe
    categoria = db.query(models.CategoriaCliente).filter(
        models.CategoriaCliente.id == associacao.categoria_id,
        models.CategoriaCliente.ativo == True
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada ou inativa")
    
    # Verificar se o cliente existe
    cliente = db.query(models.ClienteEvento).filter(
        models.ClienteEvento.id == associacao.cliente_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar se já existe associação ativa
    associacao_existente = db.query(models.ClienteCategoria).filter(
        models.ClienteCategoria.cliente_id == associacao.cliente_id,
        models.ClienteCategoria.categoria_id == associacao.categoria_id,
        models.ClienteCategoria.data_fim.is_(None)
    ).first()
    
    if associacao_existente:
        raise HTTPException(
            status_code=400,
            detail="Cliente já está associado a esta categoria"
        )
    
    # Criar associação
    db_associacao = models.ClienteCategoria(**associacao.model_dump())
    db.add(db_associacao)
    db.commit()
    db.refresh(db_associacao)
    
    # Adicionar informações da categoria
    db_associacao.categoria = categoria
    
    return db_associacao

@router.delete("/associar/{associacao_id}")
def desassociar_cliente_categoria(
    associacao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Remove a associação entre cliente e categoria"""
    associacao = db.query(models.ClienteCategoria).filter(
        models.ClienteCategoria.id == associacao_id,
        models.ClienteCategoria.data_fim.is_(None)
    ).first()
    
    if not associacao:
        raise HTTPException(
            status_code=404,
            detail="Associação não encontrada ou já desativada"
        )
    
    # Marcar como finalizada
    associacao.data_fim = func.now()
    db.commit()
    
    return {"message": "Associação removida com sucesso"}

@router.get("/cliente/{cliente_id}", response_model=List[ClienteCategoria])
def listar_categorias_cliente(
    cliente_id: int,
    incluir_inativas: bool = False,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as categorias de um cliente"""
    query = db.query(models.ClienteCategoria).filter(
        models.ClienteCategoria.cliente_id == cliente_id
    )
    
    if not incluir_inativas:
        query = query.filter(models.ClienteCategoria.data_fim.is_(None))
    
    associacoes = query.all()
    
    # Adicionar informações da categoria
    for associacao in associacoes:
        associacao.categoria = db.query(models.CategoriaCliente).filter(
            models.CategoriaCliente.id == associacao.categoria_id
        ).first()
    
    return associacoes

@router.get("/categoria/{categoria_id}/clientes")
def listar_clientes_categoria(
    categoria_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os clientes de uma categoria"""
    # Verificar se a categoria existe
    categoria = db.query(models.CategoriaCliente).filter(
        models.CategoriaCliente.id == categoria_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Buscar clientes associados
    query = db.query(models.ClienteEvento).join(
        models.ClienteCategoria,
        models.ClienteEvento.id == models.ClienteCategoria.cliente_id
    ).filter(
        models.ClienteCategoria.categoria_id == categoria_id,
        models.ClienteCategoria.data_fim.is_(None)
    )
    
    total = query.count()
    clientes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "categoria": categoria.nome,
        "clientes": clientes
    }