#!/usr/bin/env python3
"""
Servidor Mock MEEP - Simula API MEEP com dados realistas
Para testar a integração completa localmente
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import uvicorn
import random
import uuid
from typing import Optional, List, Dict, Any

app = FastAPI(title="MEEP Mock Server", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dados simulados
MOCK_TOKEN = "mock_bearer_token_12345"
MOCK_EVENTS = []
MOCK_ATTENDEES = []
MOCK_CHECKINS = []
MOCK_TRANSACTIONS = []

# Gerar dados de teste
def generate_mock_data():
    """Gerar dados realistas para teste"""
    global MOCK_EVENTS, MOCK_ATTENDEES, MOCK_CHECKINS, MOCK_TRANSACTIONS
    
    # Eventos
    MOCK_EVENTS = [
        {
            "id": f"evt_{i}",
            "name": f"Festival de Verão {2025 if i < 3 else 2024}",
            "date": (datetime.now() + timedelta(days=30-i*10)).isoformat(),
            "location": ["São Paulo", "Rio de Janeiro", "Belo Horizonte"][i % 3],
            "capacity": 5000 + i * 1000,
            "tickets_sold": 3000 + i * 500,
            "status": "active" if i < 3 else "completed",
            "revenue": 150000 + i * 25000
        }
        for i in range(5)
    ]
    
    # Participantes
    MOCK_ATTENDEES = []
    for event in MOCK_EVENTS[:3]:  # Apenas eventos ativos
        for j in range(100):
            MOCK_ATTENDEES.append({
                "id": f"att_{event['id']}_{j}",
                "event_id": event["id"],
                "name": f"Participante {j}",
                "cpf": f"{random.randint(10000000000, 99999999999)}",
                "email": f"user{j}@email.com",
                "ticket_type": ["VIP", "NORMAL", "MEIA"][j % 3],
                "status": "confirmed",
                "check_in": random.choice([True, False])
            })
    
    # Check-ins
    checked_in_attendees = [a for a in MOCK_ATTENDEES if a["check_in"]]
    MOCK_CHECKINS = [
        {
            "id": f"chk_{att['id']}",
            "attendee_id": att["id"],
            "event_id": att["event_id"],
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "method": random.choice(["qrcode", "cpf", "manual"]),
            "gate": f"Gate {random.randint(1, 4)}"
        }
        for att in checked_in_attendees
    ]
    
    # Transações
    MOCK_TRANSACTIONS = [
        {
            "id": f"txn_{i}",
            "event_id": MOCK_EVENTS[i % len(MOCK_EVENTS)]["id"],
            "amount": random.randint(50, 500) * 10,
            "status": "completed",
            "payment_method": ["credit_card", "pix", "debit"][i % 3],
            "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "description": f"Ingresso - {['VIP', 'NORMAL', 'MEIA'][i % 3]}"
        }
        for i in range(50)
    ]

# Gerar dados ao iniciar
generate_mock_data()

# Modelos
class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    user: Optional[str] = None
    password: str

class LoginResponse(BaseModel):
    token: str
    user: Dict[str, Any]
    expires_at: str

# Endpoints

@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "service": "MEEP Mock Server"}

@app.post("/api/auth/login", response_model=LoginResponse)
@app.post("/auth/login", response_model=LoginResponse)
@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Mock login"""
    # Aceitar qualquer login para teste
    return LoginResponse(
        token=MOCK_TOKEN,
        user={
            "id": "user_123",
            "email": request.email or request.username or request.user,
            "name": "Usuário Teste",
            "role": "admin"
        },
        expires_at=(datetime.now() + timedelta(hours=24)).isoformat()
    )

@app.get("/api/events")
async def get_events(
    limit: int = 100,
    offset: int = 0,
    authorization: Optional[str] = Header(None)
):
    """Listar eventos"""
    return MOCK_EVENTS[offset:offset+limit]

@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    """Obter evento específico"""
    event = next((e for e in MOCK_EVENTS if e["id"] == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event

@app.get("/api/events/{event_id}/attendees")
async def get_attendees(
    event_id: str,
    limit: int = 100,
    offset: int = 0
):
    """Listar participantes de um evento"""
    attendees = [a for a in MOCK_ATTENDEES if a["event_id"] == event_id]
    return attendees[offset:offset+limit]

@app.get("/api/attendees/cpf/{cpf}")
async def get_attendee_by_cpf(cpf: str):
    """Buscar participante por CPF"""
    attendee = next((a for a in MOCK_ATTENDEES if a["cpf"] == cpf), None)
    if not attendee:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return attendee

@app.get("/api/checkins")
async def get_checkins(
    event_id: Optional[str] = None,
    limit: int = 100
):
    """Listar check-ins"""
    checkins = MOCK_CHECKINS
    if event_id:
        checkins = [c for c in checkins if c["event_id"] == event_id]
    return checkins[:limit]

@app.post("/api/checkins")
async def create_checkin(data: Dict[str, Any]):
    """Criar check-in"""
    checkin = {
        "id": f"chk_{uuid.uuid4().hex[:8]}",
        "attendee_id": data.get("attendee_id"),
        "event_id": data.get("event_id"),
        "timestamp": datetime.now().isoformat(),
        "method": data.get("method", "manual"),
        "gate": data.get("gate", "Gate 1")
    }
    MOCK_CHECKINS.append(checkin)
    return checkin

@app.get("/api/transactions")
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """Listar transações"""
    transactions = MOCK_TRANSACTIONS
    if status:
        transactions = [t for t in transactions if t["status"] == status]
    return transactions[:limit]

@app.get("/api/events/{event_id}/analytics")
async def get_analytics(event_id: str):
    """Analytics de um evento"""
    event = next((e for e in MOCK_EVENTS if e["id"] == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    attendees = [a for a in MOCK_ATTENDEES if a["event_id"] == event_id]
    checkins = [c for c in MOCK_CHECKINS if c["event_id"] == event_id]
    
    return {
        "event_id": event_id,
        "total_tickets": event["capacity"],
        "tickets_sold": event["tickets_sold"],
        "occupancy_rate": (event["tickets_sold"] / event["capacity"]) * 100,
        "total_checkins": len(checkins),
        "checkin_rate": (len(checkins) / event["tickets_sold"]) * 100 if event["tickets_sold"] > 0 else 0,
        "revenue": event["revenue"],
        "average_ticket_price": event["revenue"] / event["tickets_sold"] if event["tickets_sold"] > 0 else 0,
        "by_ticket_type": {
            "VIP": len([a for a in attendees if a["ticket_type"] == "VIP"]),
            "NORMAL": len([a for a in attendees if a["ticket_type"] == "NORMAL"]),
            "MEIA": len([a for a in attendees if a["ticket_type"] == "MEIA"])
        },
        "checkin_timeline": {
            "last_hour": random.randint(10, 50),
            "last_6_hours": random.randint(100, 300),
            "last_24_hours": len(checkins)
        }
    }

@app.get("/api/analytics/dashboard")
async def analytics_dashboard(period: str = "today"):
    """Dashboard geral de analytics"""
    total_events = len(MOCK_EVENTS)
    active_events = len([e for e in MOCK_EVENTS if e["status"] == "active"])
    total_attendees = len(MOCK_ATTENDEES)
    total_checkins = len(MOCK_CHECKINS)
    total_revenue = sum(e["revenue"] for e in MOCK_EVENTS)
    
    return {
        "period": period,
        "metrics": {
            "total_events": total_events,
            "active_events": active_events,
            "total_attendees": total_attendees,
            "total_checkins": total_checkins,
            "total_revenue": total_revenue,
            "average_occupancy": 65.3,
            "average_checkin_rate": 78.5
        },
        "trends": {
            "events_growth": 15.2,
            "revenue_growth": 23.5,
            "attendees_growth": 18.7
        },
        "top_events": MOCK_EVENTS[:3],
        "recent_checkins": MOCK_CHECKINS[:10]
    }

@app.get("/api/stats")
async def get_stats():
    """Estatísticas gerais"""
    return {
        "total_events": len(MOCK_EVENTS),
        "total_attendees": len(MOCK_ATTENDEES),
        "total_checkins": len(MOCK_CHECKINS),
        "total_revenue": sum(e["revenue"] for e in MOCK_EVENTS),
        "active_events": len([e for e in MOCK_EVENTS if e["status"] == "active"])
    }

if __name__ == "__main__":
    print("="*60)
    print("    MEEP MOCK SERVER - TESTE LOCAL")
    print("="*60)
    print()
    print("Servidor iniciando em: http://localhost:8002")
    print("Documentação: http://localhost:8002/docs")
    print()
    print("Este servidor simula a API MEEP com dados realistas")
    print("para testar a integração completa localmente.")
    print()
    print(f"Dados gerados:")
    print(f"  - {len(MOCK_EVENTS)} eventos")
    print(f"  - {len(MOCK_ATTENDEES)} participantes")
    print(f"  - {len(MOCK_CHECKINS)} check-ins")
    print(f"  - {len(MOCK_TRANSACTIONS)} transações")
    print()
    print("Pressione CTRL+C para parar")
    print("="*60)
    
    uvicorn.run(app, host="127.0.0.1", port=8002)