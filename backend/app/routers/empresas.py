from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Empresa, Usuario
from ..schemas import Empresa as EmpresaSchema, EmpresaCreate, EmpresaUpdate
from ..auth_functions import obter_usuario_atual, verificar_permissao_admin

router = APIRouter()

@router.post("/", response_model=EmpresaSchema)
async def criar_empresa(
    empresa: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Criar nova empresa (apenas admins)"""
    
    # Verificar se CNPJ já existe
    empresa_existente = db.query(Empresa).filter(Empresa.cnpj == empresa.cnpj).first()
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )
    
    # Verificar se email já existe
    if empresa.email:
        email_existente = db.query(Empresa).filter(Empresa.email == empresa.email).first()
        if email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
    
    db_empresa = Empresa(**empresa.model_dump())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    
    return db_empresa

@router.get("/", response_model=List[EmpresaSchema])
async def listar_empresas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ativa: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Listar empresas com filtros (apenas admins)"""
    query = db.query(Empresa)
    
    # Aplicar filtros
    if ativa is not None:
        query = query.filter(Empresa.ativa == ativa)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Empresa.razao_social.ilike(search_term)) |
            (Empresa.nome_fantasia.ilike(search_term)) |
            (Empresa.cnpj.ilike(search_term)) |
            (Empresa.email.ilike(search_term))
        )
    
    empresas = query.offset(skip).limit(limit).all()
    return empresas

@router.get("/{empresa_id}", response_model=EmpresaSchema)
async def obter_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados de uma empresa"""
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    return empresa

@router.put("/{empresa_id}", response_model=EmpresaSchema)
async def atualizar_empresa(
    empresa_id: int,
    empresa_update: EmpresaUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Atualizar dados da empresa (apenas admins)"""
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Verificar CNPJ único se fornecido
    if empresa_update.cnpj and empresa_update.cnpj != empresa.cnpj:
        empresa_existente = db.query(Empresa).filter(Empresa.cnpj == empresa_update.cnpj).first()
        if empresa_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )
    
    # Verificar email único se fornecido
    if empresa_update.email and empresa_update.email != empresa.email:
        email_existente = db.query(Empresa).filter(Empresa.email == empresa_update.email).first()
        if email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
    
    # Atualizar apenas campos fornecidos
    update_data = empresa_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(empresa, field, value)
    
    db.commit()
    db.refresh(empresa)
    
    return empresa

@router.delete("/{empresa_id}")
async def desativar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Desativar empresa (soft delete) - apenas admins"""
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    empresa.ativa = False
    db.commit()
    
    return {"mensagem": "Empresa desativada com sucesso"}

@router.patch("/{empresa_id}/ativar")
async def ativar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Reativar empresa - apenas admins"""
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    empresa.ativa = True
    db.commit()
    
    return {"mensagem": "Empresa ativada com sucesso"}
