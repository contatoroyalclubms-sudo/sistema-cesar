"""
Router para gerenciamento de Workspaces (Multi-tenant)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models import Workspace, UsuarioWorkspace, Usuario, Empresa, Evento
from app.schemas_advanced import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse,
    UsuarioWorkspaceBase, UsuarioWorkspaceResponse
)
from app.auth import get_current_user
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])

@router.post("/", response_model=WorkspaceResponse)
async def criar_workspace(
    workspace: WorkspaceCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo workspace"""
    # Verificar se slug já existe
    existing = db.query(Workspace).filter(Workspace.slug == workspace.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug já em uso"
        )
    
    # Criar workspace
    db_workspace = Workspace(
        **workspace.dict(),
        features_habilitadas=json.dumps(["eventos", "checkin", "pdv", "relatorios"]),
        configuracoes=json.dumps({}),
        trial_ate=datetime.utcnow() + timedelta(days=30)  # 30 dias de trial
    )
    db.add(db_workspace)
    db.flush()
    
    # Adicionar usuário como owner
    user_workspace = UsuarioWorkspace(
        usuario_id=current_user.id,
        workspace_id=db_workspace.id,
        papel="owner",
        permissoes=json.dumps(["*"]),  # Todas as permissões
        workspace_padrao=True
    )
    db.add(user_workspace)
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=db_workspace.id,
        acao="create",
        entidade="workspace",
        entidade_id=db_workspace.id,
        dados_novos={"nome": db_workspace.nome, "slug": db_workspace.slug},
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_workspace)
    
    # Converter JSON strings para listas
    db_workspace.features_habilitadas = json.loads(db_workspace.features_habilitadas or "[]")
    
    return db_workspace

@router.get("/", response_model=List[WorkspaceResponse])
async def listar_workspaces(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar workspaces do usuário"""
    user_workspaces = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id
    ).all()
    
    workspace_ids = [uw.workspace_id for uw in user_workspaces]
    workspaces = db.query(Workspace).filter(
        Workspace.id.in_(workspace_ids),
        Workspace.ativo == True
    ).all()
    
    # Converter JSON strings para listas
    for workspace in workspaces:
        workspace.features_habilitadas = json.loads(workspace.features_habilitadas or "[]")
    
    return workspaces

@router.get("/current", response_model=WorkspaceResponse)
async def obter_workspace_atual(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter workspace atual do usuário"""
    # Buscar workspace padrão
    user_workspace = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_padrao == True
    ).first()
    
    if not user_workspace:
        # Se não há workspace padrão, pegar o primeiro
        user_workspace = db.query(UsuarioWorkspace).filter(
            UsuarioWorkspace.usuario_id == current_user.id
        ).first()
    
    if not user_workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não pertence a nenhum workspace"
        )
    
    workspace = db.query(Workspace).filter(
        Workspace.id == user_workspace.workspace_id,
        Workspace.ativo == True
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace não encontrado"
        )
    
    # Converter JSON strings para listas
    workspace.features_habilitadas = json.loads(workspace.features_habilitadas or "[]")
    
    return workspace

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def obter_workspace(
    workspace_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes de um workspace"""
    # Verificar se usuário tem acesso
    user_workspace = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_id == workspace_id
    ).first()
    
    if not user_workspace:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem acesso ao workspace"
        )
    
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace não encontrado"
        )
    
    # Converter JSON strings para listas
    workspace.features_habilitadas = json.loads(workspace.features_habilitadas or "[]")
    
    return workspace

@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def atualizar_workspace(
    workspace_id: int,
    workspace: WorkspaceUpdate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar workspace"""
    # Verificar se usuário tem permissão
    user_workspace = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_id == workspace_id,
        UsuarioWorkspace.papel.in_(["owner", "admin"])
    ).first()
    
    if not user_workspace:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar workspace"
        )
    
    db_workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not db_workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace não encontrado"
        )
    
    # Guardar dados anteriores para audit
    dados_anteriores = {
        "nome": db_workspace.nome,
        "logo_url": db_workspace.logo_url,
        "plano": db_workspace.plano
    }
    
    # Atualizar
    for key, value in workspace.dict(exclude_unset=True).items():
        if key == "configuracoes":
            setattr(db_workspace, key, json.dumps(value))
        else:
            setattr(db_workspace, key, value)
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=workspace_id,
        acao="update",
        entidade="workspace",
        entidade_id=workspace_id,
        dados_anteriores=dados_anteriores,
        dados_novos=workspace.dict(exclude_unset=True),
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_workspace)
    
    # Converter JSON strings para listas
    db_workspace.features_habilitadas = json.loads(db_workspace.features_habilitadas or "[]")
    
    return db_workspace

@router.post("/{workspace_id}/switch")
async def trocar_workspace(
    workspace_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trocar workspace ativo"""
    # Verificar se usuário tem acesso
    user_workspace = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_id == workspace_id
    ).first()
    
    if not user_workspace:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem acesso ao workspace"
        )
    
    # Remover workspace padrão anterior
    db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_padrao == True
    ).update({"workspace_padrao": False})
    
    # Definir novo workspace padrão
    user_workspace.workspace_padrao = True
    user_workspace.ultimo_acesso = datetime.utcnow()
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=workspace_id,
        acao="switch",
        entidade="workspace",
        entidade_id=workspace_id,
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {"message": "Workspace alterado com sucesso", "workspace_id": workspace_id}

@router.get("/{workspace_id}/stats")
async def obter_estatisticas_workspace(
    workspace_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas do workspace"""
    # Verificar se usuário tem acesso
    user_workspace = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_id == workspace_id
    ).first()
    
    if not user_workspace:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem acesso ao workspace"
        )
    
    # Contar recursos
    total_usuarios = db.query(func.count(UsuarioWorkspace.id)).filter(
        UsuarioWorkspace.workspace_id == workspace_id
    ).scalar()
    
    total_empresas = db.query(func.count(Empresa.id)).filter(
        Empresa.workspace_id == workspace_id
    ).scalar()
    
    total_eventos = db.query(func.count(Evento.id)).join(Empresa).filter(
        Empresa.workspace_id == workspace_id
    ).scalar()
    
    # Buscar workspace para limites
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    return {
        "total_usuarios": total_usuarios,
        "limite_usuarios": workspace.limite_usuarios,
        "total_empresas": total_empresas,
        "total_eventos": total_eventos,
        "limite_eventos": workspace.limite_eventos,
        "plano": workspace.plano,
        "trial_ate": workspace.trial_ate,
        "uso_percentual": {
            "usuarios": (total_usuarios / workspace.limite_usuarios * 100) if workspace.limite_usuarios > 0 else 0,
            "eventos": (total_eventos / workspace.limite_eventos * 100) if workspace.limite_eventos > 0 else 0
        }
    }

@router.post("/{workspace_id}/usuarios", response_model=UsuarioWorkspaceResponse)
async def adicionar_usuario_workspace(
    workspace_id: int,
    usuario_workspace: UsuarioWorkspaceBase,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adicionar usuário ao workspace"""
    # Verificar se usuário tem permissão
    user_workspace_admin = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_id == workspace_id,
        UsuarioWorkspace.papel.in_(["owner", "admin"])
    ).first()
    
    if not user_workspace_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para adicionar usuários"
        )
    
    # Verificar limite de usuários
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    total_usuarios = db.query(func.count(UsuarioWorkspace.id)).filter(
        UsuarioWorkspace.workspace_id == workspace_id
    ).scalar()
    
    if total_usuarios >= workspace.limite_usuarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limite de usuários atingido ({workspace.limite_usuarios})"
        )
    
    # Verificar se usuário já está no workspace
    existing = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == usuario_workspace.usuario_id,
        UsuarioWorkspace.workspace_id == workspace_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já pertence ao workspace"
        )
    
    # Adicionar usuário
    db_user_workspace = UsuarioWorkspace(
        **usuario_workspace.dict(),
        permissoes=json.dumps(usuario_workspace.permissoes)
    )
    db.add(db_user_workspace)
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=workspace_id,
        acao="add_user",
        entidade="workspace",
        entidade_id=workspace_id,
        dados_novos={"usuario_id": usuario_workspace.usuario_id, "papel": usuario_workspace.papel},
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_user_workspace)
    
    # Converter JSON string para lista
    db_user_workspace.permissoes = json.loads(db_user_workspace.permissoes or "[]")
    
    return db_user_workspace

@router.delete("/{workspace_id}/usuarios/{usuario_id}")
async def remover_usuario_workspace(
    workspace_id: int,
    usuario_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remover usuário do workspace"""
    # Verificar se usuário tem permissão
    user_workspace_admin = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == current_user.id,
        UsuarioWorkspace.workspace_id == workspace_id,
        UsuarioWorkspace.papel.in_(["owner", "admin"])
    ).first()
    
    if not user_workspace_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para remover usuários"
        )
    
    # Não permitir remover o owner
    user_to_remove = db.query(UsuarioWorkspace).filter(
        UsuarioWorkspace.usuario_id == usuario_id,
        UsuarioWorkspace.workspace_id == workspace_id
    ).first()
    
    if not user_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado no workspace"
        )
    
    if user_to_remove.papel == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover o proprietário do workspace"
        )
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=workspace_id,
        acao="remove_user",
        entidade="workspace",
        entidade_id=workspace_id,
        dados_anteriores={"usuario_id": usuario_id, "papel": user_to_remove.papel},
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Remover
    db.delete(user_to_remove)
    db.commit()
    
    return {"message": "Usuário removido do workspace com sucesso"}