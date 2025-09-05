"""
Router para gerenciamento de Eventos Recorrentes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date
import json
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY

from app.database import get_db
from app.models import Evento, EventoRecorrencia, Usuario
from app.schemas_advanced import (
    EventoRecorrenciaCreate, EventoRecorrenciaUpdate, EventoRecorrenciaResponse
)
from app.auth import get_current_user
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/eventos/recorrencia", tags=["eventos-recorrentes"])

def gerar_datas_recorrencia(recorrencia: EventoRecorrenciaCreate, data_inicial: datetime) -> List[datetime]:
    """Gera lista de datas baseado na recorrência"""
    datas = []
    
    if recorrencia.tipo_recorrencia == "diario":
        regra = rrule(DAILY, 
                     interval=recorrencia.intervalo,
                     dtstart=data_inicial,
                     until=recorrencia.data_fim)
    
    elif recorrencia.tipo_recorrencia == "semanal":
        byweekday = recorrencia.dias_semana if recorrencia.dias_semana else None
        regra = rrule(WEEKLY,
                     interval=recorrencia.intervalo,
                     byweekday=byweekday,
                     dtstart=data_inicial,
                     until=recorrencia.data_fim)
    
    elif recorrencia.tipo_recorrencia == "mensal":
        bymonthday = recorrencia.dia_mes if recorrencia.dia_mes else data_inicial.day
        regra = rrule(MONTHLY,
                     interval=recorrencia.intervalo,
                     bymonthday=bymonthday,
                     dtstart=data_inicial,
                     until=recorrencia.data_fim)
    
    elif recorrencia.tipo_recorrencia == "anual":
        regra = rrule(YEARLY,
                     interval=recorrencia.intervalo,
                     dtstart=data_inicial,
                     until=recorrencia.data_fim)
    else:
        return []
    
    # Filtrar exceções
    for data in regra:
        if recorrencia.excecoes and data.date().isoformat() not in recorrencia.excecoes:
            datas.append(data)
            if recorrencia.max_ocorrencias and len(datas) >= recorrencia.max_ocorrencias:
                break
    
    return datas

@router.post("/{evento_id}", response_model=EventoRecorrenciaResponse)
async def criar_recorrencia(
    evento_id: int,
    recorrencia: EventoRecorrenciaCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar recorrência para evento"""
    # Buscar evento
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Verificar permissão
    if evento.criador_id != current_user.id and current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar recorrência"
        )
    
    # Verificar se já existe recorrência
    existing = db.query(EventoRecorrencia).filter(
        EventoRecorrencia.evento_pai_id == evento_id,
        EventoRecorrencia.ativo == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evento já possui recorrência ativa"
        )
    
    # Criar recorrência
    db_recorrencia = EventoRecorrencia(
        evento_pai_id=evento_id,
        tipo_recorrencia=recorrencia.tipo_recorrencia,
        intervalo=recorrencia.intervalo,
        dias_semana=json.dumps(recorrencia.dias_semana) if recorrencia.dias_semana else None,
        dia_mes=recorrencia.dia_mes,
        data_fim=recorrencia.data_fim,
        max_ocorrencias=recorrencia.max_ocorrencias,
        excecoes=json.dumps(recorrencia.excecoes) if recorrencia.excecoes else "[]"
    )
    db.add(db_recorrencia)
    db.flush()
    
    # Gerar eventos recorrentes
    datas = gerar_datas_recorrencia(recorrencia, evento.data_evento)
    eventos_criados = []
    
    for data in datas[1:]:  # Pular primeira data (evento pai)
        novo_evento = Evento(
            nome=f"{evento.nome}",
            descricao=evento.descricao,
            data_evento=data,
            local=evento.local,
            endereco=evento.endereco,
            limite_idade=evento.limite_idade,
            capacidade_maxima=evento.capacidade_maxima,
            status=evento.status,
            empresa_id=evento.empresa_id,
            criador_id=evento.criador_id
        )
        db.add(novo_evento)
        eventos_criados.append(novo_evento)
    
    db_recorrencia.ocorrencias_criadas = len(eventos_criados) + 1
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=None,
        acao="create",
        entidade="evento_recorrencia",
        entidade_id=db_recorrencia.id,
        dados_novos={
            "evento_pai_id": evento_id,
            "tipo": recorrencia.tipo_recorrencia,
            "ocorrencias_criadas": db_recorrencia.ocorrencias_criadas
        },
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_recorrencia)
    
    # Converter JSON strings
    if db_recorrencia.dias_semana:
        db_recorrencia.dias_semana = json.loads(db_recorrencia.dias_semana)
    if db_recorrencia.excecoes:
        db_recorrencia.excecoes = json.loads(db_recorrencia.excecoes)
    
    return db_recorrencia

@router.get("/{evento_id}", response_model=EventoRecorrenciaResponse)
async def obter_recorrencia(
    evento_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter recorrência de um evento"""
    recorrencia = db.query(EventoRecorrencia).filter(
        EventoRecorrencia.evento_pai_id == evento_id,
        EventoRecorrencia.ativo == True
    ).first()
    
    if not recorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrência não encontrada"
        )
    
    # Converter JSON strings
    if recorrencia.dias_semana:
        recorrencia.dias_semana = json.loads(recorrencia.dias_semana)
    if recorrencia.excecoes:
        recorrencia.excecoes = json.loads(recorrencia.excecoes)
    
    return recorrencia

@router.put("/{recorrencia_id}", response_model=EventoRecorrenciaResponse)
async def atualizar_recorrencia(
    recorrencia_id: int,
    recorrencia_update: EventoRecorrenciaUpdate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar recorrência"""
    # Buscar recorrência
    db_recorrencia = db.query(EventoRecorrencia).filter(
        EventoRecorrencia.id == recorrencia_id
    ).first()
    
    if not db_recorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrência não encontrada"
        )
    
    # Verificar permissão
    evento = db.query(Evento).filter(Evento.id == db_recorrencia.evento_pai_id).first()
    if evento.criador_id != current_user.id and current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar recorrência"
        )
    
    # Guardar dados anteriores para audit
    dados_anteriores = {
        "ativo": db_recorrencia.ativo,
        "data_fim": db_recorrencia.data_fim.isoformat() if db_recorrencia.data_fim else None,
        "excecoes": json.loads(db_recorrencia.excecoes or "[]")
    }
    
    # Atualizar
    for key, value in recorrencia_update.dict(exclude_unset=True).items():
        if key == "excecoes":
            setattr(db_recorrencia, key, json.dumps(value))
        else:
            setattr(db_recorrencia, key, value)
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=None,
        acao="update",
        entidade="evento_recorrencia",
        entidade_id=recorrencia_id,
        dados_anteriores=dados_anteriores,
        dados_novos=recorrencia_update.dict(exclude_unset=True),
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_recorrencia)
    
    # Converter JSON strings
    if db_recorrencia.dias_semana:
        db_recorrencia.dias_semana = json.loads(db_recorrencia.dias_semana)
    if db_recorrencia.excecoes:
        db_recorrencia.excecoes = json.loads(db_recorrencia.excecoes)
    
    return db_recorrencia

@router.delete("/{recorrencia_id}")
async def cancelar_recorrencia(
    recorrencia_id: int,
    request: Request,
    deletar_futuros: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancelar recorrência e opcionalmente deletar eventos futuros"""
    # Buscar recorrência
    db_recorrencia = db.query(EventoRecorrencia).filter(
        EventoRecorrencia.id == recorrencia_id
    ).first()
    
    if not db_recorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrência não encontrada"
        )
    
    # Verificar permissão
    evento = db.query(Evento).filter(Evento.id == db_recorrencia.evento_pai_id).first()
    if evento.criador_id != current_user.id and current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para cancelar recorrência"
        )
    
    # Desativar recorrência
    db_recorrencia.ativo = False
    
    if deletar_futuros:
        # Buscar e cancelar eventos futuros criados pela recorrência
        from app.models import StatusEvento
        
        eventos_futuros = db.query(Evento).filter(
            Evento.criador_id == evento.criador_id,
            Evento.nome.like(f"{evento.nome}%"),
            Evento.data_evento > datetime.utcnow(),
            Evento.status != StatusEvento.CANCELADO
        ).all()
        
        for evt in eventos_futuros:
            evt.status = StatusEvento.CANCELADO
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=None,
        acao="cancel",
        entidade="evento_recorrencia",
        entidade_id=recorrencia_id,
        dados_anteriores={"ativo": True},
        dados_novos={"ativo": False, "deletar_futuros": deletar_futuros},
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {
        "message": "Recorrência cancelada com sucesso",
        "eventos_cancelados": len(eventos_futuros) if deletar_futuros else 0
    }

@router.get("/{evento_id}/proximas", response_model=List[dict])
async def listar_proximas_ocorrencias(
    evento_id: int,
    limite: int = 10,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar próximas ocorrências de um evento recorrente"""
    # Buscar recorrência
    recorrencia = db.query(EventoRecorrencia).filter(
        EventoRecorrencia.evento_pai_id == evento_id,
        EventoRecorrencia.ativo == True
    ).first()
    
    if not recorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrência não encontrada"
        )
    
    # Buscar evento pai
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    
    # Converter JSON strings
    dias_semana = json.loads(recorrencia.dias_semana) if recorrencia.dias_semana else None
    excecoes = json.loads(recorrencia.excecoes) if recorrencia.excecoes else []
    
    # Criar objeto de recorrência para gerar datas
    rec_obj = EventoRecorrenciaCreate(
        evento_pai_id=evento_id,
        tipo_recorrencia=recorrencia.tipo_recorrencia,
        intervalo=recorrencia.intervalo,
        dias_semana=dias_semana,
        dia_mes=recorrencia.dia_mes,
        data_fim=recorrencia.data_fim,
        max_ocorrencias=limite,
        excecoes=excecoes
    )
    
    # Gerar próximas datas
    datas = gerar_datas_recorrencia(rec_obj, datetime.utcnow())
    
    # Filtrar apenas datas futuras
    datas_futuras = [d for d in datas if d > datetime.utcnow()][:limite]
    
    return [
        {
            "data": data.isoformat(),
            "nome": f"{evento.nome}",
            "local": evento.local,
            "status": "agendado"
        }
        for data in datas_futuras
    ]

@router.post("/{recorrencia_id}/excecoes")
async def adicionar_excecao(
    recorrencia_id: int,
    data_excecao: date,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adicionar data de exceção (pular uma ocorrência)"""
    # Buscar recorrência
    db_recorrencia = db.query(EventoRecorrencia).filter(
        EventoRecorrencia.id == recorrencia_id
    ).first()
    
    if not db_recorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrência não encontrada"
        )
    
    # Verificar permissão
    evento = db.query(Evento).filter(Evento.id == db_recorrencia.evento_pai_id).first()
    if evento.criador_id != current_user.id and current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para adicionar exceção"
        )
    
    # Adicionar exceção
    excecoes = json.loads(db_recorrencia.excecoes or "[]")
    data_str = data_excecao.isoformat()
    
    if data_str not in excecoes:
        excecoes.append(data_str)
        db_recorrencia.excecoes = json.dumps(excecoes)
        
        # Audit log
        AuditService.log_action(
            db=db,
            usuario_id=current_user.id,
            workspace_id=None,
            acao="add_exception",
            entidade="evento_recorrencia",
            entidade_id=recorrencia_id,
            dados_novos={"data_excecao": data_str},
            ip_origem=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        db.commit()
        
        return {"message": "Exceção adicionada com sucesso", "excecoes": excecoes}
    
    return {"message": "Data já está nas exceções", "excecoes": excecoes}