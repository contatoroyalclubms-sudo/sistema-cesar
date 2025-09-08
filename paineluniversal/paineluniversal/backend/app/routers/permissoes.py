from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from ..database import get_db
from ..models import Usuario, Cargo, Permissao, PermissaoCargo, Colaborador
from ..schemas_extended import (
    PermissaoCreate, PermissaoResponse,
    CargoCreate, CargoUpdate, CargoResponse,
    PermissaoCargoCreate, PermissaoCargoResponse,
    PermissaoCheckRequest, PermissaoCheckResponse,
    PermissaoBulkAssignRequest
)
from ..auth_functions import get_current_user

router = APIRouter(prefix="/api/permissoes", tags=["permissoes"])

# Lista completa de módulos e suas ações (132+ permissões)
MODULOS_SISTEMA = {
    "dashboard": {
        "nome": "Dashboard",
        "acoes": ["visualizar", "exportar", "personalizar"],
        "descricao": "Painel principal e métricas"
    },
    "eventos": {
        "nome": "Eventos",
        "acoes": ["visualizar", "criar", "editar", "deletar", "publicar", "arquivar", "clonar"],
        "descricao": "Gestão de eventos"
    },
    "vendas": {
        "nome": "Vendas",
        "acoes": ["visualizar", "criar", "editar", "cancelar", "estornar", "aprovar", "relatorio"],
        "descricao": "Vendas e transações"
    },
    "checkin": {
        "nome": "Check-in",
        "acoes": ["visualizar", "realizar", "validar", "cancelar", "relatorio", "exportar"],
        "descricao": "Controle de entrada"
    },
    "pdv": {
        "nome": "PDV",
        "acoes": ["visualizar", "vender", "cancelar", "desconto", "fechar_caixa", "sangria", "suprimento"],
        "descricao": "Ponto de venda"
    },
    "comandas": {
        "nome": "Comandas",
        "acoes": ["visualizar", "criar", "recarregar", "bloquear", "transferir", "fechar", "relatorio"],
        "descricao": "Gestão de comandas"
    },
    "produtos": {
        "nome": "Produtos",
        "acoes": ["visualizar", "criar", "editar", "deletar", "importar", "exportar", "precificar"],
        "descricao": "Catálogo de produtos"
    },
    "estoque": {
        "nome": "Estoque",
        "acoes": ["visualizar", "entrada", "saida", "ajustar", "transferir", "inventario", "relatorio"],
        "descricao": "Controle de estoque"
    },
    "financeiro": {
        "nome": "Financeiro",
        "acoes": ["visualizar", "lancar", "aprovar", "relatorio", "exportar", "conciliar", "fechar_periodo"],
        "descricao": "Gestão financeira"
    },
    "clientes": {
        "nome": "Clientes",
        "acoes": ["visualizar", "criar", "editar", "deletar", "importar", "exportar", "comunicar"],
        "descricao": "Base de clientes"
    },
    "promoters": {
        "nome": "Promoters",
        "acoes": ["visualizar", "criar", "editar", "deletar", "comissao", "meta", "relatorio"],
        "descricao": "Gestão de promoters"
    },
    "usuarios": {
        "nome": "Usuários",
        "acoes": ["visualizar", "criar", "editar", "deletar", "resetar_senha", "bloquear", "permissoes"],
        "descricao": "Controle de usuários"
    },
    "relatorios": {
        "nome": "Relatórios",
        "acoes": ["visualizar", "gerar", "exportar", "agendar", "personalizar", "compartilhar"],
        "descricao": "Central de relatórios"
    },
    "configuracoes": {
        "nome": "Configurações",
        "acoes": ["visualizar", "editar", "backup", "restaurar", "logs", "integrações"],
        "descricao": "Configurações do sistema"
    },
    "listas": {
        "nome": "Listas",
        "acoes": ["visualizar", "criar", "editar", "deletar", "aprovar", "publicar", "relatorio"],
        "descricao": "Listas de convidados"
    },
    "ranking": {
        "nome": "Ranking",
        "acoes": ["visualizar", "editar", "resetar", "premiar", "exportar"],
        "descricao": "Sistema de gamificação"
    },
    "cardapio": {
        "nome": "Cardápio",
        "acoes": ["visualizar", "criar", "editar", "deletar", "publicar", "qrcode", "personalizar"],
        "descricao": "Cardápios digitais"
    },
    "mesas": {
        "nome": "Mesas",
        "acoes": ["visualizar", "criar", "reservar", "liberar", "transferir", "juntar", "mapa"],
        "descricao": "Gestão de mesas"
    },
    "kds": {
        "nome": "KDS",
        "acoes": ["visualizar", "preparar", "finalizar", "cancelar", "priorizar", "relatorio"],
        "descricao": "Kitchen Display System"
    },
    "cashless": {
        "nome": "Cashless",
        "acoes": ["visualizar", "ativar", "recarregar", "bloquear", "transferir", "relatorio"],
        "descricao": "Sistema cashless"
    },
    "fidelidade": {
        "nome": "Fidelidade",
        "acoes": ["visualizar", "criar", "editar", "creditar", "resgatar", "relatorio"],
        "descricao": "Programa de fidelidade"
    },
    "pesquisa": {
        "nome": "Pesquisas",
        "acoes": ["visualizar", "criar", "editar", "coletar", "analisar", "exportar"],
        "descricao": "Pesquisas de satisfação"
    },
    "automacao": {
        "nome": "Automação",
        "acoes": ["visualizar", "criar", "editar", "executar", "pausar", "logs"],
        "descricao": "Fluxos automatizados"
    },
    "bi": {
        "nome": "Business Intelligence",
        "acoes": ["visualizar", "criar", "editar", "exportar", "compartilhar", "agendar"],
        "descricao": "Dashboards e analytics"
    },
    "integracoes": {
        "nome": "Integrações",
        "acoes": ["visualizar", "configurar", "conectar", "desconectar", "sincronizar", "logs"],
        "descricao": "Integrações externas"
    },
    "app": {
        "nome": "Aplicativo",
        "acoes": ["visualizar", "configurar", "publicar", "notificar", "analytics"],
        "descricao": "App mobile"
    },
    "tickets": {
        "nome": "Tickets",
        "acoes": ["visualizar", "criar", "editar", "vender", "validar", "transferir", "cancelar"],
        "descricao": "Ingressos e tickets"
    },
    "colaboradores": {
        "nome": "Colaboradores",
        "acoes": ["visualizar", "criar", "editar", "escalar", "avaliar", "relatorio"],
        "descricao": "Gestão de equipe"
    },
    "impressoras": {
        "nome": "Impressoras",
        "acoes": ["visualizar", "configurar", "testar", "monitorar"],
        "descricao": "Impressoras térmicas"
    },
    "whatsapp": {
        "nome": "WhatsApp",
        "acoes": ["visualizar", "enviar", "campanhas", "automacao", "relatorio"],
        "descricao": "Comunicação WhatsApp"
    },
    "cupons": {
        "nome": "Cupons",
        "acoes": ["visualizar", "criar", "editar", "ativar", "desativar", "relatorio"],
        "descricao": "Cupons de desconto"
    },
    "meep": {
        "nome": "Analytics Avançado",
        "acoes": ["visualizar", "analisar", "prever", "exportar", "configurar"],
        "descricao": "Analytics e IA"
    }
}

@router.post("/init-permissions")
def initialize_permissions(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Inicializar todas as permissões do sistema (132+)"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    created_count = 0
    existing_count = 0
    
    for modulo_key, modulo_info in MODULOS_SISTEMA.items():
        for acao in modulo_info["acoes"]:
            # Verificar se já existe
            existing = db.query(Permissao).filter(
                and_(
                    Permissao.modulo == modulo_key,
                    Permissao.acao == acao
                )
            ).first()
            
            if not existing:
                permissao = Permissao(
                    modulo=modulo_key,
                    acao=acao,
                    descricao=f"{acao.capitalize()} em {modulo_info['nome']}"
                )
                db.add(permissao)
                created_count += 1
            else:
                existing_count += 1
    
    db.commit()
    
    total_permissions = created_count + existing_count
    return {
        "message": "Permissões inicializadas",
        "criadas": created_count,
        "existentes": existing_count,
        "total": total_permissions
    }

# Cargos
@router.post("/cargos", response_model=CargoResponse)
def create_cargo(
    cargo: CargoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo cargo"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    # Verificar duplicação
    existing = db.query(Cargo).filter_by(nome=cargo.nome).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cargo já existe")
    
    db_cargo = Cargo(**cargo.dict())
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

@router.get("/cargos", response_model=List[CargoResponse])
def list_cargos(
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar cargos"""
    query = db.query(Cargo)
    
    if ativo is not None:
        query = query.filter_by(ativo=ativo)
    
    return query.order_by(Cargo.nivel_hierarquia, Cargo.nome).all()

@router.get("/cargos/{cargo_id}", response_model=CargoResponse)
def get_cargo(
    cargo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter cargo com suas permissões"""
    cargo = db.query(Cargo).filter_by(id=cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    # Carregar permissões
    cargo.total_permissoes = db.query(PermissaoCargo).filter_by(cargo_id=cargo_id).count()
    
    return cargo

@router.put("/cargos/{cargo_id}", response_model=CargoResponse)
def update_cargo(
    cargo_id: int,
    cargo: CargoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar cargo"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    db_cargo = db.query(Cargo).filter_by(id=cargo_id).first()
    if not db_cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    for key, value in cargo.dict(exclude_unset=True).items():
        setattr(db_cargo, key, value)
    
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

@router.delete("/cargos/{cargo_id}")
def delete_cargo(
    cargo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Excluir cargo"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    db_cargo = db.query(Cargo).filter_by(id=cargo_id).first()
    if not db_cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    # Verificar se há colaboradores com este cargo
    colaboradores_count = db.query(Colaborador).filter_by(cargo_id=cargo_id).count()
    if colaboradores_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cargo possui {colaboradores_count} colaboradores vinculados"
        )
    
    # Remover permissões do cargo
    db.query(PermissaoCargo).filter_by(cargo_id=cargo_id).delete()
    
    db.delete(db_cargo)
    db.commit()
    return {"message": "Cargo excluído com sucesso"}

# Permissões
@router.get("/permissoes", response_model=List[PermissaoResponse])
def list_permissoes(
    modulo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas as permissões disponíveis"""
    query = db.query(Permissao)
    
    if modulo:
        query = query.filter_by(modulo=modulo)
    
    return query.order_by(Permissao.modulo, Permissao.acao).all()

@router.get("/permissoes/modulos")
def list_modulos(
    current_user: Usuario = Depends(get_current_user)
):
    """Listar módulos e suas ações disponíveis"""
    return MODULOS_SISTEMA

@router.get("/cargos/{cargo_id}/permissoes", response_model=List[PermissaoResponse])
def list_cargo_permissoes(
    cargo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar permissões de um cargo"""
    permissoes = db.query(Permissao).join(PermissaoCargo).filter(
        PermissaoCargo.cargo_id == cargo_id
    ).all()
    
    return permissoes

@router.post("/cargos/{cargo_id}/permissoes")
def assign_permissao_cargo(
    cargo_id: int,
    permissao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atribuir permissão a um cargo"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    # Verificar se já existe
    existing = db.query(PermissaoCargo).filter(
        and_(
            PermissaoCargo.cargo_id == cargo_id,
            PermissaoCargo.permissao_id == permissao_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Permissão já atribuída")
    
    permissao_cargo = PermissaoCargo(
        cargo_id=cargo_id,
        permissao_id=permissao_id
    )
    db.add(permissao_cargo)
    db.commit()
    
    return {"message": "Permissão atribuída com sucesso"}

@router.delete("/cargos/{cargo_id}/permissoes/{permissao_id}")
def remove_permissao_cargo(
    cargo_id: int,
    permissao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remover permissão de um cargo"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    result = db.query(PermissaoCargo).filter(
        and_(
            PermissaoCargo.cargo_id == cargo_id,
            PermissaoCargo.permissao_id == permissao_id
        )
    ).delete()
    
    if result == 0:
        raise HTTPException(status_code=404, detail="Permissão não encontrada")
    
    db.commit()
    return {"message": "Permissão removida com sucesso"}

@router.post("/cargos/{cargo_id}/permissoes/bulk")
def bulk_assign_permissoes(
    cargo_id: int,
    request: PermissaoBulkAssignRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atribuir múltiplas permissões a um cargo"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    # Remover permissões existentes se solicitado
    if request.replace_existing:
        db.query(PermissaoCargo).filter_by(cargo_id=cargo_id).delete()
    
    added_count = 0
    for permissao_id in request.permissao_ids:
        # Verificar se já existe
        existing = db.query(PermissaoCargo).filter(
            and_(
                PermissaoCargo.cargo_id == cargo_id,
                PermissaoCargo.permissao_id == permissao_id
            )
        ).first()
        
        if not existing:
            permissao_cargo = PermissaoCargo(
                cargo_id=cargo_id,
                permissao_id=permissao_id
            )
            db.add(permissao_cargo)
            added_count += 1
    
    db.commit()
    
    return {
        "message": "Permissões atribuídas com sucesso",
        "adicionadas": added_count,
        "total": len(request.permissao_ids)
    }

@router.post("/check-permission")
def check_user_permission(
    request: PermissaoCheckRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Verificar se usuário tem uma permissão específica"""
    # Admins têm todas as permissões
    if current_user.tipo == "admin":
        return PermissaoCheckResponse(
            has_permission=True,
            reason="Usuário é administrador"
        )
    
    # Buscar colaborador e cargo
    colaborador = db.query(Colaborador).filter_by(usuario_id=current_user.id).first()
    if not colaborador:
        return PermissaoCheckResponse(
            has_permission=False,
            reason="Usuário não é colaborador"
        )
    
    # Verificar permissão através do cargo
    permissao = db.query(Permissao).filter(
        and_(
            Permissao.modulo == request.modulo,
            Permissao.acao == request.acao
        )
    ).first()
    
    if not permissao:
        return PermissaoCheckResponse(
            has_permission=False,
            reason="Permissão não existe no sistema"
        )
    
    # Verificar se o cargo tem a permissão
    has_perm = db.query(PermissaoCargo).filter(
        and_(
            PermissaoCargo.cargo_id == colaborador.cargo_id,
            PermissaoCargo.permissao_id == permissao.id
        )
    ).first() is not None
    
    return PermissaoCheckResponse(
        has_permission=has_perm,
        reason="Permissão verificada através do cargo" if has_perm else "Cargo não possui esta permissão"
    )

@router.get("/usuarios/{usuario_id}/permissoes")
def get_usuario_permissoes(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter todas as permissões de um usuário"""
    if current_user.tipo != "admin" and current_user.id != usuario_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Admin tem todas as permissões
    if usuario.tipo == "admin":
        all_permissions = db.query(Permissao).all()
        return {
            "usuario": usuario.nome,
            "tipo": usuario.tipo,
            "cargo": "Administrador",
            "total_permissoes": len(all_permissions),
            "permissoes": [
                {
                    "modulo": p.modulo,
                    "acao": p.acao,
                    "descricao": p.descricao
                } for p in all_permissions
            ]
        }
    
    # Buscar colaborador e cargo
    colaborador = db.query(Colaborador).filter_by(usuario_id=usuario_id).first()
    if not colaborador:
        return {
            "usuario": usuario.nome,
            "tipo": usuario.tipo,
            "cargo": None,
            "total_permissoes": 0,
            "permissoes": []
        }
    
    # Buscar permissões do cargo
    permissoes = db.query(Permissao).join(PermissaoCargo).filter(
        PermissaoCargo.cargo_id == colaborador.cargo_id
    ).all()
    
    cargo = db.query(Cargo).filter_by(id=colaborador.cargo_id).first()
    
    return {
        "usuario": usuario.nome,
        "tipo": usuario.tipo,
        "cargo": cargo.nome if cargo else None,
        "total_permissoes": len(permissoes),
        "permissoes": [
            {
                "modulo": p.modulo,
                "acao": p.acao,
                "descricao": p.descricao
            } for p in permissoes
        ]
    }

@router.get("/cargos/{cargo_id}/matriz-permissoes")
def get_cargo_permission_matrix(
    cargo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter matriz de permissões do cargo (todos os módulos e ações)"""
    cargo = db.query(Cargo).filter_by(id=cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    # Buscar permissões atribuídas
    permissoes_atribuidas = db.query(PermissaoCargo).filter_by(cargo_id=cargo_id).all()
    permissao_ids = {pc.permissao_id for pc in permissoes_atribuidas}
    
    # Construir matriz
    matriz = {}
    for modulo_key, modulo_info in MODULOS_SISTEMA.items():
        matriz[modulo_key] = {
            "nome": modulo_info["nome"],
            "descricao": modulo_info["descricao"],
            "acoes": {}
        }
        
        for acao in modulo_info["acoes"]:
            # Verificar se existe a permissão
            permissao = db.query(Permissao).filter(
                and_(
                    Permissao.modulo == modulo_key,
                    Permissao.acao == acao
                )
            ).first()
            
            matriz[modulo_key]["acoes"][acao] = {
                "permitido": permissao.id in permissao_ids if permissao else False,
                "permissao_id": permissao.id if permissao else None
            }
    
    return {
        "cargo": cargo.nome,
        "total_permissoes_atribuidas": len(permissao_ids),
        "total_permissoes_possiveis": sum(len(m["acoes"]) for m in MODULOS_SISTEMA.values()),
        "matriz": matriz
    }

@router.post("/cargos/presets")
def create_cargo_presets(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar cargos pré-definidos com permissões padrão"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    presets = {
        "Gerente": {
            "nivel": 2,
            "modulos_completos": ["dashboard", "eventos", "vendas", "checkin", "pdv", "comandas", 
                                 "produtos", "estoque", "financeiro", "clientes", "relatorios"],
            "modulos_parciais": {
                "usuarios": ["visualizar", "editar"],
                "configuracoes": ["visualizar"]
            }
        },
        "Supervisor": {
            "nivel": 3,
            "modulos_completos": ["dashboard", "vendas", "checkin", "pdv", "comandas", "produtos", "clientes"],
            "modulos_parciais": {
                "estoque": ["visualizar", "entrada", "saida"],
                "financeiro": ["visualizar", "relatorio"],
                "relatorios": ["visualizar", "gerar", "exportar"]
            }
        },
        "Operador PDV": {
            "nivel": 4,
            "modulos_completos": ["pdv", "comandas"],
            "modulos_parciais": {
                "dashboard": ["visualizar"],
                "produtos": ["visualizar"],
                "clientes": ["visualizar", "criar"]
            }
        },
        "Caixa": {
            "nivel": 4,
            "modulos_completos": ["pdv"],
            "modulos_parciais": {
                "comandas": ["visualizar", "recarregar", "fechar"],
                "financeiro": ["visualizar", "lancar"]
            }
        },
        "Recepcionista": {
            "nivel": 5,
            "modulos_completos": ["checkin"],
            "modulos_parciais": {
                "listas": ["visualizar"],
                "clientes": ["visualizar", "criar", "editar"]
            }
        },
        "Bartender": {
            "nivel": 5,
            "modulos_completos": ["kds"],
            "modulos_parciais": {
                "produtos": ["visualizar"],
                "estoque": ["visualizar", "saida"]
            }
        },
        "Garçom": {
            "nivel": 5,
            "modulos_completos": ["mesas", "comandas"],
            "modulos_parciais": {
                "cardapio": ["visualizar"],
                "produtos": ["visualizar"]
            }
        }
    }
    
    created_cargos = []
    
    for nome_cargo, config in presets.items():
        # Verificar se já existe
        existing = db.query(Cargo).filter_by(nome=nome_cargo).first()
        if existing:
            continue
        
        # Criar cargo
        cargo = Cargo(
            nome=nome_cargo,
            descricao=f"Cargo pré-definido: {nome_cargo}",
            nivel_hierarquia=config["nivel"],
            ativo=True
        )
        db.add(cargo)
        db.flush()
        
        # Adicionar permissões
        for modulo in config.get("modulos_completos", []):
            if modulo in MODULOS_SISTEMA:
                for acao in MODULOS_SISTEMA[modulo]["acoes"]:
                    permissao = db.query(Permissao).filter(
                        and_(
                            Permissao.modulo == modulo,
                            Permissao.acao == acao
                        )
                    ).first()
                    
                    if permissao:
                        pc = PermissaoCargo(
                            cargo_id=cargo.id,
                            permissao_id=permissao.id
                        )
                        db.add(pc)
        
        for modulo, acoes in config.get("modulos_parciais", {}).items():
            for acao in acoes:
                permissao = db.query(Permissao).filter(
                    and_(
                        Permissao.modulo == modulo,
                        Permissao.acao == acao
                    )
                ).first()
                
                if permissao:
                    pc = PermissaoCargo(
                        cargo_id=cargo.id,
                        permissao_id=permissao.id
                    )
                    db.add(pc)
        
        created_cargos.append(nome_cargo)
    
    db.commit()
    
    return {
        "message": "Cargos pré-definidos criados",
        "cargos_criados": created_cargos,
        "total": len(created_cargos)
    }

@router.get("/audit/permissoes")
def audit_permissions(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Auditoria completa do sistema de permissões"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    # Estatísticas gerais
    total_usuarios = db.query(Usuario).count()
    total_cargos = db.query(Cargo).count()
    total_permissoes = db.query(Permissao).count()
    total_atribuicoes = db.query(PermissaoCargo).count()
    
    # Cargos sem permissões
    cargos_sem_permissoes = db.query(Cargo).outerjoin(PermissaoCargo).filter(
        PermissaoCargo.id == None
    ).all()
    
    # Usuários sem cargo
    usuarios_sem_cargo = db.query(Usuario).outerjoin(Colaborador).filter(
        and_(
            Colaborador.id == None,
            Usuario.tipo != "admin"
        )
    ).all()
    
    # Permissões mais atribuídas
    from sqlalchemy import desc
    permissoes_populares = db.query(
        Permissao.modulo,
        Permissao.acao,
        func.count(PermissaoCargo.id).label('total')
    ).join(PermissaoCargo).group_by(
        Permissao.modulo,
        Permissao.acao
    ).order_by(desc('total')).limit(10).all()
    
    return {
        "estatisticas": {
            "total_usuarios": total_usuarios,
            "total_cargos": total_cargos,
            "total_permissoes_sistema": total_permissoes,
            "total_atribuicoes": total_atribuicoes,
            "media_permissoes_por_cargo": total_atribuicoes / total_cargos if total_cargos > 0 else 0
        },
        "alertas": {
            "cargos_sem_permissoes": [{"id": c.id, "nome": c.nome} for c in cargos_sem_permissoes],
            "usuarios_sem_cargo": [{"id": u.id, "nome": u.nome} for u in usuarios_sem_cargo]
        },
        "top_permissoes": [
            {
                "modulo": p.modulo,
                "acao": p.acao,
                "atribuicoes": p.total
            } for p in permissoes_populares
        ]
    }