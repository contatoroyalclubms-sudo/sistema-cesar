from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from math import ceil

from ..database import get_db
from ..models import FormaPagamento, Usuario
from ..schemas import (
    FormaPagamento as FormaPagamentoSchema,
    FormaPagamentoCreate,
    FormaPagamentoUpdate,
    FormaPagamentoDetalhada,
    FormaPagamentoList
)
from ..auth_functions import obter_usuario_atual, verificar_permissao_admin

router = APIRouter()

@router.get("/", response_model=FormaPagamentoList)
async def listar_formas_pagamento(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Busca por nome, código ou descrição"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    ativo: Optional[bool] = Query(None, description="Filtrar por ativo"),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar formas de pagamento com filtros e paginação"""
    
    # Query base
    query = db.query(FormaPagamento)
    
    # Aplicar filtros
    if search:
        search_filter = f"%{search.lower()}%"
        query = query.filter(
            or_(
                FormaPagamento.nome.ilike(search_filter),
                FormaPagamento.codigo.ilike(search_filter),
                FormaPagamento.descricao.ilike(search_filter)
            )
        )
    
    if tipo:
        query = query.filter(FormaPagamento.tipo_usuario== tipo.upper())
    
    if status:
        query = query.filter(FormaPagamento.status == status.upper())
    
    if ativo is not None:
        query = query.filter(FormaPagamento.ativo == ativo)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação e ordenação
    items = query.order_by(
        FormaPagamento.ordem_exibicao.asc(),
        FormaPagamento.nome.asc()
    ).offset((page - 1) * per_page).limit(per_page).all()
    
    # Calcular total de páginas
    pages = ceil(total / per_page) if total > 0 else 1
    
    return FormaPagamentoList(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )

@router.get("/{forma_pagamento_id}", response_model=FormaPagamentoDetalhada)
async def obter_forma_pagamento(
    forma_pagamento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter forma de pagamento por ID"""
    
    forma_pagamento = db.query(FormaPagamento).filter(
        FormaPagamento.id == forma_pagamento_id
    ).first()
    
    if not forma_pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    return forma_pagamento

@router.post("/", response_model=FormaPagamentoSchema)
async def criar_forma_pagamento(
    forma_pagamento: FormaPagamentoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Criar nova forma de pagamento (apenas admins)"""
    
    # Verificar se nome já existe
    if db.query(FormaPagamento).filter(FormaPagamento.nome == forma_pagamento.nome).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma forma de pagamento com este nome"
        )
    
    # Verificar se código já existe
    if db.query(FormaPagamento).filter(FormaPagamento.codigo == forma_pagamento.codigo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma forma de pagamento com este código"
        )
    
    # Validar limites
    if (forma_pagamento.limite_maximo and 
        forma_pagamento.limite_minimo and 
        forma_pagamento.limite_maximo < forma_pagamento.limite_minimo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limite máximo não pode ser menor que o limite mínimo"
        )
    
    # Criar forma de pagamento
    db_forma_pagamento = FormaPagamento(
        **forma_pagamento.model_dump(),
        criado_por=usuario_atual.id
    )
    
    db.add(db_forma_pagamento)
    db.commit()
    db.refresh(db_forma_pagamento)
    
    return db_forma_pagamento

@router.put("/{forma_pagamento_id}", response_model=FormaPagamentoSchema)
async def atualizar_forma_pagamento(
    forma_pagamento_id: int,
    forma_pagamento_update: FormaPagamentoUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Atualizar forma de pagamento (apenas admins)"""
    
    # Buscar forma de pagamento
    db_forma_pagamento = db.query(FormaPagamento).filter(
        FormaPagamento.id == forma_pagamento_id
    ).first()
    
    if not db_forma_pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    # Verificar conflitos de nome
    if forma_pagamento_update.nome:
        conflito_nome = db.query(FormaPagamento).filter(
            and_(
                FormaPagamento.nome == forma_pagamento_update.nome,
                FormaPagamento.id != forma_pagamento_id
            )
        ).first()
        
        if conflito_nome:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma forma de pagamento com este nome"
            )
    
    # Verificar conflitos de código
    if forma_pagamento_update.codigo:
        conflito_codigo = db.query(FormaPagamento).filter(
            and_(
                FormaPagamento.codigo == forma_pagamento_update.codigo,
                FormaPagamento.id != forma_pagamento_id
            )
        ).first()
        
        if conflito_codigo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma forma de pagamento com este código"
            )
    
    # Validar limites se informados
    limite_min = forma_pagamento_update.limite_minimo or db_forma_pagamento.limite_minimo
    limite_max = forma_pagamento_update.limite_maximo or db_forma_pagamento.limite_maximo
    
    if limite_max and limite_min and limite_max < limite_min:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limite máximo não pode ser menor que o limite mínimo"
        )
    
    # Atualizar campos informados
    update_data = forma_pagamento_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_forma_pagamento, field, value)
    
    db.commit()
    db.refresh(db_forma_pagamento)
    
    return db_forma_pagamento

@router.delete("/{forma_pagamento_id}")
async def excluir_forma_pagamento(
    forma_pagamento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Excluir forma de pagamento (apenas admins)"""
    
    # Buscar forma de pagamento
    db_forma_pagamento = db.query(FormaPagamento).filter(
        FormaPagamento.id == forma_pagamento_id
    ).first()
    
    if not db_forma_pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    # TODO: Verificar se a forma de pagamento está sendo usada em vendas/transações
    # if db.query(VendaPDV).filter(VendaPDV.forma_pagamento_id == forma_pagamento_id).first():
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Não é possível excluir forma de pagamento que possui vendas associadas"
    #     )
    
    db.delete(db_forma_pagamento)
    db.commit()
    
    return {"message": "Forma de pagamento excluída com sucesso"}

@router.patch("/{forma_pagamento_id}/toggle-status")
async def alternar_status_forma_pagamento(
    forma_pagamento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Alternar status ativo/inativo da forma de pagamento"""
    
    db_forma_pagamento = db.query(FormaPagamento).filter(
        FormaPagamento.id == forma_pagamento_id
    ).first()
    
    if not db_forma_pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    db_forma_pagamento.ativo = not db_forma_pagamento.ativo
    db.commit()
    db.refresh(db_forma_pagamento)
    
    return {
        "message": f"Forma de pagamento {'ativada' if db_forma_pagamento.ativo else 'desativada'} com sucesso",
        "ativo": db_forma_pagamento.ativo
    }

@router.get("/tipos/opcoes")
async def listar_tipos_forma_pagamento(
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar tipos de forma de pagamento disponíveis"""
    from ..models import TipoFormaPagamento, StatusFormaPagamento
    
    return {
        "tipos": [{"value": tipo.value, "label": tipo.value.replace("_", " ").title()} for tipo in TipoFormaPagamento],
        "status": [{"value": status.value, "label": status.value.replace("_", " ").title()} for status in StatusFormaPagamento]
    }
