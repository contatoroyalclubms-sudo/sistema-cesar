"""
Router para Gestão de Equipe - Funcionalidades completas do MEEP
Colaboradores, Cargos, Permissões
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user, get_password_hash
from ..models import Usuario, Cargo, Permissao, TipoUsuario, usuario_cargo, cargo_permissao
from ..schemas_meep_complete import UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter(
    prefix="/api/equipe",
    tags=["Equipe"]
)

# ==================== COLABORADORES ====================

@router.get("/colaboradores", response_model=List[UsuarioResponse])
async def listar_colaboradores(
    busca: Optional[str] = Query(None, description="Buscar por nome, cargo ou email"),
    cargo_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista colaboradores da empresa
    Replica funcionalidade: MEEP Equipe > Colaboradores
    """
    
    query = db.query(Usuario)
    
    # Filtrar por empresa
    if current_user.empresa_id:
        query = query.filter(Usuario.empresa_id == current_user.empresa_id)
    
    # Excluir clientes
    query = query.filter(Usuario.tipo != TipoUsuario.CLIENTE)
    
    # Busca
    if busca:
        query = query.filter(
            or_(
                Usuario.nome.ilike(f"%{busca}%"),
                Usuario.email.ilike(f"%{busca}%")
            )
        )
    
    # Filtro por cargo
    if cargo_id:
        query = query.join(usuario_cargo).filter(usuario_cargo.c.cargo_id == cargo_id)
    
    # Filtro por status
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    colaboradores = query.all()
    
    # Adicionar informações de cargo
    for colaborador in colaboradores:
        colaborador.cargos = db.query(Cargo).join(usuario_cargo).filter(
            usuario_cargo.c.usuario_id == colaborador.id
        ).all()
    
    return colaboradores

@router.post("/colaboradores", response_model=UsuarioResponse)
async def criar_colaborador(
    colaborador: UsuarioCreate,
    cargo_ids: List[int] = [],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo colaborador
    """
    
    # Verificar se email ou CPF já existe
    existe = db.query(Usuario).filter(
        or_(
            Usuario.email == colaborador.email,
            Usuario.cpf == colaborador.cpf
        )
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ou CPF já cadastrado"
        )
    
    # Criar usuário
    db_colaborador = Usuario(
        nome=colaborador.nome,
        email=colaborador.email,
        cpf=colaborador.cpf,
        telefone=colaborador.telefone,
        senha_hash=get_password_hash(colaborador.senha),
        tipo=colaborador.tipo or TipoUsuario.COLABORADOR,
        empresa_id=colaborador.empresa_id or current_user.empresa_id,
        avatar_url=colaborador.avatar_url,
        ativo=True
    )
    
    db.add(db_colaborador)
    db.commit()
    db.refresh(db_colaborador)
    
    # Associar cargos
    for cargo_id in cargo_ids:
        cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
        if cargo:
            db_colaborador.cargos.append(cargo)
    
    db.commit()
    db.refresh(db_colaborador)
    
    return db_colaborador

@router.put("/colaboradores/{colaborador_id}", response_model=UsuarioResponse)
async def atualizar_colaborador(
    colaborador_id: int,
    update_data: UsuarioUpdate,
    cargo_ids: Optional[List[int]] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados do colaborador
    """
    
    colaborador = db.query(Usuario).filter(Usuario.id == colaborador_id).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    # Atualizar dados
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(colaborador, field, value)
    
    # Atualizar cargos se fornecido
    if cargo_ids is not None:
        # Limpar cargos atuais
        colaborador.cargos = []
        
        # Adicionar novos cargos
        for cargo_id in cargo_ids:
            cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
            if cargo:
                colaborador.cargos.append(cargo)
    
    db.commit()
    db.refresh(colaborador)
    
    return colaborador

@router.delete("/colaboradores/{colaborador_id}")
async def deletar_colaborador(
    colaborador_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Desativa colaborador (soft delete)
    """
    
    colaborador = db.query(Usuario).filter(Usuario.id == colaborador_id).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    colaborador.ativo = False
    db.commit()
    
    return {"message": "Colaborador desativado com sucesso"}

# ==================== CARGOS ====================

@router.get("/cargos")
async def listar_cargos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista cargos disponíveis
    Replica funcionalidade: MEEP Equipe > Cargos
    """
    
    cargos = db.query(Cargo).all()
    
    resultado = []
    for cargo in cargos:
        # Contar permissões
        qtd_permissoes = db.query(func.count(cargo_permissao.c.permissao_id)).filter(
            cargo_permissao.c.cargo_id == cargo.id
        ).scalar() or 0
        
        # Contar colaboradores
        qtd_colaboradores = db.query(func.count(usuario_cargo.c.usuario_id)).filter(
            usuario_cargo.c.cargo_id == cargo.id
        ).scalar() or 0
        
        resultado.append({
            "id": cargo.id,
            "nome": cargo.nome,
            "descricao": cargo.descricao,
            "nivel": cargo.nivel,
            "permissoes_count": qtd_permissoes,
            "colaboradores_count": qtd_colaboradores,
            "criado_em": cargo.criado_em.isoformat() if cargo.criado_em else None
        })
    
    return resultado

@router.post("/cargos")
async def criar_cargo(
    nome: str,
    descricao: Optional[str] = None,
    nivel: int = 1,
    permissao_ids: List[int] = [],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo cargo
    """
    
    # Verificar se já existe
    existe = db.query(Cargo).filter(Cargo.nome == nome).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cargo já existe"
        )
    
    # Criar cargo
    db_cargo = Cargo(
        nome=nome,
        descricao=descricao,
        nivel=nivel
    )
    
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    
    # Associar permissões
    for permissao_id in permissao_ids:
        permissao = db.query(Permissao).filter(Permissao.id == permissao_id).first()
        if permissao:
            db_cargo.permissoes.append(permissao)
    
    db.commit()
    
    return {
        "id": db_cargo.id,
        "nome": db_cargo.nome,
        "descricao": db_cargo.descricao,
        "nivel": db_cargo.nivel,
        "permissoes_count": len(permissao_ids)
    }

@router.put("/cargos/{cargo_id}")
async def atualizar_cargo(
    cargo_id: int,
    nome: Optional[str] = None,
    descricao: Optional[str] = None,
    nivel: Optional[int] = None,
    permissao_ids: Optional[List[int]] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza cargo e suas permissões
    """
    
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    # Atualizar dados básicos
    if nome:
        cargo.nome = nome
    if descricao is not None:
        cargo.descricao = descricao
    if nivel:
        cargo.nivel = nivel
    
    # Atualizar permissões
    if permissao_ids is not None:
        # Limpar permissões atuais
        cargo.permissoes = []
        
        # Adicionar novas permissões
        for permissao_id in permissao_ids:
            permissao = db.query(Permissao).filter(Permissao.id == permissao_id).first()
            if permissao:
                cargo.permissoes.append(permissao)
    
    db.commit()
    db.refresh(cargo)
    
    return {"message": "Cargo atualizado com sucesso"}

@router.delete("/cargos/{cargo_id}")
async def deletar_cargo(
    cargo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta cargo
    """
    
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    # Verificar se há colaboradores com este cargo
    colaboradores = db.query(func.count(usuario_cargo.c.usuario_id)).filter(
        usuario_cargo.c.cargo_id == cargo_id
    ).scalar() or 0
    
    if colaboradores > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível deletar cargo com {colaboradores} colaborador(es) associado(s)"
        )
    
    db.delete(cargo)
    db.commit()
    
    return {"message": "Cargo deletado com sucesso"}

# ==================== PERMISSÕES ====================

@router.get("/permissoes")
async def listar_permissoes(
    modulo: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as permissões disponíveis no sistema
    """
    
    query = db.query(Permissao)
    
    if modulo:
        query = query.filter(Permissao.modulo == modulo)
    
    permissoes = query.all()
    
    # Agrupar por módulo
    resultado = {}
    for permissao in permissoes:
        if permissao.modulo not in resultado:
            resultado[permissao.modulo] = []
        
        resultado[permissao.modulo].append({
            "id": permissao.id,
            "nome": permissao.nome,
            "descricao": permissao.descricao,
            "acao": permissao.acao
        })
    
    return resultado

@router.post("/permissoes/seed")
async def criar_permissoes_padrao(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria permissões padrão do sistema (seed inicial)
    Baseado nas 132 permissões do ADMIN no MEEP
    """
    
    permissoes_padrao = [
        # Dashboard
        ("dashboard.view", "Visualizar Dashboard", "Dashboard", "view"),
        ("dashboard.export", "Exportar Dashboard", "Dashboard", "export"),
        
        # Clientes
        ("clientes.view", "Visualizar Clientes", "Clientes", "view"),
        ("clientes.create", "Criar Clientes", "Clientes", "create"),
        ("clientes.edit", "Editar Clientes", "Clientes", "edit"),
        ("clientes.delete", "Deletar Clientes", "Clientes", "delete"),
        ("clientes.export", "Exportar Clientes", "Clientes", "export"),
        
        # Comandas
        ("comandas.view", "Visualizar Comandas", "Comandas", "view"),
        ("comandas.create", "Criar Comandas", "Comandas", "create"),
        ("comandas.edit", "Editar Comandas", "Comandas", "edit"),
        ("comandas.close", "Fechar Comandas", "Comandas", "close"),
        
        # Cashless
        ("cashless.view", "Visualizar Cashless", "Cashless", "view"),
        ("cashless.recharge", "Recarregar Cashless", "Cashless", "recharge"),
        ("cashless.block", "Bloquear Cartões", "Cashless", "block"),
        
        # Equipe
        ("equipe.view", "Visualizar Equipe", "Equipe", "view"),
        ("equipe.create", "Criar Colaborador", "Equipe", "create"),
        ("equipe.edit", "Editar Colaborador", "Equipe", "edit"),
        ("equipe.delete", "Deletar Colaborador", "Equipe", "delete"),
        
        # Cargos
        ("cargos.view", "Visualizar Cargos", "Cargos", "view"),
        ("cargos.create", "Criar Cargos", "Cargos", "create"),
        ("cargos.edit", "Editar Cargos", "Cargos", "edit"),
        ("cargos.delete", "Deletar Cargos", "Cargos", "delete"),
        
        # Cardápio
        ("cardapio.view", "Visualizar Cardápio", "Cardápio", "view"),
        ("cardapio.create", "Criar Cardápio", "Cardápio", "create"),
        ("cardapio.edit", "Editar Cardápio", "Cardápio", "edit"),
        ("cardapio.delete", "Deletar Cardápio", "Cardápio", "delete"),
        
        # Produtos
        ("produtos.view", "Visualizar Produtos", "Produtos", "view"),
        ("produtos.create", "Criar Produtos", "Produtos", "create"),
        ("produtos.edit", "Editar Produtos", "Produtos", "edit"),
        ("produtos.delete", "Deletar Produtos", "Produtos", "delete"),
        
        # PDV
        ("pdv.view", "Visualizar PDV", "PDV", "view"),
        ("pdv.sell", "Realizar Vendas", "PDV", "sell"),
        ("pdv.cancel", "Cancelar Vendas", "PDV", "cancel"),
        ("pdv.discount", "Aplicar Descontos", "PDV", "discount"),
        
        # Relatórios
        ("relatorios.view", "Visualizar Relatórios", "Relatórios", "view"),
        ("relatorios.export", "Exportar Relatórios", "Relatórios", "export"),
        
        # Financeiro
        ("financeiro.view", "Visualizar Financeiro", "Financeiro", "view"),
        ("financeiro.manage", "Gerenciar Financeiro", "Financeiro", "manage"),
        
        # Estoque
        ("estoque.view", "Visualizar Estoque", "Estoque", "view"),
        ("estoque.manage", "Gerenciar Estoque", "Estoque", "manage"),
        
        # Marketing
        ("marketing.view", "Visualizar Marketing", "Marketing", "view"),
        ("marketing.create", "Criar Campanhas", "Marketing", "create"),
        
        # Configurações
        ("config.view", "Visualizar Configurações", "Configurações", "view"),
        ("config.edit", "Editar Configurações", "Configurações", "edit"),
    ]
    
    criadas = 0
    for nome, descricao, modulo, acao in permissoes_padrao:
        # Verificar se já existe
        existe = db.query(Permissao).filter(Permissao.nome == nome).first()
        if not existe:
            permissao = Permissao(
                nome=nome,
                descricao=descricao,
                modulo=modulo,
                acao=acao
            )
            db.add(permissao)
            criadas += 1
    
    db.commit()
    
    return {
        "message": f"{criadas} permissões criadas com sucesso",
        "total": criadas
    }

@router.get("/cargos/{cargo_id}/permissoes")
async def obter_permissoes_cargo(
    cargo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém permissões de um cargo específico
    """
    
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    permissoes = db.query(Permissao).join(cargo_permissao).filter(
        cargo_permissao.c.cargo_id == cargo_id
    ).all()
    
    return {
        "cargo": cargo.nome,
        "total_permissoes": len(permissoes),
        "permissoes": [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "modulo": p.modulo,
                "acao": p.acao
            }
            for p in permissoes
        ]
    }

@router.get("/colaboradores/{colaborador_id}/permissoes")
async def obter_permissoes_colaborador(
    colaborador_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém todas as permissões de um colaborador (através de seus cargos)
    """
    
    colaborador = db.query(Usuario).filter(Usuario.id == colaborador_id).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    # Obter todos os cargos do colaborador
    cargos = db.query(Cargo).join(usuario_cargo).filter(
        usuario_cargo.c.usuario_id == colaborador_id
    ).all()
    
    # Obter todas as permissões únicas
    permissoes_set = set()
    for cargo in cargos:
        perms = db.query(Permissao).join(cargo_permissao).filter(
            cargo_permissao.c.cargo_id == cargo.id
        ).all()
        permissoes_set.update(perms)
    
    return {
        "colaborador": colaborador.nome,
        "cargos": [c.nome for c in cargos],
        "total_permissoes": len(permissoes_set),
        "permissoes": [
            {
                "id": p.id,
                "nome": p.nome,
                "modulo": p.modulo,
                "acao": p.acao
            }
            for p in permissoes_set
        ]
    }