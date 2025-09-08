"""
Router para gerenciamento de colaboradores e cargos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
import json
from enum import Enum

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    Cargo, CargoCreate, CargoUpdate,
    Colaborador, ColaboradorCreate, ColaboradorUpdate,
    EscalaTrabalho, EscalaTrabalhoCreate, EscalaTrabalhoUpdate,
    TarefaColaborador, TarefaColaboradorCreate, TarefaColaboradorUpdate
)

router = APIRouter(
    prefix="/api/colaboradores",
    tags=["colaboradores"]
)

class TipoColaborador(str, Enum):
    FIXO = "fixo"
    TEMPORARIO = "temporario"
    FREELANCER = "freelancer"
    VOLUNTARIO = "voluntario"
    TERCEIRIZADO = "terceirizado"

class StatusColaborador(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    FERIAS = "ferias"
    AFASTADO = "afastado"
    DESLIGADO = "desligado"

class TipoEscala(str, Enum):
    NORMAL = "normal"
    PLANTAO = "plantao"
    REVEZAMENTO = "revezamento"
    EVENTO = "evento"
    EXTRA = "extra"

class StatusTarefa(str, Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    ATRASADA = "atrasada"

def calcular_horas_trabalhadas(entrada: datetime, saida: datetime) -> float:
    """Calcula horas trabalhadas entre entrada e saída"""
    delta = saida - entrada
    return round(delta.total_seconds() / 3600, 2)

def verificar_disponibilidade_colaborador(
    colaborador_id: int,
    data_inicio: datetime,
    data_fim: datetime,
    db: Session
) -> bool:
    """Verifica se colaborador está disponível no período"""
    escalas_conflitantes = db.query(models.EscalaTrabalho).filter(
        models.EscalaTrabalho.colaborador_id == colaborador_id,
        models.EscalaTrabalho.status != "cancelada",
        or_(
            and_(
                models.EscalaTrabalho.data_inicio <= data_inicio,
                models.EscalaTrabalho.data_fim >= data_inicio
            ),
            and_(
                models.EscalaTrabalho.data_inicio <= data_fim,
                models.EscalaTrabalho.data_fim >= data_fim
            ),
            and_(
                models.EscalaTrabalho.data_inicio >= data_inicio,
                models.EscalaTrabalho.data_fim <= data_fim
            )
        )
    ).count()
    
    return escalas_conflitantes == 0

# ====== CARGOS ======

@router.get("/cargos/", response_model=List[Cargo])
def listar_cargos(
    skip: int = 0,
    limit: int = 100,
    departamento: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os cargos"""
    query = db.query(models.Cargo)
    
    if departamento:
        query = query.filter(models.Cargo.departamento == departamento)
    
    if ativo is not None:
        query = query.filter(models.Cargo.ativo == ativo)
    
    cargos = query.order_by(
        models.Cargo.nivel_hierarquia,
        models.Cargo.nome
    ).offset(skip).limit(limit).all()
    
    # Adicionar contagem de colaboradores
    for cargo in cargos:
        cargo.total_colaboradores = db.query(models.Colaborador).filter(
            models.Colaborador.cargo_id == cargo.id,
            models.Colaborador.status == "ativo"
        ).count()
    
    return cargos

@router.get("/cargos/{cargo_id}", response_model=Cargo)
def obter_cargo(
    cargo_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém um cargo específico"""
    cargo = db.query(models.Cargo).filter(
        models.Cargo.id == cargo_id
    ).first()
    
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    return cargo

@router.post("/cargos/", response_model=Cargo)
def criar_cargo(
    cargo: CargoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo cargo"""
    # Verificar se já existe cargo com mesmo nome
    cargo_existente = db.query(models.Cargo).filter(
        models.Cargo.nome == cargo.nome,
        models.Cargo.departamento == cargo.departamento
    ).first()
    
    if cargo_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um cargo com este nome neste departamento"
        )
    
    # Converter permissões para JSON
    permissoes = json.dumps(cargo.permissoes) if cargo.permissoes else None
    requisitos = json.dumps(cargo.requisitos) if cargo.requisitos else None
    
    db_cargo = models.Cargo(
        **cargo.model_dump(exclude={'permissoes', 'requisitos'}),
        permissoes=permissoes,
        requisitos=requisitos
    )
    
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    
    return db_cargo

@router.put("/cargos/{cargo_id}", response_model=Cargo)
def atualizar_cargo(
    cargo_id: int,
    cargo_update: CargoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um cargo"""
    cargo = db.query(models.Cargo).filter(
        models.Cargo.id == cargo_id
    ).first()
    
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    update_data = cargo_update.model_dump(exclude_unset=True)
    
    if 'permissoes' in update_data and update_data['permissoes']:
        update_data['permissoes'] = json.dumps(update_data['permissoes'])
    
    if 'requisitos' in update_data and update_data['requisitos']:
        update_data['requisitos'] = json.dumps(update_data['requisitos'])
    
    for key, value in update_data.items():
        setattr(cargo, key, value)
    
    db.commit()
    db.refresh(cargo)
    
    return cargo

@router.delete("/cargos/{cargo_id}")
def deletar_cargo(
    cargo_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Desativa um cargo"""
    cargo = db.query(models.Cargo).filter(
        models.Cargo.id == cargo_id
    ).first()
    
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    # Verificar se há colaboradores ativos
    colaboradores_ativos = db.query(models.Colaborador).filter(
        models.Colaborador.cargo_id == cargo_id,
        models.Colaborador.status == "ativo"
    ).count()
    
    if colaboradores_ativos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível desativar o cargo. Há {colaboradores_ativos} colaboradores ativos."
        )
    
    cargo.ativo = False
    db.commit()
    
    return {"message": "Cargo desativado com sucesso"}

# ====== COLABORADORES ======

@router.get("/", response_model=List[Colaborador])
def listar_colaboradores(
    skip: int = 0,
    limit: int = 100,
    cargo_id: Optional[int] = None,
    departamento: Optional[str] = None,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    evento_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os colaboradores"""
    query = db.query(models.Colaborador)
    
    if cargo_id:
        query = query.filter(models.Colaborador.cargo_id == cargo_id)
    
    if departamento:
        query = query.join(models.Cargo).filter(
            models.Cargo.departamento == departamento
        )
    
    if tipo:
        query = query.filter(models.Colaborador.tipo == tipo)
    
    if status:
        query = query.filter(models.Colaborador.status == status)
    
    if evento_id:
        # Filtrar colaboradores alocados para um evento específico
        query = query.join(models.EscalaTrabalho).filter(
            models.EscalaTrabalho.evento_id == evento_id
        )
    
    if search:
        query = query.filter(
            or_(
                models.Colaborador.nome.ilike(f"%{search}%"),
                models.Colaborador.email.ilike(f"%{search}%"),
                models.Colaborador.cpf.ilike(f"%{search}%")
            )
        )
    
    colaboradores = query.order_by(
        models.Colaborador.nome
    ).offset(skip).limit(limit).all()
    
    # Adicionar informações do cargo
    for colaborador in colaboradores:
        if colaborador.cargo_id:
            colaborador.cargo = db.query(models.Cargo).filter(
                models.Cargo.id == colaborador.cargo_id
            ).first()
    
    return colaboradores

@router.get("/{colaborador_id}", response_model=Colaborador)
def obter_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém um colaborador específico"""
    colaborador = db.query(models.Colaborador).filter(
        models.Colaborador.id == colaborador_id
    ).first()
    
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    
    # Adicionar informações do cargo
    if colaborador.cargo_id:
        colaborador.cargo = db.query(models.Cargo).filter(
            models.Cargo.id == colaborador.cargo_id
        ).first()
    
    # Adicionar estatísticas
    colaborador.total_escalas = db.query(models.EscalaTrabalho).filter(
        models.EscalaTrabalho.colaborador_id == colaborador_id
    ).count()
    
    colaborador.total_tarefas = db.query(models.TarefaColaborador).filter(
        models.TarefaColaborador.colaborador_id == colaborador_id
    ).count()
    
    return colaborador

@router.post("/", response_model=Colaborador)
def criar_colaborador(
    colaborador: ColaboradorCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo colaborador"""
    # Verificar se CPF já existe
    cpf_existente = db.query(models.Colaborador).filter(
        models.Colaborador.cpf == colaborador.cpf
    ).first()
    
    if cpf_existente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Verificar se cargo existe
    if colaborador.cargo_id:
        cargo = db.query(models.Cargo).filter(
            models.Cargo.id == colaborador.cargo_id
        ).first()
        
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    # Converter dados para JSON
    habilidades = json.dumps(colaborador.habilidades) if colaborador.habilidades else None
    documentos = json.dumps(colaborador.documentos) if colaborador.documentos else None
    
    db_colaborador = models.Colaborador(
        **colaborador.model_dump(exclude={'habilidades', 'documentos'}),
        habilidades=habilidades,
        documentos=documentos
    )
    
    db.add(db_colaborador)
    db.commit()
    db.refresh(db_colaborador)
    
    return db_colaborador

@router.put("/{colaborador_id}", response_model=Colaborador)
def atualizar_colaborador(
    colaborador_id: int,
    colaborador_update: ColaboradorUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um colaborador"""
    colaborador = db.query(models.Colaborador).filter(
        models.Colaborador.id == colaborador_id
    ).first()
    
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    
    update_data = colaborador_update.model_dump(exclude_unset=True)
    
    if 'habilidades' in update_data and update_data['habilidades']:
        update_data['habilidades'] = json.dumps(update_data['habilidades'])
    
    if 'documentos' in update_data and update_data['documentos']:
        update_data['documentos'] = json.dumps(update_data['documentos'])
    
    for key, value in update_data.items():
        setattr(colaborador, key, value)
    
    db.commit()
    db.refresh(colaborador)
    
    return colaborador

@router.delete("/{colaborador_id}")
def deletar_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Desliga um colaborador"""
    colaborador = db.query(models.Colaborador).filter(
        models.Colaborador.id == colaborador_id
    ).first()
    
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    
    colaborador.status = "desligado"
    colaborador.data_desligamento = datetime.now()
    db.commit()
    
    return {"message": "Colaborador desligado com sucesso"}

# ====== ESCALAS DE TRABALHO ======

@router.get("/escalas/", response_model=List[EscalaTrabalho])
def listar_escalas(
    skip: int = 0,
    limit: int = 100,
    colaborador_id: Optional[int] = None,
    evento_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista escalas de trabalho"""
    query = db.query(models.EscalaTrabalho)
    
    if colaborador_id:
        query = query.filter(models.EscalaTrabalho.colaborador_id == colaborador_id)
    
    if evento_id:
        query = query.filter(models.EscalaTrabalho.evento_id == evento_id)
    
    if data_inicio:
        query = query.filter(models.EscalaTrabalho.data_fim >= data_inicio)
    
    if data_fim:
        query = query.filter(models.EscalaTrabalho.data_inicio <= data_fim)
    
    if tipo:
        query = query.filter(models.EscalaTrabalho.tipo == tipo)
    
    escalas = query.order_by(
        models.EscalaTrabalho.data_inicio
    ).offset(skip).limit(limit).all()
    
    # Adicionar informações do colaborador
    for escala in escalas:
        if escala.colaborador_id:
            escala.colaborador = db.query(models.Colaborador).filter(
                models.Colaborador.id == escala.colaborador_id
            ).first()
    
    return escalas

@router.post("/escalas/", response_model=EscalaTrabalho)
def criar_escala(
    escala: EscalaTrabalhoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova escala de trabalho"""
    # Verificar colaborador
    colaborador = db.query(models.Colaborador).filter(
        models.Colaborador.id == escala.colaborador_id,
        models.Colaborador.status == "ativo"
    ).first()
    
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado ou inativo")
    
    # Verificar disponibilidade
    if not verificar_disponibilidade_colaborador(
        escala.colaborador_id,
        escala.data_inicio,
        escala.data_fim,
        db
    ):
        raise HTTPException(
            status_code=400,
            detail="Colaborador já tem escala neste período"
        )
    
    # Calcular horas previstas
    horas_previstas = calcular_horas_trabalhadas(escala.data_inicio, escala.data_fim)
    
    db_escala = models.EscalaTrabalho(
        **escala.model_dump(),
        horas_previstas=horas_previstas,
        status="agendada",
        criado_por_id=current_user.id
    )
    
    db.add(db_escala)
    db.commit()
    db.refresh(db_escala)
    
    return db_escala

@router.put("/escalas/{escala_id}", response_model=EscalaTrabalho)
def atualizar_escala(
    escala_id: int,
    escala_update: EscalaTrabalhoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma escala de trabalho"""
    escala = db.query(models.EscalaTrabalho).filter(
        models.EscalaTrabalho.id == escala_id
    ).first()
    
    if not escala:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    
    update_data = escala_update.model_dump(exclude_unset=True)
    
    # Recalcular horas se datas mudaram
    if 'data_inicio' in update_data or 'data_fim' in update_data:
        data_inicio = update_data.get('data_inicio', escala.data_inicio)
        data_fim = update_data.get('data_fim', escala.data_fim)
        update_data['horas_previstas'] = calcular_horas_trabalhadas(data_inicio, data_fim)
    
    for key, value in update_data.items():
        setattr(escala, key, value)
    
    db.commit()
    db.refresh(escala)
    
    return escala

@router.post("/escalas/{escala_id}/check-in")
def fazer_checkin_escala(
    escala_id: int,
    localizacao: Optional[Dict[str, float]] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Registra entrada na escala"""
    escala = db.query(models.EscalaTrabalho).filter(
        models.EscalaTrabalho.id == escala_id
    ).first()
    
    if not escala:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    
    if escala.checkin_realizado:
        raise HTTPException(status_code=400, detail="Check-in já realizado")
    
    escala.checkin_realizado = datetime.now()
    escala.status = "em_andamento"
    
    if localizacao:
        escala.localizacao_checkin = json.dumps(localizacao)
    
    db.commit()
    
    return {
        "message": "Check-in realizado com sucesso",
        "horario": escala.checkin_realizado.isoformat()
    }

@router.post("/escalas/{escala_id}/check-out")
def fazer_checkout_escala(
    escala_id: int,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Registra saída da escala"""
    escala = db.query(models.EscalaTrabalho).filter(
        models.EscalaTrabalho.id == escala_id
    ).first()
    
    if not escala:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    
    if not escala.checkin_realizado:
        raise HTTPException(status_code=400, detail="Check-in não realizado")
    
    if escala.checkout_realizado:
        raise HTTPException(status_code=400, detail="Check-out já realizado")
    
    escala.checkout_realizado = datetime.now()
    escala.status = "concluida"
    
    # Calcular horas trabalhadas
    escala.horas_trabalhadas = calcular_horas_trabalhadas(
        escala.checkin_realizado,
        escala.checkout_realizado
    )
    
    if observacoes:
        escala.observacoes = observacoes
    
    db.commit()
    
    return {
        "message": "Check-out realizado com sucesso",
        "horario": escala.checkout_realizado.isoformat(),
        "horas_trabalhadas": escala.horas_trabalhadas
    }

# ====== TAREFAS ======

@router.get("/tarefas/", response_model=List[TarefaColaborador])
def listar_tarefas(
    skip: int = 0,
    limit: int = 100,
    colaborador_id: Optional[int] = None,
    escala_id: Optional[int] = None,
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista tarefas de colaboradores"""
    query = db.query(models.TarefaColaborador)
    
    if colaborador_id:
        query = query.filter(models.TarefaColaborador.colaborador_id == colaborador_id)
    
    if escala_id:
        query = query.filter(models.TarefaColaborador.escala_id == escala_id)
    
    if status:
        query = query.filter(models.TarefaColaborador.status == status)
    
    if prioridade:
        query = query.filter(models.TarefaColaborador.prioridade == prioridade)
    
    tarefas = query.order_by(
        models.TarefaColaborador.prioridade.desc(),
        models.TarefaColaborador.prazo
    ).offset(skip).limit(limit).all()
    
    return tarefas

@router.post("/tarefas/", response_model=TarefaColaborador)
def criar_tarefa(
    tarefa: TarefaColaboradorCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova tarefa"""
    # Verificar colaborador
    colaborador = db.query(models.Colaborador).filter(
        models.Colaborador.id == tarefa.colaborador_id
    ).first()
    
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    
    db_tarefa = models.TarefaColaborador(
        **tarefa.model_dump(),
        criado_por_id=current_user.id,
        status="pendente"
    )
    
    db.add(db_tarefa)
    db.commit()
    db.refresh(db_tarefa)
    
    return db_tarefa

@router.put("/tarefas/{tarefa_id}", response_model=TarefaColaborador)
def atualizar_tarefa(
    tarefa_id: int,
    tarefa_update: TarefaColaboradorUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma tarefa"""
    tarefa = db.query(models.TarefaColaborador).filter(
        models.TarefaColaborador.id == tarefa_id
    ).first()
    
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    update_data = tarefa_update.model_dump(exclude_unset=True)
    
    # Registrar conclusão se status mudou para concluída
    if 'status' in update_data and update_data['status'] == 'concluida':
        update_data['data_conclusao'] = datetime.now()
    
    for key, value in update_data.items():
        setattr(tarefa, key, value)
    
    db.commit()
    db.refresh(tarefa)
    
    return tarefa

@router.get("/relatorios/horas")
def relatorio_horas_trabalhadas(
    colaborador_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera relatório de horas trabalhadas"""
    query = db.query(models.EscalaTrabalho).filter(
        models.EscalaTrabalho.status == "concluida"
    )
    
    if colaborador_id:
        query = query.filter(models.EscalaTrabalho.colaborador_id == colaborador_id)
    
    if data_inicio:
        query = query.filter(models.EscalaTrabalho.data_inicio >= data_inicio)
    
    if data_fim:
        query = query.filter(models.EscalaTrabalho.data_fim <= data_fim)
    
    escalas = query.all()
    
    # Calcular totais
    total_horas_previstas = sum(e.horas_previstas or 0 for e in escalas)
    total_horas_trabalhadas = sum(e.horas_trabalhadas or 0 for e in escalas)
    
    # Agrupar por colaborador
    por_colaborador = {}
    for escala in escalas:
        colab_id = escala.colaborador_id
        if colab_id not in por_colaborador:
            colaborador = db.query(models.Colaborador).filter(
                models.Colaborador.id == colab_id
            ).first()
            por_colaborador[colab_id] = {
                "nome": colaborador.nome if colaborador else "Desconhecido",
                "horas_previstas": 0,
                "horas_trabalhadas": 0,
                "escalas": 0
            }
        
        por_colaborador[colab_id]["horas_previstas"] += escala.horas_previstas or 0
        por_colaborador[colab_id]["horas_trabalhadas"] += escala.horas_trabalhadas or 0
        por_colaborador[colab_id]["escalas"] += 1
    
    return {
        "periodo": {
            "inicio": data_inicio.isoformat() if data_inicio else None,
            "fim": data_fim.isoformat() if data_fim else None
        },
        "resumo": {
            "total_escalas": len(escalas),
            "total_horas_previstas": round(total_horas_previstas, 2),
            "total_horas_trabalhadas": round(total_horas_trabalhadas, 2),
            "eficiencia": round((total_horas_trabalhadas / total_horas_previstas * 100) if total_horas_previstas > 0 else 0, 2)
        },
        "por_colaborador": [
            {
                "colaborador_id": colab_id,
                "nome": dados["nome"],
                "horas_previstas": round(dados["horas_previstas"], 2),
                "horas_trabalhadas": round(dados["horas_trabalhadas"], 2),
                "total_escalas": dados["escalas"]
            }
            for colab_id, dados in por_colaborador.items()
        ]
    }