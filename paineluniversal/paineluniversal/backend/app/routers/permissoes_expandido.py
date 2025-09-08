"""
Router para Sistema de Permissões e Roles Expandido
Gestão completa de controle de acesso granular e auditoria
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import json

from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario, Empresa
from ..models_permissoes import (
    Role, Permissao, UsuarioRole, RolePermissao, LogAcesso, SessaoUsuario,
    TipoPermissao, CategoriaPermissao, StatusRole,
    PERMISSOES_SISTEMA, ROLES_SISTEMA
)

router = APIRouter()

# ================================================================================
# SCHEMAS PYDANTIC
# ================================================================================

from pydantic import BaseModel, validator
from enum import Enum

class RoleCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    cor_hexadecimal: str = "#6366f1"
    icone: Optional[str] = None
    nivel_hierarquia: int = 0
    is_admin: bool = False
    acesso_total: bool = False

class RoleUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    cor_hexadecimal: Optional[str] = None
    icone: Optional[str] = None
    nivel_hierarquia: Optional[int] = None
    status: Optional[str] = None

class PermissaoCreate(BaseModel):
    codigo: str
    nome: str
    descricao: Optional[str] = None
    categoria: str
    tipo: str
    nivel_risco: int = 1
    requer_aprovacao: bool = False

class UsuarioRoleCreate(BaseModel):
    usuario_id: int
    role_id: int
    data_fim: Optional[datetime] = None

class RolePermissaoCreate(BaseModel):
    role_id: int
    permissao_ids: List[int]

class LogAcessoCreate(BaseModel):
    acao: str
    recurso: Optional[str] = None
    resultado: str
    endpoint: Optional[str] = None
    metodo_http: Optional[str] = None
    detalhes: Optional[str] = None

# ================================================================================
# CONSTANTES
# ================================================================================

ROLE_NAO_ENCONTRADO = "Role não encontrado"
PERMISSAO_NAO_ENCONTRADA = "Permissão não encontrada"
USUARIO_NAO_ENCONTRADO = "Usuário não encontrado"
ACESSO_NEGADO = "Acesso negado"

# ================================================================================
# INICIALIZAÇÃO DO SISTEMA
# ================================================================================

@router.post("/inicializar", response_model=dict)
async def inicializar_sistema_permissoes_expandido(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Inicializar permissões e roles padrão do sistema expandido"""
    
    try:
        # Criar permissões padrão
        permissoes_criadas = 0
        for perm_data in PERMISSOES_SISTEMA:
            existe = db.query(Permissao).filter(Permissao.codigo == perm_data["codigo"]).first()
            if not existe:
                permissao = Permissao(
                    **perm_data,
                    is_sistema=True,
                    ativo=True
                )
                db.add(permissao)
                permissoes_criadas += 1
        
        db.commit()
        
        # Criar roles padrão para a empresa
        roles_criados = 0
        for role_data in ROLES_SISTEMA:
            existe = db.query(Role).filter(
                Role.empresa_id == current_user.empresa_id,
                Role.nome == role_data["nome"]
            ).first()
            
            if not existe:
                role = Role(
                    empresa_id=current_user.empresa_id,
                    **role_data,
                    criado_por_id=current_user.id
                )
                db.add(role)
                roles_criados += 1
        
        db.commit()
        
        return {
            "message": "Sistema de permissões expandido inicializado com sucesso",
            "permissoes_criadas": permissoes_criadas,
            "roles_criados": roles_criados
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# GESTÃO DE ROLES
# ================================================================================

@router.post("/roles", response_model=dict)
async def criar_role_expandido(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo role/perfil expandido"""
    
    try:
        # Verificar se já existe role com mesmo nome
        existe = db.query(Role).filter(
            Role.empresa_id == current_user.empresa_id,
            Role.nome == role_data.nome
        ).first()
        
        if existe:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um role com o nome '{role_data.nome}'"
            )
        
        role = Role(
            empresa_id=current_user.empresa_id,
            **role_data.model_dump(),
            criado_por_id=current_user.id
        )
        
        db.add(role)
        db.commit()
        db.refresh(role)
        
        # Log da ação
        _criar_log_acesso(
            db, current_user, "roles.criar", f"Role {role.nome}",
            "sucesso", detalhes=f"Criado role ID {role.id}"
        )
        
        return {
            "id": role.id,
            "message": "Role criado com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roles", response_model=List[dict])
async def listar_roles_expandido(
    ativo: Optional[bool] = Query(None),
    is_sistema: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar roles da empresa expandido"""
    
    query = db.query(Role).filter(Role.empresa_id == current_user.empresa_id)
    
    if ativo is not None:
        query = query.filter(Role.status == (StatusRole.ATIVO.value if ativo else StatusRole.INATIVO.value))
    
    if is_sistema is not None:
        query = query.filter(Role.is_sistema == is_sistema)
    
    roles = query.order_by(desc(Role.nivel_hierarquia), Role.nome).all()
    
    # Adicionar contagem de usuários por role
    resultado = []
    for role in roles:
        total_usuarios = db.query(func.count(UsuarioRole.id)).filter(
            UsuarioRole.role_id == role.id,
            UsuarioRole.ativo == True
        ).scalar() or 0
        
        total_permissoes = db.query(func.count(RolePermissao.id)).filter(
            RolePermissao.role_id == role.id,
            RolePermissao.ativo == True,
            RolePermissao.concedido == True
        ).scalar() or 0
        
        resultado.append({
            "role": role,
            "total_usuarios": total_usuarios,
            "total_permissoes": total_permissoes
        })
    
    return resultado

@router.get("/roles/{role_id}", response_model=dict)
async def obter_role_expandido(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter detalhes de um role específico expandido"""
    
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.empresa_id == current_user.empresa_id
    ).first()
    
    if not role:
        raise HTTPException(status_code=404, detail=ROLE_NAO_ENCONTRADO)
    
    # Buscar permissões do role
    permissoes = db.query(Permissao, RolePermissao.concedido).join(
        RolePermissao, Permissao.id == RolePermissao.permissao_id
    ).filter(
        RolePermissao.role_id == role_id,
        RolePermissao.ativo == True
    ).all()
    
    # Buscar usuários do role
    usuarios = db.query(Usuario, UsuarioRole.ativo, UsuarioRole.data_inicio, UsuarioRole.data_fim).join(
        UsuarioRole, Usuario.id == UsuarioRole.usuario_id
    ).filter(
        UsuarioRole.role_id == role_id,
        UsuarioRole.empresa_id == current_user.empresa_id
    ).all()
    
    return {
        "role": role,
        "permissoes": [
            {
                "permissao": p[0],
                "concedido": p[1]
            } for p in permissoes
        ],
        "usuarios": [
            {
                "usuario": u[0],
                "ativo": u[1],
                "data_inicio": u[2],
                "data_fim": u[3]
            } for u in usuarios
        ]
    }

# ================================================================================
# GESTÃO DE PERMISSÕES
# ================================================================================

@router.get("/permissoes", response_model=List[dict])
async def listar_permissoes_expandido(
    categoria: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar permissões disponíveis expandido"""
    
    query = db.query(Permissao)
    
    if categoria:
        query = query.filter(Permissao.categoria == categoria)
    
    if tipo:
        query = query.filter(Permissao.tipo == tipo)
    
    if ativo is not None:
        query = query.filter(Permissao.ativo == ativo)
    
    permissoes = query.order_by(Permissao.categoria, Permissao.nome).all()
    
    # Agrupar por categoria
    categorias = {}
    for permissao in permissoes:
        if permissao.categoria not in categorias:
            categorias[permissao.categoria] = []
        categorias[permissao.categoria].append(permissao)
    
    return [
        {
            "categoria": categoria,
            "permissoes": perms
        } for categoria, perms in categorias.items()
    ]

# ================================================================================
# VERIFICAÇÃO DE PERMISSÕES
# ================================================================================

@router.get("/usuarios/{usuario_id}/permissoes", response_model=List[str])
async def obter_permissoes_usuario_expandido(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter todas as permissões de um usuário expandido"""
    
    # Verificar acesso
    if usuario_id != current_user.id and not _tem_permissao(db, current_user, "usuarios.ler"):
        raise HTTPException(status_code=403, detail=ACESSO_NEGADO)
    
    # Buscar permissões através dos roles
    permissoes = db.query(Permissao.codigo).join(
        RolePermissao, Permissao.id == RolePermissao.permissao_id
    ).join(
        UsuarioRole, RolePermissao.role_id == UsuarioRole.role_id
    ).filter(
        UsuarioRole.usuario_id == usuario_id,
        UsuarioRole.empresa_id == current_user.empresa_id,
        UsuarioRole.ativo == True,
        RolePermissao.ativo == True,
        RolePermissao.concedido == True,
        Permissao.ativo == True
    ).distinct().all()
    
    return [p.codigo for p in permissoes]

@router.post("/verificar-permissao", response_model=dict)
async def verificar_permissao_expandido(
    acao: str,
    usuario_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Verificar se usuário tem permissão para executar ação expandido"""
    
    usuario_verificar = current_user if not usuario_id else db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario_verificar:
        raise HTTPException(status_code=404, detail=USUARIO_NAO_ENCONTRADO)
    
    tem_permissao = _tem_permissao(db, usuario_verificar, acao)
    
    return {
        "tem_permissao": tem_permissao,
        "acao": acao,
        "usuario_id": usuario_verificar.id
    }

# ================================================================================
# DASHBOARD DE PERMISSÕES
# ================================================================================

@router.get("/dashboard", response_model=dict)
async def dashboard_permissoes_expandido(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Dashboard do sistema de permissões expandido"""
    
    # Estatísticas básicas
    total_usuarios = db.query(func.count(Usuario.id)).filter(
        Usuario.empresa_id == current_user.empresa_id
    ).scalar() or 0
    
    total_roles = db.query(func.count(Role.id)).filter(
        Role.empresa_id == current_user.empresa_id
    ).scalar() or 0
    
    total_permissoes = db.query(func.count(Permissao.id)).filter(
        Permissao.ativo == True
    ).scalar() or 0
    
    # Distribuição de usuários por role
    distribuicao_roles = db.query(
        Role.nome,
        Role.cor_hexadecimal,
        func.count(UsuarioRole.id).label('total_usuarios')
    ).outerjoin(UsuarioRole).filter(
        Role.empresa_id == current_user.empresa_id,
        UsuarioRole.ativo == True
    ).group_by(Role.id, Role.nome, Role.cor_hexadecimal).all()
    
    # Logs recentes
    logs_recentes = db.query(LogAcesso).filter(
        LogAcesso.empresa_id == current_user.empresa_id,
        LogAcesso.criado_em >= datetime.now(timezone.utc) - timedelta(hours=24)
    ).order_by(desc(LogAcesso.criado_em)).limit(10).all()
    
    # Sessões ativas
    sessoes_ativas = db.query(func.count(SessaoUsuario.id)).filter(
        SessaoUsuario.empresa_id == current_user.empresa_id,
        SessaoUsuario.ativa == True
    ).scalar() or 0
    
    return {
        "total_usuarios": total_usuarios,
        "total_roles": total_roles,
        "total_permissoes": total_permissoes,
        "sessoes_ativas": sessoes_ativas,
        "distribuicao_roles": [
            {
                "nome": d.nome,
                "cor": d.cor_hexadecimal,
                "total_usuarios": d.total_usuarios
            } for d in distribuicao_roles
        ],
        "logs_recentes": [{"log": log} for log in logs_recentes]
    }

# ================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================

def _tem_permissao(db: Session, usuario: Usuario, acao: str) -> bool:
    """Verificar se usuário tem permissão para executar ação"""
    
    # Verificar se usuário tem role com acesso total
    role_acesso_total = db.query(Role).join(
        UsuarioRole, Role.id == UsuarioRole.role_id
    ).filter(
        UsuarioRole.usuario_id == usuario.id,
        UsuarioRole.empresa_id == usuario.empresa_id,
        UsuarioRole.ativo == True,
        Role.acesso_total == True,
        Role.status == StatusRole.ATIVO.value
    ).first()
    
    if role_acesso_total:
        return True
    
    # Verificar permissão específica
    permissao = db.query(Permissao).join(
        RolePermissao, Permissao.id == RolePermissao.permissao_id
    ).join(
        UsuarioRole, RolePermissao.role_id == UsuarioRole.role_id
    ).filter(
        UsuarioRole.usuario_id == usuario.id,
        UsuarioRole.empresa_id == usuario.empresa_id,
        UsuarioRole.ativo == True,
        RolePermissao.ativo == True,
        RolePermissao.concedido == True,
        Permissao.codigo == acao,
        Permissao.ativo == True
    ).first()
    
    return permissao is not None

def _criar_log_acesso(
    db: Session, 
    usuario: Usuario, 
    acao: str, 
    recurso: str, 
    resultado: str,
    detalhes: Optional[str] = None,
    endpoint: Optional[str] = None,
    metodo_http: Optional[str] = None
):
    """Criar log de acesso para auditoria"""
    
    try:
        log = LogAcesso(
            usuario_id=usuario.id,
            empresa_id=usuario.empresa_id,
            acao=acao,
            recurso=recurso,
            resultado=resultado,
            detalhes=detalhes,
            endpoint=endpoint,
            metodo_http=metodo_http
        )
        db.add(log)
        # Não fazer commit aqui, deixar para a transação principal
        
    except Exception as e:
        # Log de auditoria não deve quebrar a operação principal
        print(f"Erro ao criar log de acesso: {e}")

# ================================================================================
# DECORADOR PARA VERIFICAÇÃO DE PERMISSÕES
# ================================================================================

def requer_permissao(acao: str):
    """Decorador para verificar permissões em endpoints"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extrair usuário atual e db dos kwargs
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(status_code=401, detail="Usuário não autenticado")
            
            if not _tem_permissao(db, current_user, acao):
                _criar_log_acesso(
                    db, current_user, acao, "N/A", "negado",
                    detalhes=f"Tentativa de acesso negada para ação: {acao}"
                )
                raise HTTPException(status_code=403, detail=ACESSO_NEGADO)
            
            # Executar função original
            resultado = func(*args, **kwargs)
            
            # Log de sucesso
            _criar_log_acesso(
                db, current_user, acao, "N/A", "sucesso",
                detalhes=f"Ação executada com sucesso: {acao}"
            )
            
            return resultado
        
        return wrapper
    return decorator
