#!/usr/bin/env python
"""
Servidor de teste para MEEP Integration
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime

# Configurar path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, get_db
from app.models import Base, MEEPIntegration, MEEPAnalytics, Usuario, Evento

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Criar app
app = FastAPI(title="MEEP Test Server", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "MEEP Test Server"}

# MEEP Endpoints
@app.post("/api/meep/integrate")
def create_meep_integration(
    evento_id: int,
    meep_event_id: str,
    api_key: str,
    db: Session = Depends(get_db)
):
    """Criar integração MEEP para um evento"""
    # Verificar se já existe
    existing = db.query(MEEPIntegration).filter(
        MEEPIntegration.evento_id == evento_id
    ).first()
    
    if existing:
        # Atualizar
        existing.meep_event_id = meep_event_id
        existing.api_key = api_key
        existing.updated_at = datetime.utcnow()
        existing.sync_status = "active"
        db.commit()
        db.refresh(existing)
        return existing
    
    # Criar nova
    integration = MEEPIntegration(
        evento_id=evento_id,
        meep_event_id=meep_event_id,
        api_key=api_key,
        sync_status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    return {
        "id": integration.id,
        "evento_id": integration.evento_id,
        "meep_event_id": integration.meep_event_id,
        "sync_status": integration.sync_status,
        "message": "Integração MEEP criada com sucesso"
    }

@app.get("/api/meep/integration/{evento_id}")
def get_meep_integration(evento_id: int, db: Session = Depends(get_db)):
    """Obter integração MEEP de um evento"""
    integration = db.query(MEEPIntegration).filter(
        MEEPIntegration.evento_id == evento_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    
    return {
        "id": integration.id,
        "evento_id": integration.evento_id,
        "meep_event_id": integration.meep_event_id,
        "sync_status": integration.sync_status,
        "last_sync": integration.last_sync
    }

@app.post("/api/meep/analytics/{evento_id}")
def create_meep_analytics(
    evento_id: int,
    total_requests: int = 100,
    unique_visitors: int = 50,
    db: Session = Depends(get_db)
):
    """Criar analytics MEEP para teste"""
    analytics = MEEPAnalytics(
        evento_id=evento_id,
        total_requests=total_requests,
        unique_visitors=unique_visitors,
        conversion_rate=25.5,
        avg_session_time=180.0,
        top_sources={"google": 30, "direct": 20},
        heat_map_data={"clicks": {"button1": 50}},
        captured_at=datetime.utcnow()
    )
    
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    
    return {
        "id": analytics.id,
        "evento_id": analytics.evento_id,
        "total_requests": analytics.total_requests,
        "unique_visitors": analytics.unique_visitors,
        "message": "Analytics MEEP criado com sucesso"
    }

@app.get("/api/meep/analytics/{evento_id}")
def get_meep_analytics(evento_id: int, db: Session = Depends(get_db)):
    """Obter analytics MEEP de um evento"""
    analytics = db.query(MEEPAnalytics).filter(
        MEEPAnalytics.evento_id == evento_id
    ).order_by(MEEPAnalytics.captured_at.desc()).first()
    
    if not analytics:
        return {
            "evento_id": evento_id,
            "total_requests": 0,
            "unique_visitors": 0,
            "message": "Nenhum analytics encontrado"
        }
    
    return {
        "id": analytics.id,
        "evento_id": analytics.evento_id,
        "total_requests": analytics.total_requests,
        "unique_visitors": analytics.unique_visitors,
        "conversion_rate": analytics.conversion_rate,
        "avg_session_time": analytics.avg_session_time,
        "top_sources": analytics.top_sources
    }

@app.get("/api/meep/status")
def get_meep_status():
    """Status do serviço MEEP"""
    return {
        "status": "online",
        "version": "1.0.0",
        "features": [
            "integration",
            "analytics",
            "capture",
            "real_time"
        ],
        "message": "MEEP Test Server funcionando"
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MEEP TEST SERVER")
    print("="*60)
    print("Servidor rodando em: http://localhost:8004")
    print("Documentação: http://localhost:8004/docs")
    print("\nEndpoints disponíveis:")
    print("  - POST /api/meep/integrate")
    print("  - GET  /api/meep/integration/{evento_id}")
    print("  - POST /api/meep/analytics/{evento_id}")
    print("  - GET  /api/meep/analytics/{evento_id}")
    print("  - GET  /api/meep/status")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8004)