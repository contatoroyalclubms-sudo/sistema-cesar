"""
Router avançado do sistema KDS com workflow e automação
Implementa funcionalidades avançadas baseadas na arquitetura MEEP
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime, timedelta, date

from ..database import get_db
from ..models import (
    FilaKDS, FluxoKDS, EtapaFluxoKDS, NotificacaoKDS, 
    TemplateFluxoKDS, MetricaKDS, AlertaKDS, PedidoKDS,
    EstacaoKDS, ItemPedidoKDS
)
from ..schemas_kds_avancado import (
    # Fila KDS
    FilaKDSCreate, FilaKDSUpdate, FilaKDSResponse,
    # Fluxo KDS
    FluxoKDSCreate, FluxoKDSUpdate, FluxoKDSResponse, FluxoKDSCompleto,
    # Etapa Fluxo KDS
    EtapaFluxoKDSCreate, EtapaFluxoKDSUpdate, EtapaFluxoKDSResponse,
    # Notificação KDS
    NotificacaoKDSCreate, NotificacaoKDSUpdate, NotificacaoKDSResponse,
    # Template Fluxo KDS
    TemplateFluxoKDSCreate, TemplateFluxoKDSUpdate, TemplateFluxoKDSResponse,
    # Métrica KDS
    MetricaKDSCreate, MetricaKDSUpdate, MetricaKDSResponse,
    # Alerta KDS
    AlertaKDSCreate, AlertaKDSUpdate, AlertaKDSResponse,
    # Schemas complexos
    DashboardKDSMetricas, EstacaoKDSStatus, ResumoOperacionalKDS,
    # Enums
    StatusEtapaKDS, TipoNotificacaoKDS, SeveridadeAlerta
)
from ..services.kds_avancado_service import KDSAvancadoService
from ..auth import get_current_user

router = APIRouter(tags=["KDS Avançado"], prefix="/kds-avancado")

# WebSocket connection manager aprimorado
class KDSAdvancedConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str, user_id: Optional[int] = None):
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str, user_id: Optional[int] = None):
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)
        
        if user_id and user_id in self.user_connections and websocket in self.user_connections[user_id]:
            self.user_connections[user_id].remove(websocket)
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        if channel in self.active_connections:
            disconnected = []
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(json.dumps(message, default=str))
                except:
                    disconnected.append(connection)
            
            # Remove conexões desconectadas
            for conn in disconnected:
                self.active_connections[channel].remove(conn)
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message, default=str))
                except:
                    disconnected.append(connection)
            
            # Remove conexões desconectadas
            for conn in disconnected:
                self.user_connections[user_id].remove(conn)

manager = KDSAdvancedConnectionManager()

# ====== WEBSOCKET ENDPOINTS ======

@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket para dashboard geral do KDS"""
    await manager.connect(websocket, "dashboard")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # Broadcast para todos conectados no dashboard
            await manager.broadcast_to_channel("dashboard", {
                "type": "dashboard_update",
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")

@router.websocket("/ws/estacao/{estacao_id}")
async def websocket_estacao(websocket: WebSocket, estacao_id: int):
    """WebSocket específico para uma estação KDS"""
    channel = f"estacao_{estacao_id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await manager.broadcast_to_channel(channel, {
                "type": "estacao_update",
                "estacao_id": estacao_id,
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)

@router.websocket("/ws/alertas")
async def websocket_alertas(websocket: WebSocket):
    """WebSocket para alertas e notificações"""
    await manager.connect(websocket, "alertas")
    try:
        while True:
            data = await websocket.receive_text()
            # Canal específico para alertas críticos
            await manager.broadcast_to_channel("alertas", {
                "type": "alerta_update",
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alertas")

# ====== ENDPOINTS DE FILAS KDS ======

@router.post("/filas", response_model=FilaKDSResponse)
def criar_fila_kds(
    fila: FilaKDSCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria uma nova fila KDS para uma estação"""
    db_fila = FilaKDS(**fila.dict())
    db.add(db_fila)
    db.commit()
    db.refresh(db_fila)
    return db_fila

@router.get("/filas", response_model=List[FilaKDSResponse])
def listar_filas_kds(
    estacao_id: Optional[int] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista todas as filas KDS com filtros opcionais"""
    query = db.query(FilaKDS)
    
    if estacao_id:
        query = query.filter(FilaKDS.estacao_id == estacao_id)
    if ativo is not None:
        query = query.filter(FilaKDS.ativo == ativo)
    
    return query.order_by(FilaKDS.ordem).all()

@router.put("/filas/{fila_id}", response_model=FilaKDSResponse)
def atualizar_fila_kds(
    fila_id: int,
    fila_update: FilaKDSUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza configurações de uma fila KDS"""
    fila = db.query(FilaKDS).filter(FilaKDS.id == fila_id).first()
    if not fila:
        raise HTTPException(status_code=404, detail="Fila não encontrada")
    
    for key, value in fila_update.dict(exclude_unset=True).items():
        setattr(fila, key, value)
    
    db.commit()
    db.refresh(fila)
    return fila

# ====== ENDPOINTS DE FLUXOS KDS ======

@router.post("/fluxos", response_model=FluxoKDSResponse)
def criar_fluxo_kds(
    fluxo: FluxoKDSCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria um novo fluxo de trabalho KDS"""
    db_fluxo = FluxoKDS(
        nome=fluxo.nome,
        descricao=fluxo.descricao,
        tipo=fluxo.tipo,
        estacoes=json.dumps(fluxo.estacoes),
        regras=json.dumps(fluxo.regras) if fluxo.regras else None,
        tempo_estimado_total=fluxo.tempo_estimado_total,
        ativo=fluxo.ativo
    )
    
    db.add(db_fluxo)
    db.commit()
    db.refresh(db_fluxo)
    return db_fluxo

@router.get("/fluxos", response_model=List[FluxoKDSResponse])
def listar_fluxos_kds(
    ativo: Optional[bool] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista todos os fluxos KDS com filtros opcionais"""
    query = db.query(FluxoKDS)
    
    if ativo is not None:
        query = query.filter(FluxoKDS.ativo == ativo)
    if tipo:
        query = query.filter(FluxoKDS.tipo == tipo)
    
    fluxos = query.order_by(FluxoKDS.created_at.desc()).all()
    
    # Converter estacoes de JSON string para list
    for fluxo in fluxos:
        if isinstance(fluxo.estacoes, str):
            fluxo.estacoes = json.loads(fluxo.estacoes)
        if isinstance(fluxo.regras, str):
            fluxo.regras = json.loads(fluxo.regras) if fluxo.regras else None
    
    return fluxos

@router.get("/fluxos/{fluxo_id}/completo", response_model=FluxoKDSCompleto)
def obter_fluxo_completo(
    fluxo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém um fluxo KDS com todas as etapas e dados relacionados"""
    fluxo = db.query(FluxoKDS).filter(FluxoKDS.id == fluxo_id).first()
    if not fluxo:
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    
    # Converter estacoes e regras de JSON
    if isinstance(fluxo.estacoes, str):
        fluxo.estacoes = json.loads(fluxo.estacoes)
    if isinstance(fluxo.regras, str):
        fluxo.regras = json.loads(fluxo.regras) if fluxo.regras else None
    
    # Buscar etapas do fluxo
    etapas = db.query(EtapaFluxoKDS).filter(
        EtapaFluxoKDS.fluxo_id == fluxo_id
    ).order_by(EtapaFluxoKDS.ordem).all()
    
    # Calcular métricas de performance
    etapas_concluidas = len([e for e in etapas if e.status == StatusEtapaKDS.CONCLUIDA])
    total_etapas = len(etapas)
    progresso = (etapas_concluidas / total_etapas * 100) if total_etapas > 0 else 0
    
    tempo_total_real = sum([e.tempo_real for e in etapas if e.tempo_real]) or 0
    
    metricas_performance = {
        "progresso_percentual": progresso,
        "etapas_concluidas": etapas_concluidas,
        "total_etapas": total_etapas,
        "tempo_estimado_minutos": fluxo.tempo_estimado_total,
        "tempo_real_minutos": tempo_total_real,
        "diferenca_tempo": tempo_total_real - (fluxo.tempo_estimado_total or 0)
    }
    
    return FluxoKDSCompleto(
        fluxo=fluxo,
        etapas=etapas,
        template_origem=None,  # Implementar busca de template se necessário
        metricas_performance=metricas_performance
    )

# ====== ENDPOINTS DE ETAPAS DO FLUXO ======

@router.post("/fluxos/{fluxo_id}/pedidos/{pedido_id}/etapas", response_model=List[EtapaFluxoKDSResponse])
async def criar_etapas_fluxo(
    fluxo_id: int,
    pedido_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria automaticamente as etapas de um fluxo para um pedido específico"""
    fluxo = db.query(FluxoKDS).filter(FluxoKDS.id == fluxo_id).first()
    if not fluxo:
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    
    pedido = db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Verificar se já existem etapas para este fluxo/pedido
    etapas_existentes = db.query(EtapaFluxoKDS).filter(
        EtapaFluxoKDS.fluxo_id == fluxo_id,
        EtapaFluxoKDS.pedido_id == pedido_id
    ).count()
    
    if etapas_existentes > 0:
        raise HTTPException(status_code=400, detail="Etapas já foram criadas para este pedido")
    
    estacoes = json.loads(fluxo.estacoes) if isinstance(fluxo.estacoes, str) else fluxo.estacoes
    regras = json.loads(fluxo.regras) if isinstance(fluxo.regras, str) and fluxo.regras else {}
    
    etapas_criadas = []
    tempo_estimado_base = (fluxo.tempo_estimado_total or 30) // len(estacoes)
    
    for ordem, estacao_id in enumerate(estacoes):
        etapa = EtapaFluxoKDS(
            fluxo_id=fluxo_id,
            pedido_id=pedido_id,
            estacao_id=estacao_id,
            ordem=ordem,
            tempo_estimado=regras.get(f"tempo_estacao_{estacao_id}", tempo_estimado_base),
            status=StatusEtapaKDS.PENDENTE
        )
        
        db.add(etapa)
        etapas_criadas.append(etapa)
    
    db.commit()
    
    # Refresh para obter IDs
    for etapa in etapas_criadas:
        db.refresh(etapa)
    
    # Notificar primeira estação se fluxo for sequencial
    if fluxo.tipo == "sequencial" and etapas_criadas:
        primeira_etapa = etapas_criadas[0]
        background_tasks.add_task(
            notificar_nova_etapa,
            db,
            primeira_etapa.estacao_id,
            pedido_id,
            f"Nova etapa disponível - Pedido #{pedido.numero_pedido}"
        )
    
    return etapas_criadas

@router.put("/etapas/{etapa_id}/status", response_model=EtapaFluxoKDSResponse)
async def atualizar_status_etapa(
    etapa_id: int,
    novo_status: StatusEtapaKDS,
    observacoes: Optional[str] = None,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza o status de uma etapa do fluxo"""
    service = KDSAvancadoService(db)
    
    try:
        etapa = service.avancar_etapa_fluxo(etapa_id, novo_status, observacoes)
        
        # Notificar via WebSocket
        background_tasks.add_task(
            broadcast_etapa_update,
            etapa.estacao_id,
            etapa_id,
            novo_status.value
        )
        
        return etapa
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/etapas/pedido/{pedido_id}", response_model=List[EtapaFluxoKDSResponse])
def listar_etapas_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista todas as etapas de um pedido específico"""
    return db.query(EtapaFluxoKDS).filter(
        EtapaFluxoKDS.pedido_id == pedido_id
    ).order_by(EtapaFluxoKDS.ordem).all()

# ====== ENDPOINTS DE TEMPLATES ======

@router.post("/templates", response_model=TemplateFluxoKDSResponse)
def criar_template_fluxo(
    template: TemplateFluxoKDSCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria um novo template de fluxo KDS"""
    db_template = TemplateFluxoKDS(
        nome=template.nome,
        categoria=template.categoria,
        fluxo_config=json.dumps(template.fluxo_config),
        tempo_estimado=template.tempo_estimado,
        complexidade=template.complexidade,
        tags=json.dumps(template.tags) if template.tags else None,
        criado_por_id=template.criado_por_id
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/templates", response_model=List[TemplateFluxoKDSResponse])
def listar_templates_fluxo(
    categoria: Optional[str] = Query(None),
    complexidade: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista templates de fluxo com filtros opcionais"""
    query = db.query(TemplateFluxoKDS)
    
    if categoria:
        query = query.filter(TemplateFluxoKDS.categoria == categoria)
    if complexidade:
        query = query.filter(TemplateFluxoKDS.complexidade == complexidade)
    if ativo is not None:
        query = query.filter(TemplateFluxoKDS.ativo == ativo)
    
    templates = query.order_by(TemplateFluxoKDS.uso_count.desc()).all()
    
    # Converter JSON fields
    for template in templates:
        if isinstance(template.fluxo_config, str):
            template.fluxo_config = json.loads(template.fluxo_config)
        if isinstance(template.tags, str):
            template.tags = json.loads(template.tags) if template.tags else []
    
    return templates

@router.post("/templates/{template_id}/aplicar/{pedido_id}", response_model=FluxoKDSResponse)
async def aplicar_template_fluxo(
    template_id: int,
    pedido_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Aplica um template de fluxo a um pedido específico"""
    template = db.query(TemplateFluxoKDS).filter(
        TemplateFluxoKDS.id == template_id,
        TemplateFluxoKDS.ativo == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    pedido = db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Incrementar uso do template
    template.uso_count += 1
    
    # Criar fluxo baseado no template
    fluxo_config = json.loads(template.fluxo_config) if isinstance(template.fluxo_config, str) else template.fluxo_config
    
    novo_fluxo = FluxoKDS(
        nome=f"{template.nome} - Pedido #{pedido.numero_pedido}",
        descricao=f"Fluxo baseado no template {template.nome}",
        tipo=fluxo_config.get("tipo", "sequencial"),
        estacoes=json.dumps(fluxo_config.get("estacoes", [])),
        regras=json.dumps(fluxo_config.get("regras", {})),
        tempo_estimado_total=template.tempo_estimado
    )
    
    db.add(novo_fluxo)
    db.flush()
    
    # Criar etapas automaticamente
    estacoes = fluxo_config.get("estacoes", [])
    regras = fluxo_config.get("regras", {})
    
    for ordem, estacao_id in enumerate(estacoes):
        etapa = EtapaFluxoKDS(
            fluxo_id=novo_fluxo.id,
            pedido_id=pedido_id,
            estacao_id=estacao_id,
            ordem=ordem,
            tempo_estimado=regras.get(f"tempo_estacao_{estacao_id}", 15)
        )
        db.add(etapa)
    
    db.commit()
    db.refresh(novo_fluxo)
    
    # Converter para response format
    novo_fluxo.estacoes = json.loads(novo_fluxo.estacoes)
    novo_fluxo.regras = json.loads(novo_fluxo.regras) if novo_fluxo.regras else None
    
    return novo_fluxo

# ====== ENDPOINTS DE NOTIFICAÇÕES ======

@router.post("/notificacoes", response_model=NotificacaoKDSResponse)
async def criar_notificacao_kds(
    notificacao: NotificacaoKDSCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria uma nova notificação KDS"""
    db_notificacao = NotificacaoKDS(**notificacao.dict())
    db.add(db_notificacao)
    db.commit()
    db.refresh(db_notificacao)
    
    # Broadcast via WebSocket
    background_tasks.add_task(
        broadcast_notificacao,
        db_notificacao.estacao_id,
        db_notificacao.usuario_id,
        {
            "id": db_notificacao.id,
            "tipo": db_notificacao.tipo,
            "titulo": db_notificacao.titulo,
            "mensagem": db_notificacao.mensagem,
            "urgente": db_notificacao.urgente,
            "criado_em": db_notificacao.criado_em.isoformat()
        }
    )
    
    return db_notificacao

@router.get("/notificacoes", response_model=List[NotificacaoKDSResponse])
def listar_notificacoes_kds(
    estacao_id: Optional[int] = Query(None),
    usuario_id: Optional[int] = Query(None),
    lida: Optional[bool] = Query(None),
    urgente: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista notificações KDS com filtros opcionais"""
    query = db.query(NotificacaoKDS)
    
    if estacao_id:
        query = query.filter(NotificacaoKDS.estacao_id == estacao_id)
    if usuario_id:
        query = query.filter(NotificacaoKDS.usuario_id == usuario_id)
    if lida is not None:
        query = query.filter(NotificacaoKDS.lida == lida)
    if urgente is not None:
        query = query.filter(NotificacaoKDS.urgente == urgente)
    
    return query.order_by(NotificacaoKDS.criado_em.desc()).limit(limit).all()

@router.put("/notificacoes/{notificacao_id}/marcar-lida", response_model=NotificacaoKDSResponse)
def marcar_notificacao_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Marca uma notificação como lida"""
    notificacao = db.query(NotificacaoKDS).filter(
        NotificacaoKDS.id == notificacao_id
    ).first()
    
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    notificacao.lida = True
    notificacao.lida_em = datetime.now()
    
    db.commit()
    db.refresh(notificacao)
    return notificacao

# ====== ENDPOINTS DE ALERTAS ======

@router.get("/alertas", response_model=List[AlertaKDSResponse])
def listar_alertas_kds(
    estacao_id: Optional[int] = Query(None),
    severidade: Optional[SeveridadeAlerta] = Query(None),
    resolvido: Optional[bool] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista alertas KDS com filtros opcionais"""
    query = db.query(AlertaKDS)
    
    if estacao_id:
        query = query.filter(AlertaKDS.estacao_id == estacao_id)
    if severidade:
        query = query.filter(AlertaKDS.severidade == severidade)
    if resolvido is not None:
        query = query.filter(AlertaKDS.resolvido == resolvido)
    if tipo:
        query = query.filter(AlertaKDS.tipo == tipo)
    
    return query.order_by(AlertaKDS.criado_em.desc()).all()

@router.put("/alertas/{alerta_id}/resolver", response_model=AlertaKDSResponse)
def resolver_alerta_kds(
    alerta_id: int,
    notas_resolucao: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Resolve um alerta KDS"""
    alerta = db.query(AlertaKDS).filter(AlertaKDS.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    
    alerta.resolvido = True
    alerta.resolvido_por_id = current_user.id
    alerta.resolvido_em = datetime.now()
    alerta.notas_resolucao = notas_resolucao
    
    db.commit()
    db.refresh(alerta)
    return alerta

# ====== ENDPOINTS DE DASHBOARD E ANALYTICS ======

@router.get("/dashboard/metricas", response_model=DashboardKDSMetricas)
def obter_metricas_dashboard(
    periodo_horas: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém métricas consolidadas para dashboard KDS"""
    service = KDSAvancadoService(db)
    return service.gerar_dashboard_metricas(periodo_horas)

@router.get("/dashboard/resumo-operacional", response_model=ResumoOperacionalKDS)
def obter_resumo_operacional(
    periodo_horas: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém resumo operacional completo do KDS"""
    service = KDSAvancadoService(db)
    return service.gerar_resumo_operacional(periodo_horas)

@router.get("/dashboard/status-estacoes", response_model=List[EstacaoKDSStatus])
def obter_status_estacoes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém status detalhado de todas as estações KDS"""
    estacoes = db.query(EstacaoKDS).filter(EstacaoKDS.ativo == True).all()
    status_list = []
    
    for estacao in estacoes:
        # Contar pedidos na fila
        pedidos_fila = db.query(PedidoKDS).filter(
            PedidoKDS.estacao_id == estacao.id,
            PedidoKDS.status.in_(['pendente', 'em_preparo'])
        ).count()
        
        # Tempo médio atual (última hora)
        tempo_medio = db.query(
            func.avg(
                func.extract('epoch', 
                    PedidoKDS.finalizado_em - PedidoKDS.iniciado_em
                ) / 60
            )
        ).filter(
            PedidoKDS.estacao_id == estacao.id,
            PedidoKDS.status == 'entregue',
            PedidoKDS.finalizado_em >= datetime.now() - timedelta(hours=1),
            PedidoKDS.iniciado_em.isnot(None),
            PedidoKDS.finalizado_em.isnot(None)
        ).scalar()
        
        # Último pedido
        ultimo_pedido_query = db.query(PedidoKDS.created_at).filter(
            PedidoKDS.estacao_id == estacao.id
        ).order_by(PedidoKDS.created_at.desc()).first()
        ultimo_pedido = ultimo_pedido_query.created_at if ultimo_pedido_query else None
        
        # Alertas ativos
        alertas = db.query(AlertaKDS).filter(
            AlertaKDS.estacao_id == estacao.id,
            AlertaKDS.resolvido == False
        ).all()
        
        # Filas da estação
        filas = db.query(FilaKDS).filter(
            FilaKDS.estacao_id == estacao.id,
            FilaKDS.ativo == True
        ).all()
        
        status_list.append(EstacaoKDSStatus(
            estacao_id=estacao.id,
            nome=estacao.nome,
            status="ativa" if estacao.ativo else "inativa",
            filas=filas,
            pedidos_na_fila=pedidos_fila,
            tempo_medio_atual=float(tempo_medio) if tempo_medio else None,
            ultimo_pedido=ultimo_pedido,
            alertas_ativos=alertas,
            operadores_online=1  # Simplificado - seria obtido do sistema de sessões
        ))
    
    return status_list

# ====== ENDPOINTS DE AUTOMAÇÃO ======

@router.post("/automacao/verificar-alertas")
async def verificar_alertas_automaticos(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Executa verificação automática de alertas"""
    service = KDSAvancadoService(db)
    alertas_criados = service.verificar_alertas_automaticos()
    
    # Broadcast alertas via WebSocket
    for alerta in alertas_criados:
        background_tasks.add_task(
            broadcast_novo_alerta,
            alerta.estacao_id,
            {
                "id": alerta.id,
                "tipo": alerta.tipo,
                "severidade": alerta.severidade,
                "titulo": alerta.titulo,
                "criado_em": alerta.criado_em.isoformat()
            }
        )
    
    return {"alertas_criados": len(alertas_criados)}

@router.post("/automacao/processar-notificacoes")
async def processar_notificacoes_automaticas(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Processa notificações automáticas do sistema"""
    service = KDSAvancadoService(db)
    notificacoes_criadas = service.processar_notificacoes_automaticas()
    
    return {"notificacoes_criadas": len(notificacoes_criadas)}

# ====== BACKGROUND TASKS ======

async def notificar_nova_etapa(
    db: Session, 
    estacao_id: int, 
    pedido_id: int, 
    mensagem: str
):
    """Task em background para notificar nova etapa"""
    await manager.broadcast_to_channel(f"estacao_{estacao_id}", {
        "type": "nova_etapa",
        "pedido_id": pedido_id,
        "mensagem": mensagem,
        "timestamp": datetime.now().isoformat()
    })

async def broadcast_etapa_update(estacao_id: int, etapa_id: int, novo_status: str):
    """Broadcast de atualização de etapa via WebSocket"""
    await manager.broadcast_to_channel(f"estacao_{estacao_id}", {
        "type": "etapa_atualizada",
        "etapa_id": etapa_id,
        "novo_status": novo_status,
        "timestamp": datetime.now().isoformat()
    })

async def broadcast_notificacao(
    estacao_id: int, 
    usuario_id: Optional[int], 
    notificacao_data: Dict[str, Any]
):
    """Broadcast de notificação via WebSocket"""
    message = {
        "type": "nova_notificacao",
        "data": notificacao_data
    }
    
    await manager.broadcast_to_channel(f"estacao_{estacao_id}", message)
    await manager.broadcast_to_channel("alertas", message)
    
    if usuario_id:
        await manager.send_to_user(usuario_id, message)

async def broadcast_novo_alerta(estacao_id: int, alerta_data: Dict[str, Any]):
    """Broadcast de novo alerta via WebSocket"""
    message = {
        "type": "novo_alerta",
        "data": alerta_data
    }
    
    await manager.broadcast_to_channel(f"estacao_{estacao_id}", message)
    await manager.broadcast_to_channel("alertas", message)
    await manager.broadcast_to_channel("dashboard", message)