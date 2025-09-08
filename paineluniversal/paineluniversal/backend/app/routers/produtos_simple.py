from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..models import Produto, Empresa, TipoProduto, StatusProduto
from ..schemas.produtos import (
    ProdutoCreate, ProdutoUpdate, ProdutoResponse, ProdutoList, ProdutoFilter
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.get("/", response_model=ProdutoList)
async def listar_produtos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    estoque_baixo: Optional[bool] = Query(None, description="Produtos com estoque baixo"),
    db: Session = Depends(get_db)
):
    """Listar produtos com filtros e paginação"""
    try:
        # Query base
        query = db.query(Produto)
        
        # Aplicar filtros
        if nome:
            query = query.filter(Produto.nome.ilike(f"%{nome}%"))
        if tipo:
            query = query.filter(Produto.tipo_usuario== tipo)
        if categoria:
            query = query.filter(Produto.categoria.ilike(f"%{categoria}%"))
        if status:
            query = query.filter(Produto.status == status)
        if estoque_baixo:
            query = query.filter(Produto.estoque_atual <= Produto.estoque_minimo)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação e ordenação
        produtos = query.order_by(Produto.nome).offset(skip).limit(limit).all()
        
        # Calcular páginas
        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return ProdutoList(
            produtos=produtos,
            total=total,
            page=page,
            size=len(produtos),
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db)
):
    """Criar novo produto"""
    try:
        # Verificar código interno único se fornecido
        if produto.codigo_interno:
            produto_existente = db.query(Produto).filter(
                Produto.codigo_interno == produto.codigo_interno
            ).first()
            if produto_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe um produto com este código interno"
                )
        
        # Criar produto
        produto_data = produto.dict()
        db_produto = Produto(**produto_data)
        
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        
        logger.info(f"Produto criado: {db_produto.nome} (ID: {db_produto.id})")
        return db_produto
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar produto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Obter produto por ID"""
    try:
        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )
        
        return produto
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter produto {produto_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.put("/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: int,
    produto: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar produto"""
    try:
        # Buscar produto
        db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if not db_produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )
        
        # Verificar código interno único se alterado
        if produto.codigo_interno and produto.codigo_interno != db_produto.codigo_interno:
            produto_existente = db.query(Produto).filter(
                and_(
                    Produto.codigo_interno == produto.codigo_interno,
                    Produto.id != produto_id
                )
            ).first()
            if produto_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe um produto com este código interno"
                )
        
        # Atualizar campos
        produto_data = produto.dict(exclude_unset=True)
        for field, value in produto_data.items():
            setattr(db_produto, field, value)
        
        db_produto.atualizado_em = datetime.utcnow()
        db.commit()
        db.refresh(db_produto)
        
        logger.info(f"Produto atualizado: {db_produto.nome} (ID: {db_produto.id})")
        return db_produto
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar produto {produto_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/{produto_id}")
async def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Deletar produto (soft delete)"""
    try:
        # Buscar produto
        db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if not db_produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )
        
        # Soft delete
        db_produto.status = StatusProduto.INATIVO
        db_produto.atualizado_em = datetime.utcnow()
        db.commit()
        
        logger.info(f"Produto deletado: {db_produto.nome} (ID: {db_produto.id})")
        
        return {"message": "Produto deletado com sucesso"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar produto {produto_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )
