"""
MEEP API Router - Endpoints de Integração
Kit Legal - Sem código proprietário
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..services.meep_client import MEEPClient
from ..services.meep_sync import MeepSyncService, SyncDirection
from ..services.meep_mapper import (
    map_event, map_ticket, map_attendee, 
    map_checkin, map_transaction, map_analytics
)
from ..schemas.meep_models import (
    EventCreate, EventUpdate, EventResponse,
    TicketCreate, TicketResponse,
    AttendeeCreate, AttendeeResponse,
    CheckinCreate, CheckinResponse,
    TransactionResponse,
    AnalyticsResponse,
    SyncRequest, SyncResponse,
    IntegrationStatus, HealthCheckResponse,
    WebhookEvent, WebhookResponse,
    BatchImportRequest, BatchImportResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/meep",
    tags=["MEEP Integration"],
    responses={404: {"description": "Not found"}},
)

# Dependências

def get_meep_client() -> MEEPClient:
    """Obter cliente MEEP"""
    client = MEEPClient()
    if not client.login():
        raise HTTPException(status_code=401, detail="Falha na autenticação MEEP")
    return client

def get_sync_service() -> MeepSyncService:
    """Obter serviço de sincronização"""
    return MeepSyncService()

# Health & Status

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Verificar saúde da integração"""
    client = MEEPClient()
    
    health = {
        "status": "healthy",
        "meep_api": client.health_check(),
        "database": True,  # TODO: Verificar conexão real
        "cache": False,  # TODO: Verificar Redis se configurado
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }
    
    if not health["meep_api"]:
        health["status"] = "degraded"
    
    return health

@router.get("/status", response_model=IntegrationStatus)
async def integration_status(
    sync_service: MeepSyncService = Depends(get_sync_service)
):
    """Status da integração MEEP"""
    last_sync = sync_service.get_sync_status()
    
    return IntegrationStatus(
        connected=True,  # TODO: Verificar conexão real
        last_sync=last_sync.get("completed_at") if last_sync else None,
        sync_status=last_sync.get("status") if last_sync else None,
        total_events=0,  # TODO: Contar do banco
        total_attendees=0,  # TODO: Contar do banco
        total_checkins=0,  # TODO: Contar do banco
        total_transactions=0,  # TODO: Contar do banco
        errors=[],
        warnings=[]
    )

# Sync Operations

@router.post("/sync", response_model=SyncResponse)
async def sync_data(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    sync_service: MeepSyncService = Depends(get_sync_service)
):
    """Sincronizar dados com MEEP"""
    direction_map = {
        "meep_to_local": SyncDirection.MEEP_TO_LOCAL,
        "local_to_meep": SyncDirection.LOCAL_TO_MEEP,
        "bidirectional": SyncDirection.BIDIRECTIONAL
    }
    
    direction = direction_map.get(request.direction, SyncDirection.BIDIRECTIONAL)
    
    # Executar sincronização em background
    background_tasks.add_task(
        sync_service.sync_all,
        direction=direction
    )
    
    return SyncResponse(
        status="started",
        started_at=datetime.utcnow(),
        completed_at=None,
        direction=request.direction,
        events={"synced": 0, "errors": 0},
        tickets={"synced": 0, "errors": 0},
        attendees={"synced": 0, "errors": 0},
        checkins={"synced": 0, "errors": 0},
        transactions={"synced": 0, "errors": 0},
        analytics={"synced": 0, "errors": 0}
    )

@router.post("/sync/events/{event_id}")
async def sync_event(
    event_id: int,
    background_tasks: BackgroundTasks,
    sync_service: MeepSyncService = Depends(get_sync_service)
):
    """Sincronizar evento específico"""
    background_tasks.add_task(
        sync_service.sync_events,
        event_ids=[event_id]
    )
    
    return {"message": f"Sincronização do evento {event_id} iniciada"}

# Events

@router.get("/events", response_model=List[EventResponse])
async def list_events(
    client: MEEPClient = Depends(get_meep_client),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Listar eventos do MEEP"""
    try:
        response = client.get("/api/events", params={"limit": limit, "offset": offset})
        if response.status_code == 200:
            meep_events = response.json()
            return [map_event(e) for e in meep_events]
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar eventos")
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    client: MEEPClient = Depends(get_meep_client)
):
    """Obter evento específico do MEEP"""
    try:
        response = client.get(f"/api/events/{event_id}")
        if response.status_code == 200:
            return map_event(response.json())
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar evento")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter evento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Tickets

@router.get("/events/{event_id}/tickets", response_model=List[TicketResponse])
async def list_tickets(
    event_id: str,
    client: MEEPClient = Depends(get_meep_client)
):
    """Listar ingressos de um evento"""
    try:
        response = client.get(f"/api/events/{event_id}/tickets")
        if response.status_code == 200:
            meep_tickets = response.json()
            return [map_ticket(t) for t in meep_tickets]
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar ingressos")
    except Exception as e:
        logger.error(f"Erro ao listar ingressos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Attendees

@router.get("/events/{event_id}/attendees", response_model=List[AttendeeResponse])
async def list_attendees(
    event_id: str,
    client: MEEPClient = Depends(get_meep_client),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Listar participantes de um evento"""
    try:
        params = {"limit": limit, "offset": offset}
        response = client.get(f"/api/events/{event_id}/attendees", params=params)
        if response.status_code == 200:
            meep_attendees = response.json()
            return [map_attendee(a) for a in meep_attendees]
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar participantes")
    except Exception as e:
        logger.error(f"Erro ao listar participantes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attendees/cpf/{cpf}", response_model=AttendeeResponse)
async def get_attendee_by_cpf(
    cpf: str,
    client: MEEPClient = Depends(get_meep_client)
):
    """Buscar participante por CPF"""
    try:
        # Normalizar CPF
        import re
        cpf_clean = re.sub(r'\D', '', cpf)
        
        response = client.get(f"/api/attendees/cpf/{cpf_clean}")
        if response.status_code == 200:
            return map_attendee(response.json())
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Participante não encontrado")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar participante")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar participante: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Check-ins

@router.get("/checkins", response_model=List[CheckinResponse])
async def list_checkins(
    client: MEEPClient = Depends(get_meep_client),
    event_id: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Listar check-ins"""
    try:
        params = {"limit": limit}
        if event_id:
            params["event_id"] = event_id
        if since:
            params["since"] = since.isoformat()
        
        response = client.get("/api/checkins", params=params)
        if response.status_code == 200:
            meep_checkins = response.json()
            return [map_checkin(c) for c in meep_checkins]
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar check-ins")
    except Exception as e:
        logger.error(f"Erro ao listar check-ins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkins", response_model=CheckinResponse)
async def create_checkin(
    checkin: CheckinCreate,
    client: MEEPClient = Depends(get_meep_client)
):
    """Criar check-in"""
    try:
        checkin_data = checkin.model_dump()
        response = client.post("/api/checkins", json=checkin_data)
        
        if response.status_code == 201:
            return map_checkin(response.json())
        elif response.status_code == 409:
            raise HTTPException(status_code=409, detail="Check-in já realizado")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao criar check-in")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar check-in: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Transactions

@router.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    client: MEEPClient = Depends(get_meep_client),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Listar transações"""
    try:
        params = {"limit": limit}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        if status:
            params["status"] = status
        
        response = client.get("/api/transactions", params=params)
        if response.status_code == 200:
            meep_transactions = response.json()
            return [map_transaction(t) for t in meep_transactions]
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar transações")
    except Exception as e:
        logger.error(f"Erro ao listar transações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics

@router.get("/events/{event_id}/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    event_id: str,
    client: MEEPClient = Depends(get_meep_client)
):
    """Obter analytics de um evento"""
    try:
        response = client.get(f"/api/events/{event_id}/analytics")
        if response.status_code == 200:
            return map_analytics(response.json())
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Analytics não disponível")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar analytics")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/dashboard")
async def analytics_dashboard(
    client: MEEPClient = Depends(get_meep_client),
    period: str = Query("today", regex="^(today|week|month|year)$")
):
    """Dashboard de analytics"""
    try:
        response = client.get("/api/analytics/dashboard", params={"period": period})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Erro ao buscar dashboard")
    except Exception as e:
        logger.error(f"Erro ao obter dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhooks

@router.post("/webhook", response_model=WebhookResponse)
async def receive_webhook(
    event: WebhookEvent,
    background_tasks: BackgroundTasks
):
    """Receber webhook do MEEP"""
    logger.info(f"Webhook recebido: {event.event_type}")
    
    # TODO: Validar assinatura do webhook
    # if not validate_webhook_signature(event.signature):
    #     raise HTTPException(status_code=401, detail="Assinatura inválida")
    
    # Processar evento em background
    background_tasks.add_task(process_webhook_event, event)
    
    return WebhookResponse(
        received=True,
        processed=False,
        message=f"Evento {event.event_type} recebido"
    )

async def process_webhook_event(event: WebhookEvent):
    """Processar evento webhook"""
    try:
        if event.event_type == "checkin.created":
            # Processar novo check-in
            pass
        elif event.event_type == "transaction.paid":
            # Processar pagamento confirmado
            pass
        elif event.event_type == "attendee.registered":
            # Processar novo participante
            pass
        # Adicionar mais tipos conforme necessário
        
        logger.info(f"Evento {event.event_type} processado")
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")

# Batch Operations

@router.post("/batch/import", response_model=BatchImportResponse)
async def batch_import(
    request: BatchImportRequest,
    background_tasks: BackgroundTasks,
    sync_service: MeepSyncService = Depends(get_sync_service)
):
    """Importação em lote"""
    # Validar dados
    errors = []
    warnings = []
    
    if request.validate_only:
        # Apenas validar sem importar
        for idx, item in enumerate(request.data):
            try:
                if request.entity_type == "events":
                    EventCreate(**item)
                elif request.entity_type == "tickets":
                    TicketCreate(**item)
                elif request.entity_type == "attendees":
                    AttendeeCreate(**item)
            except Exception as e:
                errors.append({"index": idx, "error": str(e)})
        
        return BatchImportResponse(
            total=len(request.data),
            imported=0,
            updated=0,
            errors=errors,
            warnings=warnings
        )
    
    # Importar dados em background
    background_tasks.add_task(
        import_batch_data,
        request.entity_type,
        request.data,
        request.update_existing
    )
    
    return BatchImportResponse(
        total=len(request.data),
        imported=0,
        updated=0,
        errors=[],
        warnings=[{"message": "Importação iniciada em background"}]
    )

async def import_batch_data(
    entity_type: str,
    data: List[Dict[str, Any]],
    update_existing: bool
):
    """Importar dados em lote"""
    # TODO: Implementar importação real
    logger.info(f"Importando {len(data)} {entity_type}")

# Real-time Updates

@router.get("/realtime/{event_id}")
async def realtime_updates(
    event_id: int,
    background_tasks: BackgroundTasks,
    sync_service: MeepSyncService = Depends(get_sync_service),
    interval: int = Query(60, ge=10, le=300)
):
    """Iniciar atualizações em tempo real"""
    background_tasks.add_task(
        sync_service.real_time_sync,
        event_id,
        interval
    )
    
    return {
        "message": f"Sincronização em tempo real iniciada para evento {event_id}",
        "interval": interval
    }

# Auto Sync Control

@router.post("/sync/auto/start")
async def start_auto_sync(
    background_tasks: BackgroundTasks
):
    """Iniciar sincronização automática"""
    from ..services.meep_auto_sync import start_auto_sync as start_sync
    background_tasks.add_task(start_sync)
    return {"message": "Sincronização automática iniciada"}

@router.post("/sync/auto/stop")
async def stop_auto_sync():
    """Parar sincronização automática"""
    from ..services.meep_auto_sync import stop_auto_sync as stop_sync
    await stop_sync()
    return {"message": "Sincronização automática parada"}

@router.api_route("/sync/auto/status", methods=["GET", "POST"])
async def get_auto_sync_status():
    """Status da sincronização automática"""
    from ..services.meep_auto_sync import get_sync_status
    return get_sync_status()

@router.post("/sync/auto/force")
async def force_sync_now(
    background_tasks: BackgroundTasks
):
    """Forçar sincronização imediata"""
    from ..services.meep_auto_sync import auto_sync_service
    background_tasks.add_task(auto_sync_service.force_sync)
    return {"message": "Sincronização forçada iniciada"}

# Statistics

@router.get("/stats")
async def get_statistics(
    client: MEEPClient = Depends(get_meep_client)
):
    """Estatísticas gerais da integração"""
    try:
        response = client.get("/api/stats")
        if response.status_code == 200:
            return response.json()
        else:
            # Retornar estatísticas vazias se não disponível
            return {
                "total_events": 0,
                "total_attendees": 0,
                "total_checkins": 0,
                "total_revenue": 0,
                "active_events": 0
            }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {
            "error": str(e),
            "total_events": 0,
            "total_attendees": 0,
            "total_checkins": 0,
            "total_revenue": 0,
            "active_events": 0
        }