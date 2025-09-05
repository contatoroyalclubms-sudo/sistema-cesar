"""
Router para gerenciamento de Filas Virtuais
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import json
import secrets
import asyncio

from app.database import get_db
from app.models import FilaVirtual, ParticipanteFila, Evento, Usuario
from app.schemas_advanced import (
    FilaVirtualCreate, FilaVirtualUpdate, FilaVirtualResponse,
    ParticipanteFilaCreate, ParticipanteFilaUpdate, ParticipanteFilaResponse
)
from app.auth import get_current_user
from app.services.audit_service import AuditService
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/api/filas", tags=["filas-virtuais"])

# Armazenar conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, fila_id: int):
        await websocket.accept()
        if fila_id not in self.active_connections:
            self.active_connections[fila_id] = []
        self.active_connections[fila_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, fila_id: int):
        if fila_id in self.active_connections:
            self.active_connections[fila_id].remove(websocket)
            if not self.active_connections[fila_id]:
                del self.active_connections[fila_id]
    
    async def broadcast(self, message: dict, fila_id: int):
        if fila_id in self.active_connections:
            for connection in self.active_connections[fila_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

def gerar_senha_fila() -> str:
    """Gera senha única para atendimento"""
    return f"{secrets.choice('ABCDEFGHIJ')}{secrets.randbelow(1000):03d}"

def calcular_tempo_espera(fila: FilaVirtual, posicao: int) -> int:
    """Calcula tempo estimado de espera em minutos"""
    if fila.tempo_estimado_atendimento:
        return posicao * fila.tempo_estimado_atendimento
    return posicao * 5  # Default 5 minutos por pessoa

@router.post("/", response_model=FilaVirtualResponse)
async def criar_fila(
    fila: FilaVirtualCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova fila virtual"""
    # Verificar se evento existe
    evento = db.query(Evento).filter(Evento.id == fila.evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Verificar permissão
    if evento.criador_id != current_user.id and current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar fila"
        )
    
    # Criar fila
    db_fila = FilaVirtual(
        **fila.dict(),
        qr_code_acesso=f"FILA_{evento.id}_{secrets.token_hex(8)}"
    )
    db.add(db_fila)
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=None,
        acao="create",
        entidade="fila_virtual",
        entidade_id=db_fila.id,
        dados_novos=fila.dict(),
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_fila)
    
    return db_fila

@router.get("/evento/{evento_id}", response_model=List[FilaVirtualResponse])
async def listar_filas_evento(
    evento_id: int,
    apenas_ativas: bool = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar filas de um evento"""
    query = db.query(FilaVirtual).filter(FilaVirtual.evento_id == evento_id)
    
    if apenas_ativas:
        query = query.filter(FilaVirtual.ativa == True)
    
    filas = query.all()
    return filas

@router.get("/{fila_id}", response_model=FilaVirtualResponse)
async def obter_fila(
    fila_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes de uma fila"""
    fila = db.query(FilaVirtual).filter(FilaVirtual.id == fila_id).first()
    
    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fila não encontrada"
        )
    
    return fila

@router.put("/{fila_id}", response_model=FilaVirtualResponse)
async def atualizar_fila(
    fila_id: int,
    fila_update: FilaVirtualUpdate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar fila virtual"""
    db_fila = db.query(FilaVirtual).filter(FilaVirtual.id == fila_id).first()
    
    if not db_fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fila não encontrada"
        )
    
    # Verificar permissão
    evento = db.query(Evento).filter(Evento.id == db_fila.evento_id).first()
    if evento.criador_id != current_user.id and current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar fila"
        )
    
    # Guardar dados anteriores
    dados_anteriores = {
        "nome": db_fila.nome,
        "ativa": db_fila.ativa,
        "capacidade_maxima": db_fila.capacidade_maxima
    }
    
    # Atualizar
    for key, value in fila_update.dict(exclude_unset=True).items():
        setattr(db_fila, key, value)
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=None,
        acao="update",
        entidade="fila_virtual",
        entidade_id=fila_id,
        dados_anteriores=dados_anteriores,
        dados_novos=fila_update.dict(exclude_unset=True),
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_fila)
    
    # Notificar via WebSocket
    await manager.broadcast({
        "tipo": "fila_atualizada",
        "fila_id": fila_id,
        "dados": fila_update.dict(exclude_unset=True)
    }, fila_id)
    
    return db_fila

@router.post("/{fila_id}/entrar", response_model=ParticipanteFilaResponse)
async def entrar_na_fila(
    fila_id: int,
    participante: ParticipanteFilaCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Entrar em uma fila virtual"""
    # Verificar se fila existe e está ativa
    fila = db.query(FilaVirtual).filter(
        FilaVirtual.id == fila_id,
        FilaVirtual.ativa == True
    ).first()
    
    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fila não encontrada ou inativa"
        )
    
    # Verificar capacidade máxima
    if fila.capacidade_maxima:
        total_na_fila = db.query(func.count(ParticipanteFila.id)).filter(
            ParticipanteFila.fila_id == fila_id,
            ParticipanteFila.status.in_(["aguardando", "chamado"])
        ).scalar()
        
        if total_na_fila >= fila.capacidade_maxima:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fila está cheia"
            )
    
    # Verificar se já está na fila
    existing = db.query(ParticipanteFila).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.cpf == participante.cpf,
        ParticipanteFila.status.in_(["aguardando", "chamado"])
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já está na fila"
        )
    
    # Calcular posição
    ultima_posicao = db.query(func.max(ParticipanteFila.posicao)).filter(
        ParticipanteFila.fila_id == fila_id
    ).scalar() or 0
    
    # Criar participante
    db_participante = ParticipanteFila(
        fila_id=fila_id,
        cpf=participante.cpf,
        nome=participante.nome,
        telefone=participante.telefone,
        email=participante.email,
        prioridade=participante.prioridade,
        posicao=ultima_posicao + 1,
        senha=gerar_senha_fila()
    )
    
    # Se for prioridade, recalcular posições
    if participante.prioridade:
        # Contar quantos prioritários já existem
        prioritarios = db.query(func.count(ParticipanteFila.id)).filter(
            ParticipanteFila.fila_id == fila_id,
            ParticipanteFila.prioridade == True,
            ParticipanteFila.status == "aguardando"
        ).scalar()
        
        # Colocar após os prioritários existentes
        db_participante.posicao = prioritarios + 1
        
        # Ajustar posições dos não prioritários
        db.query(ParticipanteFila).filter(
            ParticipanteFila.fila_id == fila_id,
            ParticipanteFila.prioridade == False,
            ParticipanteFila.posicao >= db_participante.posicao,
            ParticipanteFila.status == "aguardando"
        ).update({ParticipanteFila.posicao: ParticipanteFila.posicao + 1})
    
    db.add(db_participante)
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=None,
        workspace_id=None,
        acao="entrar_fila",
        entidade="fila_virtual",
        entidade_id=fila_id,
        dados_novos={
            "cpf": participante.cpf,
            "posicao": db_participante.posicao,
            "senha": db_participante.senha
        },
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    db.refresh(db_participante)
    
    # Notificar via WebSocket
    await manager.broadcast({
        "tipo": "novo_participante",
        "fila_id": fila_id,
        "posicao": db_participante.posicao,
        "total_fila": ultima_posicao + 1
    }, fila_id)
    
    # Enviar notificação WhatsApp se tiver telefone
    if db_participante.telefone:
        tempo_espera = calcular_tempo_espera(fila, db_participante.posicao)
        try:
            WhatsAppService.enviar_notificacao_fila(
                telefone=db_participante.telefone,
                nome=db_participante.nome,
                senha=db_participante.senha,
                posicao=db_participante.posicao,
                tempo_estimado=tempo_espera
            )
        except:
            pass  # Não falhar se WhatsApp não funcionar
    
    return db_participante

@router.post("/{fila_id}/chamar-proximo")
async def chamar_proximo(
    fila_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chamar próximo da fila"""
    # Verificar permissão
    fila = db.query(FilaVirtual).filter(FilaVirtual.id == fila_id).first()
    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fila não encontrada"
        )
    
    evento = db.query(Evento).filter(Evento.id == fila.evento_id).first()
    if evento.criador_id != current_user.id and current_user.tipo not in ["admin", "operador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para chamar participantes"
        )
    
    # Buscar próximo aguardando
    proximo = db.query(ParticipanteFila).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.status == "aguardando"
    ).order_by(
        ParticipanteFila.prioridade.desc(),  # Prioridades primeiro
        ParticipanteFila.posicao
    ).first()
    
    if not proximo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não há ninguém aguardando na fila"
        )
    
    # Atualizar status
    proximo.status = "chamado"
    proximo.hora_chamada = datetime.utcnow()
    proximo.notificado = False
    
    fila.posicao_atual = proximo.posicao
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=None,
        acao="chamar_participante",
        entidade="fila_virtual",
        entidade_id=fila_id,
        dados_novos={
            "participante_id": proximo.id,
            "senha": proximo.senha,
            "posicao": proximo.posicao
        },
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    # Notificar via WebSocket
    await manager.broadcast({
        "tipo": "chamada",
        "fila_id": fila_id,
        "senha": proximo.senha,
        "nome": proximo.nome[:20] + "...",  # Privacidade
        "posicao": proximo.posicao
    }, fila_id)
    
    # Enviar notificação WhatsApp
    if proximo.telefone and not proximo.notificado:
        try:
            WhatsAppService.enviar_chamada_fila(
                telefone=proximo.telefone,
                nome=proximo.nome,
                senha=proximo.senha
            )
            proximo.notificado = True
            db.commit()
        except:
            pass
    
    return {
        "senha": proximo.senha,
        "nome": proximo.nome,
        "posicao": proximo.posicao,
        "prioridade": proximo.prioridade
    }

@router.post("/{fila_id}/atender/{participante_id}")
async def atender_participante(
    fila_id: int,
    participante_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar participante como atendido"""
    participante = db.query(ParticipanteFila).filter(
        ParticipanteFila.id == participante_id,
        ParticipanteFila.fila_id == fila_id
    ).first()
    
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante não encontrado"
        )
    
    # Atualizar status
    participante.status = "atendido"
    participante.hora_atendimento = datetime.utcnow()
    
    # Atualizar contador da fila
    fila = db.query(FilaVirtual).filter(FilaVirtual.id == fila_id).first()
    fila.total_atendidos += 1
    
    # Recalcular posições
    db.query(ParticipanteFila).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.posicao > participante.posicao,
        ParticipanteFila.status == "aguardando"
    ).update({ParticipanteFila.posicao: ParticipanteFila.posicao - 1})
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=current_user.id,
        workspace_id=None,
        acao="atender_participante",
        entidade="fila_virtual",
        entidade_id=fila_id,
        dados_novos={
            "participante_id": participante_id,
            "tempo_atendimento": (
                participante.hora_atendimento - participante.hora_entrada
            ).total_seconds() / 60  # Em minutos
        },
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    # Notificar via WebSocket
    await manager.broadcast({
        "tipo": "atendimento",
        "fila_id": fila_id,
        "total_atendidos": fila.total_atendidos
    }, fila_id)
    
    return {"message": "Participante atendido com sucesso"}

@router.get("/{fila_id}/participantes", response_model=List[ParticipanteFilaResponse])
async def listar_participantes(
    fila_id: int,
    status: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar participantes da fila"""
    query = db.query(ParticipanteFila).filter(ParticipanteFila.fila_id == fila_id)
    
    if status:
        query = query.filter(ParticipanteFila.status == status)
    
    # Ordenar por prioridade e posição
    participantes = query.order_by(
        ParticipanteFila.prioridade.desc(),
        ParticipanteFila.posicao
    ).all()
    
    return participantes

@router.get("/{fila_id}/estatisticas")
async def obter_estatisticas(
    fila_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas da fila"""
    fila = db.query(FilaVirtual).filter(FilaVirtual.id == fila_id).first()
    
    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fila não encontrada"
        )
    
    # Contar participantes por status
    aguardando = db.query(func.count(ParticipanteFila.id)).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.status == "aguardando"
    ).scalar()
    
    chamados = db.query(func.count(ParticipanteFila.id)).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.status == "chamado"
    ).scalar()
    
    atendidos = db.query(func.count(ParticipanteFila.id)).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.status == "atendido"
    ).scalar()
    
    desistentes = db.query(func.count(ParticipanteFila.id)).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.status == "desistente"
    ).scalar()
    
    # Calcular tempo médio de espera
    tempo_medio = db.query(
        func.avg(
            func.extract('epoch', ParticipanteFila.hora_atendimento - ParticipanteFila.hora_entrada)
        )
    ).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.status == "atendido",
        ParticipanteFila.hora_atendimento != None
    ).scalar()
    
    tempo_medio_minutos = (tempo_medio / 60) if tempo_medio else 0
    
    return {
        "fila_id": fila_id,
        "nome": fila.nome,
        "aguardando": aguardando,
        "chamados": chamados,
        "atendidos": atendidos,
        "desistentes": desistentes,
        "total": aguardando + chamados + atendidos + desistentes,
        "tempo_medio_espera_minutos": round(tempo_medio_minutos, 2),
        "posicao_atual": fila.posicao_atual,
        "capacidade_maxima": fila.capacidade_maxima
    }

@router.websocket("/ws/{fila_id}")
async def websocket_endpoint(websocket: WebSocket, fila_id: int):
    """WebSocket para atualizações em tempo real da fila"""
    await manager.connect(websocket, fila_id)
    try:
        while True:
            # Manter conexão aberta
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, fila_id)

@router.delete("/{fila_id}/sair/{cpf}")
async def sair_da_fila(
    fila_id: int,
    cpf: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Sair da fila (desistir)"""
    participante = db.query(ParticipanteFila).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.cpf == cpf,
        ParticipanteFila.status.in_(["aguardando", "chamado"])
    ).first()
    
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Você não está na fila"
        )
    
    # Marcar como desistente
    participante.status = "desistente"
    
    # Recalcular posições
    db.query(ParticipanteFila).filter(
        ParticipanteFila.fila_id == fila_id,
        ParticipanteFila.posicao > participante.posicao,
        ParticipanteFila.status == "aguardando"
    ).update({ParticipanteFila.posicao: ParticipanteFila.posicao - 1})
    
    # Audit log
    AuditService.log_action(
        db=db,
        usuario_id=None,
        workspace_id=None,
        acao="sair_fila",
        entidade="fila_virtual",
        entidade_id=fila_id,
        dados_novos={
            "cpf": cpf,
            "posicao_anterior": participante.posicao
        },
        ip_origem=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    # Notificar via WebSocket
    await manager.broadcast({
        "tipo": "desistencia",
        "fila_id": fila_id,
        "posicao": participante.posicao
    }, fila_id)
    
    return {"message": "Você saiu da fila com sucesso"}