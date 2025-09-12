#!/usr/bin/env python3
"""
Backend Simples com JWT e Refresh Token
Para testar o sistema de autenticação completo
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional
import uvicorn

# Configurações
SECRET_KEY = "sua-chave-secreta-super-segura-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 horas
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Modelos
class LoginRequest(BaseModel):
    cpf: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None

# App
app = FastAPI(title="Backend JWT Simples")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Usuário de teste
TEST_USER = {
    "id": 1,
    "cpf": "00000000000",
    "senha": "admin123",
    "nome": "Administrador Sistema",
    "email": "admin@sistema.com",
    "tipo": "admin"
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Criar JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, allow_expired: bool = False):
    """Verificar e decodificar token"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_exp": not allow_expired}
        )
        return payload
    except JWTError:
        return None

@app.get("/")
def root():
    return {
        "message": "Backend JWT Simples",
        "endpoints": {
            "login": "POST /api/auth/login",
            "refresh": "POST /api/auth/refresh",
            "me": "GET /api/usuarios/me",
            "health": "GET /api/health"
        }
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "backend-jwt-simple"}

@app.post("/api/auth/login", response_model=Token)
def login(request: LoginRequest):
    """Login com CPF e senha"""
    print(f"[LOGIN] Tentativa para CPF: {request.cpf}")
    
    # Validar credenciais
    if request.cpf != TEST_USER["cpf"] or request.senha != TEST_USER["senha"]:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Criar token
    access_token = create_access_token(
        data={"sub": TEST_USER["cpf"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    print(f"[LOGIN] Sucesso! Token gerado para: {TEST_USER['nome']}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": TEST_USER["id"],
            "cpf": TEST_USER["cpf"],
            "nome": TEST_USER["nome"],
            "email": TEST_USER["email"],
            "tipo": TEST_USER["tipo"]
        }
    }

@app.post("/api/auth/refresh", response_model=Token)
def refresh_token(request: Request):
    """Refresh do token JWT"""
    # Extrair token do header
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "").replace("bearer ", "")
    print(f"[REFRESH] Tentando renovar token...")
    
    # Verificar token (permitindo expirado)
    payload = verify_token(token, allow_expired=True)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    cpf = payload.get("sub")
    if cpf != TEST_USER["cpf"]:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    # Verificar período de graça (7 dias)
    exp = payload.get("exp")
    if exp:
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        grace_period = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        if now > exp_datetime + grace_period:
            raise HTTPException(
                status_code=401, 
                detail="Token expirado além do período de graça"
            )
    
    # Criar novo token
    new_token = create_access_token(
        data={"sub": TEST_USER["cpf"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    print(f"[REFRESH] Novo token gerado com sucesso!")
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }

@app.get("/api/usuarios/me")
def get_current_user(request: Request):
    """Obter usuário atual (endpoint protegido)"""
    # Extrair token
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "").replace("bearer ", "")
    
    # Verificar token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    cpf = payload.get("sub")
    if cpf != TEST_USER["cpf"]:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    return {
        "id": TEST_USER["id"],
        "cpf": TEST_USER["cpf"],
        "nome": TEST_USER["nome"],
        "email": TEST_USER["email"],
        "tipo": TEST_USER["tipo"],
        "ativo": True
    }

@app.get("/api/eventos")
def list_events(request: Request):
    """Listar eventos (endpoint protegido)"""
    # Verificar autenticação
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "").replace("bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    # Retornar eventos mock
    return [
        {
            "id": 1,
            "nome": "Evento de Teste",
            "data": "2025-09-15",
            "local": "São Paulo",
            "participantes": 150
        },
        {
            "id": 2,
            "nome": "Workshop JWT",
            "data": "2025-09-20",
            "local": "Online",
            "participantes": 500
        }
    ]

if __name__ == "__main__":
    print("\n" + "="*60)
    print("    BACKEND JWT SIMPLES")
    print("="*60)
    print("Servidor rodando em: http://localhost:8000")
    print("Documentação: http://localhost:8000/docs")
    print("\nCredenciais de teste:")
    print("  CPF: 00000000000")
    print("  Senha: admin123")
    print("\nEndpoints principais:")
    print("  POST /api/auth/login - Login")
    print("  POST /api/auth/refresh - Refresh token")
    print("  GET /api/usuarios/me - Dados do usuário")
    print("  GET /api/eventos - Listar eventos")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)