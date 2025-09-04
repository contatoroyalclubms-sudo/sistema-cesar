from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import json
from datetime import datetime

from ..database import get_db
from ..models_clean import EstacaoKDS, PedidoKDS, ItemPedidoKDS, StatusPedidoKDS, TipoEstacaoKDS
from ..schemas_kds_mesas import (
    EstacaoKDSCreate, EstacaoKDSUpdate, EstacaoKDSResponse,
    PedidoKDSCreate, PedidoKDSUpdate, PedidoKDSResponse,
    ItemPedidoKDSCreate, ItemPedidoKDSUpdate, ItemPedidoKDSResponse
)
from ..auth import get_current_user

router = APIRouter(tags=["KDS"])

# WebSocket connection manager
class KDSConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connections_by_station: dict = {}

    async def connect(self, websocket: WebSocket, station_id: int = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if station_id:
            if station_id not in self.connections_by_station:
                self.connections_by_station[station_id] = []
            self.connections_by_station[station_id].append(websocket)

    def disconnect(self, websocket: WebSocket, station_id: int = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if station_id and station_id in self.connections_by_station:
            if websocket in self.connections_by_station[station_id]:
                self.connections_by_station[station_id].remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.active_connections.remove(connection)

    async def broadcast_to_station(self, station_id: int, message: dict):
        if station_id in self.connections_by_station:
            for connection in self.connections_by_station[station_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    self.connections_by_station[station_id].remove(connection)

manager = KDSConnectionManager()

# WebSocket endpoint
@router.websocket("/ws/{station_id}")
async def websocket_endpoint(websocket: WebSocket, station_id: int):
    await manager.connect(websocket, station_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Broadcast update to all connections in this station
            await manager.broadcast_to_station(station_id, {
                "type": "update",
                "station_id": station_id,
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, station_id)

# Estações KDS
@router.post("/estacoes", response_model=EstacaoKDSResponse)
def create_estacao(
    estacao: EstacaoKDSCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_estacao = EstacaoKDS(**estacao.dict())
    db.add(db_estacao)
    db.commit()
    db.refresh(db_estacao)
    return db_estacao

@router.get("/estacoes", response_model=List[EstacaoKDSResponse])
def list_estacoes(
    evento_id: Optional[int] = Query(None),
    tipo: Optional[TipoEstacaoKDS] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(EstacaoKDS)
    
    if evento_id:
        query = query.filter(EstacaoKDS.evento_id == evento_id)
    if tipo:
        query = query.filter(EstacaoKDS.tipo == tipo)
    if ativo is not None:
        query = query.filter(EstacaoKDS.ativo == ativo)
        
    return query.all()

@router.get("/estacoes/{estacao_id}", response_model=EstacaoKDSResponse)
def get_estacao(
    estacao_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    estacao = db.query(EstacaoKDS).filter(EstacaoKDS.id == estacao_id).first()
    if not estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    return estacao

@router.put("/estacoes/{estacao_id}", response_model=EstacaoKDSResponse)
def update_estacao(
    estacao_id: int,
    estacao_update: EstacaoKDSUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    estacao = db.query(EstacaoKDS).filter(EstacaoKDS.id == estacao_id).first()
    if not estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    
    for key, value in estacao_update.dict(exclude_unset=True).items():
        setattr(estacao, key, value)
    
    db.commit()
    db.refresh(estacao)
    return estacao

@router.delete("/estacoes/{estacao_id}")
def delete_estacao(
    estacao_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    estacao = db.query(EstacaoKDS).filter(EstacaoKDS.id == estacao_id).first()
    if not estacao:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    
    db.delete(estacao)
    db.commit()
    return {"message": "Estação excluída com sucesso"}

# Pedidos KDS
@router.post("/pedidos", response_model=PedidoKDSResponse)
async def create_pedido(
    pedido: PedidoKDSCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_pedido = PedidoKDS(**pedido.dict())
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    
    # Broadcast new order to relevant stations
    await manager.broadcast({
        "type": "new_order",
        "pedido_id": db_pedido.id,
        "estacao_id": db_pedido.estacao_id,
        "data": {
            "id": db_pedido.id,
            "numero_pedido": db_pedido.numero_pedido,
            "status": db_pedido.status.value,
            "tempo_estimado": db_pedido.tempo_estimado_minutos,
            "created_at": db_pedido.created_at.isoformat()
        }
    })
    
    return db_pedido

@router.get("/pedidos", response_model=List[PedidoKDSResponse])
def list_pedidos(
    estacao_id: Optional[int] = Query(None),
    status: Optional[StatusPedidoKDS] = Query(None),
    numero_pedido: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(PedidoKDS)
    
    if estacao_id:
        query = query.filter(PedidoKDS.estacao_id == estacao_id)
    if status:
        query = query.filter(PedidoKDS.status == status)
    if numero_pedido:
        query = query.filter(PedidoKDS.numero_pedido.ilike(f"%{numero_pedido}%"))
        
    return query.order_by(PedidoKDS.created_at.desc()).all()

@router.get("/pedidos/{pedido_id}", response_model=PedidoKDSResponse)
def get_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pedido = db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

@router.put("/pedidos/{pedido_id}", response_model=PedidoKDSResponse)
async def update_pedido(
    pedido_id: int,
    pedido_update: PedidoKDSUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pedido = db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    old_status = pedido.status
    
    for key, value in pedido_update.dict(exclude_unset=True).items():
        setattr(pedido, key, value)
    
    # Update timestamps based on status changes
    if hasattr(pedido_update, 'status') and pedido_update.status:
        if pedido_update.status == StatusPedidoKDS.EM_PREPARO and old_status != StatusPedidoKDS.EM_PREPARO:
            pedido.iniciado_em = datetime.now()
        elif pedido_update.status == StatusPedidoKDS.PRONTO and old_status != StatusPedidoKDS.PRONTO:
            pedido.finalizado_em = datetime.now()
        elif pedido_update.status == StatusPedidoKDS.ENTREGUE and old_status != StatusPedidoKDS.ENTREGUE:
            pedido.entregue_em = datetime.now()
    
    db.commit()
    db.refresh(pedido)
    
    # Broadcast status change
    await manager.broadcast_to_station(pedido.estacao_id, {
        "type": "status_change",
        "pedido_id": pedido.id,
        "old_status": old_status.value if old_status else None,
        "new_status": pedido.status.value,
        "timestamp": datetime.now().isoformat()
    })
    
    return pedido

@router.delete("/pedidos/{pedido_id}")
def delete_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pedido = db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    db.delete(pedido)
    db.commit()
    return {"message": "Pedido excluído com sucesso"}

# Itens do Pedido KDS
@router.post("/pedidos/{pedido_id}/itens", response_model=ItemPedidoKDSResponse)
async def create_item_pedido(
    pedido_id: int,
    item: ItemPedidoKDSCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verify pedido exists
    pedido = db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    db_item = ItemPedidoKDS(pedido_id=pedido_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Broadcast new item
    await manager.broadcast_to_station(pedido.estacao_id, {
        "type": "new_item",
        "pedido_id": pedido_id,
        "item_id": db_item.id,
        "data": {
            "id": db_item.id,
            "produto_nome": db_item.produto_nome,
            "quantidade": db_item.quantidade,
            "observacoes": db_item.observacoes
        }
    })
    
    return db_item

@router.get("/pedidos/{pedido_id}/itens", response_model=List[ItemPedidoKDSResponse])
def list_itens_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(ItemPedidoKDS).filter(ItemPedidoKDS.pedido_id == pedido_id).all()

@router.put("/itens/{item_id}", response_model=ItemPedidoKDSResponse)
async def update_item_pedido(
    item_id: int,
    item_update: ItemPedidoKDSUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    item = db.query(ItemPedidoKDS).filter(ItemPedidoKDS.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    
    # Get pedido to broadcast to correct station
    pedido = db.query(PedidoKDS).filter(PedidoKDS.id == item.pedido_id).first()
    if pedido:
        await manager.broadcast_to_station(pedido.estacao_id, {
            "type": "item_update",
            "pedido_id": item.pedido_id,
            "item_id": item.id,
            "data": {
                "id": item.id,
                "produto_nome": item.produto_nome,
                "quantidade": item.quantidade,
                "observacoes": item.observacoes,
                "pronto": item.pronto
            }
        })
    
    return item

@router.delete("/itens/{item_id}")
def delete_item_pedido(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    item = db.query(ItemPedidoKDS).filter(ItemPedidoKDS.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    db.delete(item)
    db.commit()
    return {"message": "Item excluído com sucesso"}

# Analytics endpoints
@router.get("/analytics/tempos-preparo")
def get_analytics_tempos_preparo(
    estacao_id: Optional[int] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(PedidoKDS).filter(
        PedidoKDS.status == StatusPedidoKDS.ENTREGUE,
        PedidoKDS.iniciado_em.isnot(None),
        PedidoKDS.finalizado_em.isnot(None)
    )
    
    if estacao_id:
        query = query.filter(PedidoKDS.estacao_id == estacao_id)
        
    if data_inicio:
        query = query.filter(PedidoKDS.created_at >= datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(PedidoKDS.created_at <= datetime.fromisoformat(data_fim))
    
    pedidos = query.all()
    
    # Calculate average preparation times
    tempos = []
    for pedido in pedidos:
        if pedido.iniciado_em and pedido.finalizado_em:
            tempo_preparo = (pedido.finalizado_em - pedido.iniciado_em).total_seconds() / 60  # minutes
            tempos.append({
                "pedido_id": pedido.id,
                "numero_pedido": pedido.numero_pedido,
                "tempo_preparo_minutos": round(tempo_preparo, 2),
                "tempo_estimado_minutos": pedido.tempo_estimado_minutos,
                "diferenca_estimativa": round(tempo_preparo - (pedido.tempo_estimado_minutos or 0), 2)
            })
    
    tempo_medio = sum([t["tempo_preparo_minutos"] for t in tempos]) / len(tempos) if tempos else 0
    
    return {
        "total_pedidos": len(tempos),
        "tempo_medio_preparo": round(tempo_medio, 2),
        "pedidos": tempos
    }

@router.get("/analytics/performance-estacoes")
def get_analytics_performance_estacoes(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(EstacaoKDS)
    estacoes = query.all()
    
    performance = []
    for estacao in estacoes:
        pedidos_query = db.query(PedidoKDS).filter(PedidoKDS.estacao_id == estacao.id)
        
        if data_inicio:
            pedidos_query = pedidos_query.filter(PedidoKDS.created_at >= datetime.fromisoformat(data_inicio))
        if data_fim:
            pedidos_query = pedidos_query.filter(PedidoKDS.created_at <= datetime.fromisoformat(data_fim))
        
        total_pedidos = pedidos_query.count()
        pedidos_prontos = pedidos_query.filter(PedidoKDS.status == StatusPedidoKDS.PRONTO).count()
        pedidos_entregues = pedidos_query.filter(PedidoKDS.status == StatusPedidoKDS.ENTREGUE).count()
        
        performance.append({
            "estacao_id": estacao.id,
            "nome": estacao.nome,
            "tipo": estacao.tipo.value,
            "total_pedidos": total_pedidos,
            "pedidos_prontos": pedidos_prontos,
            "pedidos_entregues": pedidos_entregues,
            "taxa_conclusao": round((pedidos_entregues / total_pedidos * 100) if total_pedidos > 0 else 0, 2)
        })
    
    return performance