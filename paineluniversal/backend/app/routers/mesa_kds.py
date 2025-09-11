"""
Router FastAPI para Sistema de Mesas + KDS - Implementação Completa Meep
========================================================================

Endpoints completos para sistema avançado de gestão de mesas e cozinha 
baseado na engenharia reversa do sistema Meep.

Funcionalidades implementadas:
- CRUD completo para pedidos de mesa
- Sistema KDS (Kitchen Display System) para cozinha
- Notificações em tempo real
- Relatórios e analytics
- Dashboard operacional
- WebSockets para atualizações em tempo real
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json
import asyncio
from decimal import Decimal

# Imports do projeto
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..models_mesa_kds import (
    PedidoMesa, ItemPedidoMesa, EstacaoKDS, ConfiguracaoKDS, 
    NotificacaoKDS, RelatorioTempoMesa, LogEventoKDS
)
from ..schemas_mesa_kds import (
    # Schemas de Pedido
    PedidoMesaCreate, PedidoMesaUpdate, PedidoMesaResponse, PedidoMesaDetalhado,
    # Schemas de Item
    ItemPedidoMesaCreate, ItemPedidoMesaUpdate, ItemPedidoMesaResponse,
    # Schemas de KDS
    EstacaoKDSCreate, EstacaoKDSUpdate, EstacaoKDSResponse,
    ConfiguracaoKDSCreate, ConfiguracaoKDSUpdate, ConfiguracaoKDSResponse,
    # Schemas de Notificação
    NotificacaoKDSCreate, NotificacaoKDSUpdate, NotificacaoKDSResponse,
    # Schemas de Relatório
    RelatorioTempoMesaResponse, DashboardKDSResponse, EstatisticasEstacaoResponse,
    # Schemas de Filtro
    FiltrosPedidoMesa, FiltrosNotificacaoKDS, ParametrosPaginacao, RespostaPaginada,
    # Schemas de Ação
    AcaoStatusPedido, AcaoStatusItem, AcaoTransferirEstacao, ComandoKDS
)
from ..models_mesa_kds import (
    StatusPedidoMesa, StatusItemPedido, TipoNotificacaoKDS, 
    TipoEstacaoKDS, PrioridadePedido
)

router = APIRouter(prefix="/api/mesa-kds", tags=["Sistema Mesas + KDS"])

# ================================================================================
# WEBSOCKET MANAGER PARA TEMPO REAL
# ================================================================================

class WebSocketManager:
    """Gerenciador de conexões WebSocket para KDS"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.estacao_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, estacao_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if estacao_id:
            if estacao_id not in self.estacao_connections:
                self.estacao_connections[estacao_id] = []
            self.estacao_connections[estacao_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, estacao_id: Optional[int] = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if estacao_id and estacao_id in self.estacao_connections:
            if websocket in self.estacao_connections[estacao_id]:
                self.estacao_connections[estacao_id].remove(websocket)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remove conexões desconectadas
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
    async def broadcast_to_estacao(self, message: dict, estacao_id: int):
        if estacao_id not in self.estacao_connections:
            return
        
        disconnected = []
        for connection in self.estacao_connections[estacao_id]:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remove conexões desconectadas
        for conn in disconnected:
            if conn in self.estacao_connections[estacao_id]:
                self.estacao_connections[estacao_id].remove(conn)

websocket_manager = WebSocketManager()

# ================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================

def gerar_numero_pedido(mesa_numero: str, db: Session) -> str:
    """Gera número único para pedido"""
    hoje = datetime.now().strftime("%y%m%d")
    
    # Buscar último número do dia
    ultimo_pedido = db.query(PedidoMesa).filter(
        PedidoMesa.numero_pedido.like(f"M{mesa_numero}-{hoje}-%")
    ).order_by(desc(PedidoMesa.numero_pedido)).first()
    
    if ultimo_pedido:
        ultimo_num = int(ultimo_pedido.numero_pedido.split("-")[-1])
        proximo_num = ultimo_num + 1
    else:
        proximo_num = 1
    
    return f"M{mesa_numero}-{hoje}-{proximo_num:03d}"

async def criar_notificacao_kds(
    db: Session, 
    tipo: TipoNotificacaoKDS, 
    titulo: str, 
    mensagem: str,
    pedido_id: Optional[int] = None,
    estacao_id: Optional[int] = None,
    mesa_id: Optional[int] = None,
    urgencia: PrioridadePedido = PrioridadePedido.NORMAL
):
    """Cria notificação KDS e envia via WebSocket"""
    
    notificacao = NotificacaoKDS(
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        urgencia=urgencia,
        pedido_id=pedido_id,
        estacao_id=estacao_id,
        mesa_id=mesa_id
    )
    
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    
    # Enviar via WebSocket
    websocket_data = {
        "tipo": "nova_notificacao",
        "dados": {
            "id": notificacao.id,
            "tipo": notificacao.tipo.value,
            "titulo": notificacao.titulo,
            "mensagem": notificacao.mensagem,
            "urgencia": notificacao.urgencia.value,
            "data_criacao": notificacao.data_criacao.isoformat()
        }
    }
    
    if estacao_id:
        await websocket_manager.broadcast_to_estacao(websocket_data, estacao_id)
    else:
        await websocket_manager.broadcast(websocket_data)
    
    return notificacao

def criar_log_evento(
    db: Session,
    tipo_evento: str,
    descricao: str,
    usuario_id: int,
    pedido_id: Optional[int] = None,
    mesa_id: Optional[int] = None,
    estacao_id: Optional[int] = None,
    dados_antes: Optional[Dict] = None,
    dados_depois: Optional[Dict] = None
):
    """Cria log de evento para auditoria"""
    
    log = LogEventoKDS(
        tipo_evento=tipo_evento,
        descricao=descricao,
        usuario_id=usuario_id,
        pedido_id=pedido_id,
        mesa_id=mesa_id,
        estacao_id=estacao_id,
        dados_antes=dados_antes or {},
        dados_depois=dados_depois or {}
    )
    
    db.add(log)
    db.commit()
    return log

# ================================================================================
# ENDPOINTS WEBSOCKET
# ================================================================================

@router.websocket("/ws/kds")
async def websocket_kds_geral(websocket: WebSocket):
    """WebSocket para notificações gerais do KDS"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Manter conexão viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@router.websocket("/ws/kds/estacao/{estacao_id}")
async def websocket_kds_estacao(websocket: WebSocket, estacao_id: int):
    """WebSocket para notificações específicas de uma estação"""
    await websocket_manager.connect(websocket, estacao_id)
    try:
        while True:
            # Manter conexão viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, estacao_id)

# ================================================================================
# ENDPOINTS PARA PEDIDOS DE MESA
# ================================================================================

@router.post("/pedidos", response_model=PedidoMesaResponse)
async def criar_pedido_mesa(
    pedido: PedidoMesaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria novo pedido de mesa"""
    
    # Gerar número do pedido
    numero_pedido = gerar_numero_pedido(pedido.numero_mesa, db)
    
    db_pedido = PedidoMesa(
        numero_pedido=numero_pedido,
        usuario_criacao_id=current_user.id,
        **pedido.model_dump()
    )
    
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    
    # Criar notificação
    background_tasks.add_task(
        criar_notificacao_kds,
        db, TipoNotificacaoKDS.NOVO_PEDIDO,
        f"Novo Pedido Mesa {pedido.numero_mesa}",
        f"Pedido {numero_pedido} criado",
        db_pedido.id, None, pedido.mesa_id
    )
    
    # Log da ação
    criar_log_evento(
        db, "pedido_criado", f"Pedido {numero_pedido} criado",
        current_user.id, db_pedido.id, pedido.mesa_id
    )
    
    return db_pedido

@router.get("/pedidos", response_model=RespostaPaginada[PedidoMesaResponse])
def listar_pedidos_mesa(
    filtros: FiltrosPedidoMesa = Depends(),
    paginacao: ParametrosPaginacao = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista pedidos de mesa com filtros"""
    
    query = db.query(PedidoMesa)
    
    # Aplicar filtros
    if filtros.status:
        query = query.filter(PedidoMesa.status.in_(filtros.status))
    
    if filtros.prioridade:
        query = query.filter(PedidoMesa.prioridade.in_(filtros.prioridade))
    
    if filtros.mesa_id:
        query = query.filter(PedidoMesa.mesa_id.in_(filtros.mesa_id))
    
    if filtros.data_inicio:
        query = query.filter(PedidoMesa.data_pedido >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(PedidoMesa.data_pedido <= filtros.data_fim)
    
    if filtros.modo_pedido:
        query = query.filter(PedidoMesa.modo_pedido.in_(filtros.modo_pedido))
    
    if filtros.estacao_responsavel:
        query = query.filter(PedidoMesa.estacao_responsavel.in_(filtros.estacao_responsavel))
    
    if filtros.atrasados_apenas:
        agora = datetime.now()
        query = query.filter(
            and_(
                PedidoMesa.status.in_([StatusPedidoMesa.CONFIRMADO, StatusPedidoMesa.PREPARANDO]),
                func.extract('epoch', agora - PedidoMesa.data_pedido) / 60 > PedidoMesa.tempo_estimado_preparo
            )
        )
    
    if filtros.empresa_id:
        query = query.filter(PedidoMesa.empresa_id == filtros.empresa_id)
    
    if filtros.evento_id:
        query = query.filter(PedidoMesa.evento_id == filtros.evento_id)
    
    # Contar total
    total = query.count()
    
    # Aplicar ordenação
    if hasattr(PedidoMesa, paginacao.ordenar_por):
        campo_ordem = getattr(PedidoMesa, paginacao.ordenar_por)
        if paginacao.ordem_desc:
            query = query.order_by(desc(campo_ordem))
        else:
            query = query.order_by(asc(campo_ordem))
    
    # Aplicar paginação
    offset = (paginacao.page - 1) * paginacao.size
    pedidos = query.offset(offset).limit(paginacao.size).all()
    
    # Calcular informações de paginação
    total_pages = (total + paginacao.size - 1) // paginacao.size
    
    return RespostaPaginada(
        items=pedidos,
        total=total,
        page=paginacao.page,
        size=paginacao.size,
        pages=total_pages,
        has_next=paginacao.page < total_pages,
        has_prev=paginacao.page > 1
    )

@router.get("/pedidos/{pedido_id}", response_model=PedidoMesaDetalhado)
def obter_pedido_mesa(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém detalhes completos de um pedido"""
    
    pedido = db.query(PedidoMesa).options(
        joinedload(PedidoMesa.itens),
        joinedload(PedidoMesa.notificacoes)
    ).filter(PedidoMesa.id == pedido_id).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Calcular tempo decorrido
    tempo_decorrido = None
    if pedido.data_pedido:
        tempo_decorrido = int((datetime.now() - pedido.data_pedido).total_seconds() / 60)
    
    # Calcular atraso estimado
    atraso_estimado = None
    if tempo_decorrido and pedido.tempo_estimado_preparo:
        if tempo_decorrido > pedido.tempo_estimado_preparo:
            atraso_estimado = tempo_decorrido - pedido.tempo_estimado_preparo
    
    # Adicionar campos calculados
    pedido_dict = PedidoMesaDetalhado.model_validate(pedido).model_dump()
    pedido_dict['tempo_decorrido'] = tempo_decorrido
    pedido_dict['atraso_estimado'] = atraso_estimado
    
    return pedido_dict

@router.patch("/pedidos/{pedido_id}", response_model=PedidoMesaResponse)
async def atualizar_pedido_mesa(
    pedido_id: int,
    atualizacao: PedidoMesaUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza pedido de mesa"""
    
    pedido = db.query(PedidoMesa).filter(PedidoMesa.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Armazenar estado anterior para log
    dados_antes = {
        "status": pedido.status.value if pedido.status else None,
        "prioridade": pedido.prioridade.value if pedido.prioridade else None
    }
    
    # Atualizar campos
    for campo, valor in atualizacao.model_dump(exclude_unset=True).items():
        setattr(pedido, campo, valor)
    
    db.commit()
    db.refresh(pedido)
    
    # Estado após alteração
    dados_depois = {
        "status": pedido.status.value if pedido.status else None,
        "prioridade": pedido.prioridade.value if pedido.prioridade else None
    }
    
    # Log da alteração
    criar_log_evento(
        db, "pedido_atualizado", f"Pedido {pedido.numero_pedido} atualizado",
        current_user.id, pedido.id, pedido.mesa_id, None, dados_antes, dados_depois
    )
    
    return pedido

@router.post("/pedidos/{pedido_id}/status", response_model=PedidoMesaResponse)
async def alterar_status_pedido(
    pedido_id: int,
    acao: AcaoStatusPedido,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Altera status do pedido com notificações automáticas"""
    
    pedido = db.query(PedidoMesa).filter(PedidoMesa.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    status_anterior = pedido.status
    pedido.status = acao.novo_status
    
    # Atualizar timestamps baseado no status
    agora = datetime.now()
    if acao.novo_status == StatusPedidoMesa.CONFIRMADO:
        pedido.data_confirmacao = agora
        pedido.usuario_confirmacao_id = acao.usuario_id
    elif acao.novo_status == StatusPedidoMesa.PREPARANDO:
        pedido.data_inicio_preparo = agora
    elif acao.novo_status == StatusPedidoMesa.PRONTO:
        pedido.data_conclusao = agora
    elif acao.novo_status == StatusPedidoMesa.ENTREGUE:
        pedido.data_entrega = agora
        pedido.usuario_entrega_id = acao.usuario_id
    
    db.commit()
    db.refresh(pedido)
    
    # Criar notificação baseada no novo status
    mensagens_status = {
        StatusPedidoMesa.CONFIRMADO: f"Pedido {pedido.numero_pedido} confirmado",
        StatusPedidoMesa.PREPARANDO: f"Pedido {pedido.numero_pedido} em preparo",
        StatusPedidoMesa.PRONTO: f"Pedido {pedido.numero_pedido} pronto para entrega",
        StatusPedidoMesa.ENTREGUE: f"Pedido {pedido.numero_pedido} entregue",
        StatusPedidoMesa.CANCELADO: f"Pedido {pedido.numero_pedido} cancelado"
    }
    
    if acao.novo_status in mensagens_status:
        background_tasks.add_task(
            criar_notificacao_kds,
            db, TipoNotificacaoKDS.SISTEMA,
            f"Status Alterado - Mesa {pedido.numero_mesa}",
            mensagens_status[acao.novo_status],
            pedido.id, None, pedido.mesa_id
        )
    
    # Log da alteração
    criar_log_evento(
        db, "status_alterado", 
        f"Status do pedido {pedido.numero_pedido} alterado de {status_anterior.value} para {acao.novo_status.value}",
        acao.usuario_id, pedido.id, pedido.mesa_id
    )
    
    return pedido

# ================================================================================
# ENDPOINTS PARA ITENS DE PEDIDO
# ================================================================================

@router.post("/pedidos/{pedido_id}/itens", response_model=ItemPedidoMesaResponse)
async def adicionar_item_pedido(
    pedido_id: int,
    item: ItemPedidoMesaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Adiciona item ao pedido"""
    
    # Verificar se pedido existe
    pedido = db.query(PedidoMesa).filter(PedidoMesa.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Calcular valor total do item
    valor_total = item.quantidade * item.valor_unitario
    
    db_item = ItemPedidoMesa(
        pedido_id=pedido_id,
        valor_total=valor_total,
        **item.model_dump(exclude={'pedido_id'})
    )
    
    db.add(db_item)
    
    # Atualizar total do pedido
    pedido.valor_subtotal += valor_total
    pedido.valor_total = pedido.valor_subtotal + pedido.valor_acrescimo - pedido.valor_desconto
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.get("/pedidos/{pedido_id}/itens", response_model=List[ItemPedidoMesaResponse])
def listar_itens_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista itens do pedido"""
    
    itens = db.query(ItemPedidoMesa).filter(ItemPedidoMesa.pedido_id == pedido_id).all()
    return itens

@router.patch("/itens/{item_id}/status", response_model=ItemPedidoMesaResponse)
async def alterar_status_item(
    item_id: int,
    acao: AcaoStatusItem,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Altera status de item específico"""
    
    item = db.query(ItemPedidoMesa).filter(ItemPedidoMesa.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    status_anterior = item.status
    item.status = acao.novo_status
    
    # Atualizar timestamps
    agora = datetime.now()
    if acao.novo_status == StatusItemPedido.PREPARANDO:
        item.data_inicio_preparo = agora
        item.responsavel_preparo_id = acao.usuario_id
    elif acao.novo_status == StatusItemPedido.PRONTO:
        item.data_conclusao_preparo = agora
    elif acao.novo_status == StatusItemPedido.ENTREGUE:
        item.data_entrega = agora
        item.responsavel_entrega_id = acao.usuario_id
    
    db.commit()
    db.refresh(item)
    
    return item

# ================================================================================
# ENDPOINTS PARA ESTAÇÕES KDS
# ================================================================================

@router.post("/estacoes", response_model=EstacaoKDSResponse)
def criar_estacao_kds(
    estacao: EstacaoKDSCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria nova estação KDS"""
    
    db_estacao = EstacaoKDS(**estacao.model_dump())
    db.add(db_estacao)
    db.commit()
    db.refresh(db_estacao)
    
    return db_estacao

@router.get("/estacoes", response_model=List[EstacaoKDSResponse])
def listar_estacoes_kds(
    ativas_apenas: bool = Query(True, description="Listar apenas estações ativas"),
    empresa_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista estações KDS"""
    
    query = db.query(EstacaoKDS)
    
    if ativas_apenas:
        query = query.filter(EstacaoKDS.ativa == True)
    
    if empresa_id:
        query = query.filter(EstacaoKDS.empresa_id == empresa_id)
    
    return query.order_by(EstacaoKDS.posicao_ordem).all()

@router.get("/estacoes/{estacao_id}/estatisticas", response_model=EstatisticasEstacaoResponse)
def obter_estatisticas_estacao(
    estacao_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém estatísticas de uma estação específica"""
    
    estacao = db.query(EstacaoKDS).filter(EstacaoKDS.id == estacao_id).first()
    if not estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    
    hoje = date.today()
    
    # Contar pedidos por status
    pedidos_pendentes = db.query(PedidoMesa).filter(
        and_(
            PedidoMesa.estacao_responsavel == estacao.tipo,
            PedidoMesa.status == StatusPedidoMesa.PENDENTE
        )
    ).count()
    
    pedidos_preparando = db.query(PedidoMesa).filter(
        and_(
            PedidoMesa.estacao_responsavel == estacao.tipo,
            PedidoMesa.status == StatusPedidoMesa.PREPARANDO
        )
    ).count()
    
    pedidos_concluidos_hoje = db.query(PedidoMesa).filter(
        and_(
            PedidoMesa.estacao_responsavel == estacao.tipo,
            PedidoMesa.status.in_([StatusPedidoMesa.PRONTO, StatusPedidoMesa.ENTREGUE]),
            func.date(PedidoMesa.data_conclusao) == hoje
        )
    ).count()
    
    # Calcular tempo médio de preparo (últimos 30 dias)
    tempo_medio = db.query(
        func.avg(
            func.extract('epoch', PedidoMesa.data_conclusao - PedidoMesa.data_inicio_preparo) / 60
        )
    ).filter(
        and_(
            PedidoMesa.estacao_responsavel == estacao.tipo,
            PedidoMesa.data_conclusao.isnot(None),
            PedidoMesa.data_inicio_preparo.isnot(None),
            PedidoMesa.data_conclusao >= datetime.now() - timedelta(days=30)
        )
    ).scalar() or 0
    
    # Calcular eficiência (pedidos no prazo / total)
    total_com_tempo = db.query(PedidoMesa).filter(
        and_(
            PedidoMesa.estacao_responsavel == estacao.tipo,
            PedidoMesa.data_conclusao.isnot(None),
            PedidoMesa.tempo_estimado_preparo > 0,
            func.date(PedidoMesa.data_conclusao) == hoje
        )
    ).count()
    
    no_prazo = db.query(PedidoMesa).filter(
        and_(
            PedidoMesa.estacao_responsavel == estacao.tipo,
            PedidoMesa.data_conclusao.isnot(None),
            PedidoMesa.tempo_estimado_preparo > 0,
            func.date(PedidoMesa.data_conclusao) == hoje,
            func.extract('epoch', PedidoMesa.data_conclusao - PedidoMesa.data_inicio_preparo) / 60 <= PedidoMesa.tempo_estimado_preparo
        )
    ).count()
    
    eficiencia = Decimal(str((no_prazo / total_com_tempo * 100) if total_com_tempo > 0 else 0))
    
    # Calcular capacidade utilizada
    total_pedidos_ativos = pedidos_pendentes + pedidos_preparando
    capacidade_utilizada = Decimal(str((total_pedidos_ativos / estacao.capacidade_maxima_pedidos * 100)))
    
    return EstatisticasEstacaoResponse(
        estacao_id=estacao.id,
        nome_estacao=estacao.nome,
        tipo_estacao=estacao.tipo,
        pedidos_pendentes=pedidos_pendentes,
        pedidos_preparando=pedidos_preparando,
        pedidos_concluidos_hoje=pedidos_concluidos_hoje,
        tempo_medio_preparo=int(tempo_medio),
        eficiencia_percentual=eficiencia,
        capacidade_utilizada=capacidade_utilizada
    )

# ================================================================================
# ENDPOINTS PARA DASHBOARD E RELATÓRIOS
# ================================================================================

@router.get("/dashboard", response_model=DashboardKDSResponse)
def obter_dashboard_kds(
    empresa_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    evento_id: Optional[int] = Query(None, description="Filtrar por evento"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém dados do dashboard KDS"""
    
    # Filtros base
    filtros_base = []
    if empresa_id:
        filtros_base.append(PedidoMesa.empresa_id == empresa_id)
    if evento_id:
        filtros_base.append(PedidoMesa.evento_id == evento_id)
    
    # Contar pedidos por status
    total_pendentes = db.query(PedidoMesa).filter(
        and_(PedidoMesa.status == StatusPedidoMesa.PENDENTE, *filtros_base)
    ).count()
    
    total_preparando = db.query(PedidoMesa).filter(
        and_(PedidoMesa.status == StatusPedidoMesa.PREPARANDO, *filtros_base)
    ).count()
    
    total_prontos = db.query(PedidoMesa).filter(
        and_(PedidoMesa.status == StatusPedidoMesa.PRONTO, *filtros_base)
    ).count()
    
    # Contar pedidos atrasados
    agora = datetime.now()
    pedidos_atrasados = db.query(PedidoMesa).filter(
        and_(
            PedidoMesa.status.in_([StatusPedidoMesa.CONFIRMADO, StatusPedidoMesa.PREPARANDO]),
            func.extract('epoch', agora - PedidoMesa.data_pedido) / 60 > PedidoMesa.tempo_estimado_preparo,
            *filtros_base
        )
    ).count()
    
    # Calcular tempo médio de preparo (hoje)
    hoje = date.today()
    tempo_medio = db.query(
        func.avg(
            func.extract('epoch', PedidoMesa.data_conclusao - PedidoMesa.data_inicio_preparo) / 60
        )
    ).filter(
        and_(
            PedidoMesa.data_conclusao.isnot(None),
            PedidoMesa.data_inicio_preparo.isnot(None),
            func.date(PedidoMesa.data_conclusao) == hoje,
            *filtros_base
        )
    ).scalar() or 0
    
    # Contar estações ativas
    estacoes_ativas = db.query(EstacaoKDS).filter(EstacaoKDS.ativa == True).count()
    
    # Contar notificações não lidas
    notificacoes_nao_lidas = db.query(NotificacaoKDS).filter(
        NotificacaoKDS.lida == False
    ).count()
    
    # Contar mesas ocupadas (com pedidos ativos)
    mesas_ocupadas = db.query(PedidoMesa.mesa_id).filter(
        and_(
            PedidoMesa.status.in_([
                StatusPedidoMesa.PENDENTE, 
                StatusPedidoMesa.CONFIRMADO, 
                StatusPedidoMesa.PREPARANDO,
                StatusPedidoMesa.PRONTO
            ]),
            *filtros_base
        )
    ).distinct().count()
    
    return DashboardKDSResponse(
        total_pedidos_pendentes=total_pendentes,
        total_pedidos_preparando=total_preparando,
        total_pedidos_prontos=total_prontos,
        pedidos_atrasados=pedidos_atrasados,
        tempo_medio_preparo=int(tempo_medio),
        estacoes_ativas=estacoes_ativas,
        notificacoes_nao_lidas=notificacoes_nao_lidas,
        mesas_ocupadas=mesas_ocupadas,
        ultima_atualizacao=datetime.now()
    )

@router.get("/relatorios/tempo-mesa", response_model=List[RelatorioTempoMesaResponse])
def gerar_relatorio_tempo_mesa(
    data_inicio: date = Query(..., description="Data de início"),
    data_fim: date = Query(..., description="Data de fim"),
    mesa_id: Optional[int] = Query(None, description="ID da mesa específica"),
    empresa_id: Optional[int] = Query(None, description="ID da empresa"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Gera relatório de tempo e performance das mesas"""
    
    # Validar datas
    if data_fim < data_inicio:
        raise HTTPException(status_code=400, detail="Data fim deve ser posterior à data início")
    
    # Construir filtros
    filtros = [
        func.date(PedidoMesa.data_pedido) >= data_inicio,
        func.date(PedidoMesa.data_pedido) <= data_fim
    ]
    
    if mesa_id:
        filtros.append(PedidoMesa.mesa_id == mesa_id)
    
    if empresa_id:
        filtros.append(PedidoMesa.empresa_id == empresa_id)
    
    # Query agregada por mesa
    resultado = db.query(
        PedidoMesa.mesa_id,
        PedidoMesa.numero_mesa,
        func.count(PedidoMesa.id).label('total_pedidos'),
        func.avg(
            func.extract('epoch', PedidoMesa.data_conclusao - PedidoMesa.data_inicio_preparo) / 60
        ).label('tempo_medio_preparo'),
        func.avg(
            func.extract('epoch', PedidoMesa.data_entrega - PedidoMesa.data_pedido) / 60
        ).label('tempo_medio_entrega'),
        func.sum(PedidoMesa.valor_total).label('faturamento_total'),
        func.avg(PedidoMesa.valor_total).label('ticket_medio'),
        func.sum(
            func.case(
                (PedidoMesa.status.in_([StatusPedidoMesa.PRONTO, StatusPedidoMesa.ENTREGUE]), 1),
                else_=0
            )
        ).label('pedidos_no_prazo'),
        func.sum(
            func.case(
                (PedidoMesa.status == StatusPedidoMesa.CANCELADO, 1),
                else_=0
            )
        ).label('pedidos_cancelados')
    ).filter(
        and_(*filtros)
    ).group_by(
        PedidoMesa.mesa_id, PedidoMesa.numero_mesa
    ).all()
    
    # Converter para formato de resposta
    relatorios = []
    for row in resultado:
        pedidos_atrasados = max(0, row.total_pedidos - row.pedidos_no_prazo - row.pedidos_cancelados)
        taxa_sucesso = Decimal(str((row.pedidos_no_prazo / row.total_pedidos * 100) if row.total_pedidos > 0 else 0))
        
        relatorio = RelatorioTempoMesaResponse(
            id=0,  # Relatório dinâmico
            data_inicio=data_inicio,
            data_fim=data_fim,
            mesa_id=row.mesa_id,
            numero_mesa=row.numero_mesa,
            tempo_medio_preparo=int(row.tempo_medio_preparo or 0),
            tempo_medio_entrega=int(row.tempo_medio_entrega or 0),
            tempo_medio_ocupacao=0,  # Calcular se necessário
            tempo_total_ocupada=0,   # Calcular se necessário
            total_pedidos=row.total_pedidos,
            pedidos_no_prazo=row.pedidos_no_prazo,
            pedidos_atrasados=pedidos_atrasados,
            pedidos_cancelados=row.pedidos_cancelados,
            faturamento_total=row.faturamento_total or Decimal('0'),
            ticket_medio=row.ticket_medio or Decimal('0'),
            taxa_ocupacao=Decimal('0'),  # Calcular se necessário
            taxa_sucesso=taxa_sucesso,
            indice_satisfacao=Decimal('0'),  # Implementar se tiver sistema de feedback
            empresa_id=empresa_id or 0,
            evento_id=None,
            gerado_em=datetime.now()
        )
        
        relatorios.append(relatorio)
    
    return relatorios

# ================================================================================
# ENDPOINTS PARA NOTIFICAÇÕES
# ================================================================================

@router.get("/notificacoes", response_model=RespostaPaginada[NotificacaoKDSResponse])
def listar_notificacoes_kds(
    filtros: FiltrosNotificacaoKDS = Depends(),
    paginacao: ParametrosPaginacao = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista notificações do KDS com filtros"""
    
    query = db.query(NotificacaoKDS)
    
    # Aplicar filtros
    if filtros.tipo:
        query = query.filter(NotificacaoKDS.tipo.in_(filtros.tipo))
    
    if filtros.urgencia:
        query = query.filter(NotificacaoKDS.urgencia.in_(filtros.urgencia))
    
    if filtros.lida is not None:
        query = query.filter(NotificacaoKDS.lida == filtros.lida)
    
    if filtros.estacao_id:
        query = query.filter(NotificacaoKDS.estacao_id.in_(filtros.estacao_id))
    
    if filtros.data_inicio:
        query = query.filter(NotificacaoKDS.data_criacao >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(NotificacaoKDS.data_criacao <= filtros.data_fim)
    
    if filtros.apenas_ativas:
        agora = datetime.now()
        query = query.filter(
            or_(
                NotificacaoKDS.data_expiracao.is_(None),
                NotificacaoKDS.data_expiracao > agora
            )
        )
    
    # Contar total
    total = query.count()
    
    # Aplicar ordenação (padrão: mais recentes primeiro)
    query = query.order_by(desc(NotificacaoKDS.data_criacao))
    
    # Aplicar paginação
    offset = (paginacao.page - 1) * paginacao.size
    notificacoes = query.offset(offset).limit(paginacao.size).all()
    
    # Calcular informações de paginação
    total_pages = (total + paginacao.size - 1) // paginacao.size
    
    return RespostaPaginada(
        items=notificacoes,
        total=total,
        page=paginacao.page,
        size=paginacao.size,
        pages=total_pages,
        has_next=paginacao.page < total_pages,
        has_prev=paginacao.page > 1
    )

@router.patch("/notificacoes/{notificacao_id}/marcar-lida", response_model=NotificacaoKDSResponse)
def marcar_notificacao_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Marca notificação como lida"""
    
    notificacao = db.query(NotificacaoKDS).filter(NotificacaoKDS.id == notificacao_id).first()
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    notificacao.lida = True
    notificacao.data_leitura = datetime.now()
    notificacao.usuario_leitura_id = current_user.id
    
    db.commit()
    db.refresh(notificacao)
    
    return notificacao

# ================================================================================
# ENDPOINTS DE AÇÕES ESPECIAIS
# ================================================================================

@router.post("/pedidos/{pedido_id}/transferir-estacao", response_model=PedidoMesaResponse)
async def transferir_pedido_estacao(
    pedido_id: int,
    acao: AcaoTransferirEstacao,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Transfere pedido para outra estação"""
    
    pedido = db.query(PedidoMesa).filter(PedidoMesa.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    estacao_anterior = pedido.estacao_responsavel
    pedido.estacao_responsavel = acao.nova_estacao
    
    db.commit()
    db.refresh(pedido)
    
    # Criar notificação de transferência
    background_tasks.add_task(
        criar_notificacao_kds,
        db, TipoNotificacaoKDS.SISTEMA,
        f"Pedido Transferido - {pedido.numero_pedido}",
        f"Pedido transferido de {estacao_anterior.value} para {acao.nova_estacao.value}. Motivo: {acao.motivo}",
        pedido.id
    )
    
    # Log da transferência
    criar_log_evento(
        db, "pedido_transferido",
        f"Pedido {pedido.numero_pedido} transferido de {estacao_anterior.value} para {acao.nova_estacao.value}",
        acao.usuario_id, pedido.id, pedido.mesa_id
    )
    
    return pedido

@router.post("/kds/comando", response_model=Dict[str, Any])
async def executar_comando_kds(
    comando: ComandoKDS,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Executa comandos especiais do KDS"""
    
    resultado = {"sucesso": False, "mensagem": ""}
    
    if comando.comando == "pausar_todas_estacoes":
        # Implementar lógica para pausar todas as estações
        resultado = {"sucesso": True, "mensagem": "Todas as estações foram pausadas"}
        
    elif comando.comando == "reativar_todas_estacoes":
        # Implementar lógica para reativar todas as estações
        resultado = {"sucesso": True, "mensagem": "Todas as estações foram reativadas"}
        
    elif comando.comando == "limpar_notificacoes_antigas":
        # Limpar notificações antigas
        dias_limite = comando.parametros.get("dias", 7)
        data_limite = datetime.now() - timedelta(days=dias_limite)
        
        deletadas = db.query(NotificacaoKDS).filter(
            and_(
                NotificacaoKDS.lida == True,
                NotificacaoKDS.data_criacao < data_limite
            )
        ).delete()
        
        db.commit()
        resultado = {"sucesso": True, "mensagem": f"{deletadas} notificações antigas removidas"}
        
    else:
        raise HTTPException(status_code=400, detail="Comando não reconhecido")
    
    # Log do comando
    criar_log_evento(
        db, f"comando_kds_{comando.comando}",
        f"Comando KDS executado: {comando.comando}",
        comando.usuario_id
    )
    
    return resultado
