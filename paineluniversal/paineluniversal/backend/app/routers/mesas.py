from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import json
from datetime import datetime

from ..database import get_db
from ..models_clean import MesaEvento, StatusMesa, TipoMesa
from ..schemas_kds_mesas import (
    MesaEventoCreate, MesaEventoUpdate, MesaEventoResponse,
    MesaEventoReservaCreate, MesaEventoReservaUpdate, MesaEventoReservaResponse
)
from ..auth import get_current_user

router = APIRouter(tags=["Mesas"])

# WebSocket connection manager for tables
class MesasConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connections_by_event: dict = {}

    async def connect(self, websocket: WebSocket, evento_id: int = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if evento_id:
            if evento_id not in self.connections_by_event:
                self.connections_by_event[evento_id] = []
            self.connections_by_event[evento_id].append(websocket)

    def disconnect(self, websocket: WebSocket, evento_id: int = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if evento_id and evento_id in self.connections_by_event:
            if websocket in self.connections_by_event[evento_id]:
                self.connections_by_event[evento_id].remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.active_connections.remove(connection)

    async def broadcast_to_event(self, evento_id: int, message: dict):
        if evento_id in self.connections_by_event:
            for connection in self.connections_by_event[evento_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    self.connections_by_event[evento_id].remove(connection)

manager = MesasConnectionManager()

# WebSocket endpoint
@router.websocket("/ws/{evento_id}")
async def websocket_endpoint(websocket: WebSocket, evento_id: int):
    await manager.connect(websocket, evento_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Broadcast update to all connections in this event
            await manager.broadcast_to_event(evento_id, {
                "type": "update",
                "evento_id": evento_id,
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, evento_id)

# CRUD Mesas
@router.post("/", response_model=MesaEventoResponse)
async def create_mesa(
    mesa: MesaEventoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_mesa = MesaEvento(**mesa.dict())
    db.add(db_mesa)
    db.commit()
    db.refresh(db_mesa)
    
    # Broadcast new table
    await manager.broadcast_to_event(db_mesa.evento_id, {
        "type": "new_table",
        "mesa_id": db_mesa.id,
        "data": {
            "id": db_mesa.id,
            "numero": db_mesa.numero,
            "nome": db_mesa.nome,
            "tipo": db_mesa.tipo.value,
            "status": db_mesa.status.value,
            "capacidade": db_mesa.capacidade,
            "posicao_x": db_mesa.posicao_x,
            "posicao_y": db_mesa.posicao_y
        }
    })
    
    return db_mesa

@router.get("/", response_model=List[MesaEventoResponse])
def list_mesas(
    evento_id: Optional[int] = Query(None),
    status: Optional[StatusMesa] = Query(None),
    tipo: Optional[TipoMesa] = Query(None),
    numero: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(MesaEvento)
    
    if evento_id:
        query = query.filter(MesaEvento.evento_id == evento_id)
    if status:
        query = query.filter(MesaEvento.status == status)
    if tipo:
        query = query.filter(MesaEvento.tipo == tipo)
    if numero:
        query = query.filter(MesaEvento.numero.ilike(f"%{numero}%"))
        
    return query.order_by(MesaEvento.numero).all()

@router.get("/{mesa_id}", response_model=MesaEventoResponse)
def get_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mesa = db.query(MesaEvento).filter(MesaEvento.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    return mesa

@router.put("/{mesa_id}", response_model=MesaEventoResponse)
async def update_mesa(
    mesa_id: int,
    mesa_update: MesaEventoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mesa = db.query(MesaEvento).filter(MesaEvento.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    old_status = mesa.status
    
    for key, value in mesa_update.dict(exclude_unset=True).items():
        setattr(mesa, key, value)
    
    db.commit()
    db.refresh(mesa)
    
    # Broadcast status change
    await manager.broadcast_to_event(mesa.evento_id, {
        "type": "table_update",
        "mesa_id": mesa.id,
        "old_status": old_status.value if old_status else None,
        "new_status": mesa.status.value,
        "data": {
            "id": mesa.id,
            "numero": mesa.numero,
            "nome": mesa.nome,
            "tipo": mesa.tipo.value,
            "status": mesa.status.value,
            "capacidade": mesa.capacidade,
            "posicao_x": mesa.posicao_x,
            "posicao_y": mesa.posicao_y
        },
        "timestamp": datetime.now().isoformat()
    })
    
    return mesa

@router.delete("/{mesa_id}")
async def delete_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mesa = db.query(MesaEvento).filter(MesaEvento.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    evento_id = mesa.evento_id
    
    db.delete(mesa)
    db.commit()
    
    # Broadcast table deletion
    await manager.broadcast_to_event(evento_id, {
        "type": "table_deleted",
        "mesa_id": mesa_id,
        "timestamp": datetime.now().isoformat()
    })
    
    return {"message": "Mesa excluída com sucesso"}

# Layout Management
@router.post("/layout/{evento_id}")
async def update_layout(
    evento_id: int,
    layout_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update multiple table positions at once"""
    try:
        for mesa_data in layout_data.get("mesas", []):
            mesa = db.query(MesaEvento).filter(
                MesaEvento.id == mesa_data["id"],
                MesaEvento.evento_id == evento_id
            ).first()
            
            if mesa:
                mesa.posicao_x = mesa_data.get("posicao_x", mesa.posicao_x)
                mesa.posicao_y = mesa_data.get("posicao_y", mesa.posicao_y)
                if "rotacao" in mesa_data:
                    mesa.rotacao = mesa_data["rotacao"]
        
        db.commit()
        
        # Broadcast layout update
        await manager.broadcast_to_event(evento_id, {
            "type": "layout_update",
            "evento_id": evento_id,
            "layout_data": layout_data,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"message": "Layout atualizado com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar layout: {str(e)}")

@router.get("/layout/{evento_id}")
def get_layout(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get complete table layout for an event"""
    mesas = db.query(MesaEvento).filter(MesaEvento.evento_id == evento_id).all()
    
    return {
        "evento_id": evento_id,
        "mesas": [
            {
                "id": mesa.id,
                "numero": mesa.numero,
                "nome": mesa.nome,
                "tipo": mesa.tipo.value,
                "status": mesa.status.value,
                "capacidade": mesa.capacidade,
                "posicao_x": mesa.posicao_x,
                "posicao_y": mesa.posicao_y,
                "largura": mesa.largura,
                "altura": mesa.altura,
                "rotacao": mesa.rotacao,
                "cor": mesa.cor,
                "ativo": mesa.ativo
            }
            for mesa in mesas
        ]
    }

# Status Operations
@router.put("/{mesa_id}/status")
async def update_mesa_status(
    mesa_id: int,
    new_status: StatusMesa,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mesa = db.query(MesaEvento).filter(MesaEvento.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    old_status = mesa.status
    mesa.status = new_status
    
    # Update timestamps based on status
    now = datetime.now()
    if new_status == StatusMesa.OCUPADA and old_status != StatusMesa.OCUPADA:
        mesa.ocupada_em = now
    elif new_status == StatusMesa.LIVRE and old_status != StatusMesa.LIVRE:
        mesa.liberada_em = now
    elif new_status == StatusMesa.RESERVADA and old_status != StatusMesa.RESERVADA:
        mesa.reservada_em = now
    
    db.commit()
    
    # Broadcast status change
    await manager.broadcast_to_event(mesa.evento_id, {
        "type": "status_change",
        "mesa_id": mesa.id,
        "old_status": old_status.value,
        "new_status": new_status.value,
        "timestamp": now.isoformat()
    })
    
    return {"message": f"Status da mesa atualizado para {new_status.value}"}

# Batch Operations
@router.post("/batch-create")
async def batch_create_mesas(
    evento_id: int,
    quantidade: int,
    tipo: TipoMesa,
    capacidade: int = 4,
    prefixo: str = "Mesa",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create multiple tables at once"""
    if quantidade > 100:
        raise HTTPException(status_code=400, detail="Máximo de 100 mesas por batch")
    
    try:
        # Get highest table number for this event
        last_mesa = db.query(MesaEvento).filter(
            MesaEvento.evento_id == evento_id
        ).order_by(MesaEvento.numero.desc()).first()
        
        start_number = 1
        if last_mesa and last_mesa.numero.isdigit():
            start_number = int(last_mesa.numero) + 1
        
        created_mesas = []
        for i in range(quantidade):
            numero = str(start_number + i)
            nome = f"{prefixo} {numero}"
            
            mesa = MesaEvento(
                numero=numero,
                nome=nome,
                tipo=tipo,
                capacidade=capacidade,
                evento_id=evento_id,
                status=StatusMesa.LIVRE,
                posicao_x=100 + (i % 10) * 120,  # Basic grid layout
                posicao_y=100 + (i // 10) * 120,
                largura=100,
                altura=100,
                ativo=True
            )
            
            db.add(mesa)
            created_mesas.append(mesa)
        
        db.commit()
        
        # Refresh all created tables
        for mesa in created_mesas:
            db.refresh(mesa)
        
        # Broadcast batch creation
        await manager.broadcast_to_event(evento_id, {
            "type": "batch_created",
            "evento_id": evento_id,
            "quantidade": quantidade,
            "mesas": [
                {
                    "id": mesa.id,
                    "numero": mesa.numero,
                    "nome": mesa.nome,
                    "tipo": mesa.tipo.value,
                    "status": mesa.status.value,
                    "capacidade": mesa.capacidade
                }
                for mesa in created_mesas
            ],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "message": f"{quantidade} mesas criadas com sucesso",
            "mesas": [
                {
                    "id": mesa.id,
                    "numero": mesa.numero,
                    "nome": mesa.nome
                }
                for mesa in created_mesas
            ]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar mesas: {str(e)}")

@router.delete("/batch-delete")
async def batch_delete_mesas(
    evento_id: int,
    mesa_ids: List[int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete multiple tables at once"""
    try:
        deleted_count = db.query(MesaEvento).filter(
            MesaEvento.id.in_(mesa_ids),
            MesaEvento.evento_id == evento_id
        ).delete(synchronize_session=False)
        
        db.commit()
        
        # Broadcast batch deletion
        await manager.broadcast_to_event(evento_id, {
            "type": "batch_deleted",
            "evento_id": evento_id,
            "mesa_ids": mesa_ids,
            "deleted_count": deleted_count,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"message": f"{deleted_count} mesas excluídas com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao excluir mesas: {str(e)}")

# Analytics
@router.get("/analytics/{evento_id}")
def get_mesas_analytics(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get table analytics for an event"""
    mesas = db.query(MesaEvento).filter(MesaEvento.evento_id == evento_id).all()
    
    if not mesas:
        return {
            "total_mesas": 0,
            "por_status": {},
            "por_tipo": {},
            "taxa_ocupacao": 0,
            "capacidade_total": 0
        }
    
    # Count by status
    status_counts = {}
    for status in StatusMesa:
        status_counts[status.value] = len([m for m in mesas if m.status == status])
    
    # Count by type
    tipo_counts = {}
    for tipo in TipoMesa:
        tipo_counts[tipo.value] = len([m for m in mesas if m.tipo == tipo])
    
    # Calculate occupancy rate
    mesas_ocupadas = len([m for m in mesas if m.status == StatusMesa.OCUPADA])
    mesas_ativas = len([m for m in mesas if m.ativo])
    taxa_ocupacao = (mesas_ocupadas / mesas_ativas * 100) if mesas_ativas > 0 else 0
    
    # Total capacity
    capacidade_total = sum([m.capacidade for m in mesas if m.ativo])
    
    return {
        "total_mesas": len(mesas),
        "mesas_ativas": mesas_ativas,
        "por_status": status_counts,
        "por_tipo": tipo_counts,
        "taxa_ocupacao": round(taxa_ocupacao, 2),
        "capacidade_total": capacidade_total,
        "mesas_ocupadas": mesas_ocupadas,
        "mesas_livres": status_counts.get("LIVRE", 0),
        "mesas_reservadas": status_counts.get("RESERVADA", 0)
    }

# Templates
@router.get("/templates")
def get_mesa_templates():
    """Get predefined table layout templates"""
    return {
        "templates": [
            {
                "id": "restaurant_small",
                "nome": "Restaurante Pequeno",
                "descricao": "Layout para restaurante pequeno (20 mesas)",
                "mesas": [
                    {"numero": f"{i+1}", "tipo": "NORMAL", "capacidade": 4, "posicao_x": 100 + (i % 5) * 120, "posicao_y": 100 + (i // 5) * 120}
                    for i in range(20)
                ]
            },
            {
                "id": "bar_counter",
                "nome": "Balcão de Bar",
                "descricao": "Layout de balcão com mesas altas",
                "mesas": [
                    {"numero": f"B{i+1}", "tipo": "BALCAO", "capacidade": 2, "posicao_x": 100 + i * 80, "posicao_y": 100}
                    for i in range(10)
                ]
            },
            {
                "id": "event_hall",
                "nome": "Salão de Eventos",
                "descricao": "Layout para eventos com mesas redondas",
                "mesas": [
                    {"numero": f"R{i+1}", "tipo": "REDONDA", "capacidade": 8, "posicao_x": 150 + (i % 6) * 150, "posicao_y": 150 + (i // 6) * 150}
                    for i in range(24)
                ]
            }
        ]
    }

@router.post("/apply-template")
async def apply_template(
    evento_id: int,
    template_id: str,
    clear_existing: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Apply a predefined template to an event"""
    templates = get_mesa_templates()["templates"]
    template = next((t for t in templates if t["id"] == template_id), None)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    try:
        # Clear existing tables if requested
        if clear_existing:
            db.query(MesaEvento).filter(MesaEvento.evento_id == evento_id).delete()
        
        # Create tables from template
        created_mesas = []
        for mesa_data in template["mesas"]:
            mesa = MesaEvento(
                numero=mesa_data["numero"],
                nome=f"Mesa {mesa_data['numero']}",
                tipo=TipoMesa(mesa_data["tipo"]),
                capacidade=mesa_data["capacidade"],
                evento_id=evento_id,
                status=StatusMesa.LIVRE,
                posicao_x=mesa_data["posicao_x"],
                posicao_y=mesa_data["posicao_y"],
                largura=100,
                altura=100,
                ativo=True
            )
            db.add(mesa)
            created_mesas.append(mesa)
        
        db.commit()
        
        # Broadcast template applied
        await manager.broadcast_to_event(evento_id, {
            "type": "template_applied",
            "evento_id": evento_id,
            "template_id": template_id,
            "template_nome": template["nome"],
            "mesas_criadas": len(created_mesas),
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "message": f"Template '{template['nome']}' aplicado com sucesso",
            "mesas_criadas": len(created_mesas)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao aplicar template: {str(e)}")

# QR Code Generation
@router.get("/{mesa_id}/qrcode")
def generate_mesa_qrcode(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate QR code for table (for digital menu access)"""
    mesa = db.query(MesaEvento).filter(MesaEvento.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    # Generate QR code URL pointing to digital menu
    base_url = "https://paineluniversal.com"  # Replace with actual domain
    qr_url = f"{base_url}/menu/{mesa.evento_id}?mesa={mesa.id}"
    
    return {
        "mesa_id": mesa.id,
        "numero": mesa.numero,
        "nome": mesa.nome,
        "qr_url": qr_url,
        "qr_code_data": qr_url  # Frontend can generate QR code image from this
    }