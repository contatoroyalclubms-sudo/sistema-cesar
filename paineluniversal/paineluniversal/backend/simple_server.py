#!/usr/bin/env python
"""
Servidor simplificado para desenvolvimento rápido
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Sistema V6 - Dev Server")

# CORS ultra-permissivo para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos básicos
class LoginRequest(BaseModel):
    cpf: str
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# Rotas básicas
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Sistema V6 Backend Running"}

@app.get("/api")
def api_root():
    return {"status": "ok", "version": "6.0.0"}

@app.post("/api/auth/login")
def login(request: LoginRequest):
    """Login simplificado para testes"""
    # Usuário de teste
    if request.cpf == "00000000000" and request.senha == "admin123":
        return LoginResponse(
            access_token="dev-token-admin-123",
            user={
                "id": 1,
                "cpf": "00000000000",
                "nome": "Admin Dev",
                "email": "admin@dev.com",
                "tipo": "admin"
            }
        )
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.get("/api/eventos")
def list_eventos():
    """Lista de eventos mock"""
    return [
        {
            "id": 1,
            "nome": "Evento Teste 1",
            "data_evento": "2025-09-15T20:00:00",
            "local": "Local Teste",
            "status": "ativo"
        },
        {
            "id": 2,
            "nome": "Evento Teste 2",
            "data_evento": "2025-09-20T22:00:00",
            "local": "Outro Local",
            "status": "ativo"
        }
    ]

@app.get("/api/dashboard/stats")
def dashboard_stats():
    """Estatísticas mock do dashboard"""
    return {
        "total_eventos": 15,
        "total_usuarios": 250,
        "vendas_hoje": 45,
        "receita_mes": 15000.00
    }

if __name__ == "__main__":
    print("Iniciando servidor simplificado na porta 8000...")
    print("Credenciais de teste: CPF: 00000000000 | Senha: admin123")
    uvicorn.run(app, host="0.0.0.0", port=8000)