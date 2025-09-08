from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta, date
import json

from ..database import get_db
from ..models import (
    ClienteEvento, ValidacaoAcesso, EquipamentoEvento, 
    SessaoOperador, PrevisaoIA, AnalyticsMEEP, LogSegurancaMEEP,
    Evento, Usuario
)
from ..schemas import (
    ClienteEventoResponse, ValidacaoAcessoResponse, EquipamentoEventoResponse,
    PrevisaoIAResponse, AnalyticsMEEPResponse, LogSegurancaMEEPResponse,
    ClienteEventoCreate, EquipamentoEventoCreate
)
from ..auth_functions import obter_usuario_atual

router = APIRouter()
security = HTTPBearer()

@router.get("/analytics/dashboard/{evento_id}")
async def get_analytics_dashboard(
    evento_id: int,
    periodo: str = "24h",
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Dashboard de analytics em tempo real para um evento específico"""
    
    # Verificar se o evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Definir período
    if periodo == "1h":
        data_inicio = datetime.now() - timedelta(hours=1)
    elif periodo == "24h":
        data_inicio = datetime.now() - timedelta(hours=24)
    elif periodo == "7d":
        data_inicio = datetime.now() - timedelta(days=7)
    else:
        data_inicio = datetime.now() - timedelta(hours=24)
    
    # Métricas gerais
    total_validacoes = db.query(ValidacaoAcesso).filter(
        ValidacaoAcesso.evento_id == evento_id,
        ValidacaoAcesso.timestamp_validacao >= data_inicio
    ).count()
    
    validacoes_sucesso = db.query(ValidacaoAcesso).filter(
        ValidacaoAcesso.evento_id == evento_id,
        ValidacaoAcesso.timestamp_validacao >= data_inicio,
        ValidacaoAcesso.sucesso == True
    ).count()
    
    # Status dos equipamentos
    equipamentos = db.query(EquipamentoEvento).filter(
        EquipamentoEvento.evento_id == evento_id
    ).all()
    
    equipamentos_online = sum(1 for eq in equipamentos if eq.status == 'online')
    equipamentos_total = len(equipamentos)
    
    # Alertas de segurança
    alertas_criticos = db.query(LogSegurancaMEEP).filter(
        LogSegurancaMEEP.evento_id == evento_id,
        LogSegurancaMEEP.gravidade.in_(['critical', 'error']),
        LogSegurancaMEEP.resolvido == False,
        LogSegurancaMEEP.timestamp_evento >= data_inicio
    ).count()
    
    # Fluxo por hora (últimas 24h)
    fluxo_horario = db.query(
        func.date_trunc('hour', ValidacaoAcesso.timestamp_validacao).label('hora'),
        func.count(ValidacaoAcesso.id).label('total'),
        func.count().filter(ValidacaoAcesso.sucesso == True).label('sucessos')
    ).filter(
        ValidacaoAcesso.evento_id == evento_id,
        ValidacaoAcesso.timestamp_validacao >= datetime.now() - timedelta(hours=24)
    ).group_by('hora').order_by('hora').all()
    
    # IPs únicos
    ips_unicos = db.query(func.count(func.distinct(ValidacaoAcesso.ip_address))).filter(
        ValidacaoAcesso.evento_id == evento_id,
        ValidacaoAcesso.timestamp_validacao >= data_inicio
    ).scalar()
    
    return {
        "evento_id": evento_id,
        "periodo": periodo,
        "metricas_gerais": {
            "total_validacoes": total_validacoes,
            "validacoes_sucesso": validacoes_sucesso,
            "taxa_sucesso": round((validacoes_sucesso / total_validacoes * 100) if total_validacoes > 0 else 0, 2),
            "ips_unicos": ips_unicos
        },
        "equipamentos": {
            "online": equipamentos_online,
            "total": equipamentos_total,
            "taxa_online": round((equipamentos_online / equipamentos_total * 100) if equipamentos_total > 0 else 0, 2)
        },
        "seguranca": {
            "alertas_criticos": alertas_criticos
        },
        "fluxo_horario": [
            {
                "hora": item.hora.isoformat(),
                "total": item.total,
                "sucessos": item.sucessos,
                "falhas": item.total - item.sucessos
            }
            for item in fluxo_horario
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/validacoes/{evento_id}")
async def get_validacoes_evento(
    evento_id: int,
    page: int = 1,
    limit: int = 50,
    sucesso: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar validações de acesso de um evento"""
    
    query = db.query(ValidacaoAcesso).filter(ValidacaoAcesso.evento_id == evento_id)
    
    if sucesso is not None:
        query = query.filter(ValidacaoAcesso.sucesso == sucesso)
    
    # Paginação
    offset = (page - 1) * limit
    total = query.count()
    validacoes = query.order_by(desc(ValidacaoAcesso.timestamp_validacao)).offset(offset).limit(limit).all()
    
    return {
        "validacoes": validacoes,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }

@router.get("/equipamentos/{evento_id}")
async def get_equipamentos_evento(
    evento_id: int,
    incluir_offline: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar equipamentos de um evento"""
    
    query = db.query(EquipamentoEvento).filter(EquipamentoEvento.evento_id == evento_id)
    
    if not incluir_offline:
        query = query.filter(EquipamentoEvento.status != 'offline')
    
    equipamentos = query.order_by(desc(EquipamentoEvento.ultima_atividade)).all()
    
    # Enriquecer com status de conexão
    equipamentos_enriched = []
    for eq in equipamentos:
        status_conexao = 'offline'
        if eq.ultima_atividade:
            diff = datetime.now() - eq.ultima_atividade
            if diff.total_seconds() < 120:  # 2 minutos
                status_conexao = 'online'
            elif diff.total_seconds() < 600:  # 10 minutos
                status_conexao = 'warning'
        
        equipamentos_enriched.append({
            **eq.__dict__,
            "status_conexao": status_conexao,
            "segundos_inativo": int((datetime.now() - eq.ultima_atividade).total_seconds()) if eq.ultima_atividade else None
        })
    
    return {
        "equipamentos": equipamentos_enriched,
        "total": len(equipamentos_enriched),
        "estatisticas": {
            "online": len([eq for eq in equipamentos_enriched if eq["status_conexao"] == "online"]),
            "warning": len([eq for eq in equipamentos_enriched if eq["status_conexao"] == "warning"]),
            "offline": len([eq for eq in equipamentos_enriched if eq["status_conexao"] == "offline"])
        }
    }

@router.post("/equipamentos")
async def criar_equipamento(
    equipamento: EquipamentoEventoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Registrar novo equipamento"""
    
    # Verificar se o evento existe
    evento = db.query(Evento).filter(Evento.id == equipamento.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verificar duplicata de IP
    existing = db.query(EquipamentoEvento).filter(
        EquipamentoEvento.evento_id == equipamento.evento_id,
        EquipamentoEvento.ip_address == equipamento.ip_address
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="IP address já registrado para este evento")
    
    # Criar equipamento
    db_equipamento = EquipamentoEvento(
        **equipamento.dict(),
        status='online',
        ultima_atividade=datetime.now()
    )
    
    db.add(db_equipamento)
    db.commit()
    db.refresh(db_equipamento)
    
    return db_equipamento

@router.get("/previsoes/{evento_id}")
async def get_previsoes_evento(
    evento_id: int,
    tipo: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Obter previsões de IA para um evento"""
    
    query = db.query(PrevisaoIA).filter(PrevisaoIA.evento_id == evento_id)
    
    if tipo:
        query = query.filter(PrevisaoIA.tipo_previsao == tipo)
    
    previsoes = query.order_by(desc(PrevisaoIA.timestamp_previsao)).limit(limit).all()
    
    # Parse JSON strings
    previsoes_parsed = []
    for previsao in previsoes:
        previsao_dict = previsao.__dict__.copy()
        try:
            previsao_dict['dados_entrada'] = json.loads(previsao.dados_entrada) if previsao.dados_entrada else {}
            previsao_dict['resultado_previsao'] = json.loads(previsao.resultado_previsao) if previsao.resultado_previsao else {}
            previsao_dict['feedback_real'] = json.loads(previsao.feedback_real) if previsao.feedback_real else {}
        except json.JSONDecodeError:
            pass
        previsoes_parsed.append(previsao_dict)
    
    return {
        "previsoes": previsoes_parsed,
        "total": len(previsoes_parsed)
    }

@router.get("/logs-seguranca/{evento_id}")
async def get_logs_seguranca(
    evento_id: int,
    gravidade: Optional[str] = None,
    tipo_evento: Optional[str] = None,
    resolvido: Optional[bool] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Obter logs de segurança de um evento"""
    
    query = db.query(LogSegurancaMEEP).filter(LogSegurancaMEEP.evento_id == evento_id)
    
    if gravidade:
        query = query.filter(LogSegurancaMEEP.gravidade == gravidade)
    
    if tipo_evento:
        query = query.filter(LogSegurancaMEEP.tipo_evento == tipo_evento)
    
    if resolvido is not None:
        query = query.filter(LogSegurancaMEEP.resolvido == resolvido)
    
    # Paginação
    offset = (page - 1) * limit
    total = query.count()
    logs = query.order_by(desc(LogSegurancaMEEP.timestamp_evento)).offset(offset).limit(limit).all()
    
    # Parse JSON
    logs_parsed = []
    for log in logs:
        log_dict = log.__dict__.copy()
        try:
            log_dict['dados_evento'] = json.loads(log.dados_evento) if log.dados_evento else {}
        except json.JSONDecodeError:
            pass
        logs_parsed.append(log_dict)
    
    return {
        "logs": logs_parsed,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }

@router.post("/logs-seguranca")
async def criar_log_seguranca(
    evento_id: Optional[int] = None,
    tipo_evento: str = "sistema",
    gravidade: str = "info",
    dados_evento: dict = {},
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar log de segurança"""
    
    log = LogSegurancaMEEP(
        evento_id=evento_id,
        tipo_evento=tipo_evento,
        gravidade=gravidade,
        dados_evento=json.dumps(dados_evento),
        usuario_id=current_user.id
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return {"message": "Log criado com sucesso", "log_id": log.id}

@router.get("/stats/{evento_id}")
async def get_stats_evento(
    evento_id: int,
    periodo: str = "7d",
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Estatísticas completas de um evento"""
    
    # Definir período
    if periodo == "1d":
        data_inicio = datetime.now() - timedelta(days=1)
    elif periodo == "7d":
        data_inicio = datetime.now() - timedelta(days=7)
    elif periodo == "30d":
        data_inicio = datetime.now() - timedelta(days=30)
    else:
        data_inicio = datetime.now() - timedelta(days=7)
    
    # Stats de validações
    stats_validacoes = db.query(
        func.count(ValidacaoAcesso.id).label('total'),
        func.count().filter(ValidacaoAcesso.sucesso == True).label('sucessos'),
        func.count().filter(ValidacaoAcesso.sucesso == False).label('falhas'),
        func.count(func.distinct(ValidacaoAcesso.ip_address)).label('ips_unicos'),
        func.count(func.distinct(ValidacaoAcesso.cliente_id)).label('clientes_unicos')
    ).filter(
        ValidacaoAcesso.evento_id == evento_id,
        ValidacaoAcesso.timestamp_validacao >= data_inicio
    ).first()
    
    # Top motivos de falha
    top_falhas = db.query(
        ValidacaoAcesso.motivo_falha,
        func.count(ValidacaoAcesso.id).label('quantidade')
    ).filter(
        ValidacaoAcesso.evento_id == evento_id,
        ValidacaoAcesso.sucesso == False,
        ValidacaoAcesso.motivo_falha.isnot(None),
        ValidacaoAcesso.timestamp_validacao >= data_inicio
    ).group_by(ValidacaoAcesso.motivo_falha).order_by(desc('quantidade')).limit(5).all()
    
    # Tendência temporal
    tendencia = db.query(
        func.date_trunc('hour', ValidacaoAcesso.timestamp_validacao).label('hora'),
        func.count(ValidacaoAcesso.id).label('tentativas'),
        func.count().filter(ValidacaoAcesso.sucesso == True).label('sucessos')
    ).filter(
        ValidacaoAcesso.evento_id == evento_id,
        ValidacaoAcesso.timestamp_validacao >= data_inicio
    ).group_by('hora').order_by('hora').all()
    
    return {
        "evento_id": evento_id,
        "periodo": periodo,
        "estatisticas_gerais": {
            "total_tentativas": stats_validacoes.total or 0,
            "sucessos": stats_validacoes.sucessos or 0,
            "falhas": stats_validacoes.falhas or 0,
            "taxa_sucesso": round((stats_validacoes.sucessos / stats_validacoes.total * 100) if stats_validacoes.total > 0 else 0, 2),
            "ips_unicos": stats_validacoes.ips_unicos or 0,
            "clientes_unicos": stats_validacoes.clientes_unicos or 0
        },
        "principais_falhas": [
            {"motivo": falha.motivo_falha, "quantidade": falha.quantidade}
            for falha in top_falhas
        ],
        "tendencia_temporal": [
            {
                "hora": item.hora.isoformat(),
                "tentativas": item.tentativas,
                "sucessos": item.sucessos,
                "falhas": item.tentativas - item.sucessos
            }
            for item in tendencia
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/clientes", response_model=List[ClienteEventoResponse])
async def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar clientes com filtros opcionais"""
    
    query = db.query(ClienteEvento)
    
    if nome:
        query = query.filter(ClienteEvento.nome_completo.ilike(f"%{nome}%"))
    if cpf:
        query = query.filter(ClienteEvento.cpf.ilike(f"%{cpf}%"))
    if email:
        query = query.filter(ClienteEvento.email.ilike(f"%{email}%"))
    if status:
        query = query.filter(ClienteEvento.status == status)
    
    clientes = query.offset(skip).limit(limit).all()
    return clientes

@router.get("/clientes/{cpf}")
async def get_cliente_by_cpf(
    cpf: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Buscar cliente por CPF"""
    
    cliente = db.query(ClienteEvento).filter(ClienteEvento.cpf == cpf.replace(".", "").replace("-", "")).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente

@router.post("/clientes")
async def criar_cliente(
    cliente: ClienteEventoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo cliente"""
    
    # Verificar se CPF já existe
    existing = db.query(ClienteEvento).filter(ClienteEvento.cpf == cliente.cpf).first()
    if existing:
        raise HTTPException(status_code=409, detail="CPF já cadastrado")
    
    db_cliente = ClienteEvento(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    
    return db_cliente
