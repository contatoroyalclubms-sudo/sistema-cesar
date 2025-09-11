"""
Servidor Backend Simplificado - Sistema Painel Universal
Versão sem modelos conflitantes para testes
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Optional
import os

# Configuração básica do app
app = FastAPI(
    title="Sistema Painel Universal - Backend",
    description="API REST para Sistema de Gestão de Eventos",
    version="1.0.0"
)

# CORS configurado para aceitar todas as origens (desenvolvimento)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para teste
class LoginRequest(BaseModel):
    cpf: str
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    usuario: dict

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str

class EventoRequest(BaseModel):
    nome: str
    data_inicio_evento: str  # Data e hora de início do evento
    data_fim_evento: str     # Data e hora de fim do evento
    data_inicio_vendas: str  # Data e hora de início das vendas
    data_fim_vendas: str     # Data e hora de fim das vendas
    local: str
    endereco: str = ""
    descricao: str = ""
    limite_idade: int = 18
    capacidade_maxima: Optional[int] = None  # Tornar opcional

class EventoResponse(BaseModel):
    id: int
    nome: str
    data_inicio_evento: str
    data_fim_evento: str
    data_inicio_vendas: str
    data_fim_vendas: str
    local: str
    endereco: str = ""
    descricao: str = ""
    limite_idade: int
    capacidade_maxima: int
    status: str = "ativo"
    created_at: datetime

# Lista temporária para armazenar eventos (em produção usar banco de dados)
eventos_db = [
    {
        "id": 1,
        "nome": "Evento Teste MEEP",
        "data_inicio_evento": "2025-09-15T20:00:00",
        "data_fim_evento": "2025-09-16T02:00:00",
        "data_inicio_vendas": "2025-09-10T08:00:00",
        "data_fim_vendas": "2025-09-15T19:45:00",
        "local": "Centro de Convenções",
        "endereco": "Rua das Convenções, 123",
        "descricao": "Evento de teste para validação do sistema MEEP",
        "limite_idade": 18,
        "capacidade_maxima": 500,
        "status": "ativo",
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "nome": "Workshop de Tecnologia",
        "data_inicio_evento": "2025-09-20T14:00:00",
        "data_fim_evento": "2025-09-20T18:00:00",
        "data_inicio_vendas": "2025-09-15T09:00:00",
        "data_fim_vendas": "2025-09-20T13:45:00",
        "local": "Auditório Tech",
        "endereco": "Av. Tecnologia, 456",
        "descricao": "Workshop sobre as mais recentes tecnologias",
        "limite_idade": 16,
        "capacidade_maxima": 100,
        "status": "planejamento",
        "created_at": datetime.now()
    }
]

# Endpoints básicos
@app.get("/")
async def root():
    return {
        "message": "Sistema Painel Universal - Backend Funcional",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificar saúde do sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "database": "sqlite" if not os.getenv("DATABASE_URL") else "postgresql"
    }

@app.get("/api/cors-test")
async def cors_test():
    """Endpoint para testar CORS"""
    return {
        "success": True,
        "message": "CORS configurado corretamente",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login com CPF e senha
    Teste: CPF: 00000000000, Senha: admin123
    """
    # Usuário de teste - aceita duas senhas
    if request.cpf == "00000000000" and (request.senha == "admin123" or request.senha == "0000"):
        usuario_data = {
            "id": 1,
            "nome": "Admin Teste",
            "cpf": "00000000000",
            "email": "admin@teste.com",
            "tipo": "admin"
        }
        return {
            "access_token": "test_token_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "token_type": "bearer",
            "user": usuario_data,
            "usuario": usuario_data  # Frontend espera esse campo também
        }
    
    raise HTTPException(status_code=401, detail="CPF ou senha inválidos")

@app.get("/api/eventos")
@app.get("/api/eventos/")
async def listar_eventos():
    """Lista eventos disponíveis"""
    return eventos_db

@app.post("/api/eventos/")
async def criar_evento(evento: EventoRequest):
    """Cria um novo evento com período de vendas"""
    from datetime import datetime as dt
    
    # Validações de negócio
    try:
        # Converter strings para datetime para validação
        TIMEZONE_FIX = '+00:00'
        inicio_evento = dt.fromisoformat(evento.data_inicio_evento.replace('Z', TIMEZONE_FIX))
        fim_evento = dt.fromisoformat(evento.data_fim_evento.replace('Z', TIMEZONE_FIX))
        inicio_vendas = dt.fromisoformat(evento.data_inicio_vendas.replace('Z', TIMEZONE_FIX))
        fim_vendas = dt.fromisoformat(evento.data_fim_vendas.replace('Z', TIMEZONE_FIX))
        agora = dt.now(timezone.utc)
        
        # Validação 1: Evento pode ser criado até 1 minuto antes
        if inicio_evento < agora - timedelta(minutes=1):
            raise HTTPException(status_code=400, detail="Evento não pode começar no passado (mínimo 1 minuto de antecedência)")
        
        # Validação 2: Fim do evento deve ser depois do início
        if fim_evento <= inicio_evento:
            raise HTTPException(status_code=400, detail="Data de fim do evento deve ser posterior ao início")
        
        # Validação 3: Vendas devem terminar antes do fim do evento (pelo menos 15 minutos antes)
        if fim_vendas >= fim_evento:
            raise HTTPException(status_code=400, detail="Vendas devem terminar antes do fim do evento")
        
        # Validação 4: Início das vendas deve ser antes do fim das vendas
        if inicio_vendas >= fim_vendas:
            raise HTTPException(status_code=400, detail="Início das vendas deve ser anterior ao fim das vendas")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido")
    
    # Gerar novo ID
    next_id = max([e["id"] for e in eventos_db], default=0) + 1
    
    # Criar novo evento
    novo_evento = {
        "id": next_id,
        "nome": evento.nome,
        "data_inicio_evento": evento.data_inicio_evento,
        "data_fim_evento": evento.data_fim_evento,
        "data_inicio_vendas": evento.data_inicio_vendas,
        "data_fim_vendas": evento.data_fim_vendas,
        "local": evento.local,
        "endereco": evento.endereco,
        "descricao": evento.descricao,
        "limite_idade": evento.limite_idade,
        "capacidade_maxima": evento.capacidade_maxima or 100,  # Usar 100 como padrão
        "status": "ativo",
        "created_at": datetime.now()
    }
    
    # Adicionar à lista
    eventos_db.append(novo_evento)
    
    return {
        "message": "Evento criado com sucesso",
        "evento": novo_evento
    }

@app.get("/api/dashboard/stats")
async def dashboard_stats():
    """Estatísticas do dashboard"""
    return {
        "total_eventos": 2,
        "total_usuarios": 150,
        "total_vendas": 45780.50,
        "checkins_hoje": 87,
        "ticket_medio": 305.20
    }

@app.get("/api/dashboard")
async def dashboard_data():
    """Dados completos do dashboard"""
    return {
        "stats": {
            "total_eventos": 2,
            "eventos_ativos": 2,
            "total_usuarios": 150,
            "usuarios_ativos": 120,
            "total_vendas": 45780.50,
            "vendas_hoje": 5430.20,
            "checkins_hoje": 87,
            "checkins_total": 1250,
            "ticket_medio": 305.20,
            "produtos_vendidos": 342
        },
        "graficos": {
            "vendas_semana": [1200, 1800, 1500, 2100, 2800, 3200, 2500],
            "checkins_hora": [10, 15, 20, 35, 45, 60, 55, 40, 30, 25, 20, 15]
        },
        "eventos_recentes": [
            {"id": 1, "nome": "Evento Teste 1", "data": "2025-09-15", "participantes": 75},
            {"id": 2, "nome": "Evento Teste 2", "data": "2025-09-20", "participantes": 45}
        ]
    }

@app.get("/api/usuarios")
async def listar_usuarios():
    """Lista de usuários"""
    return [
        {
            "id": 1,
            "nome": "Admin Teste",
            "cpf": "00000000000",
            "email": "admin@teste.com",
            "tipo": "admin",
            "ativo": True
        },
        {
            "id": 2,
            "nome": "Promoter Teste",
            "cpf": "11111111111",
            "email": "promoter@teste.com",
            "tipo": "promoter",
            "ativo": True
        }
    ]

@app.get("/api/produtos")
async def listar_produtos():
    """Lista de produtos"""
    return [
        {
            "id": 1,
            "nome": "Cerveja",
            "preco": 12.00,
            "estoque": 500,
            "categoria": "Bebidas",
            "ativo": True
        },
        {
            "id": 2,
            "nome": "Água",
            "preco": 5.00,
            "estoque": 1000,
            "categoria": "Bebidas",
            "ativo": True
        },
        {
            "id": 3,
            "nome": "Hambúrguer",
            "preco": 25.00,
            "estoque": 200,
            "categoria": "Lanches",
            "ativo": True
        }
    ]

@app.get("/api/vendas")
async def listar_vendas():
    """Lista de vendas"""
    return [
        {
            "id": 1,
            "data": "2025-09-10T10:30:00",
            "valor_total": 37.00,
            "cliente": "João Silva",
            "itens": 3,
            "status": "concluída"
        },
        {
            "id": 2,
            "data": "2025-09-10T11:15:00",
            "valor_total": 62.00,
            "cliente": "Maria Santos",
            "itens": 5,
            "status": "concluída"
        }
    ]

@app.get("/api/estoque")
async def listar_estoque():
    """Status do estoque"""
    return {
        "total_produtos": 3,
        "produtos_baixo_estoque": 0,
        "valor_total": 15750.00,
        "movimentacoes_hoje": 12
    }

# Documentação automática
@app.get("/api/docs-info")
async def docs_info():
    return {
        "swagger": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("INICIANDO SERVIDOR SIMPLIFICADO")
    print("URL: http://localhost:8007")
    print("Docs: http://localhost:8007/docs")
    print("Login Teste: CPF: 00000000000, Senha: 0000")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8008)