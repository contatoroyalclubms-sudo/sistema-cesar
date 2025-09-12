from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario
from ..models.meep_models import MEEPEvento
from ..schemas.meep_schemas import MEEPEventoResponse, MEEPSyncRequest, MEEPSyncResponse
from ..services.meep_client import MEEPClient

router = APIRouter(prefix="/api/meep", tags=["MEEP Integration"])

@router.get("/eventos", response_model=List[MEEPEventoResponse])
async def listar_eventos_meep(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista eventos do MEEP"""
    eventos = db.query(MEEPEvento).all()
    return eventos

@router.post("/sync", response_model=MEEPSyncResponse)
async def sincronizar_meep(
    request: MEEPSyncRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Sincroniza com MEEP (mock)"""
    async with MEEPClient() as client:
        mock_eventos = await client.get_mock_eventos()
        
        eventos_sincronizados = 0
        for evento_data in mock_eventos:
            existe = db.query(MEEPEvento).filter(
                MEEPEvento.meep_id == evento_data["meep_id"]
            ).first()
            
            if not existe:
                novo_evento = MEEPEvento(
                    meep_id=evento_data["meep_id"],
                    nome=evento_data["nome"],
                    data_inicio=datetime.fromisoformat(evento_data["data_inicio"]),
                    data_fim=datetime.fromisoformat(evento_data["data_fim"]),
                    local=evento_data["local"],
                    cidade=evento_data["cidade"],
                    estado=evento_data["estado"],
                    total_inscritos=evento_data["total_inscritos"],
                    total_presentes=evento_data["total_presentes"],
                    total_vendas=evento_data["total_vendas"],
                    taxa_conversao=(evento_data["total_presentes"] / evento_data["total_inscritos"] * 100),
                    sincronizado=True,
                    ultima_sincronizacao=datetime.utcnow()
                )
                db.add(novo_evento)
                eventos_sincronizados += 1
        
        db.commit()
        
        return {
            "status": "concluído",
            "eventos_sincronizados": eventos_sincronizados,
            "participantes_sincronizados": 0,
            "erros": [],
            "tempo_execucao": 1.5
        }

@router.get("/sync/status")
async def status_sincronizacao(
    current_user: Usuario = Depends(get_current_user)
):
    """Status da sincronização"""
    return {
        "status": "idle",
        "ultima_sincronizacao": datetime.utcnow().isoformat(),
        "proxima_sincronizacao": None
    }
