# 📦 BACKEND COMPLETO - ARQUIVOS IMPORTANTES (11/09/2025)

## 🆕 ARQUIVOS CRIADOS HOJE

### 1. `local_auth_server.py`
```python
"""
Servidor de autenticação local para desenvolvimento
Sistema simplificado sem dependências externas
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import datetime
import uvicorn

app = FastAPI(title="Local Auth Server", version="1.0.0")

# Configuração CORS ultra permissiva para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Configuração JWT
SECRET_KEY = "desenvolvimento-local-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Base de dados mock
MOCK_USERS = {
    "00000000000": {
        "cpf": "00000000000",
        "nome": "Admin Local",
        "email": "admin@local.com",
        "senha": "admin123",
        "tipo": "admin",
        "id": 1
    },
    "11111111111": {
        "cpf": "11111111111",
        "nome": "Promoter Teste",
        "email": "promoter@local.com",
        "senha": "promoter123",
        "tipo": "promoter",
        "id": 2
    },
    "22222222222": {
        "cpf": "22222222222",
        "nome": "Cliente Teste",
        "email": "cliente@local.com",
        "senha": "cliente123",
        "tipo": "cliente",
        "id": 3
    }
}

# Modelos Pydantic
class LoginRequest(BaseModel):
    cpf: str
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class RegisterRequest(BaseModel):
    cpf: str
    nome: str
    email: str
    senha: str
    tipo: str = "cliente"

# Funções auxiliares
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    cpf = payload.get("cpf")
    if cpf not in MOCK_USERS:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    return MOCK_USERS[cpf]

# Rotas
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Servidor de autenticação local rodando",
        "users": [
            {"cpf": "00000000000", "senha": "admin123", "tipo": "admin"},
            {"cpf": "11111111111", "senha": "promoter123", "tipo": "promoter"},
            {"cpf": "22222222222", "senha": "cliente123", "tipo": "cliente"}
        ]
    }

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Remove caracteres especiais do CPF
    cpf = request.cpf.replace(".", "").replace("-", "").strip()
    
    # Verifica se o usuário existe
    if cpf not in MOCK_USERS:
        raise HTTPException(
            status_code=401,
            detail="CPF ou senha incorretos"
        )
    
    user = MOCK_USERS[cpf]
    
    # Verifica a senha
    if request.senha != user["senha"]:
        raise HTTPException(
            status_code=401,
            detail="CPF ou senha incorretos"
        )
    
    # Cria o token
    access_token = create_access_token({
        "cpf": user["cpf"],
        "tipo": user["tipo"],
        "id": user["id"],
        "nome": user["nome"]
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "cpf": user["cpf"],
            "nome": user["nome"],
            "email": user["email"],
            "tipo": user["tipo"]
        }
    }

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    cpf = request.cpf.replace(".", "").replace("-", "").strip()
    
    if cpf in MOCK_USERS:
        raise HTTPException(
            status_code=400,
            detail="CPF já cadastrado"
        )
    
    # Adiciona novo usuário
    new_id = len(MOCK_USERS) + 1
    MOCK_USERS[cpf] = {
        "cpf": cpf,
        "nome": request.nome,
        "email": request.email,
        "senha": request.senha,
        "tipo": request.tipo,
        "id": new_id
    }
    
    # Cria token para o novo usuário
    access_token = create_access_token({
        "cpf": cpf,
        "tipo": request.tipo,
        "id": new_id,
        "nome": request.nome
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_id,
            "cpf": cpf,
            "nome": request.nome,
            "email": request.email,
            "tipo": request.tipo
        }
    }

@app.get("/api/auth/verify-token")
async def verify_token_route(current_user: dict = Depends(get_current_user)):
    return {
        "valid": True,
        "user": current_user
    }

@app.post("/api/auth/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    # Cria novo token
    access_token = create_access_token({
        "cpf": current_user["cpf"],
        "tipo": current_user["tipo"],
        "id": current_user["id"],
        "nome": current_user["nome"]
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}

# Rotas mock para evitar erros 404
@app.get("/api/eventos")
async def get_eventos():
    return []

@app.get("/api/usuarios")
async def get_usuarios(current_user: dict = Depends(get_current_user)):
    if current_user["tipo"] != "admin":
        raise HTTPException(status_code=403, detail="Sem permissão")
    return list(MOCK_USERS.values())

@app.get("/api/meep/sync/auto/status")
@app.post("/api/meep/sync/auto/status")
async def meep_sync_status():
    return {
        "is_running": False,
        "last_sync": None,
        "next_sync": None,
        "sync_interval": 300,
        "stats": {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0
        }
    }

if __name__ == "__main__":
    print("=" * 60)
    print("SERVIDOR DE AUTENTICAÇÃO LOCAL")
    print("=" * 60)
    print("\nUsuários disponíveis para teste:")
    print("- CPF: 00000000000 | Senha: admin123 | Tipo: admin")
    print("- CPF: 11111111111 | Senha: promoter123 | Tipo: promoter")
    print("- CPF: 22222222222 | Senha: cliente123 | Tipo: cliente")
    print("\nServidor rodando em: http://localhost:8000")
    print("Documentação: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## ✏️ ARQUIVOS MODIFICADOS HOJE

### 2. `.env` (Atualizado)
```env
# Configuração Local de Desenvolvimento
DATABASE_URL=sqlite:///./paineluniversal.db
SECRET_KEY=desenvolvimento-secret-key-2025
JWT_SECRET=jwt-secret-desenvolvimento-2025

# Servidor
HOST=0.0.0.0
PORT=8003

# Redis (opcional para dev)
REDIS_URL=redis://localhost:6379

# Frontend
FRONTEND_URL=http://localhost:5174
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=
EMAIL_PASSWORD=

# WhatsApp (opcional)
WHATSAPP_TOKEN=
N8N_WEBHOOK_URL=

# Analytics
ENABLE_ANALYTICS=false
```

### 3. `app/routers/meep_router.py` (Linha 503 modificada)
```python
# Antes:
@router.get("/sync/auto/status")

# Depois:
@router.api_route("/sync/auto/status", methods=["GET", "POST"])
async def get_auto_sync_status():
    """Status da sincronização automática"""
    from ..services.meep_auto_sync import get_sync_status
    return get_sync_status()
```

## 📁 ESTRUTURA COMPLETA DO BACKEND

```
paineluniversal/backend/
├── .env                          # ✅ Modificado hoje
├── .env.example                  
├── .env.production               
├── local_auth_server.py          # ✅ Criado hoje
├── auth_server.py                # Servidor principal (porta 8003)
├── requirements.txt              
├── pyproject.toml                
├── app/
│   ├── main.py                   
│   ├── models.py                 
│   ├── schemas.py                
│   ├── database.py               
│   ├── auth.py                   
│   ├── auth_functions.py         
│   ├── routers/
│   │   ├── auth.py               
│   │   ├── eventos.py            
│   │   ├── usuarios.py           
│   │   ├── pdv.py                
│   │   ├── checkins.py           
│   │   ├── produtos.py           
│   │   ├── estoque.py            
│   │   ├── financeiro.py         
│   │   ├── meep_router.py        # ✅ Modificado hoje
│   │   └── ... (30+ routers)
│   └── services/
│       ├── meep_client.py        
│       ├── meep_sync.py          
│       ├── meep_auto_sync.py     
│       └── ... (outros serviços)
└── tests/
    └── ... (testes)
```

## 🔧 COMANDOS PARA INICIAR O BACKEND

### Servidor Principal (auth_server.py)
```bash
cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend
python auth_server.py
# Roda na porta 8003
```

### Servidor Mock (local_auth_server.py)
```bash
cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend
python local_auth_server.py
# Roda na porta 8000
```

## 🔑 CREDENCIAIS

### auth_server.py (Porta 8003)
- CPF: `00000000000`
- Senha: `0000`

### local_auth_server.py (Porta 8000)
- CPF: `00000000000` | Senha: `admin123`
- CPF: `11111111111` | Senha: `promoter123`
- CPF: `22222222222` | Senha: `cliente123`

## 📋 CHECKLIST DE ARQUIVOS DO BACKEND

- [x] `local_auth_server.py` - Servidor mock criado
- [x] `.env` - Variáveis de ambiente atualizadas
- [x] `meep_router.py` - Endpoint corrigido
- [x] `auth_server.py` - Servidor principal funcionando
- [x] CORS configurado para todas as portas locais
- [x] JWT configurado com 24h de expiração
- [x] SQLite configurado para desenvolvimento

## 💾 BACKUP DOS ARQUIVOS

Para fazer backup completo do backend:

```bash
# Criar pasta de backup
mkdir C:\Backup_Backend_11092025

# Copiar todos os arquivos importantes
xcopy "C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend" "C:\Backup_Backend_11092025" /E /I /Y

# Ou copiar apenas os modificados hoje
copy "C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend\local_auth_server.py" C:\Backup_Backend_11092025\
copy "C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend\.env" C:\Backup_Backend_11092025\
```

---

**Data:** 11/09/2025
**Status:** ✅ Backend funcionando perfeitamente
**Portas:** 8003 (principal) | 8000 (mock)